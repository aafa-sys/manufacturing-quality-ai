import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agent.tools import TOOLS
from agent.prompts import SYSTEM_PROMPT

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    response = client.models.generate_content(
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
        function_call = response.function_calls[0]
        nama_tool = function_call.name
        parameter = function_call.args

        print(f"[AGENT] Memutuskan memanggil tool: '{nama_tool}' dengan parameter: {parameter}")

        fungsi_python = next((t["function"] for t in TOOLS if t["name"] == nama_tool), None)
        if fungsi_python:
            try:
                hasil_tool = fungsi_python(**parameter)
                print(f"[TOOL] Hasil: {hasil_tool}")
            except Exception as e:
                hasil_tool = f"Error eksekusi: {e}"
                print(f"[TOOL] Gagal: {hasil_tool}")
        else:
            hasil_tool = f"Error: Tool '{nama_tool}' tidak ditemukan."
            print(f"[TOOL] {hasil_tool}")

        # Kirim hasil balik ke Gemini
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                pertanyaan_user,
                response.candidates[0].content,
                types.Part.from_function_response(name=nama_tool, response={"result": hasil_tool})
            ],
            config=types.GenerateContentConfig(tools=tools)
        )

    print("[AGENT] Selesai menganalisis, tidak butuh tool lagi.")
    return response.text

if __name__ == "__main__":
    pertanyaan = "Tolong cariin semua batch yang reject nya diatas 20"
    print("="*50)
    print("MENJALANKAN AI AGENT...")
    print("="*50)
    jawaban_akhir = jalankan_agent(pertanyaan)
    print("\n" + "="*50)
    print("--- JAWABAN AKHIR DARI AGENT ---")
    print(jawaban_akhir)
    print("="*50)