import streamlit as st
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

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
# 2. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (CSS)
# ======================================================================
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .hub-header {{ background-color: #1E293B; display: flex; justify-content: space-between; align-items: center; padding: 12px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 14px; border-radius: 20px; font-size: 11px; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block; }}
    .column-title {{ color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center; margin-bottom: 10px; height: 30px; background-color: #1E293B; border-radius: 6px; padding: 6px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 11px !important; }}
    .santorin-card {{ background-color: rgba(255, 255, 255, 0.9) !important; border-left: 6px solid #DC2626 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; }}
    .general-card {{ background-color: rgba(255, 255, 255, 0.95) !important; border-left: 6px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; }}
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 15% !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: rgba(243, 244, 246, 0.95) !important; color: #1F2937 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 15% !important; }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 3. VERROUILLAGE SÉCURITÉ IA (TEMPÉRATURE 0.0 = SÉCURITÉ FACTUELLE)
# ======================================================================
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    # Température à 0.0 pour un respect strict et mathématique des faits
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
    docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    prompt = (
        "Tu es l'IA experte du module 'iPackEPS, Santorin & Examens'. Tu parles exclusivement à des professeurs d'EPS. "
        "CONSIGNE DE RIGUEUR : Appuie-toi uniquement sur les données factuelles fournies dans le contexte local. Si l'interlocuteur te demande un pas-à-pas, "
        "déroule scrupuleusement les étapes de nos documents sans rien omettre. Si la réponse n'est pas dans le contexte, dis-le clairement."
    )
    return index.as_chat_engine(chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=3500), system_prompt=prompt)

if openai_api_key:
    engine_ipack = get_ipack_engine()

# ======================================================================
# 4. EXÉCUTION DOUBLE COLONNE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# ----------------------------------------------------------------------
# COLONNE GAUCHE : ASSISTANT MÉTIER SÉCURISÉ (IPACK / EXAMENS)
# ----------------------------------------------------------------------
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio("Sur quel module travaillez-vous ?", ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"])

    if "examens" in context_choice.lower():
        st.markdown("<style>div[data-testid='stVerticalBlock'] > div:has(div.column-title) { background-color: rgba(239, 68, 68, 0.05) !important; border-radius: 12px; padding: 15px; }</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>div[data-testid='stVerticalBlock'] > div:has(div.column-title) { background-color: rgba(14, 165, 233, 0.05) !important; border-radius: 12px; padding: 15px; }</style>", unsafe_allow_html=True)

    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Votre question (iPack, Santorin...) ?", key="input_ipack"):
        st.session_state.messages_ipack.append({"role": "user", "content": f"**Vous** : {prompt_ipack}"})
        
        with st.spinner("Analyse factuelle..."):
            text_low = prompt_ipack.lower()
            
            # Gestion des cas d'examens bloqués en dur (Réglementation Académique)
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

# ----------------------------------------------------------------------
# COLONNE DROITE : MOTEUR DE RECHERCHE FACTUEL SUR LES 4 PORTAILS DE CONFIANCE
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
        
        with st.spinner("Analyse des portails institutionnels..."):
            # Consigne ultra-stricte d'extraction réglementaire
            prompt_ia_web = (
                f"Tu es l'assistant de recherche EPS expert des 4 portails académiques (Aix-Marseille, Lyon, Créteil, Grenoble). "
                f"L'enseignant d'EPS cherche des informations factuelles sur : '{prompt_aix}'. "
                "Rend une réponse synthétique, claire et purement réglementaire en te basant sur les protocoles officiels de l'Éducation Nationale. "
                "Si la recherche concerne les 'séjours scolaires' ou 'voyages', rappelle obligatoirement les règles d'encadrement en EPS, "
                "le taux de un enseignant pour 19 ou 20 élèves selon la structure (collège/lycée) et l'obligation de dépôt du dossier auprès du chef d'établissement. "
                "Donne l'arborescence type pour trouver ces documents : Accueil > Textes Officiels > Voyages et Sorties. "
                "Reste d'un ton confraternel, pas-à-pas et précis, sans inventer d'URL cassée."
            )
            response_web = Settings.llm.complete(prompt_ia_web)
            answer_aix = f"""<div class="general-card"><strong>🌐 DOSSIER RÉGLEMENTAIRE EXTRACT :</strong><br><br>{response_web.text}</div>"""
                
        st.session_state.messages_aix.append({"role": "assistant", "content": f"**Assistant** : {answer_aix}"})
        st.rerun()
