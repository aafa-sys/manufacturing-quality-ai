import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agent.tools import TOOLS
from agent.prompts import SYSTEM_PROMPT
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ServerError

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@retry(
    retry=retry_if_exception_type(ServerError), # Hanya retry kalau error server (503)
    stop=stop_after_attempt(5),                 # Coba maksimal 5 kali
    wait=wait_exponential(multiplier=1, min=2, max=10) # Jeda 2s, 4s, 8s, 10s
)
def panggil_gemini_aman(model, contents, config):
    """Fungsi pembungkus untuk manggil Gemini dengan fitur retry."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

def jalankan_agent(pertanyaan_user: str) :
    function_declarations = [
        types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters_json_schema={
                "type": "object",
                "type": "object",
                "properties": tool["parameters"],
                "requiered": tool["required"]
            }
        ) for tool in TOOLS
    ]
    tools = [types.Tool(function_declarations=function_declarations)]

    # 2. Kirim pertanyaan ke Gemini (pakai model yang valid)
    print(f"[USER] {pertanyaan_user}")
    response = panggil_gemini_aman(
        model="gemini-3.5-flash",  # Model terbaru yang aktif
        contents=pertanyaan_user,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
    )

    # 3. Agent Loop
    while response.function_calls:
      hasil = []
    
    for function_call in response.function_calls:
        nama_tool = function_call.name
        parameter = dict(function_call.args)
        
        print(f"[AGENT] Memutuskan memanggil tool: '{nama_tool}'")
        
        # Cari fungsi Python yang cocok
        fungsi_python = next((t["function"] for t in TOOLS if t["name"] == nama_tool), None)
        
        if fungsi_python:
            try:
                hasil_tool = fungsi_python(parameter)
                print(f"[TOOL] Hasil didapat dari {nama_tool}")
            except Exception as e:
                hasil_tool = f"Error saat menjalankan tool: {e}"
        else:
            hasil_tool = f"Error: Tool '{nama_tool}' tidak terdaftar."
            
        # 2. Masukkan hasilnya ke dalam wadah list 
        hasil.append(
            types.Part.from_function_response(
                name=nama_tool,
                response={"result": hasil_tool}
            )
        )
        
    # 3. Tembak SEMUA hasil sekaligus ke Gemini (di luar for loop)
    response = panggil_gemini_aman(
        model="gemini-3.5-flash",
        contents=[
            pertanyaan_user,
            response.candidates[0].content,
            types.Content(parts=hasil) 
        ],
        config=types.GenerateContentConfig(tools=tools)
    )

    print("[AGENT] Selesai menganalisis, tidak butuh tool lagi.")
    return response.text

if __name__ == "__main__":
    pertanyaan = "Tolong cek data batch B000001, dan cek kpi produksi keseluruhan"
    print("="*50)
    print("MENJALANKAN AI AGENT...")
    print("="*50)
    jawaban_akhir = jalankan_agent(pertanyaan)
    print("\n" + "="*50)
    print("--- JAWABAN AKHIR DARI AGENT ---")
    print(jawaban_akhir)
    print("="*50)
