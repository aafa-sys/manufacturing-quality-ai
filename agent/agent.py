import os
import db
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agent.tools import TOOLS
from agent.prompts import SYSTEM_PROMPT
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ServerError,ClientError

class ApiError(Exception):
    """Base class untuk semua API error yang sudah ditangani."""

class QuotaExceededError(ApiError):
    """Kuota API habis (429)."""

class ApiAuthError(ApiError):
    """API key salah atau permission ditolak (401/403)."""

class ApiNotFoundError(ApiError):
    """Model atau endpoint tidak ditemukan (404)."""

class ApiUnexpectedError(ApiError):
    """Error API lain yang tidak terklasifikasi."""

chat_history = []


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),
                      http_options=types.HttpOptions(timeout=30_000))

@retry(
    retry=retry_if_exception_type(ServerError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def _panggil_gemini_internal(model, contents, config):
    """Hanya handle transient error (ServerError) dengan retry."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )


def panggil_gemini_aman(model, contents, config):
    """Wrapper: bedakan jenis error, jangan sampai crash."""
    try:
        return _panggil_gemini_internal(model, contents, config)
    
    except ClientError as e:
        # ClientError = 4xx. Bisa 429, 401, 403, 404, dll.
        status_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
        
        if status_code == 429:
            print("[API ERROR] 429 — kuota/rate limit habis")
            raise QuotaExceededError(
                "Kuota API habis. Layanan akan pulih dalam beberapa jam. "
                "Silakan coba lagi nanti atau hubungi admin."
            ) from e
        
        elif status_code in (401, 403):
            print(f"[API ERROR] {status_code} — auth/permission issue")
            raise ApiAuthError(
                "Konfigurasi API bermasalah. Hubungi admin untuk memperbaiki API key atau permission."
            ) from e
        
        elif status_code == 404:
            print(f"[API ERROR] 404 — model/endpoint tidak ditemukan")
            raise ApiNotFoundError(
                "Model AI tidak tersedia. Hubungi admin untuk mengecek konfigurasi model."
            ) from e
        
        else:
            print(f"[API ERROR] {status_code} — client error tidak terduga")
            raise ApiUnexpectedError(
                f"Terjadi kesalahan pada layanan AI (kode {status_code}). Coba lagi nanti."
            ) from e
    
    except Exception as e:
        # Error lain (network, parsing, dll)
        print(f"[API ERROR] Unexpected: {type(e).__name__}: {e}")
        raise ApiUnexpectedError(
            "Layanan AI tidak dapat dihubungi. Periksa koneksi internet dan coba lagi."
        ) from e


def cari_id_dari_batch_no(batch_no):
    """cari B000001 dari BT26G001"""
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT batch_id FROM public.batch_production WHERE batch_no = %s",(batch_no,)
            )

            hasil = cur.fetchone()
            if hasil:
                return hasil[0]
            return None
    finally:
        conn.close()
    
def normalisasi_batch_id(batch_id):
    """normalisasi batch id.
    B1/B01/B001/BOOOOO1 > B000001
    jika format tidak di kenal kembalikan apa adanya"""

    if not batch_id:
        return batch_id
    batch_id = str(batch_id).strip().upper()

    if batch_id.startswith("BT"):
        hasil_db =  cari_id_dari_batch_no(batch_id)
        if hasil_db:
            return hasil_db
        return batch_id

  

    if batch_id.startswith("B") and batch_id[1:].isdigit():
        angka = batch_id[1:] .lstrip("0") or "0"
        return f"B{angka.zfill(6)}"

    return batch_id 


def jalankan_agent(pertanyaan_user: str):
    try:
        function_declarations = [
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters_json_schema={
                    "type": "object",
                    "properties": tool["parameters"],
                    "required": tool["required"]
                }
            ) for tool in TOOLS
        ]
        tools = [types.Tool(function_declarations=function_declarations)]

        chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=pertanyaan_user)]))

        print(f"[USER] {pertanyaan_user}")

        response = panggil_gemini_aman(
            model="gemini-3.5-flash",
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
        )

        jumlah_loop = 0
        tool_call_tracker = {}

        while response.function_calls and jumlah_loop < 6:
            list_hasil = []

            for function_call in response.function_calls:
                nama_tool = function_call.name
                parameter = dict(function_call.args)
                if "batch_id" in parameter:
                    parameter["batch_id"] = normalisasi_batch_id(parameter["batch_id"])

                print(f"[AGENT] Memutuskan memanggil tool: '{nama_tool}'")

                fungsi_python = next((t["function"] for t in TOOLS if t["name"] == nama_tool), None)
                if fungsi_python:
                    tool_key = (nama_tool, frozenset(parameter.items()))

                    if tool_key in tool_call_tracker:
                        hasil_tool = tool_call_tracker[tool_key]
                        print(f"[TOOL CACHED] {nama_tool} — pakai hasil sebelumnya")
                    else:
                        try:
                            hasil_tool = fungsi_python(**parameter)
                            print(f"[TOOL] Hasil didapat dari {nama_tool}")
                            tool_call_tracker[tool_key] = hasil_tool
                        except Exception as e:
                            print(f"[TOOL ERROR] {nama_tool}: {type(e).__name__}: {e}")
                            hasil_tool = (
                                f"Tool '{nama_tool}' gagal: sistem sedang gangguan. "
                                f"JANGAN panggil tool ini lagi di percobaan berikutnya. "
                                f"Sampaikan ke user bahwa fitur ini tidak tersedia, "
                                f"lalu tawarkan alternatif lain jika ada."
                            )
                            tool_call_tracker[tool_key] = hasil_tool
                else:
                    hasil_tool = f"Tool '{nama_tool}' tidak tersedia."
                    print(f"[TOOL] Tool '{nama_tool}' tidak dikenal.")

                list_hasil.append(
                    types.Part.from_function_response(
                        name=nama_tool,
                        response={"result": hasil_tool}
                    )
                )
            jumlah_loop += 1

            chat_history.append(response.candidates[0].content)

            response = panggil_gemini_aman(
                model="gemini-3.5-flash",
                contents=chat_history + [types.Content(parts=list_hasil)],
                config=types.GenerateContentConfig(
                    tools=tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
            )

        if jumlah_loop >= 6 and response.function_calls:
            return "maaf, sistem mengalami kendala teknis saat memproses permintaan anda. coba beberapa saat lagi. jika masalah berlanjut, hubungi pihak terkait"

        print("[AGENT] Selesai menganalisis, tidak butuh tool lagi.")
        return response.text

    except QuotaExceededError as e:
        return f" {e}"

    except ApiAuthError as e:
        return f" {e}"

    except ApiNotFoundError as e:
        return f"{e}"

    except ApiUnexpectedError as e:
        return f" {e}"

    except ApiError as e:
        return f" {e}"

    except Exception as e:
        print(f"[FATAL] {type(e).__name__}: {e}")
        return " Terjadi kesalahan internal. Hubungi admin."


if __name__ == "__main__":
    pertanyaan ="cek batch BT26G001 dong"
    print("="*50)
    print("MENJALANKAN AI AGENT...")
    print("="*50)
    jawaban_akhir = jalankan_agent(pertanyaan)
    print("\n" + "="*50)
    print("--- JAWABAN AKHIR DARI AGENT ---")
    print(jawaban_akhir)
    print("="*50)