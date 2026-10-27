import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agent.tools import TOOLS
from agent.prompts import SYSTEM_PROMPT
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ServerError

chat_history = []


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),
                      http_options=types.HttpOptions(timeout=30_000))

@retry(
    retry=retry_if_exception_type(ServerError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def panggil_gemini_aman(model, contents, config):
    """Fungsi pembungkus untuk manggil Gemini dengan fitur retry."""
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
        
    )

def jalankan_agent(pertanyaan_user: str) :
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

    chat_history.append(types.Content(role="user",parts=[types.Part.from_text(text=pertanyaan_user)]))
    

    # 2. Kirim pertanyaan ke Gemini
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
    # 3. Agent Loop
    while response.function_calls and jumlah_loop < 3:
        list_hasil = [] 
    
        
        for function_call in response.function_calls:
            nama_tool = function_call.name
            parameter = dict(function_call.args)
            
            print(f"[AGENT] Memutuskan memanggil tool: '{nama_tool}'")
            
            fungsi_python = next((t["function"] for t in TOOLS if t["name"] == nama_tool), None)
            
            if fungsi_python:
                try:
                    
                    hasil_tool = fungsi_python(**parameter)
                    print(f"[TOOL] Hasil didapat dari {nama_tool}")
                except Exception as e:
                    print(f"[TOOL ERROR] {nama_tool}: {type(e).__name__}: {e}")

                    hasil_tool = f"sistem gagal menjalankan tool'{nama_tool}'. "
                    "data tidak tersedia saat ini.silahkan coba beberapa saat lagi"
                    "atau hubungi pihak terkait jika masalah berlanjut"
            else:
                hasil_tool = f"Error: Tool '{nama_tool}' tidak terdaftar."
                
            list_hasil.append(
                types.Part.from_function_response(
                    name=nama_tool,
                    response={"result": hasil_tool}
                )
            )
        jumlah_loop += 1
        
        # Simpan jawaban/perintah dari Gemini ke history
        chat_history.append(response.candidates[0].content)

        response = panggil_gemini_aman(
        model="gemini-3.5-flash",
        contents=chat_history + [types.Content(parts=list_hasil)],
        config=types.GenerateContentConfig(
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True) 
           )
            )

    
    if jumlah_loop  >= 3 and response.function_calls:
        return "maaf,saya terlalu banyak mencoba menjalankan alat.silahkan perjelas pertanyaan anda"


    print("[AGENT] Selesai menganalisis, tidak butuh tool lagi.")
 
    return response.text



if __name__ == "__main__":
    pertanyaan ="cek batch B001 dong"
    print("="*50)
    print("MENJALANKAN AI AGENT...")
    print("="*50)
    jawaban_akhir = jalankan_agent(pertanyaan)
    print("\n" + "="*50)
    print("--- JAWABAN AKHIR DARI AGENT ---")
    print(jawaban_akhir)
    print("="*50)