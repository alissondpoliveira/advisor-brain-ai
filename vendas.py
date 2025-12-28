import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Advisor Brain AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stTextArea textarea {font-size: 16px !important; height: 150px;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    .script-box {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 Advisor Brain")
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🔐 Sistema Seguro")
    except Exception:
        st.error("Configure o secrets.toml!")
        api_key = None
    st.info("Modelo: gemini-flash-latest")
    st.caption("Suporta: Texto, Prints e Áudios (Gravados ou Upload).")

# --- CONTEÚDO PRINCIPAL ---
st.title("🧠 Advisor Brain AI 3.1 (Multimodal Completo)")
st.markdown("### Cole o texto, suba um print ou envie um áudio.")

# --- ABAS DE ENTRADA ---
tab_texto, tab_imagem, tab_audio = st.tabs(["📝 Texto / Digitar", "📸 Print de Conversa", "🎤 Áudio (Gravar ou Upload)"])

user_input = None 
input_type = None 
audio_mime_type = "audio/wav" # Padrão

with tab_texto:
    text_area_val = st.text_area(
        "Digite a objeção aqui:", 
        placeholder="O cliente disse: 'Achei a taxa cara...'",
        height=150
    )
    if text_area_val:
        user_input = text_area_val
        input_type = "text"

with tab_imagem:
    uploaded_image = st.file_uploader("Suba o print do WhatsApp ou E-mail", type=["jpg", "png", "jpeg"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Print carregado", use_column_width=True)
        user_input = image
        input_type = "image"

with tab_audio:
    st.markdown("##### Opção A: Gravar agora")
    audio_recorder = st.audio_input("Clique para gravar")
    
    st.markdown("##### Opção B: Subir arquivo (WhatsApp/Exportação)")
    audio_uploader = st.file_uploader("Suba arquivos de áudio", type=["wav", "mp3", "m4a", "ogg", "aac"])

    # Lógica de prioridade: Se gravou, usa o gravado. Se subiu, usa o arquivo.
    if audio_recorder:
        st.audio(audio_recorder)
        user_input = audio_recorder
        input_type = "audio"
        audio_mime_type = "audio/wav" # Gravador do browser geralmente é wav
    
    elif audio_uploader:
        st.audio(audio_uploader)
        user_input = audio_uploader
        input_type = "audio"
        audio_mime_type = audio_uploader.type # Pega o tipo real (ex: audio/mp3)

st.markdown("---")
btn_gerar = st.button("✨ Analisar e Gerar Scripts", type="primary", use_container_width=True)

# --- LÓGICA DA IA ---
def get_ai_response(content, type_content, mime_type="audio/wav"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')

    # PROMPT DE SISTEMA
    system_prompt_text = """
    Você é o "Advisor Brain". Analise a entrada (Texto, Imagem ou Áudio) que contém uma objeção de vendas.
    Base intelectual: Graham, Kahneman, FBI e Cialdini.

    PASSO 1: TRANSCRIÇÃO E CONTEXTO
    - Se for imagem/áudio, faça a transcrição completa primeiro.
    - Identifique o sentimento (ex: raiva, medo) e o viés cognitivo.

    PASSO 2: AÇÃO TÁTICA (Scripts Prontos)
    Crie 3 versões da resposta:
    📱 WHATSAPP (Curto, Pessoal, Técnica de Espelhamento).
    📧 E-MAIL (Estruturado, SPIN Selling).
    📞 SCRIPT DE LIGAÇÃO (Empático, Fechamento).

    Fale português do Brasil profissional. Use formatação Markdown.
    """

    with st.spinner("Processando entrada multimídia..."):
        input_data = [system_prompt_text]

        if type_content == "text":
            input_data.append(f"OBJEÇÃO DO CLIENTE: {content}")
        
        elif type_content == "image":
            input_data.append("Analise este print de conversa e extraia a objeção:")
            input_data.append(content)
        
        elif type_content == "audio":
            # Leitura dos bytes do arquivo
            audio_bytes = content.read()
            input_data.append("Analise este áudio, transcreva o que foi dito e responda à objeção:")
            input_data.append({
                "mime_type": mime_type, # Passa o tipo correto (mp3/wav/m4a)
                "data": audio_bytes
            })

        response = model.generate_content(input_data)
        return response.text

# --- EXIBIÇÃO ---
if btn_gerar:
    if not user_input:
        st.warning("⚠️ Por favor, forneça uma entrada (Texto, Imagem ou Áudio).")
    elif not api_key:
        st.error("🔑 Configure a API Key no secrets.toml.")
    else:
        try:
            # Passamos também o mime_type do áudio
            resultado = get_ai_response(user_input, input_type, audio_mime_type)
            st.markdown(resultado)
        except Exception as e:
            st.error(f"Erro na análise: {e}")