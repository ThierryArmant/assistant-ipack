import streamlit as st
import os
import requests
# Importation du module de recherche web live
from googlesearch import search  
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer

# ======================================================================
# 1. INITIALISATION DE LA MÉMOIRE ET DES COMPTEURS
# ======================================================================
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

# ----------------------------------------------------------------------
# 📈 GESTION DU COMPTEUR DE VISITES (FICHIER LOCAL)
# ----------------------------------------------------------------------
def incrementer_et_recuperer_compteur():
    fichier_compteur = "compteur.txt"
    if not os.path.exists(fichier_compteur):
        with open(fichier_compteur, "w", encoding="utf-8") as f:
            f.write("0")
    with open(fichier_compteur, "r", encoding="utf-8") as f:
        try:
            total_visites = int(f.read().strip())
        except ValueError:
            total_visites = 0
    if "visite_comptabilisee" not in st.session_state:
        total_visites += 1
        st.session_state.visite_comptabilisee = True
        with open(fichier_compteur, "w", encoding="utf-8") as f:
            f.write(str(total_visites))
    return total_visites

nb_visites = incrementer_et_recuperer_compteur()

# ======================================================================
# 2. CONFIGURATION DE LA PAGE ET DES FEUILLES DE STYLE (CSS)
# ======================================================================
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

img_gauche = "image_7.png"  
img_droite = "image_5.png"  
img_fond = "image_8.png"    

github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ 
        background-image: url('{github_url}{img_fond}') !important;
        background-size: cover !important; background-position: center center !important; background-repeat: no-repeat !repeat; background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    .hub-header {{
        background-color: #1E293B; display: flex; justify-content: space-between; align-items: center;
        padding: 12px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
    
    .visitor-badge {{
        background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 14px; border-radius: 20px; font-size: 11px; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block;
    }}
    
    .column-title {{
        color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center;
        margin-bottom: 10px; height: 30px; background-color: #1E293B; border-radius: 6px; padding: 6px 0;
    }}
    .stButton>button {{
        background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important;
        border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 11px !important;
    }}
    
    .video-card {{ background-color: rgba(255, 255, 255, 0.9) !important; border-left: 6px solid #4F46E5 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; }}
    .santorin-card {{ background-color: rgba(255, 255, 255, 0.9) !important; border-left: 6px solid #DC2626 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; }}
    .general-card {{ background-color: rgba(255, 255, 255, 0.95) !important; border-left: 6px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; }}
    
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 15% !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: rgba(243, 244, 246, 0.95) !important; color: #1F2937 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 15% !important; }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 3. CONFIGURATION DES MODÈLES D'IA
# ======================================================================
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# Rendu du bandeau d'en-tête centré
st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title" style="text-align: center; flex-grow: 1;">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

# Moteur interne RAG (Colonne de gauche uniquement)
@st.cache_resource
def get_ipack_engine():
    docs = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(docs)
    prompt = (
        "Tu es l'IA experte du module 'iPackEPS, Santorin & Examens'. Tu t'adresses exclusivement à des professeurs d'EPS. "
        "Adopte un ton confraternel, technique et direct. Utilise leur jargon réglementaire."
    )
    return index.as_chat_engine(chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=3500), system_prompt=prompt)

if openai_api_key:
    engine_ipack = get_ipack_engine()

# ----------------------------------------------------------------------
# 🌐 FONCTION INTERNET DE RECHERCHE CIBLÉE (COLONNE DROITE)
# ----------------------------------------------------------------------
def executer_recherche_web_eps(query):
    # On restreint intelligemment la recherche aux portails EPS clés
    requete_ciblee = f"{query} EPS (Aix-Marseille OR Lyon OR Creteil OR Grenoble)"
    liens_trouves = []
    try:
        # Scan des 4 meilleurs résultats sur la toile
        for url in search(requete_ciblee, num_results=4, lang="fr"):
            liens_trouves.append(url)
    except Exception:
        pass
    return liens_trouves


# ======================================================================
# 4. EXÉCUTION DU SPLIT ÉCRAN (DEUX COLONNES DISTINCTES)
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# ----------------------------------------------------------------------
# 🗂️ COLONNE GAUCHE : MODULE MÉTIER & CONFIGURATION (ACCÈS INTERNE LOCAL)
# ----------------------------------------------------------------------
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (iPack/Exam)", key="clear_ipack"):
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
        
        text_low = prompt_ipack.lower()
        # Sécurité sur les notes réglementaires d'examens bloquées en dur
        if "examens" in context_choice.lower() and any(w in text_low for w in ["inapte", "dispens", "absent"]):
            if "inapte" in text_low:
                answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Inapte :</strong><br><strong>On ne met pas 0.</strong> L'inaptitude médicale ouvre obligatoirement le droit à une épreuve de substitution organisée par l'établissement.</div>"""
            elif "dispens" in text_low:
                answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Dispensé :</strong><br><strong>On ne met pas 0.</strong> La dispense médicale valide entraîne la neutralisation de l'APSA sur le serveur d'examen.</div>"""
            else:
                answer = """<div class="santorin-card"><strong>📊 EXAMENS – Élève Absent :</strong><br>L'absence injustifiée à un CCF certificatif génère la note de <strong>0</strong> pour l'activité concernée.</div>"""
        else:
            response = engine_ipack.chat(f"MODULE SÉLECTIONNÉ : {context_choice}. QUESTION : {prompt_ipack}")
            answer = response.response
            
        st.session_state.messages_ipack.append({"role": "assistant", "content": f"**Assistant** : {answer}"})
        st.rerun()

# ----------------------------------------------------------------------
# 🌐 COLONNE DROITE : LE VÉRITABLE MOTEUR DE RECHERCHE WEB LIVE (4 ACADÉMIES)
# ----------------------------------------------------------------------
with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS (Moteur Web Live)</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche sur la toile (Ex: TASA, Circulaire Escalade...)", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Scan en temps réel des serveurs académiques..."):
            # 1. Le bot interroge directement Internet
            liens_moteur = executer_recherche_web_eps(prompt_aix)
            
            if liens_moteur:
                # 2. L'IA structure sa réponse autour des vrais liens extraits
                prompt_ia_web = (
                    f"Tu es l'assistant de recherche EPS. Un professeur d'EPS a tapé la requête suivante : '{prompt_aix}'. "
                    f"Voici les liens exacts trouvés en direct sur la toile : {liens_moteur}. "
                    "Rédige une réponse confraternelle, synthétique et directe. Donne-lui les pistes et affiche les liens trouvés "
                    "sous la forme de puces claires au format markdown standard : [Texte du lien explicite](url)."
                )
                response_web = Settings.llm.complete(prompt_ia_web)
                answer_aix = f"""<div class="general-card"><strong>🌐 RÉSULTATS DÉCOUVERTS EN DIRECT :</strong><br><br>{response_web.text}</div>"""
            else:
                answer_aix = "Aucun document n'a pu être extrait en direct. Veuillez vérifier vos mots-clés ou rafraîchir la page."
                
        st.session_state.messages_aix.append({"role": "assistant", "content": f"**Assistant** : {answer_aix}"})
        st.rerun()
