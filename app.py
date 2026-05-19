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
# 3. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (15% TRANSPARENCE & CLEAN SIZE)
# ======================================================================
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    /* Réduction globale des marges de l'application pour réduire l'effet zoomé */
    .block-container {{ 
        padding-top: 0.5rem !important; 
        padding-bottom: 2rem !important; 
        padding-left: 1.5rem !important; 
        padding-right: 1.5rem !important; 
        max-width: 96% !important; 
    }}
    
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* Structure du Bandeau Supérieur */
    .hub-header {{ 
        background-color: #1E293B; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 20px; 
        margin-bottom: 15px; 
        border-radius: 8px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); 
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 20px !important; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 10px !important; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 12px; border-radius: 20px; font-size: 10px !important; font-weight: bold; font-family: monospace; margin-top: 5px; display: inline-block; }}
    
    .column-title {{ color: #FFFFFF; font-size: 13px !important; font-weight: 700; text-align: center; margin-bottom: 0px; height: 30px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 5px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 10px !important; padding: 3px 12px !important; }}
    
    div[data-testid="stRadio"] {{
        background-color: #1E293B !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: inset 0px 2px 4px rgba(0,0,0,0.3) !important;
        margin-bottom: 10px !important;
    }}
    div[data-testid="stRadio"] label p {{ color: #FFFFFF !important; font-weight: 600 !important; font-size: 12px !important; }}
    
    /* Fenêtres principales transparentes à 15% */
    .glass-card {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 0px 0px 8px 8px;
        padding: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
        border-left: 1px solid rgba(255, 255, 255, 0.15);
        border-right: 1px solid rgba(255, 255, 255, 0.15);
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 15px;
    }}
    
    /* Réponses de l'IA (Correction tailles fines à 13px) */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 14px; 
        border-radius: 4px; 
        margin-bottom: 14px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }}
    .santorin-card {{ border-left: 5px solid #DC2626 !important; }}
    .general-card {{ border-left: 5px solid #10B981 !important; }}
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.4 !important; }}
    .santorin-card strong, .general-card strong {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    .santorin-card a, .general-card a {{ color: #38BDF8 !important; font-weight: bold !important; text-decoration: underline !important; }}
    
    /* Tableaux Markdown harmonisés */
    .santorin-card table, .general-card table {{ background-color: rgba(30, 41, 59, 0.6) !important; color: #FFFFFF !important; border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 12px !important; }}
    .santorin-card th, .general-card th {{ background-color: rgba(15, 23, 42, 0.85) !important; color: #FFFFFF !important; padding: 8px !important; font-weight: bold !important; font-size: 12px !important; border: 1px solid rgba(255,255,255,0.2) !important; text-align: left; }}
    .santorin-card td, .general-card td {{ padding: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; vertical-align: top !important; }}
    
    /* Input des zones de tchat */
    div[data-testid="stChatMessage"] {{ background-color: transparent !important; border: none !important; padding: 8px 12px !important; margin-bottom: 8px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(6px) !important;
        border-radius: 14px 14px 0px 14px !important; 
        margin-left: 15% !important; 
        box-shadow: 0px 3px 8px rgba(0,0,0,0.1); 
    }}
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
                    except: pass
                else:
                    try:
                        xl = pd.ExcelFile(chemin)
                        for sheet_name in xl.sheet_names:
                            df = xl.parse(sheet_name)
                            for idx, row in df.iterrows():
                                texte_ligne = f"[Onglet: {sheet_name}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                                documents_list.append(Document(text=texte_ligne))
                    except: pass
        if documents_list:
            index_santorin = VectorStoreIndex.from_documents(documents_list)
    return index_santorin

if openai_api_key:
    index_santorin = get_santorin_engine()

# ======================================================================
# 6. EXÉCUTION DE L'INTERFACE GRAPHIQUE COMPLÈTE
# ======================================================================

# --- Rendu du Bandeau Supérieur Épuré ---
st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="100"></div>
        <div class="hub-title">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="65"></div>
    </div>
""", unsafe_allow_html=True)

# --- Double Colonne pour l'alignement de la Recherche Web ---
# On utilise ce système de grille pour glisser discrètement la zone de recherche à droite sous le bandeau
col_void, col_search_box = st.columns([1.6, 1])
with col_search_box:
    query_web = st.text_input("🔍 Recherche Web EPS (BO, Académies...)", placeholder="Ex: Grilles BAC Gym, protocole TASA...", key="web_search_input")

# Si une recherche web est lancée, on affiche le résultat dans un pavé vert translucide au-dessus des modules
if query_web and tavily_api_key:
    with st.spinner("Recherche sur les portails académiques..."):
        extraits_textes = ""
        try:
            payload = {
                "api_key": tavily_api_key,
                "query": f"{query_web} EPS",
                "search_depth": "advanced",
                "include_domains": ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr", "eps.enseigne.ac-lyon.fr", "eps.ac-creteil.fr"]
            }
            res = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
            if res.status_code == 200:
                data_web = res.json()
                for item in data_web.get("results", []):
                    extraits_textes += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
        except: pass

        if extraits_textes:
            consigne_ia = f"""
            Tu es l'assistant expert des textes officiels et protocoles EPS pour l'Éducation Nationale.
            En te basant STRICTEMENT sur ces données de recherche extraites des sites académiques officiels :
            
            {extraits_textes}
            
            Réponds de manière claire, rigoureuse et exhaustive à la question suivante : '{query_web}'.
            Ajoute obligatoirement à la fin de ta réponse la liste des liens URL sources trouvés.
            """
        else:
            consigne_ia = f"Tu es l'assistant expert des textes officiels EPS. Réponds précisément à la question suivante : '{query_web}'."

        response_web = Settings.llm.complete(consigne_ia)
        st.markdown(f"""<div class="general-card"><strong>🌐 MOTEUR DE RECHERCHE EPS - RÉSULTAT :</strong><br><br>{response_web.text}</div>""", unsafe_allow_html=True)


# --- Double Colonne pour l'Espace de Discussion Central ---
col1, col2 = st.columns(2, gap="medium")

# COLONNE 1 : ASSISTANT MÉTIER (iPack / Santorin)
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
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
        
        # MODULE A : EXAMENS & SANTORIN (FICHIERS INTERNES LOCAL)
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

        # MODULE B : IPACKEPS (FOUILLE EXCLUSIVE SUR LA DOCUMENTATION OUVERTE DE CRÉTEIL)
        else:
            with st.spinner("Fouille des manuels d'assistance iPackEPS..."):
                extraits_ipack = ""
                if tavily_api_key:
                    try:
                        payload = {
                            "api_key": tavily_api_key,
                            "query": f"{prompt_ipack}",
                            "search_depth": "advanced",
                            "include_domains": ["ipackeps.ac-creteil.fr"]
                        }
                        res = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
                        if res.status_code == 200:
                            data_web = res.json()
                            for item in data_web.get("results", []):
                                extraits_ipack += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
                    except: pass

                consigne_ipack = f"""
                Tu es l'assistant technique expert de l'application iPackEPS.
                Tu réponds en te basant STRICTEMENT sur les guides d'aide officiels de l'académie de Créteil fournis ci-après :
                
                {extraits_ipack if extraits_ipack else 'Se référer aux procédures standards de configuration iPack.'}
                
                Question technique : '{prompt_ipack}'
                
                Rédige un protocole pas-à-pas précis (menus, boutons, onglets). Ne propose jamais d'options fictives. Ajoute le lien de la documentation consultée tout à la fin.
                """
                response_web = Settings.llm.complete(consigne_ipack)
                formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE OFFICIEL IPACKEPS (CRÉTEIL) :</strong><br><br>{response_web.text}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# COLONNE 2 : ESPACE D'AFFICHAGE COMPLÉMENTAIRE OU INFORMATIONS FIXES
with col2:
    st.markdown('<div class="column-title">ℹ️ Notice &amp; Ressources Globales</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <p style="font-size: 13px; color: #FFFFFF; font-weight: bold; margin-bottom: 8px;">🌐 Mode d'emploi de la recherche :</p>
        <p style="font-size: 12px; color: #E2E8F0; line-height: 1.4;">
        Pour toute recherche de textes réglementaires transversaux (DNB, grilles d'évaluation, circulaires), utilisez la barre de recherche <strong>"🔍 Recherche Web EPS"</strong> située juste au-dessus en haut à droite.<br><br>
        Le résultat se déploiera automatiquement sous forme de carte dynamique avec les liens officiels d'Aix-Marseille, Lyon, Créteil et Éduscol.
        </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
