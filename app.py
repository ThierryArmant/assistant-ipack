import streamlit as st
import os
import requests
import pandas as pd
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import Document

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
    .column-title {{ color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center; margin-bottom: 0px; height: 35px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 6px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 11px !important; }}
    .glass-card {{ background-color: rgba(255, 255, 255, 0.65) !important; backdrop-filter: blur(12px) !important; border-radius: 0px 0px 8px 8px; padding: 18px; box-shadow: 0px 8px 25px rgba(0,0,0,0.2); border: 1px solid rgba(255, 255, 255, 0.3); margin-bottom: 20px; }}
    .glass-card p, .glass-card label, .glass-card span, .glass-card div[data-baseweb="select"] {{ color: #0F172A !important; font-weight: 600 !important; }}
    .santorin-card {{ background-color: #FFFFFF !important; border-left: 6px solid #DC2626 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    .general-card {{ background-color: #FFFFFF !important; border-left: 6px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 18px; color: #1E293B !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: #FFFFFF !important; border-radius: 16px 16px 0px 16px !important; margin-left: 10% !important; box-shadow: 0px 2px 6px rgba(0,0,0,0.08); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: #F8FAFC !important; color: #1F2937 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 10% !important; box-shadow: 0px 2px 6px rgba(0,0,0,0.05); }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 3. VERROUILLAGE CONFIGURATION SÉCURITÉ IA
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

# --- CHARGEMENT DES DEUX MOTEURS REVISITÉ ET SÉCURISÉ ---
@st.cache_resource
def get_separated_engines_v4():
    index_santorin = VectorStoreIndex.from_documents([])
    chemin_csv = "./data/faq_evaluation_santorin.csv"
    
    # 📊 LECTURE SÉCURISÉE DU CSV (Gestion explicite du séparateur point-virgule)
    if os.path.exists(chemin_csv):
        try:
            df = pd.read_csv(chemin_csv, sep=";", encoding="utf-8", on_bad_lines='skip')
            documents_list = []
            for idx, row in df.iterrows():
                # On fabrique un bloc textuel hyper propre pour chaque ligne du tableau
                texte_ligne = "\n".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                documents_list.append(Document(text=texte_ligne))
            if documents_list:
                index_santorin = VectorStoreIndex.from_documents(documents_list)
        except Exception as e:
            st.error(f"Erreur d'analyse du tableau CSV : {str(e)}")
        
    # 🛠️ MOTEUR IPACKEPS : Chargement des PDF de cartes mentales
    index_ipack = VectorStoreIndex.from_documents([])
    if os.path.exists("./data"):
        ipack_files = [os.path.join("./data", f) for f in os.listdir("./data") if "ipack" in f.lower() and f.endswith(".pdf")]
        if ipack_files:
            try:
                docs_i = SimpleDirectoryReader(input_files=ipack_files).load_data()
                index_ipack = VectorStoreIndex.from_documents(docs_i)
            except Exception as e:
                st.error(f"Erreur iPack PDF : {str(e)}")
    
    return index_ipack, index_santorin

if openai_api_key:
    index_ipack, index_santorin = get_separated_engines_v4()

# ======================================================================
# 4. DOUBLE COLONNE INDÉPENDANTE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

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
            if "examens" in context_choice.lower():
                system_prompt = (
                    "Tu es l'assistant spécialisé EXAMENS & SANTORIN pour les professeurs d'EPS.\n"
                    "Tu réponds en te basant STRICTEMENT sur le tableau de FAQ fourni.\n"
                    "Regarde la ligne correspondant au problème (ex: Absence, Dispense, Inaptitude) "
                    "et lis spécifiquement la colonne demandée (Lycée GT Bac, Lycée Pro Bac, ou Reponse Collège DNB).\n"
                    "Ne mélange jamais les règles du Collège/DNB et du Lycée/CCF."
                )
                chosen_index = index_santorin
            else:
                system_prompt = (
                    "Tu es l'assistant spécialisé IPACKEPS. Tu parles exclusivement à des professeurs d'EPS.\n"
                    "Tu réponds pas-à-pas en te basant sur les guides PDF iPack fournis."
                )
                chosen_index = index_ipack
            
            chat_engine = chosen_index.as_chat_engine(
                chat_mode="condense_plus_context", 
                memory=ChatMemoryBuffer.from_defaults(token_limit=3500), 
                system_prompt=system_prompt
            )
            response_locale = chat_engine.chat(prompt_ipack)
            answer = response_locale.response

        if "examens" in context_choice.lower():
            formatted_answer = f'<div class="santorin-card"><strong>📊 RÉPONSE CERTIFICATION :</strong><br><br>{answer}</div>'
        else:
            formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE IPACKEPS :</strong><br><br>{answer}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche officielle...", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Analyse..."):
            prompt_ia_web = f"Tu es l'assistant expert des textes officiels EPS. Réponds précisément à : '{prompt_aix}'."
            response_web = Settings.llm.complete(prompt_ia_web)
            answer_aix = f"""<div class="general-card"><strong>🌐 DOSSIER RÉGLEMENTAIRE :</strong><br><br>{response_web.text}</div>"""
                
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
