import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Identification des images à la racine de ton GitHub
img_acad = "image_5.png"  # Logo iPack EPS (Gauche)
img_eps = "image_6.png"   # Logo EPS (Droite)
img_fond = "image_8.jpg"  # Ton image de fond personnalisée avec les vignettes

# Construction de l'URL GitHub pour les images
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    
    /* INTEGRATION DE IMAGE_8 EN FOND D'ECRAN GLOBAL */
    .stApp {{ 
        background-image: url('{github_url}{img_fond}') !important;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* BANDEAU SUPÉRIEUR - BLEU ARDOISE INSTITUTIONNEL */
    .hub-header {{
        background-color: #1E293B;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 25px;
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        position: relative;
        z-index: 10;
    }}
    .hub-title {{ text-align: center; color: white; }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
    
    /* TITRES DES COLONNES */
    .column-title {{
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
        height: 24px;
        background-color: #1E293B;
        border-radius: 4px;
        padding: 4px 0;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.2);
    }}
    
    /* FENÊTRES DE CHAT : BLANC PUR COMPLET ET PRIORITÉ D'AFFICHAGE */
    .scroll-chat {{
        height: 340px !important;
        overflow-y: auto !important;
        padding: 15px;
        position: relative;
        background-color: #FFFFFF !important; /* Blanc pur opaque à 100% */
        border-radius: 8px 8px 0px 0px;
        z-index: 100 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }}
    
    /* --- STYLE DES DIALOGUES ASSURANT LA LISIBILITÉ --- */
    /* Style général des lignes de message */
    div[data-testid="stChatMessage"] {{
        border: none !important;
        padding: 8px 12px !important;
        margin-bottom: 10px !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05) !important;
    }}
    
    /* Messages de l'Utilisateur (Vous) : Fond Bleu/Gris très clair discret */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: #F1F5F9 !important;
        border-radius: 12px 12px 0px 12px !important;
        margin-left: 10% !important;
    }}
    
    /* Messages de l'Assistant (IA) : Fond Blanc Pur avec petite bordure pour se détacher */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px 12px 12px 0px !important;
        margin-right: 10% !important;
    }}
    
    /* Masquer les icônes d'avatar de Streamlit */
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{
        display: none !important;
    }}
    
    /* ZONE DE REDACTION EN BLANC PUR OPAQUE */
    .stChatInputContainer {{ 
        border: 2px solid #E2E8F0 !important; 
        background-color: #FFFFFF !important;
        border-radius: 0px 0px 8px 8px !important;
        position: relative;
        z-index: 101 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }}
    
    /* Forcer le champ texte interne en blanc */
    .stChatInputContainer textarea {{
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURATION IA DYNAMIQUE
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# 3. BANDEAU DE NAVIGATION SUPÉRIEUR
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
    st.error("⚠️ Clé OpenAI invalide ou problème de configuration. Veuillez vérifier vos Secrets.")
    st.stop()

# 5. SPLIT ÉCRAN À DEUX COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("👨‍🏫 **Assistant Ipackeps Aix-Marseille** : Bonjour, que puis-je faire pour vous ?")
        for m in st.session_state.get("messages_ipack", []):
            prefix = "👤 **Vous** : " if m["role"] == "user" else "🤖 **Assistant** : "
            with st.chat_message(m["role"]): st.markdown(prefix + m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt = st.chat_input("Votre question iPack...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("💬 **Assistant Site EPS** : Bonjour, que cherchez-vous sur le site ?")
        for m in st.session_state.get("messages_aix", []):
            prefix = "👤 **Vous** : " if m["role"] == "user" else "🔍 **Assistant** : "
            with st.chat_message(m["role"]): st.markdown(prefix + m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        prompt_aix = st.chat_input("Votre question site EPS...", key="input_aix")

# 6. ENVOI ET TRAITEMENT DES MESSAGES
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

st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 10px; margin-top: 15px; background-color: rgba(30, 41, 59, 0.8); padding: 5px; border-radius: 4px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
