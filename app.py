import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Identification des images (doivent être à la racine de ton GitHub)
img_acad = "image_5.png"  # Logo iPack EPS (Gauche)
img_eps = "image_6.png"   # Logo EPS (Droite)
img_consensus = "image_7.png" # Image de filigrane consensus

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #F1F5F9 !important; }} /* Fond général gris perle */
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* BANDEAU SUPÉRIEUR - COULEUR BLEU ARDOISE PROFOND (CONSENSUS) */
    .hub-header {{
        background-color: #1E293B; /* Slate 800 - Moderne et Institutionnel */
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 25px;
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }}
    .hub-title {{ text-align: center; color: white; }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
    
    /* TITRES DES COLONNES */
    .column-title {{
        color: #334155;
        font-size: 14px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
        height: 22px;
    }}
    
    /* CONTENEUR DE CHAT AVEC FILIGRANE */
    .scroll-chat {{
        height: 320px !important;
        overflow-y: auto !important;
        padding: 15px;
        position: relative;
        background-color: rgba(255, 255, 255, 0.7); /* Fond blanc semi-transparent */
    }}
    
    /* STYLE DES BULLES DE CHAT (STYLE PREMIUM) */
    /* Utilisateur : Blanc pur, ombre portée douce */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: #FFFFFF !important;
        border-radius: 18px 18px 0px 18px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05) !important;
        margin-left: 15% !important;
        margin-bottom: 10px !important;
    }}
    
    /* Assistant : Gris très clair bleuté */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #F8FAFC !important;
        border-radius: 18px 18px 18px 0px !important;
        border: none !important;
        margin-right: 15% !important;
        margin-bottom: 10px !important;
    }}
    
    /* Masquer les avatars par défaut */
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{
        display: none !important;
    }}
    
    /* Bordure du champ de saisie */
    .stChatInputContainer {{ border-color: #1E293B !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURATION IA DYNAMIQUE
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# 3. BANDEAU LOGOS ET TITRE
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;">
            <img src="{github_url}{img_acad}" width="110">
        </div>
        <div class="hub-title">
            <h1>Hub IA - EPS Aix-Marseille</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
        </div>
        <div style="width: 150px; text-align: right;">
            <img src="{github_url}{img_eps}" width="45">
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. CHARGEMENT IA
def load_all_indexes_safe():
    if not os.path.exists("./data"): os.makedirs("./data")
    pdf_docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(pdf_docs) if pdf_docs else None
    return index, index

try:
    ipack_index, aix_index = load_all_indexes_safe()
except Exception as e:
    st.error("⚠️ Clé OpenAI invalide. Veuillez vérifier vos Secrets.")
    st.stop()

# 5. LAYOUT 2 COLONNES
col1, col2 = st.columns(2, gap="large")

# Préparation du filigrane de consensus (image_7)
watermark = f"""<img src="{github_url}{img_consensus}" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 250px; opacity: 0.07; pointer-events: none; z-index: 0;">"""

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<div class="scroll-chat">{watermark}', unsafe_allow_html=True)
        with st.chat_message("assistant"): st.markdown("💬 **Assistant Ipackeps** : Bonjour, comment puis-je vous aider ?")
        for m in st.session_state.get("messages_ipack", []):
            with st.chat_message(m["role"]): st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt = st.chat_input("Votre question iPack...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<div class="scroll-chat">{watermark}', unsafe_allow_html=True)
        with st.chat_message("assistant"): st.markdown("💬 **Assistant Site EPS** : Bonjour, que cherchez-vous sur le site ?")
        for m in st.session_state.get("messages_aix", []):
            with st.chat_message(m["role"]): st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt_aix = st.chat_input("Votre question site EPS...", key="input_aix")

# 6. GESTION DES MESSAGES
if prompt:
    if "messages_ipack" not in st.session_state: st.session_state.messages_ipack = []
    st.session_state.messages_ipack.append({"role": "user", "content": prompt})
    resp = ipack_index.as_chat_engine().chat(prompt).response
    st.session_state.messages_ipack.append({"role": "assistant", "content": resp})
    st.rerun()

if prompt_aix:
    if "messages_aix" not in st.session_state: st.session_state.messages_aix = []
    st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
    resp_a = aix_index.as_chat_engine().chat(prompt_aix).response
    st.session_state.messages_aix.append({"role": "assistant", "content": resp_a})
    st.rerun()

st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 10px; margin-top: 15px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
