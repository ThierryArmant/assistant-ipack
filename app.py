import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. INITIALISATION DE LA MÉMOIRE (Évite le gel et les doublons)
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

img_gauche = "image_7.png"  
img_droite = "image_5.png"  
img_fond = "image_8.png"    

github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ 
        background-image: url('{github_url}{img_fond}') !important;
        background-size: cover !important; background-position: center center !important; background-repeat: no-repeat !important; background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .hub-header {{
        background-color: #1E293B; display: flex; justify-content: space-between; align-items: center;
        padding: 10px 25px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .column-title {{
        color: #FFFFFF; font-size: 14px; font-weight: 700; text-align: center;
        margin-bottom: 10px; height: 24px; background-color: #1E293B; border-radius: 4px; padding: 4px 0;
    }}
    .scroll-chat {{
        height: 380px !important; overflow-y: auto !important; padding: 15px;
        background-color: rgba(255, 255, 255, 0.45) !important; backdrop-filter: blur(4px); border-radius: 8px 8px 0px 0px;
    }}
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 8px 12px !important; margin-bottom: 10px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: rgba(255, 255, 255, 0.6) !important; border-radius: 12px !important; margin-left: 8% !important;
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #E9ECEF !important; color: #212529 !important; border-radius: 12px !important; margin-right: 8% !important;
    }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    .stChatInputContainer {{ background-color: #FFFFFF !important; border-radius: 0px 0px 8px 8px !important; }}
    .stChatInputContainer textarea {{ color: #1E293B !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. CONFIGURATION ASSISTANT ET SYSTEM PROMPT (Verrouillage en Français EPS)
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(
        model="gpt-4o-mini", 
        temperature=0.1, 
        api_key=openai_api_key,
        system_prompt=(
            "Tu es l'Assistant iPack EPS et Examens pour l'Académie d'Aix-Marseille. "
            "Tu dois répondre exclusivement en français. "
            "Ne parle jamais de l'île grecque de Santorin. Pour toi, Santorin est uniquement l'application "
            "institutionnelle française de gestion des lots de correction et de saisie des notes du CCF EPS. "
            "Aide les enseignants en utilisant uniquement les documents fournis dans ton index."
        )
    )
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title"><h1>Hub IA - EPS Aix-Marseille</h1><p>Espace Ressources &amp; Assistance Numérique</p></div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

# 4. LECTURE PERFORMANTE DU DOSSIER DATA
@st.cache_resource
def load_local_index():
    if not os.path.exists("./data"): 
        os.makedirs("./data")
    # Utilisation du sélecteur automatique robuste de documents
    docs = SimpleDirectoryReader(input_dir="./data").load_data()
    if not docs:
        return None
    return VectorStoreIndex.from_documents(docs)

index_ia = load_local_index()

# 5. GESTION DES ENVOIS AVANT L'AFFICHAGE POUR ÉVITER LES DOUBLONS OUT-OF-FRAME
prompt_ipack = st.session_state.get("input_ipack_value", None)
prompt_aix = st.session_state.get("input_aix_value", None)

# ZONE DE TRAITEMENT IMÉDIAT
if st.session_state.get("input_ipack") and index_ia:
    txt = st.session_state.input_ipack
    st.session_state.messages_ipack.append({"role": "user", "content": txt})
    response = index_ia.as_chat_engine().chat(txt).response
    st.session_state.messages_ipack.append({"role": "assistant", "content": response})

if st.session_state.get("input_aix") and index_ia:
    txt_a = st.session_state.input_aix
    st.session_state.messages_aix.append({"role": "user", "content": txt_a})
    response_aix = index_ia.as_chat_engine().chat(txt_a).response
    st.session_state.messages_aix.append({"role": "assistant", "content": response_aix})

# 6. AFFICHAGE DES DEUX COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("Bonjour, que puis-je faire pour vous ?")
        for m in st.session_state.messages_ipack:
            with st.chat_message(m["role"]):
                st.markdown(f"**{'Vous' if m['role']=='user' else 'Assistant iPack'}** :\n\n{m['content']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.chat_input("Votre question iPack...", key="input_ipack")

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="scroll-chat">', unsafe_allow_html=True)
        with st.chat_message("assistant"): 
            st.markdown("Bonjour, que cherchez-vous sur le site ?")
        for m in st.session_state.messages_aix:
            with st.chat_message(m["role"]):
                st.markdown(f"**{'Vous' if m['role']=='user' else 'Assistant Site'}** :\n\n{m['content']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.chat_input("Votre question site EPS...", key="input_aix")

st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 10px; margin-top: 15px; background-color: rgba(30, 41, 59, 0.8); padding: 5px; border-radius: 4px;'>© 2026 - Académie d'Aix-Marseille</p>", unsafe_allow_html=True)
