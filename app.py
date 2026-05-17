import streamlit as st
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. INITIALISATION DE LA MÉMOIRE DE DISCUSSION
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

# 4. CHARGEMENT DE LA BASE DE CONNAISSANCES LOCALE
@st.cache_resource
def get_local_documents():
    context = ""
    try:
        if os.path.exists("./data"):
            for file in os.listdir("./data"):
                if file.endswith(".txt"):
                    with open(os.path.join("./data", file), "r", encoding="utf-8") as f:
                        context += f"\n\n=== SOURCE: {file} ===\n" + f.read()
    except Exception:
        pass
    return context

local_knowledge = get_local_documents()

# FONCTION DE VÉRIFICATION DE LIEN EN DIRECT
def check_link_status(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.head(url, headers=headers, timeout=1.5)
        return response.status_code < 400
    except Exception:
        return False

# MOTEUR DE GÉNÉRATION PAR ÉTAPES CORRIGÉ
def generate_expert_response(user_query, history_type):
    q_lower = user_query.lower()
    
    # -------------------------------------------------------------
    # PASSERELLES DE SÉCURITÉ : VERROUILLAGE DES RÈGLES MÉTIER INTERNES
    # -------------------------------------------------------------
    if history_type == "ipack":
        if "section" in q_lower or "classe" in q_lower:
            return (
                "Pour configurer les **Sections Sportives Scolaires (SSS)** ou importer vos classes dans iPackEPS, "
                "voici la démarche pas-à-pas complète sans interruption :\n\n"
                "**Étape 1 :** Connectez-vous à votre espace iPackEPS via le portail académique Arena.\n"
                "**Étape 2 :** Allez dans le menu de gauche et cliquez sur l'onglet **Dossiers**.\n"
                "**Étape 3 :** Sélectionnez la sous-rubrique **[Dossier SSS] Gestion des Sections Sportives Scolaires** (ou **[Dossier EPS] -> [Classes]** pour un import général).\n"
                "**Étape 4 :** Procédez à la configuration des classes ou à l'attribution des fiches professeurs correspondantes.\n"
                "**Étape 5 :** Validez l'importation complète des élèves rattachés pour stabiliser le protocole.\n\n"
                "[👉 Ouvrir notre espace d'assistance et de tutoriels iPack]--RECHERCHE_SECTION--"
            )

        if "dispens" in q_lower or "inapte" in q_lower or "absent" in q_lower or "0" in q_lower:
            if "dispens" in q_lower:
                return "Sur notre portail de notation, **une dispense médicale neutralise l'APSA**. L'activité concernée ne sera pas prise en compte pour le calcul de la note finale de l'élève. S'il s'agit d'une inaptitude temporaire survenue juste avant l'épreuve, l'élève a droit à une épreuve de substitution."
            if "absent" in q_lower:
                return "Conformément aux modalités d'évaluation, la saisie d'une note pour un élève **absent injustifié** à l'épreuve CCF correspond et génère la note de **0**."

        # LIENS FENÊTRE IPACK & EXAMENS
        url_ipack_creteil = "https://ipackeps.ac-creteil.fr/"
        url_exam_lyon = "https://eps.enseigne.ac-lyon.fr/spip/spip.php?rubrique9"
        url_tuto_creteil = "https://eps.ac-creteil.fr/spip.php?rubrique5" # Liens tutoriels profonds
        
        ipack_ok = check_link_status(url_ipack_creteil)
        lyon_ok = check_link_status(url_exam_lyon)
        tuto_ok = check_link_status(url_tuto_creteil)

        btn_ipack = f"[👉 Ouvrir l'interface de saisie iPackEPS]({url_ipack_creteil})" if ipack_ok else "*(Le serveur national de saisie iPackEPS est actuellement indisponible)*"
        btn_lyon = f"[👉 Consulter le référentiel des examens]({url_exam_lyon})" if lyon_ok else "*(Le serveur des examens complémentaires est en maintenance)*"
        btn_tuto = f"[👉 Consulter nos tutoriels et manuels d'aide iPackEPS]({url_tuto_creteil})" if tuto_ok else "*(Le portail d'assistance technique est temporairement inaccessible)*"

        master_prompt = (
            f"Tu es l'IA experte du module 'iPackEPS et Examens' de l'Académie d'Aix-Marseille.\n"
            f"Tu dois obligatoirement mener tes guides pas-à-pas jusqu'au bout de l'action de l'enseignant.\n\n"
            f"DOCUMENTS DE RÉFÉRENCE INTERNES :\n{local_knowledge}\n\n"
            f"RÈGLES DE CONDUITE :\n"
            f"1. Rédige uniquement sous forme d'étapes claires (Étape 1, Étape 2...).\n"
            f"2. N'invente jamais d'URL. N'affiche jamais de liens bruts contenant Créteil ou Lyon dans ton texte.\n"
            f"3. Si l'enseignant cherche un guide ou un tutoriel spécifique, utilise impérativement cette variable : {btn_tuto}\n"
            f"   Ajoute toujours cette mention d'aide : '(Une fois sur le portail, utilisez la barre de recherche interne en saisissant le mot-clé de votre dossier pour ouvrir directement le document PDF associé)'.\n"
            f"4. Pour la saisie pure, utilise la variable : {btn_ipack}\n"
            f"Question : {user_query}\nRéponse en français :"
        )

    # -------------------------------------------------------------
    # CONDITION B : FENÊTRE RECHERCHES GÉNÉRALES
    # -------------------------------------------------------------
    else:
        url_general_aix = "https://www.pedagogie.ac-aix-marseille.fr/jcms/c_78026/it/accueil"
        url_general_creteil = "https://eps.ac-creteil.fr/"
        url_general_lyon = "https://eps.enseigne.ac-lyon.fr/spip/"
        
        aix_ok = check_link_status(url_general_aix)
        creteil_gen_ok = check_link_status(url_general_creteil)
        lyon_gen_ok = check_link_status(url_general_lyon)

        btn_aix = f"[👉 Consulter le site officiel EPS Aix-Marseille]({url_general_aix})" if aix_ok else "*(Le site principal EPS Aix-Marseille est temporairement inaccessible)*"
        btn_creteil_gen = f"[👉 Explorer nos ressources pédagogiques]({url_general_creteil})" if creteil_gen_ok else "*(Notre base de ressources complémentaires est en cours de mise à jour)*"
        btn_lyon_gen = f"[👉 Accéder aux fiches et outils didactiques]({url_general_lyon})" if lyon_gen_ok else "*(Notre serveur d'outils didactiques est en maintenance)*"

        master_prompt = (
            f"Tu es l'IA experte de la fenêtre 'Recherches Générales' de l'Académie d'Aix-Marseille.\n"
            f"Oriente toujours en priorité absolue vers Aix-Marseille en structurant ton conseil sous forme d'étapes d'accès.\n\n"
            f"VARIABLES AUTORISÉES :\nSite principal : {btn_aix} | Catalogue : {btn_creteil_gen} | Outils : {btn_lyon_gen}\n"
            f"Question : {user_query}\nRéponse ordonnée en français :"
        )

    history_str = ""
    messages = st.session_state.messages_ipack if history_type == "ipack" else st.session_state.messages_aix
    for m in messages[-4:]:
        history_str += f"{m['role']}: {m['content']}\n"

    response = Settings.llm.complete(master_prompt)
    raw_answer = response.text
    
    # Traitement de sécurité final pour injecter la consigne de recherche si le bot renvoie vers l'aide
    if "--RECHERCHE_SECTION--" in raw_answer:
        url_tuto_creteil = "https://eps.ac-creteil.fr/spip.php?rubrique5"
        tuto_ok = check_link_status(url_tuto_creteil)
        if tuto_ok:
            link_str = f"[👉 Accéder à notre espace de tutoriels et guides de configuration]({url_tuto_creteil})\n\n*(💡 **Conseil pratique :** Une fois sur cette page d'aide, saisissez directement le mot-clé **'sections sportives'** ou **'classes'** dans la barre de recherche en haut du site pour ouvrir instantanément le document officiel associé).* "
        else:
            link_str = "*(Notre serveur d'assistance technique et de tutoriels est actuellement en maintenance. Veuillez vous reconnecter ultérieurement).* "
        raw_answer = raw_answer.replace("[👉 Ouvrir notre espace d'assistance et de tutoriels iPack]--RECHERCHE_SECTION--", link_str)
        
    return raw_answer

# 5. SPLIT ÉCRAN EN 2 COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (iPack)", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, posez-moi vos questions sur iPack, Santorin ou les Examens. Je vous guiderai pas à pas.")
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}")
            
    if prompt_ipack := st.chat_input("Une question sur iPack ou un Examen ?", key="input_ipack_final"):
        st.session_state.messages_ipack.append({"role": "user", "content": prompt_ipack})
        with st.spinner("Analyse des règles et serveurs examens..."):
            answer = generate_expert_response(prompt_ipack, "ipack")
        st.session_state.messages_ipack.append({"role": "assistant", "content": answer})
        st.rerun()

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, que cherchez-vous comme document ou ressource générale sur le site ?")
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}")
            
    if prompt_aix := st.chat_input("Votre recherche générale (Ressources, textes...) ?", key="input_aix_final"):
        st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
        with st.spinner("Recherche prioritaire sur Aix-Marseille..."):
            answer_aix = generate_expert_response(prompt_aix, "aix")
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
