import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. CONFIGURATION DE LA PAGE & DESIGN INTERACTIF
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Nettoyage des marges et blocage du défilement de page inutile */
    .block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }
    .stApp { background-color: #F3F4F6 !important; }
    header[data-testid="stHeader"] { display: none !important; }
    
    /* Bandeau Supérieur */
    .hub-header {
        background-color: #002060;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 20px;
        margin-bottom: 15px;
        border-radius: 4px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    .hub-title { text-align: center; color: white; }
    .hub-title h1 { color: white !important; margin: 0; font-size: 20px; font-weight: bold; }
    .hub-title p { color: #cbd5e0 !important; margin: 0; font-size: 11px; }
    
    /* Style des zones de messages (hauteur max adaptative avec scroll interne) */
    .chat-history-container {
        background-color: #FFFFFF;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    /* Titres des colonnes */
    .column-title {
        color: #002060;
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURATION IA
openai_api_key = st.secrets.get("OPENAI_API_KEY")
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# 3. AFFICHAGE DU BANDEAU SUPÉRIEUR
logo_gauche = "image_5.png" if os.path.exists("image_5.png") else ""
logo_droite = "image_6.png" if os.path.exists("image_6.png") else ""

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 120px; text-align: left;">
            {"<img src='app/static/" + logo_gauche + "' width='85'>" if logo_gauche else "<span style='color:white; font-size:10px;'>Académie</span>"}
        </div>
        <div class="hub-title">
            <h1>Hub IA - EPS Aix-Marseille</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
        </div>
        <div style="width: 120px; text-align: right;">
            {"<img src='app/static/" + logo_droite + "' width='40'>" if logo_droite else "<span style='color:white; font-size:10px;'>EPS</span>"}
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. CHARGEMENT DES INDEX
@st.cache_resource(show_spinner="Calcul des bases de connaissances en cours...")
def load_all_indexes():
    if not os.path.exists("./data") or len(os.listdir("./data")) == 0:
        os.makedirs("./data", exist_ok=True)
        with open("./data/info.txt", "w") as f:
            f.write("Base de données initialisée.")
    pdf_docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(pdf_docs)
    return index, index

ipack_index, aix_index = load_all_indexes()

# 5. CONFIGURATION DU SPLIT ÉCRAN À DEUX COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    
    # Création de l'historique dans un conteneur HTML sur mesure avec défilement interne
    chat_ipack = ipack_index.as_chat_engine(chat_mode="context", system_prompt="Tu es l'Assistant iPack EPS Aix-Marseille. Réponds de manière structurée et concise. Termine par 'Bon courage pour vos saisies !'.")
    if "messages_ipack" not in st.session_state: 
        st.session_state.messages_ipack = []
    
    # Zone d'affichage des messages
    with st.container():
        st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("💬 **Assistant Ipackeps Aix Marseille**\n\nBonjour, que puis-je faire pour vous ?")
        for m in st.session_state.messages_ipack:
            with st.chat_message(m["role"]): 
                st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    prompt = st.chat_input("Message...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant de Recherches sur le site EPS</div>', unsafe_allow_html=True)
    
    chat_aix = aix_index.as_chat_engine(chat_mode="context", system_prompt="Tu es l'Assistant de recherche du site EPS d'Aix-Marseille.")
    if "messages_aix" not in st.session_state: 
        st.session_state.messages_aix = []
        
    # Zone d'affichage des messages
    with st.container():
        st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("💬 **Assistant de recherche du site EPS**\n\nBonjour, comment puis-je vous aider aujourd'hui ?")
        for m in st.session_state.messages_aix:
            with st.chat_message(m["role"]): 
                st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    prompt_aix = st.chat_input("Message...", key="input_aix")

# 6. ENVOI DES MESSAGES
if prompt:
    st.session_state.messages_ipack.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = chat_ipack.chat(prompt)
        st.session_state.messages_ipack.append({"role": "assistant", "content": response.response})
    st.rerun()

if prompt_aix:
    st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
    with st.chat_message("assistant"):
        response_aix = chat_aix.chat(prompt_aix)
        st.session_state.messages_aix.append({"role": "assistant", "content": response_aix.response})
    st.rerun()

# Pied de page
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 10px; margin-top: 15px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
