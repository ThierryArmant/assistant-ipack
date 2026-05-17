import streamlit as st
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# 1. INITIALISATION DE LA MÉMOIRE CONVERSATIONNELLE STABLE
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

# 2. CONFIGURATION DE LA PAGE ET DES STYLES VISUELS
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

img_gauche = "image_7.png"  
img_droite = "image_5.png"  
img_fond = "image_8.png"    

github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ 
        background-image: url('{github_url}{img_fond}') !important;
        background-size: cover !important; background-position: center center !important; background-repeat: no-repeat !important; background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .hub-header {{
        background-color: #1E293B; display: flex; justify-content: space-between; align-items: center;
        padding: 10px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .column-title {{
        color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center;
        margin-bottom: 10px; height: 30px; background-color: #1E293B; border-radius: 6px; padding: 6px 0;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }}
    .stButton>button {{
        background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important;
        border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important;
        font-size: 11px !important; padding: 2px 12px !important;
    }}
    .stButton>button:hover {{ color: white !important; border-color: white !important; background-color: #1E293B !important; }}
    
    /* Style encadré type Carte Mentale / Capsule Vidéo en haut de réponse */
    .video-card {{
        background-color: rgba(79, 70, 229, 0.12) !important;
        border-left: 6px solid #4F46E5 !important;
        padding: 16px;
        border-radius: 4px 8px 8px 4px;
        margin-bottom: 18px;
    }}
    
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 15% !important;
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: rgba(233, 236, 239, 0.9) !important; color: #212529 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 15% !important;
    }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. CONFIGURATION DES MODÈLES D'IA
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title"><h1>Hub IA - EPS Aix-Marseille</h1><p>Espace Ressources &amp; Assistance Numérique</p></div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

# 4. CHARGEMENT ET CONFIGURATION DE LA MÉMOIRE CHAT ENGINE
@st.cache_resource
def get_chat_engines():
    context = ""
    try:
        if os.path.exists("./data"):
            for file in os.listdir("./data"):
                if file.endswith(".txt"):
                    with open(os.path.join("./data", file), "r", encoding="utf-8") as f:
                        context += f"\n\n=== CONTEXTE: {file} ===\n" + f.read()
    except Exception:
        pass
        
    docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    
    prompt_ipack = (
        "Tu es l'IA experte du module 'iPackEPS' d'Aix-Marseille. Quand on te parle de configurer des sections sportives ou des classes, "
        "ne parle JAMAIS d'évaluation, de notation ou de certification. Reste strictement concentré sur l'arborescence des structures "
        "et décris les étapes d'organisation de façon épurée et chronologique. Reste synchronisé avec l'historique.\n\n"
        f"CONTEXTE D'ACCÈS :\n{context}"
    )
    
    prompt_aix = (
        "Tu es l'IA experte du module 'Recherches Générales' de l'Académie d'Aix-Marseille. Tu devez orienter en priorité absolue "
        "vers les ressources de notre académie d'Aix-Marseille."
    )
    
    engine_ipack = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=3500),
        system_prompt=prompt_ipack
    )
    
    engine_aix = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=3500),
        system_prompt=prompt_aix
    )
    
    return engine_ipack, engine_aix

if openai_api_key:
    engine_ipack, engine_aix = get_chat_engines()

def check_link_status(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.head(url, headers=headers, timeout=1.2)
        return response.status_code < 400
    except Exception:
        return False

# ----------------------------------------------------------------------
# 🗂️ CARTOGRAPHIE MULTI-NIVEAUX : DISTINCTION COLLÈGE / LYCÉE
# ----------------------------------------------------------------------
def get_map_video_support(query_text):
    text = query_text.lower()
    fallback_url = "https://eps.ac-creteil.fr/spip.php?rubrique5"
    
    is_lycee = any(w in text for w in ["lycée", "lycee", "2de", "seconde", "1ere", "premiere", "terminale", "lycéen"])
    is_college = any(w in text for w in ["collège", "college", "6eme", "5eme", "4eme", "3eme", "brevet"])
    
    # Cas neutre : pas de précision collège/lycée
    if ("section" in text or "classe" in text or "import" in text) and not (is_lycee or is_college):
        return """<div class="video-card" style="background-color: rgba(234, 179, 8, 0.1) !important; border-left: 6px solid #EAB308 !important;">
            <strong>🔍 Précision requise (Collège ou Lycée ?) :</strong><br>
            Pour vous donner le bon parcours fléché de notre carte mentale, précisez votre niveau dans votre question (ex: <em>"importer mes classes au lycée"</em> ou <em>"les SSS en collège"</em>).
        </div>"""

    # --- PARCOURS LYCÉE ---
    if is_lycee:
        if "section" in text or "sss" in text or "sportive" in text:
            url = "https://www.youtube.com/watch?v=QPhqFI4czhA"
            active_url = url if check_link_status(url) else fallback_url
            return f"""<div class="video-card"><strong>📍 CARTE MENTALE LYCÉE – Étape 3.4 (Sections Sportives) :</strong><br>
                Suivez la procédure spécifique aux structures de Lycée :<br>
                <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Vidéo SSS Lycée</a><br>
                <small>💡 <em>Rappel Clic :</em> Onglet <strong>Dossiers</strong> -> <strong>[Dossier SSS] Gestion des Sections Sportives</strong>.</small></div>"""
        
        if "classe" in text or "import" in text or "eleve" in text or "groupe" in text:
            url = "https://www.youtube.com/watch?v=tu8J1RBUTwk"
            active_url = url if check_link_status(url) else fallback_url
            return f"""<div class="video-card"><strong>📍 CARTE MENTALE LYCÉE – Étape 3.1 (Classes &amp; Divisions) :</strong><br>
                Synchronisation STSWEB pour les élèves de Lycée :<br>
                <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Classes Lycée</a></div>"""

    # --- PARCOURS COLLÈGE ---
    if is_college:
        if "section" in text or "sss" in text or "sportive" in text:
            return f"""<div class="video-card" style="background-color: rgba(14, 165, 233, 0.1) !important; border-left: 6px solid #0EA5E9 !important;">
                <strong>📍 CARTE MENTALE COLLÈGE – Étape 3.4 (Sections Sportives) :</strong><br>
                Reconduction et bilans SSS pour les Collèges :<br>
                <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Guide d'aide SSS Collège</a></div>"""
                
        if "classe" in text or "import" in text or "eleve" in text or "groupe" in text:
            return f"""<div class="video-card" style="background-color: rgba(14, 165, 233, 0.1) !important; border-left: 6px solid #0EA5E9 !important;">
                <strong>📍 CARTE MENTALE COLLÈGE – Étape 3.1 (Classes &amp; Cycles) :</strong><br>
                Importation des élèves et socle commun (Collège) :<br>
                <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Classes Collège</a></div>"""

    return ""

# 5. STRUCTURE DES DEUX COLONNES INTERFACES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (iPack)", key="clear_ipack"):
        st.session_state.messages_ipack = []
        if openai_api_key: engine_ipack.reset()
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, posez-moi vos questions sur iPack, Santorin ou les Examens. Je vous guiderai pas à pas.")
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}", unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Une question sur iPack ou un Examen ?", key="input_ipack_final"):
        st.session_state.messages_ipack.append({"role": "user", "content": prompt_ipack})
        with st.spinner("Analyse..."):
            if openai_api_key:
                # Placement stratégique de la carte mentale/vidéo en PREMIER
                video_block = get_map_video_support(prompt_ipack)
                response = engine_ipack.chat(prompt_ipack)
                ai_text = response.response
                
                answer = f"{video_block}\n\n{ai_text}" if video_block else ai_text
            else:
                answer = "Clé OpenAI manquante."
        st.session_state.messages_ipack.append({"role": "assistant", "content": answer})
        st.rerun()

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        if openai_api_key: engine_aix.reset()
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, que cherchez-vous comme document ou ressource générale sur le site ?")
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}", unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche générale ?", key="input_aix_final"):
        st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
        with st.spinner("Recherche..."):
            if openai_api_key:
                response_aix = engine_aix.chat(prompt_aix)
                answer_aix = response_aix.response
            else:
                answer_aix = "Clé OpenAI manquante."
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
