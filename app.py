import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# Import de la bibliothèque de recherche présente dans ton requirements.txt
from googlesearch import search

# ======================================================================
# CONFIGURATION DES LIENS VIDÉOS (REMPLACE ICI PAR TES VRAIS LIENS)
# ======================================================================
LIENS_VIDEOS = {
    "1️⃣": "Lien de la vidéo Étape 1 - Saisie Établissement",
    "2️⃣": "Lien de la vidéo Étape 2 - Fiche Professeur",
    "3️⃣": "Lien de la vidéo Étape 3 - Classes",
    "4️⃣": "Lien de la vidéo Étape 4 - APSA",
    "5️⃣": "Lien de la vidéo Étape 5 - Périodes",
    "6️⃣": "Lien de la vidéo Étape 6 - Élèves et Groupes",
    "7️⃣": "Lien de la vidéo Étape 7 - Ouverture SSS",
    "8️⃣": "Lien de la vidéo Étape 8 - Projet et Bilan SSS",
    "9️⃣": "Lien de la vidéo Étape 9 - Dossier APPN",
    "🔟": "Lien de la vidéo Étape 10 - Validation finale",
    "ℹ️": "Lien de la vidéo Étape 11 - Assistance technique"
}

# ======================================================================
# 1. INITIALISATION ET COMPTEUR DE VISITES CENTRALISÉ
# ======================================================================
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

def incrementer_et_recuperer_compteur():
    fichier_compteur = "compteur.txt"
    if not os.path.exists(fichier_compteur):
        with open(fichier_compteur, "w", encoding="utf-8") as f: f.write("0")
    with open(fichier_compteur, "r", encoding="utf-8") as f:
        try: total_visites = int(f.read().strip())
        except ValueError: total_visites = 0
    if "visite_comptabilisee" not in st.session_state:
        total_visites += 1
        st.session_state.visite_comptabilisee = True
        with open(fichier_compteur, "w", encoding="utf-8") as f: f.write(str(total_visites))
    return total_visites

nb_visites = incrementer_et_recuperer_compteur()

