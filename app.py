import streamlit as st
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# 1. INITIALISATION DE LA MÉMOIRE ET DES COMPTEURS DE RÉPÉTITION
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "query_repeat_count" not in st.session_state:
    st.session_state.query_repeat_count = 1

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
    
    /* Styles des fenêtres d'alertes */
    .video-card {{ background-color: rgba(79, 70, 229, 0.12) !important; border-left: 6px solid #4F46E5 !important; padding: 16px; border-radius: 4px 8px 8px 4px; margin-bottom: 18px; }}
    .video-card-college {{ background-color: rgba(14, 165, 233, 0.1) !important; border-left: 6px solid #0EA5E9 !important; padding: 16px; border-radius: 4px 8px 8px 4px; margin-bottom: 18px; }}
    .santorin-card {{ background-color: rgba(239, 68, 68, 0.1) !important; border-left: 6px solid #EF4444 !important; padding: 16px; border-radius: 4px 8px 8px 4px; margin-bottom: 18px; }}
    .sos-card {{ background-color: rgba(220, 38, 38, 0.15) !important; border: 2px solid #DC2626 !important; padding: 20px; border-radius: 8px; margin-bottom: 18px; }}
    
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 15% !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: rgba(233, 236, 239, 0.9) !important; color: #212529 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 15% !important; }}
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
                        context += f"\n\n=== SOURCE: {file} ===\n" + f.read()
    except Exception:
        pass
        
    docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    
    prompt_ipack = (
        "Tu es l'IA experte du module 'iPackEPS et Saisie'. Traite uniquement de la configuration, des classes, "
        "des listes d'élèves et des dossiers sportifs (APPN, SSS). Ne confonds jamais cela avec Santorin ou les examens.\n\n"
        f"CONTEXTE :\n{context}"
    )
    prompt_aix = "Tu es l'IA experte du module 'Recherches Générales' de l'Académie d'Aix-Marseille."
    
    engine_ipack = index.as_chat_engine(
        chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=3500), system_prompt=prompt_ipack
    )
    engine_aix = index.as_chat_engine(
        chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=3500), system_prompt=prompt_aix
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
# 🗂️ LOGIQUE CONTEXTUELLE COUPLÉE (IPACK VS EXAMENS / SANTORIN)
# ----------------------------------------------------------------------
def get_forced_context_response(query_text, chosen_context):
    text = query_text.lower()
    fallback_url = "https://eps.ac-creteil.fr/spip.php?rubrique5"
    
    # Intégration de l'URL de ton document web d'évaluation
    url_document_web_eval = "https://pole-examens.github.io/tutoriels-examens/co/guide.html"

    # ------------------------------------------------------------------
    # BRANCHEMENT 1 : CONTEXTE EXAMENS & SANTORIN (COUPLÉ AU GUIDE WEB)
    # ------------------------------------------------------------------
    if chosen_context == "📊 Examens & Santorin (Notes, Absences, Dispenses)":
        
        eval_online = check_link_status(url_document_web_eval)
        if eval_online:
            btn_eval_web = f"""<div class="santorin-card" style="background-color: rgba(79, 70, 229, 0.1) !important; border-left: 6px solid #4F46E5 !important;">
                <strong>📋 PARCOURS SÉCURISÉ – Référentiel Évaluations :</strong><br>
                Pour vous guider dans la configuration de vos grilles certificatives et barèmes, utilisez notre outil d'analyse en direct :<br>
                <a href="{url_document_web_eval}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">💻 Cliquez ici pour ouvrir le Guide Interactive des Évaluations EPS</a>
            </div>"""
        else:
            btn_eval_web = """<div class="santorin-card" style="background-color: rgba(239, 68, 68, 0.05) !important; border-left: 6px solid #EF4444 !important;">
                <strong>📋 Outil d'Évaluation :</strong><br>
                <em>Notre serveur de consultation des guides d'évaluation rencontre une coupure temporaire. Veuillez vous reconnecter ultérieurement.</em>
            </div>"""

        # Traitement des cas métiers prioritaires
        if "inapte" in text or "substitution" in text:
            return f"""{btn_eval_web}
            <div class="santorin-card">
                <strong>📊 MODULE SANTORIN &amp; EXAMENS – Élève Inapte :</strong><br>
                <strong>Règle stricte : On ne met pas 0.</strong><br>
                L'inaptitude médicale constatée le jour de l'épreuve ouvre obligatoirement le droit pour l'élève de se présenter à une <strong>épreuve de substitution</strong> organisée en interne par l'établissement.
            </div>"""
        if "dispens" in text or "neutrali" in text:
            return f"""{btn_eval_web}
            <div class="santorin-card" style="background-color: rgba(245, 158, 11, 0.1) !important; border-left: 6px solid #F59E0B !important;">
                <strong>📊 MODULE SANTORIN &amp; EXAMENS – Élève Dispensé :</strong><br>
                <strong>Règle stricte : On ne met pas 0.</strong><br>
                Une dispense médicale validée entraîne la <strong>neutralisation de l'APSA</strong> sur le serveur d'examen. L'activité est exclue du calcul final pour ne pas pénaliser la moyenne certificative de l'élève.
            </div>"""
        if "absent" in text or " 0 " in text:
            return f"""{btn_eval_web}
            <div class="santorin-card" style="background-color: rgba(16, 185, 129, 0.1) !important; border-left: 6px solid #10B981 !important;">
                <strong>📊 MODULE SANTORIN &amp; EXAMENS – Élève Absent :</strong><br>
                <strong>Règle stricte : L'absence injustifiée équivaut à 0.</strong><br>
                Si un élève ne se présente pas à une situation d'évaluation sans justificatif officiel, la note obligatoire à saisir est un <strong>0</strong>.
            </div>"""
        return btn_eval_web

    # ------------------------------------------------------------------
    # BRANCHEMENT 2 : CONTEXTE IPACK EPS
    # ------------------------------------------------------------------
    else:
        is_lycee = any(w in text for w in ["lycée", "lycee", "2de", "seconde", "1ere", "premiere", "terminale"])
        is_college = any(w in text for w in ["collège", "college", "6eme", "5eme", "4eme", "3eme", "brevet"])
        
        if not (is_lycee or is_college) and any(w in text for w in ["section", "classe", "import", "commenc"]):
            return "CHOIX_STRUCTURE"

        if is_lycee:
            if "section" in text or "sss" in text or "sportive" in text:
                url = "https://www.youtube.com/watch?v=QPhqFI4czhA"
                active_url = url if check_link_status(url) else fallback_url
                return f"""<div class="video-card"><strong>🛠️ MODULE IPACK LYCÉE – Configuration SSS (3.4) :</strong><br>
                    <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Vidéo de Configuration SSS Lycée</a></div>"""
            if "classe" in text or "import" in text:
                url = "https://www.youtube.com/watch?v=tu8J1RBUTwk"
                active_url = url if check_link_status(url) else fallback_url
                return f"""<div class="video-card"><strong>🛠️ MODULE IPACK LYCÉE – Importation Classes (3.1) :</strong><br>
                    <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel d'importation STSWEB Lycée</a></div>"""

        if is_college:
            if "section" in text or "sss" in text or "sportive" in text:
                return f"""<div class="video-card-college"><strong>🛠️ MODULE IPACK COLLÈGE – Configuration SSS (3.4) :</strong><br>
                    <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Manuel de Reconduction SSS Collège</a></div>"""
            if "classe" in text or "import" in text:
                return f"""<div class="video-card-college"><strong>🛠️ MODULE IPACK COLLÈGE – Importation Classes (3.1) :</strong><br>
                    <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Guide d'importation des Groupes Socle Commun</a></div>"""

        return "REGLEMENT_IPACK"

# 5. SPLIT ÉCRAN EN 2 COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (iPack/Exam)", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.session_state.query_repeat_count = 1
        st.session_state.last_query = ""
        if openai_api_key: engine_ipack.reset()
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour. Choisissez votre thématique ci-dessous puis posez votre question.")
        
    context_choice = st.radio(
        "Sur quel module travaillez-vous actuellement ?",
        ["🛠️ iPackEPS (Configuration, Classes, Import Élevés, APPN, SSS)", 
         "📊 Examens & Santorin (Notes, Absences, Dispenses)"],
        key="context_selector"
    )
    
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}", unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Posez votre question précise ici...", key="input_ipack_final"):
        st.session_state.messages_ipack.append({"role": "user", "content": prompt_ipack})
        
        # --- LOGIQUE DE SÉCURITÉ ANTI-RÉPÉTITION ---
        cleaned_query = prompt_ipack.strip().lower()
        if cleaned_query == st.session_state.last_query:
            st.session_state.query_repeat_count += 1
        else:
            st.session_state.last_query = cleaned_query
            st.session_state.query_repeat_count = 1
            
        with st.spinner("Traitement ciblé..."):
            if st.session_state.query_repeat_count >= 3:
                answer = """<div class="sos-card">
                    <h3 style="color:#DC2626; margin:0 0 10px 0;">📬 Besoin d'une assistance humaine</h3>
                    Il semble que notre assistant virtuel ne parvienne pas à vous apporter la réponse exacte ou que votre situation nécessite une intervention technique sur les bases académiques.<br><br>
                    N'hésitez pas à contacter directement notre cellule d'assistance par courriel à l'adresse officielle dédiée :<br>
                    📧 <a href="mailto:ipackeps@ac-aix-marseille.fr" style="font-weight:bold; color:#DC2626; text-decoration:underline;">ipackeps@ac-aix-marseille.fr</a><br><br>
                    <em>Pensez à préciser votre nom, votre établissement ainsi que l'anomalie rencontrée.</em>
                </div>"""
            else:
                forced_block = get_forced_context_response(prompt_ipack, context_choice)
                
                if forced_block not in ["REGLEMENT_EXAM", "REGLEMENT_IPACK", "CHOIX_STRUCTURE"]:
                    answer = forced_block
                elif forced_block == "CHOIX_STRUCTURE":
                    answer = """<div class="video-card" style="background-color: rgba(234, 179, 8, 0.1) !important; border-left: 6px solid #EAB308 !important;">
                        <strong>🔍 Structure non détectée :</strong><br>
                        Précisez si votre demande d'import concerne le <strong>Collège</strong> ou le <strong>Lycée</strong> directement dans votre texte pour obtenir le bon guide fléché.
                    </div>"""
                else:
                    if openai_api_key:
                        response = engine_ipack.chat(f"CONTEXTE SÉLECTIONNÉ : {context_choice}. QUESTION : {prompt_ipack}")
                        answer = response.response
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
