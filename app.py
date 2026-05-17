import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Noms des images à la racine
img_acad = "image_5.png"  # Logo Gauche (Académie)
img_eps = "image_6.png"   # Logo Droite (EPS)
img_hub = "image_7.png"   # Filigrane central (Aix-Marseille)

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-color: #F3F4F6 !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* Bandeau Supérieur */
    .hub-header {{
        background-color: #002060;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 20px;
        margin-bottom: 10px;
        border-radius: 4px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }}
    .hub-title {{ text-align: center; color: white; }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 18px; font-weight: bold; }}
    .hub-title p {{ color: #cbd5e0 !important; margin: 0; font-size: 10px; }}
    
    /* Titres des colonnes */
    .column-title {{
        color: #002060;
        font-size: 13px;
        font-weight: bold;
        text-align: center;
        margin-top: 0px !important;
        margin-bottom: 8px !important;
        height: 20px !important;
        line-height: 20px !important;
    }}
    
    /* Zone interne des messages */
    .scroll-chat {{
        height: 250px !important;
        overflow-y: auto !important;
        padding-right: 5px;
        position: relative;
    }}
    
    /* --- STYLE DES BULLES DE CHAT --- */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px 12px 0px 12px !important;
        margin-left: 15% !important;
        padding: 10px !important;
    }}
    
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #E2E8F0 !important;
        border: none !important;
        border-radius: 12px 12px 12px 0px !important;
        margin-right: 15% !important;
        padding: 10px !important;
    }}
    
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{
        display: none !important;
    }}
    
    .stChatInputContainer {{
        margin-top: 4px !important;
        margin-bottom: 0px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. INITIALISATION DYNAMIQUE DE LA CLÉ (Évite le blocage du cache)
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# 3. AFFICHAGE DU BANDEAU SUPÉRIEUR
logo_l = img_acad if os.path.exists(img_acad) else ""
logo_r = img_eps if os.path.exists(img_eps) else ""

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 120px; text-align: left;">
            {"<img src='https://raw.githubusercontent.com/" + st.secrets.get("GITHUB_USERNAME", "") + "/" + st.secrets.get("GITHUB_REPO", "") + "/main/" + logo_l + "' width='80'>" if logo_l else "<span style='color:white; font-size:12px; font-weight:bold;'>Académie</span>"}
        </div>
        <div class="hub-title">
            <h1>Hub IA - EPS Aix-Marseille</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
        </div>
        <div style="width: 120px; text-align: right;">
            {"<img src='https://raw.githubusercontent.com/" + st.secrets.get("GITHUB_USERNAME", "") + "/" + st.secrets.get("GITHUB_REPO", "") + "/main/" + logo_r + "' width='35'>" if logo_r else "<span style='color:white; font-size:12px; font-weight:bold;'>EPS</span>"}
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. CHARGEMENT DES INDEX (Sécurisé sans cache persistant d'erreur)
def load_all_indexes_safe():
    if not os.path.exists("./data") or len(os.listdir("./data")) == 0:
        os.makedirs("./data", exist_ok=True)
        with open("./data/info.txt", "w") as f:
            f.write("Base de données initialisée.")
    pdf_docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(pdf_docs)
    return index, index

try:
    ipack_index, aix_index = load_all_indexes_safe()
except Exception as e:
    st.error(f"Erreur de connexion aux services d'IA. Veuillez vérifier la clé dans les Secrets. Détails : {e}")
    st.stop()

# 5. SPLIT ÉCRAN À DEUX COLONNES
col1, col2 = st.columns(2, gap="large")

filigrane_html = ""
if os.path.exists(img_hub):
    img_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME', '')}/{st.secrets.get('GITHUB_REPO', '')}/main/{img_hub}"
    filigrane_html = f"""<img src="{img_url}" style="position: absolute; top: 10px; left: 10px; width: 70px; opacity: 0.15; pointer-events: none; z-index: 0;">"""

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    
    chat_ipack = ipack_index.as_chat_engine(chat_mode="context", system_prompt="Tu es l'Assistant iPack EPS Aix-Marseille. Réponds de manière structurée et concise. Termine par 'Bon courage pour vos saisies !'.")
    if "messages_ipack" not in st.session_state: 
        st.session_state.messages_ipack = []
        
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        st.markdown(filigrane_html, unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("💬 **Assistant Ipackeps Aix-Marseille**\n\nBonjour, que puis-je faire pour vous ?")
        for m in st.session_state.messages_ipack:
            with st.chat_message(m["role"]): 
                st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        prompt = st.chat_input("Message...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    
    chat_aix = aix_index.as_chat_engine(chat_mode="context", system_prompt="Tu es l'Assistant de recherche du site EPS d'Aix-Marseille.")
    if "messages_aix" not in st.session_state: 
        st.session_state.messages_aix = []
        
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        st.markdown(filigrane_html, unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("💬 **Assistant de recherche site EPS**\n\nBonjour, comment puis-je vous aider ?")
        for m in st.session_state.messages_aix:
            with st.chat_message(m["role"]): 
                st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        prompt_aix = st.chat_input("Message...", key="input_aix")

# 6. ENVOI DES MESSAGES
if prompt:
    st.session_state.messages_ipack.append({"role": "user", "content": prompt})
    response = chat_ipack.chat(prompt)
    st.session_state.messages_ipack.append({"role": "assistant", "content": response.response})
    st.rerun()

if prompt_aix:
    st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
    response_aix = chat_aix.chat(prompt_aix)
    st.session_state.messages_aix.append({"role": "assistant", "content": response_aix.response})
    st.rerun()

st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 10px; margin-top: 10px; margin-bottom: 0px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