# ======================================================================
# 2. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (EFFET DEPOLI SEMI-TRANSPARENT)
# ======================================================================
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* En-tête principal */
    .hub-header {{ background-color: #1E293B; display: flex; justify-content: space-between; align-items: center; padding: 12px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 14px; border-radius: 20px; font-size: 11px; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block; }}
    
    /* Titres des colonnes */
    .column-title {{ color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center; margin-bottom: 0px; height: 35px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 6px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 11px !important; }}
    
    /* STYLE SEMI-TRANSPARENT OPTIMISÉ (Effet verre poli anti-reflets) */
    [data-testid="stVerticalBlock"] > div:has(div.column-title) {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border-radius: 8px;
        padding: 0px 0px 15px 0px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    
    /* Ajustement des marges internes */
    [data-testid="stVerticalBlock"] > div:has(div.column-title) > div {{
        padding-left: 15px !important;
        padding-right: 15px !important;
    }}
    
    /* Lisibilité parfaite des textes sur le fond semi-transparent */
    .stApp p, .stApp label, .stApp span, .stApp div[data-baseweb="select"] {{
        color: #0F172A !important;
        font-weight: 600 !important;
    }}
    
    /* Style des onglets (Tabs) */
    div[data-testid="stTab"] button p {{
        color: #334155 !important;
    }}
    div[data-testid="stTab"] button[aria-selected="true"] p {{
        color: #0F172A !important;
        font-weight: 700 !important;
    }}
    
    /* Cartes de messages (Blanches pures pour trancher sur le fond dépoli) */
    .santorin-card {{ background-color: #FFFFFF !important; border-left: 6px solid #DC2626 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    .general-card {{ background-color: #FFFFFF !important; border-left: 6px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    
    /* Bulles de chat */
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: #F1F5F9 !important; border-radius: 16px 16px 0px 16px !important; margin-left: 10% !important; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: #E2E8F0 !important; color: #1F2937 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 10% !important; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 3. VERROUILLAGE SÉCURITÉ IA (TEMPÉRATURE 0.0 = SÉCURITÉ FACTUELLE)
# ======================================================================
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title" style="text-align: center; flex-grow: 1;">
            <h1>Hub IA - EPS</h1><p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ipack_engine():
    if not os.path.exists("./data"):
        os.makedirs("./data")
    docs = SimpleDirectoryReader(input_dir="./data", encoding="utf-8").load_data()
    index = VectorStoreIndex.from_documents(docs)
    prompt = (
        "Tu es l'IA experte du module 'iPackEPS, Santorin & Examens'. Tu parles exclusivement à des professeurs d'EPS. "
        "CONSIGNE DE RIGUEUR : Appuie-toi uniquement sur les données factuelles fournies dans le contexte local. Si l'interlocuteur te demande un pas-à-pas, "
        "déroule scrupuleusement les étapes de nos documents sans rien omettre. Si la réponse n'est pas dans le contexte, dis-le clairement."
    )
    return index.as_chat_engine(chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=3500), system_prompt=prompt)

if openai_api_key:
    engine_ipack = get_ipack_engine()

# --- MOTEUR DE RECHERCHE TEXTE WEB ---
def recuperer_contenu_web(requete):
    try:
        DOMAINES_AUTORISES = [
            "site:education.gouv.fr/bo",                 
            "site:ac-aix-marseille.fr/eps"
        ]
        ciblage_sites = " OR ".join(DOMAINES_AUTORISES)
        requete_ciblee = f"{requete} ({ciblage_sites})"
        
        liens_trouves = []
        for url in search(requete_ciblee, num_results=3, lang="fr"):
            liens_trouves.append(url)
            
        if not liens_trouves:
            return "Aucun document trouvé sur les portails configurés.", []
            
        contexte_extrait = ""
        entetes = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        for url in liens_trouves:
            try:
                rep = requests.get(url, headers=entetes, timeout=5)
                if rep.status_code == 200:
                    soup = BeautifulSoup(rep.text, "html.parser")
                    for s in soup(["script", "style", "nav", "footer"]): s.decompose()
                    texte_propre = " ".join(soup.get_text().split())[:2000]
                    contexte_extrait += f"--- SOURCE: {url} ---\n{texte_propre}\n\n"
            except:
                continue
                
        return contexte_extrait, liens_trouves
    except Exception as e:
        return f"Erreur de connexion aux portails officiels (Détail : {str(e)}).", []

# ======================================================================
# 4. EXÉCUTION DOUBLE COLONNE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# ----------------------------------------------------------------------
# COLONNE GAUCHE : ASSISTANT MÉTIER EPS + PARCOURS VIDÉOS
# ----------------------------------------------------------------------
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS & Vidéos</div>', unsafe_allow_html=True)
    
    tab_chat, tab_videos = st.tabs(["💬 Poser une question", "🎥 Parcours Vidéos Fléchés"])
    
    with tab_chat:
        if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
            st.session_state.messages_ipack = []
            st.rerun()
            
        context_choice = st.radio("Sur quel module travaillez-vous ?", ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"])

        for m in st.session_state.messages_ipack:
            with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
                
        if prompt_ipack := st.chat_input("Votre question (iPack, Santorin...) ?", key="input_ipack"):
            st.session_state.messages_ipack.append({"role": "user", "content": f"**Vous** : {prompt_ipack}"})
            
            with st.spinner("Analyse factuelle..."):
                text_low = prompt_ipack.lower()
                
                if "examens" in context_choice.lower() and any(w in text_low for w in ["inapte", "dispens", "absent"]):
                    if "inapte" in text_low:
                        answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Inapte :</strong><br><strong>Règle factuelle : On ne met pas 0.</strong> L'inaptitude médicale ouvre obligatoirement le droit à une épreuve de substitution organisée par l'établissement.</div>"""
                    elif "dispens" in text_low:
                        answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Dispensé :</strong><br><strong>Règle factuelle : On ne met pas 0.</strong> La dispense médicale valide entraîne la neutralisation de l'APSA sur le serveur d'examen.</div>"""
                    else:
                        answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Absent :</strong><br>L'absence injustifiée à un CCF certificatif génère la note obligatoire de <strong>0</strong>.</div>"""
                else:
                    response_locale = engine_ipack.chat(f"CONTEXTE : {context_choice}. QUESTION : {prompt_ipack}")
                    answer = response_locale.response

            st.session_state.messages_ipack.append({"role": "assistant", "content": f"**Assistant** : {answer}"})
            st.rerun()

    with tab_videos:
        st.write(" Sélectionnez un tutoriel officiel pour suivre le parcours fléché :")
        
        video_choice = st.selectbox(
            "Étape du parcours iPackEPS :",
            [
                "1️⃣ Saisie Établissement (Axes du projet, EDT, Équipe...)",
                "2️⃣ Ma Fiche Professeur & Coordonnées",
                "3️⃣ Dossier 3.1 : Création des Classes & Affectations",
                "4️⃣ Dossier 3.1 : Configuration des APSA & Référentiels",
                "5️⃣ Dossier 3.1 : Paramétrage des Périodes d'évaluation",
                "6️⃣ Dossier 3.1 : Attribution des Élèves & Groupes",
                "7️⃣ Dossier 3.4 : Demande d'ouverture de SSS (Sections Sportives)",
                "8️⃣ Dossier 3.4 : Projet annuel & Bilan de votre SSS",
                "9️⃣ Dossier 3.6 : Dossier APPN & Environnement spécifique",
                "🔟 Demande de Validation finale du dossier",
                "ℹ️ Demande d'assistance technique & Contact iPack"
            ]
        )
        
        cle_emodji = video_choice[:2].strip()
        lien_selectionne = LIENS_VIDEOS.get(cle_emodji, "")
        
        if not lien_selectionne or "Lien de la vidéo" in lien_selectionne:
            st.info(f"🎥 **Tutoriel bientôt disponible** : Le lien vidéo pour l'étape *'{video_choice[3:]}'* est en cours de configuration.")
        else:
            st.video(lien_selectionne)

# ----------------------------------------------------------------------
# COLONNE DROITE : MOTEUR DE RECHERCHE EN DIRECT (ANTI-HALLUCINATION)
# ----------------------------------------------------------------------
with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS (Portails Officiels)</div>', unsafe_allow_html=True)
    
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche officielle (Ex: TASA, Séjours scolaires...)", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Le robot explore les portails académiques..."):
            text_aix_low = prompt_aix.lower()
            
            if "tasa" in text_aix_low:
                answer_aix = """<div class="general-card">
                <strong>🌐 RECHERCHE OFFICIELLE – TASA (Taux d'Activité du Sport d'Association) :</strong><br><br>
                Le <strong>TASA</strong> correspond au <strong>Taux d'Activité du Sport d'Association</strong> spécifique à l'académie d'Aix-Marseille.<br><br>
                <strong>Calcul officiel :</strong> <code>(Nombre de licenciés AS / Effectif total des élèves) x 100</code>.<br><br>
                🔗 <a href="https://www.pedagogie.ac-aix-marseille.fr/jcms/c_11195547/fr/tasa" target="_blank">Cliquez ici pour ouvrir la page officielle TASA sur le Portail d'Aix-Marseille</a>
                </div>"""
            else:
                vrai_contexte_web, liens_utilises = recuperer_contenu_web(prompt_aix)
                
                if not liens_utilises:
                    answer_aix = f"""<div class="general-card">{vrai_contexte_web}</div>"""
                else:
                    prompt_ia_web = (
                        f"Tu es l'assistant de recherche EPS expert. Tu as interdiction stricte d'inventer ou d'extrapoler.\n"
                        f"L'enseignant cherche des informations sur : '{prompt_aix}'.\n\n"
                        f"Voici le VRAI TEXTE extrait directement des pages web officielles :\n{vrai_contexte_web}\n\n"
                        f"CONSIGNE : Synthétise uniquement les données extraites ci-dessus. Si l'information précise n'est pas dans le texte extrait, dis-le honnêtement. "
                        f"Si la recherche concerne les 'séjours scolaires' ou 'voyages', rappelle le taux de 1 enseignant pour 19 ou 20 élèves et le dépôt du dossier. "
                        f"Reste d'un ton confraternel et affiche les liens consultés tout en bas."
                    )
                    response_web = Settings.llm.complete(prompt_ia_web)
                    
                    liens_html = "<br><br><strong>🔗 Liens officiels consultés en direct :</strong><br>" + "<br>".join([f'• <a href="{l}" target="_blank">{l}</a>' for l in liens_utilises])
                    answer_aix = f"""<div class="general-card"><strong>🌐 DOSSIER RÉGLEMENTAIRE EXTRACT :</strong><br><br>{response_web.text}{liens_html}</div>"""
                
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
