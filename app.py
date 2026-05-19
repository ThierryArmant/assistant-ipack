import streamlit as st
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.readers.file import PandasCSVReader

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
# 2. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (CSS CARTES TRANSPARENTES)
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
    
    /* Cartes indépendantes Effet Verre Dépoli (Laisse voir l'arrière-plan à 65%) */
    .glass-card {{
        background-color: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 0px 0px 8px 8px;
        padding: 18px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.2);
        border-left: 1px solid rgba(255, 255, 255, 0.3);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 20px;
    }}
    
    /* Renforcement de la couleur des textes sur le fond dépoli */
    .glass-card p, .glass-card label, .glass-card span, .glass-card div[data-baseweb="select"] {{
        color: #0F172A !important;
        font-weight: 600 !important;
    }}
    
    .santorin-card {{ background-color: #FFFFFF !important; border-left: 6px solid #DC2626 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    .general-card {{ background-color: #FFFFFF !important; border-left: 6px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    
    /* Bulles de discussion */
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: #FFFFFF !important; border-radius: 16px 16px 0px 16px !important; margin-left: 10% !important; box-shadow: 0px 2px 6px rgba(0,0,0,0.08); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: #F8FAFC !important; color: #1F2937 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 10% !important; box-shadow: 0px 2px 6px rgba(0,0,0,0.05); }}
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

# --- CONFIGURATION DU FILTRAGE DES DEUX ENGINES DISCRIMINANTS ---
@st.cache_resource
def get_separated_engines():
    file_extractor = {".csv": PandasCSVReader(concat_rows=False)}
    
    all_docs = SimpleDirectoryReader(input_dir="./data", file_extractor=file_extractor, required_exts=[".csv", ".txt"]).load_data()
    
    # Isolation Strict de Santorin & Examens (Mots clés : 'santorin' ou 'evaluation')
    docs_santorin = [d for d in all_docs if "santorin" in d.metadata.get("file_name", "").lower() or "evaluation" in d.metadata.get("file_name", "").lower()]
    index_santorin = VectorStoreIndex.from_documents(docs_santorin)
    
    # Isolation Strict d'iPackEPS (Mot clé : 'ipack')
    docs_ipack = [d for d in all_docs if "ipack" in d.metadata.get("file_name", "").lower()]
    index_ipack = VectorStoreIndex.from_documents(docs_ipack)
    
    return index_ipack, index_santorin

if openai_api_key:
    index_ipack, index_santorin = get_separated_engines()

# ======================================================================
# 4. EXÉCUTION DOUBLE COLONNE INDÉPENDANTE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# ----------------------------------------------------------------------
# COLONNE GAUCHE : ASSISTANT MÉTIER SÉCURISÉ & ÉTANCHE (IPACK / EXAMENS)
# ----------------------------------------------------------------------
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio("Sur quel module travaillez-vous ?", ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"])

    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Votre question (iPack, Santorin...) ?", key="input_ipack"):
        st.session_state.messages_ipack.append({"role": "user", "content": f"**Vous** : {prompt_ipack}"})
        
        with st.spinner("Analyse factuelle..."):
            
            # Branchement physique de l'IA sur le bon index selon le choix de l'utilisateur
            if "examens" in context_choice.lower():
                system_prompt = (
                    "Tu es l'assistant spécialisé EXAMENS & SANTORIN. Tu réponds exclusivement à des professeurs d'EPS.\n"
                    "Tu es connecté UNIQUEMENT au fichier Excel/CSV de la FAQ Évaluation et Certification.\n\n"
                    "CONSIGNES DE SÉCURITÉ ABSOLUES :\n"
                    "1. Extrais les données ligne par ligne depuis les colonnes du tableau correspondantes ('reponse Lycée GT Bac', 'reponse Lycée Pro Bac' ou 'Reponse Collège DNB') selon la demande.\n"
                    "2. Ne confonds jamais les règles du Lycée (CCF) et du Collège (DNB).\n"
                    "3. Si un élève est absent ou inapte au collège, s'appuyer uniquement sur la colonne 'Reponse Collège DNB' pour formuler la règle exacte sans inventer."
                )
                chosen_index = index_santorin
            else:
                system_prompt = (
                    "Tu es l'assistant spécialisé IPACKEPS. Tu parles exclusivement à des professeurs d'EPS.\n"
                    "Tu es connecté UNIQUEMENT aux données de configuration iPackEPS.\n\n"
                    "CONSIGNES DE SÉCURITÉ ABSOLUES :\n"
                    "1. Donne uniquement les étapes pas-à-pas de création des structures, des classes, des périodes et des sections sportives (SSS).\n"
                    "2. Ignore totalement les règles de notation de Santorin ou du CCF."
                )
                chosen_index = index_ipack
            
            chat_engine = chosen_index.as_chat_engine(
                chat_mode="condense_plus_context", 
                memory=ChatMemoryBuffer.from_defaults(token_limit=3500), 
                system_prompt=system_prompt
            )
            
            response_locale = chat_engine.chat(prompt_ipack)
            answer = response_locale.response

        # Formatage de la réponse selon le contexte choisi
        if "examens" in context_choice.lower():
            formatted_answer = f'<div class="santorin-card"><strong>📊 RÉPONSE CERTIFICATION :</strong><br><br>{answer}</div>'
        else:
            formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE IPACKEPS :</strong><br><br>{answer}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# COLONNE DROITE : MOTEUR DE RECHERCHE ACADÉMIQUE CIRCULAIRES (INDÉPENDANT)
# ----------------------------------------------------------------------
with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS (Portails Officiels)</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche officielle (Ex: TASA, Séjours scolaires...)", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Analyse des portails institutionnels..."):
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
                
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
