import streamlit as st
from agent.agent import jalankan_agent

# Setup halaman web
st.set_page_config(page_title="Manufacturing AI", page_icon="🏭", layout="wide")

# --- CUSTOM CSS BUAT TAMPILAN PROFESIONAL (DARK MODE) ---
st.markdown("""
<style>
    /* Background gelap elegan */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    /* Kotak chat */
    .stChatMessage { background-color: #1E2530; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363D;}
    /* Judul */
    h1 { color: #4CAF50; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------------

# Sidebar Kiri
with st.sidebar:
    st.title("🏭 Manufacturing AI")
    st.success("System Online 🟢")
    st.write("---")
    st.write("👨‍💼 **Role:** Administrator")
    st.write("📊 **Database:** PostgreSQL")
    st.write("🧠 **Engine:** Gemini Agent")

# Judul Utama
st.title("AI Asisten Produksi")
st.write("Tanyakan apa saja seputar data batch, QC, atau produksi pabrik.")

# Tempat Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kotak Input Chat di Bawah
if prompt := st.chat_input("Contoh: cek batch BT26G001 dong"):
    # 1. Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Panggil Agent lu!
    with st.chat_message("assistant"):
        with st.spinner("Menganalisis database..."):
            try:
                # Ini fungsi dari agent.py lu
                jawaban = jalankan_agent(prompt) 
                st.markdown(jawaban)
            except Exception as e:
                st.error(f"Error: {e}")
                jawaban = "Terjadi kesalahan sistem."
    
    # 3. Simpan jawaban agent ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": jawaban})