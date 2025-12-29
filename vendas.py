import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
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

# --- FUNÇÃO PARA CARREGAR BIBLIOTECA ---
def carregar_biblioteca():
    try:
        with open('biblioteca.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        texto_biblioteca = ""
        for chave, categoria in data.items():
            texto_biblioteca += f"\n{categoria['titulo']}:\n"
            for livro in categoria['livros']:
                texto_biblioteca += f"- {livro}\n"
        return texto_biblioteca
    except FileNotFoundError:
        st.error("Erro: Arquivo 'biblioteca.json' não encontrado!")
        return "Erro ao carregar biblioteca."

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
    st.caption("Biblioteca: 50+ Obras de Referência (Carregada via JSON).")

# --- CONTEÚDO PRINCIPAL ---
st.title("🧠 Advisor Brain AI 4.0 (Base Estendida)")
st.markdown("### Cole o texto, suba um print ou envie um áudio.")

# --- ABAS DE ENTRADA ---
tab_texto, tab_imagem, tab_audio = st.tabs(["📝 Texto / Digitar", "📸 Print de Conversa", "🎤 Áudio (Gravar ou Upload)"])

user_input = None 
input_type = None 
audio_mime_type = "audio/wav" 

with tab_texto:
    text_area_val = st.text_area("Digite a objeção aqui:", height=150)
    if text_area_val:
        user_input = text_area_val
        input_type = "text"

with tab_imagem:
    uploaded_image = st.file_uploader("Suba o print", type=["jpg", "png", "jpeg"])
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Print carregado", use_column_width=True)
        user_input = image
        input_type = "image"

with tab_audio:
    st.markdown("##### Gravar ou Subir Áudio")
    audio_recorder = st.audio_input("Gravar")
    audio_uploader = st.file_uploader("Subir arquivo", type=["wav", "mp3", "m4a", "ogg"])

    if audio_recorder:
        st.audio(audio_recorder)
        user_input = audio_recorder
        input_type = "audio"
    elif audio_uploader:
        st.audio(audio_uploader)
        user_input = audio_uploader
        input_type = "audio"
        audio_mime_type = audio_uploader.type

st.markdown("---")
btn_gerar = st.button("✨ Analisar e Gerar Scripts", type="primary", use_container_width=True)

# --- LÓGICA DA IA ---
def get_ai_response(content, type_content, mime_type="audio/wav"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')

    biblioteca_texto = carregar_biblioteca()

    # PROMPT AGORA É GENÉRICO E SE ADAPTA AO JSON
    system_prompt_text = f"""
    Você é o "Advisor Brain", o maior especialista em Consultoria e Wealth Management.
    
    ⚠️ SUA INTELIGÊNCIA É GUIADA EXCLUSIVAMENTE POR ESTA BIBLIOTECA DE 50 LIVROS:
    
    {biblioteca_texto}

    ---
    PASSO 1: DIAGNÓSTICO PROFUNDO
    - Identifique o sentimento do cliente e o contexto.
    - Selecione mentalmente 2 ou 3 livros dessa lista que melhor resolvem o problema específico (Ex: Se for medo, use a seção de Psicologia; Se for técnica, use Fundamentos).

    PASSO 2: AÇÃO TÁTICA (Scripts Prontos)
    Crie 3 versões da resposta para canais diferentes.
    
    📱 WHATSAPP (Curto e Pessoal)
    - Use princípios da seção de 'Relacionamento/Influência' (Ex: Dale Carnegie ou Cialdini).
    - Termine com uma pergunta aberta.

    📧 E-MAIL (Estruturado)
    - Use estrutura de Vendas (Ex: SPIN Selling ou Gatilhos Mentais).
    - Use dados da seção 'Técnica/Investimentos' para embasar a lógica.

    📞 SCRIPT DE LIGAÇÃO (Argumentação)
    - Comece com empatia e escuta ativa.
    - Use conceitos de 'Comportamento' ou 'Performance' para mudar a perspectiva do cliente (Reframing).

    Fale português do Brasil profissional. Use formatação Markdown. Cite o autor/livro usado como referência sutilmente.
    """

    with st.spinner("Consultando a biblioteca dos 50 mestres..."):
        input_data = [system_prompt_text]

        if type_content == "text":
            input_data.append(f"OBJEÇÃO: {content}")
        elif type_content == "image":
            input_data.append("Analise a imagem:")
            input_data.append(content)
        elif type_content == "audio":
            input_data.append("Analise o áudio:")
            input_data.append({"mime_type": mime_type, "data": content.read()})

        response = model.generate_content(input_data)
        return response.text

# --- EXIBIÇÃO ---
if btn_gerar:
    if not user_input:
        st.warning("⚠️ Forneça uma entrada.")
    elif not api_key:
        st.error("🔑 Configure a API Key.")
    else:
        try:
            resultado = get_ai_response(user_input, input_type, audio_mime_type)
            st.markdown(resultado)
        except Exception as e:
            st.error(f"Erro: {e}")