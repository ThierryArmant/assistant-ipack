import streamlit as st
import os
import pandas as pd
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import Document

# ======================================================================
# 1. CONFIGURATION DE L'APPLICATION (IMPÉRATIVEMENT EN PREMIER)
# ======================================================================
st.set_page_config(
    page_title="Hub IA - EPS", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ======================================================================
# 2. GESTION DE LA MÉMOIRE ET DU COMPTEUR DE VISITES
# ======================================================================
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

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
# 3. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (15% TRANSPARENCE APURÉE)
# ======================================================================
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
    
    div[data-testid="stRadio"] {{
        background-color: #1E293B !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: inset 0px 2px 4px rgba(0,0,0,0.3) !important;
        margin-bottom: 15px !important;
    }}
    div[data-testid="stRadio"] label p {{ color: #FFFFFF !important; font-weight: 600 !important; font-size: 13px !important; }}
    
    .glass-card {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 0px 0px 8px 8px;
        padding: 18px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
        border-left: 1px solid rgba(255, 255, 255, 0.15);
        border-right: 1px solid rgba(255, 255, 255, 0.15);
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 20px;
    }}
    .glass-card > p, .glass-card label:not(div[data-testid="stRadio"] label) {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 16px; 
        border-radius: 4px; 
        margin-bottom: 18px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }}
    .santorin-card {{ border-left: 6px solid #DC2626 !important; }}
    .general-card {{ border-left: 6px solid #10B981 !important; }}
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.5 !important; }}
    .santorin-card strong, .general-card strong {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    .santorin-card a, .general-card a {{ color: #38BDF8 !important; font-weight: bold !important; text-decoration: underline !important; }}
    
    .santorin-card table, .general-card table {{ background-color: rgba(30, 41, 59, 0.6) !important; color: #FFFFFF !important; border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 12px !important; }}
    .santorin-card th, .general-card th {{ background-color: rgba(15, 23, 42, 0.85) !important; color: #FFFFFF !important; padding: 10px !important; font-weight: bold !important; font-size: 13px !important; border: 1px solid rgba(255,255,255,0.2) !important; text-align: left; }}
    .santorin-card td, .general-card td {{ padding: 10px !important; border: 1px solid rgba(255,255,255,0.1) !important; vertical-align: top !important; }}
    
    div[data-testid="stChatMessage"] {{ background-color: transparent !important; border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: rgba(255, 255, 255, 0.15) !important; backdrop-filter: blur(6px) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 10% !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p {{ color: #FFFFFF !important; font-size: 13px !important; }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 4. CONFIGURATION DE L'INTELLIGENCE ARTIFICIELLE
# ======================================================================
openai_api_key = st.secrets.get("OPENAI_API_KEY")
tavily_api_key = st.secrets.get("TAVILY_API_KEY")

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

# ======================================================================
# 5. MOTEUR D'INDEXATION UNIQUE POUR SANTORIN (FICHIERS INTERNES)
# ======================================================================
@st.cache_resource
def get_santorin_engine():
    index_santorin = VectorStoreIndex.from_documents([])
    documents_list = []
    base_dir = "./data"
    
    if os.path.exists(base_dir):
        for fichier in os.listdir(base_dir):
            nom_f = fichier.lower()
            chemin = os.path.join(base_dir, fichier)
            if "santorin" in nom_f or "notation" in nom_f:
                if nom_f.endswith('.csv'):
                    try:
                        df = pd.read_csv(chemin, sep=";", encoding="utf-8", on_bad_lines='skip')
                        for idx, row in df.iterrows():
                            texte_ligne = f"[Source: {fichier}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                            documents_list.append(Document(text=texte_ligne))
                    except:
                        pass
                else:
                    try:
                        xl = pd.ExcelFile(chemin)
                        for sheet_name in xl.sheet_names:
                            df = xl.parse(sheet_name)
                            for idx, row in df.iterrows():
                                texte_ligne = f"[Onglet: {sheet_name}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                                documents_list.append(Document(text=texte_ligne))
                    except:
                        pass
        if documents_list:
            index_santorin = VectorStoreIndex.from_documents(documents_list)
    return index_santorin

if openai_api_key:
    index_santorin = get_santorin_engine()

# ======================================================================
# 6. EXÉCUTION DOUBLE COLONNE INDÉPENDANTE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# --- COLONNE 1 : ASSISTANT MÉTIER ---
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Ipackeps & Examens</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio(
        "Sur quel module travaillez-vous ?", 
        ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"]
    )

    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Votre question (iPack, Santorin...) ?", key="input_ipack"):
        st.session_state.messages_ipack.append({"role": "user", "content": f"**Vous** : {prompt_ipack}"})
        
        # MODULE A : EXAMENS & SANTORIN (FICHIERS INTERNES)
        if "examens" in context_choice.lower():
            with st.spinner("Analyse de vos fichiers de notation..."):
                system_prompt = (
                    "Tu es l'assistant expert EXAMENS & SANTORIN pour les professeurs d'EPS.\n"
                    "Tu traites STRICTEMENT de la réglementation des examens (DNB, BAC, CAP) et de la remontée des notes.\n\n"
                    "⚠️ CONSIGNE ABSOLUE SUR L'INTENTION DE SANTÉ :\n"
                    "Si l'utilisateur pose une question relative à un certificat médical, une dispense ou une inaptitude, "
                    "tu dois l'analyser SOUS L'ANGLE DE L'EXAMEN (Le Certificatif).\n"
                    "Format de réponse obligatoire : Présente TOUJOURS tes résultats sous la forme d'un tableau Markdown comparatif."
                )
                chat_engine = index_santorin.as_chat_engine(
                    chat_mode="context", 
                    memory=ChatMemoryBuffer.from_defaults(token_limit=4000), 
                    system_prompt=system_prompt
                )
                response_locale = chat_engine.chat(prompt_ipack)
                formatted_answer = f'<div class="santorin-card"><strong>📊 SYNTHÈSE CERTIFICATION :</strong><br><br>{response_locale.response}</div>'

        # MODULE B : IPACKEPS (RECHERCHE EXCLUSIVE SUR IPACKEPS.AC-CRETEIL.FR)
        else:
            with st.spinner("Recherche des protocoles officiels sur iPackEPS Créteil..."):
                extraits_ipack = ""
                if tavily_api_key:
                    try:
                        payload = {
                            "api_key": tavily_api_key,
                            "query": f"{prompt_ipack}",
                            "search_depth": "advanced",
                            # 🚀 FORCE LE BOT À N'ALLER QUE SUR CE DOMAINE EXCLUSIF
                            "include_domains": ["ipackeps.ac-creteil.fr"]
                        }
                        res = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
                        if res.status_code == 200:
                            data_web = res.json()
                            for item in data_web.get("results", []):
                                extraits_ipack += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
                    except:
                        pass

                consigne_ipack = f"""
                Tu es l'assistant technique exclusif et expert du logiciel de gestion iPackEPS.\n
                Tu réponds en te basant UNIQUEMENT et STRICTEMENT sur les tutoriels, fiches d aide et notices d assistance de la plateforme officielle iPackEPS de l'académie de Créteil fournis ci-dessous :\n
                
                {extraits_ipack if extraits_ipack else 'Utilise les règles standards iPackEPS Créteil.'}
                
                Question technique : '{prompt_ipack}'
                
                Rédige un protocole pas-à-pas clair et rigoureux (onglets, boutons à cocher, manipulations). Ne cite jamais de menus imaginaires. Si l information sur l action exacte n'est pas détaillée dans les extraits, explique au mieux ce qui est préconisé sur le portail d assistance de Créteil. Ajoute obligatoirement le lien web précis de l article consulté à la fin pour permettre à l'enseignant de s'y référer.
                """
                response_web = Settings.llm.complete(consigne_ipack)
                formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE OFFICIEL IPACKEPS (CRÉTEIL) :</strong><br><br>{response_web.text}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLONNE 2 : ASSISTANT RECHERCHES SITES (MOTEUR SECURE AVEC TAVILY) ---
with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Générales</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nettoyer le chat", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche officielle...", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Recherche approfondie sur les sites officiels d'EPS..."):
            extraits_textes = ""
            if tavily_api_key:
                try:
                    payload = {
                        "api_key": tavily_api_key,
                        "query": f"{prompt_aix} EPS",
                        "search_depth": "advanced",
                        "include_domains": [
                            "pedagogie.ac-aix-marseille.fr", 
                            "eduscol.education.gouv.fr", 
                            "eps.enseigne.ac-lyon.fr", 
                            "eps.ac-creteil.fr"
                        ]
                    }
                    res = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
                    if res.status_code == 200:
                        data_web = res.json()
                        for item in data_web.get("results", []):
                            extraits_textes += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
                except:
                    pass

            if extraits_textes:
                consigne_ia = f"""
                Tu es l'assistant expert des textes officiels et protocoles EPS pour l'Éducation Nationale.
                En te basant STRICTEMENT sur ces données de recherche extraites des sites académiques officiels :
                
                {extraits_textes}
                
                Réponds de manière claire, rigoureuse et exhaustive à la question suivante : '{prompt_aix}'.
                Ajoute obligatoirement à la fin de ta réponse la liste des liens URL sources trouvés pour que l'enseignant puisse s'y référer et télécharger les documents originaux si besoin.
                """
            else:
                consigne_ia = f"""
                Tu es l'assistant expert des textes officiels EPS. 
                Réponds de manière très précise, structurée et professionnelle à la question suivante : '{prompt_aix}'.
                Cible tes connaissances sur les directives d'Éduscol et des académies de Lyon, Créteil et Aix-Marseille.
                Si la question porte sur un dispositif comme le TASA (Travail d'Accompagnement et de Suivi des Apprenants), détaille précisément son fonctionnement réglementaire sans rien éluder.
                """

            response_web = Settings.llm.complete(consigne_ia)
            answer_aix = f"""<div class="general-card"><strong>🌐 SITES OFFICIELS EPS :</strong><br><br>{response_web.text}</div>"""
                
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
