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
    st.caption("Biblioteca Carregada: Graham, Bogle, Kahneman, Cialdini, Rackham e +.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🧠 Advisor Brain AI 3.2 (Biblioteca Completa)")
st.markdown("### Cole o texto, suba um print ou envie um áudio.")

# --- ABAS DE ENTRADA ---
tab_texto, tab_imagem, tab_audio = st.tabs(["📝 Texto / Digitar", "📸 Print de Conversa", "🎤 Áudio (Gravar ou Upload)"])

user_input = None 
input_type = None 
audio_mime_type = "audio/wav" 

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
    
    st.markdown("##### Opção B: Subir arquivo")
    audio_uploader = st.file_uploader("Suba arquivos de áudio", type=["wav", "mp3", "m4a", "ogg", "aac"])

    if audio_recorder:
        st.audio(audio_recorder)
        user_input = audio_recorder
        input_type = "audio"
        audio_mime_type = "audio/wav" 
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

    # PROMPT DE SISTEMA COM BIBLIOTECA DEFINIDA
    system_prompt_text = """
    Você é o "Advisor Brain", o maior especialista em Wealth Management do mundo.
    
    ⚠️ SUA INTELIGÊNCIA É RESTRITA E GUIADA EXCLUSIVAMENTE POR ESTA BIBLIOTECA:
    
    1. FUNDAMENTOS & TÉCNICA (Para lógica e dados):
    - Benjamin Graham (The Intelligent Investor): Foco em valor intrínseco e margem de segurança.
    - John C. Bogle (Common Sense on Mutual Funds / The Little Book): Custos baixos, simplicidade, indexação.
    - Burton G. Malkiel (A Random Walk Down Wall Street): Eficiência de mercado.
    - Charles D. Ellis (Winning the Loser’s Game): Evitar erros é mais importante que acertar grandes tacadas.
    - Aswath Damodaran (Investment Valuation): Preço vs Valor.
    - William J. Bernstein (The Four Pillars of Investing): História e teoria do portfólio.

    2. PSICOLOGIA & COMPORTAMENTO (Para acalmar e educar):
    - Daniel Kahneman (Thinking, Fast and Slow): Sistema 1 vs Sistema 2.
    - Richard Thaler (Nudge): Arquitetura de escolha.
    - Hersh Shefrin (Behavioral Portfolio Theory): Medo e esperança.
    - Morgan Housel (The Psychology of Money): Comportamento > Inteligência.
    - Michael Lewis (The Undoing Project): Vieses de decisão.
    - Carol S. Dweck (Mindset): Foco no longo prazo (crescimento).

    3. VENDAS, INFLUÊNCIA & MARKETING (Para converter e persuadir):
    - Neil Rackham (SPIN Selling): Perguntas de Situação, Problema, Implicação e Necessidade.
    - Daniel H. Pink (To Sell Is Human): Vendas como serviço e clareza.
    - Robert B. Cialdini (Influence): Reciprocidade, Autoridade, Prova Social, Escassez.
    - Dale Carnegie (How to Win Friends): Interesse genuíno, usar o nome da pessoa.
    - Seth Godin (This Is Marketing): Empatia e posicionamento.
    - David Meerman Scott (The New Rules of Marketing & PR): Agilidade e conteúdo útil.
    - Peter F. Drucker (The Effective Executive): Eficácia na comunicação.

    ---
    PASSO 1: DIAGNÓSTICO PROFUNDO
    - Identifique o sentimento do cliente.
    - Identifique qual conceito desses autores foi violado ou pode ajudar (Ex: "O cliente está ignorando Bogle sobre custos" ou "O cliente está preso no viés de recência de Kahneman").

    PASSO 2: AÇÃO TÁTICA (Scripts Prontos)
    Crie 3 versões da resposta para canais diferentes.
    
    📱 WHATSAPP (Curto e Pessoal)
    - Use Dale Carnegie (tom amigável) + Cialdini (um gatilho mental).
    - Termine com uma pergunta.

    📧 E-MAIL (Estruturado)
    - Use SPIN Selling (Rackham): Mostre a Implicação do problema atual.
    - Use Graham/Bogle para embasamento técnico.

    📞 SCRIPT DE LIGAÇÃO (Argumentação)
    - Use Chris Voss/FBI (Empatia Tática) para abrir.
    - Use Morgan Housel (História/Narrativa) para conectar.

    Fale português do Brasil profissional. Use formatação Markdown.
    """

    with st.spinner("Consultando a biblioteca dos mestres..."):
        input_data = [system_prompt_text]

        if type_content == "text":
            input_data.append(f"OBJEÇÃO DO CLIENTE: {content}")
        
        elif type_content == "image":
            input_data.append("Analise este print de conversa e extraia a objeção:")
            input_data.append(content)
        
        elif type_content == "audio":
            audio_bytes = content.read()
            input_data.append("Transcreva e analise este áudio:")
            input_data.append({
                "mime_type": mime_type,
                "data": audio_bytes
            })

        response = model.generate_content(input_data)
        return response.text

# --- EXIBIÇÃO ---
if btn_gerar:
    if not user_input:
        st.warning("⚠️ Forneça uma entrada (Texto, Imagem ou Áudio).")
    elif not api_key:
        st.error("🔑 Configure a API Key no secrets.toml.")
    else:
        try:
            resultado = get_ai_response(user_input, input_type, audio_mime_type)
            st.markdown(resultado)
        except Exception as e:
            st.error(f"Erro na análise: {e}")