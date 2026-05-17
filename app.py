import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURATION DE LA PAGE & DESIGN PREMIUM
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Chemins des images
img_acad = "image_5.png" # Académie / iPack
img_eps = "image_6.png"  # EPS
img_hub = "image_7.png"  # Logo Hub / Aix-Marseille (Filigrane)

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #F8FAFC !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* Bandeau Supérieur */
    .hub-header {{
        background-color: #002060;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 20px;
        margin-bottom: 12px;
        border-radius: 8px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }}
    .hub-title {{ text-align: center; color: white; }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 20px; font-weight: bold; }}
    .hub-title p {{ color: #cbd5e0 !important; margin: 0; font-size: 11px; }}
    
    /* Titres des colonnes */
    .column-title {{
        color: #002060;
        font-size: 13px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 8px;
        height: 20px;
    }}
    
    /* Fenêtre de Chat avec Image de fond image_7 (transparente en haut à gauche) */
    .scroll-chat {{
        height: 300px;
        overflow-y: auto;
        padding: 10px;
        position: relative;
        background-image: url('app/static/{img_hub}');
        background-repeat: no-repeat;
        background-position: 10px 10px;
        background-size: 80px;
        background-attachment: local;
        /* On crée un effet de transparence sur l'image via un filtre si possible ou simplement par le PNG */
    }}
    
    /* --- STYLE DES BULLES DE CHAT --- */
    /* Message Utilisateur : Blanc Pur avec bordure */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 15px 15px 0px 15px !important;
        margin-left: 20% !important;
    }}
    
    /* Message Assistant : Gris/Bleu très clair */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #F1F5F9 !important;
        border: None !important;
        border-radius: 15px 15px 15px 0px !important;
        margin-right: 15% !important;
    }}
    
    /* Masquer les avatars Streamlit pour un look plus "Chatbase" */
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{
        display: none !important;
    }}

    .stChatInputContainer {{ border-color: #002060 !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURATION IA
openai_api_key = st.secrets.get("OPENAI_API_KEY")
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# 3. AFFICHAGE DU BANDEAU SUPÉRIEUR AVEC LOGOS
logo_l = img_acad if os.path.exists(img_acad) else ""
logo_r = img_eps if os.path.exists(img_eps) else ""

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;">
            {"<img src='app/static/" + logo_l + "' width='100'>" if logo_l else "Académie"}
        </div>
        <div class="hub-title">
            <h1>Hub IA - EPS Aix-Marseille</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
        </div>
        <div style="width: 150px; text-align: right;">
            {"<img src='app/static/" + logo_r + "' width='50'>" if logo_r else "EPS"}
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. CHARGEMENT DES INDEX
@st.cache_resource(show_spinner="Calcul des bases de connaissances...")
def load_all_indexes():
    if not os.path.exists("./data"): os.makedirs("./data")
    pdf_docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(pdf_docs) if pdf_docs else None
    return index, index

ipack_index, aix_index = load_all_indexes()

# 5. SPLIT ÉCRAN
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        # Message de bienvenue manuel (sans bulle Streamlit pour le style)
        st.markdown("💬 **Assistant Ipackeps** : Bonjour, que puis-je faire pour vous ?")
        for m in st.session_state.get("messages_ipack", []):
            with st.chat_message(m["role"]): st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt = st.chat_input("Posez votre question iPack...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        st.markdown("💬 **Assistant Site EPS** : Bonjour, comment puis-je vous aider ?")
        for m in st.session_state.get("messages_aix", []):
            with st.chat_message(m["role"]): st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt_aix = st.chat_input("Posez votre question site EPS...", key="input_aix")

# 6. ENVOI DES MESSAGES
if prompt:
    if "messages_ipack" not in st.session_state: st.session_state.messages_ipack = []
    st.session_state.messages_ipack.append({"role": "user", "content": prompt})
    if ipack_index:
        resp = ipack_index.as_chat_engine().chat(prompt).response
        st.session_state.messages_ipack.append({"role": "assistant", "content": resp})
    st.rerun()

if prompt_aix:
    if "messages_aix" not in st.session_state: st.session_state.messages_aix = []
    st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
    if aix_index:
        resp_a = aix_index.as_chat_engine().chat(prompt_aix).response
        st.session_state.messages_aix.append({"role": "assistant", "content": resp_a})
    st.rerun()

st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 10px; margin-top: 10px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
