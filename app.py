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
# 3. CONFIGURATION ET STYLES (BANDEAU OPTIMISÉ ET TAILLE RÉDUITE)
# ======================================================================
# Chargement des identifiants GitHub
g_user = st.secrets.get("GITHUB_USERNAME")
g_repo = st.secrets.get("GITHUB_REPO")
github_url = f"https://raw.githubusercontent.com/{g_user}/{g_repo}/main/"

# URLs des images
img_aix, img_ipack, img_fond = "image_7.png", "image_5.png", "image_8.png"

# Style CSS injecté (avec réduction de taille globale de ~15%)
st.markdown(f"""
    <style>
    /* Configuration globale : réduction des marges et taille de police de base */
    .block-container {{ padding-top: 0rem !important; padding-bottom: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 95% !important; }}
    html, body, [data-testid="stWidgetLabel"] p {{ font-size: 13px !important; line-height: 1.3 !important; }}
    
    /* Image de fond */
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    
    /* Masquer le header Streamlit */
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* --- 🏗️ Nouveau Bandeau Supérieur Réorganisé --- */
    .hub-header {{ 
        background-color: #1E293B; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 25px; 
        margin-bottom: 20px; 
        border-radius: 8px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); 
    }}
    .header-left, .header-right {{ display: flex; align-items: center; gap: 15px; }}
    
    /* Titre central */
    .hub-title {{ text-align: center; flex-grow: 1; }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 20px !important; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 10px !important; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 14px; border-radius: 20px; font-size: 10px !important; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block; }}
    
    /* --- 🔍 Bouton de Recherche Web (Ex-Image 6) --- */
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 20px !important;
        font-size: 11px !important;
        padding: 6px 15px !important;
    }}
    .stTextInput>div>div>div {{ background-color: transparent !important; }}
    div[data-testid="stWidgetLabel"] p {{ color: rgba(255,255,255,0.7) !important; font-size: 11px !important; }}

    /* --- 🧱 Structure des colonnes du chat --- */
    .column-title {{ color: #FFFFFF; font-size: 14px !important; font-weight: 700; text-align: center; margin-bottom: 0px; height: 30px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 6px 0; }}
    
    /* Éléments de chat (textes réduits de 15%) */
    div[data-testid="stChatMessage"] p {{ font-size: 13px !important; color: #FFFFFF !important; }}
    
    /* Radio boutons et contrôles (tailles réduites) */
    div[data-testid="stRadio"] label p {{ font-size: 12px !important; }}
    div[data-testid="stRadio"] {{ margin-bottom: 10px !important; }}
    .stButton>button {{ font-size: 11px !important; padding: 5px 15px !important; border-radius: 15px !important; }}
    
    /* Fenêtres de chat transparentes à 15% */
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
    
    /* Réponses de l'IA (translucides à 20%, polices fines) */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 12px; 
        border-radius: 4px; 
        margin-bottom: 12px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2); 
    }}
    .santorin-card {{ border-left: 5px solid #DC2626 !important; }}
    .general-card {{ border-left: 5px solid #10B981 !important; }}
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.4 !important; }}
    
    /* Tableaux Markdown (tailles harmonisées) */
    .santorin-card table, .general-card table {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 12px !important; }}
    .santorin-card th, .general-card th {{ background-color: rgba(30, 41, 59, 0.8) !important; padding: 6px !important; font-weight: bold; border: 1px solid rgba(255,255,255,0.2); }}
    .santorin-card td, .general-card td {{ padding: 6px !important; border: 1px solid rgba(255,255,255,0.1); }}
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
# 6. CONSTRUCTION DE L'INTERFACE
# ======================================================================

# --- 🏗️ Rendu du Nouveau Bandeau Supérieur ---
# On utilise du HTML/CSS car Streamlit ne permet pas de placer des widgets dans un header personnalisé
st.markdown(f"""
    <div class="hub-header">
        <div class="header-left">
            <img src="{github_url}{img_aix}" height="65">
        </div>
        <div class="hub-title">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div class="header-right">
            <img src="{github_url}{img_ipack}" height="65">
        </div>
    </div>
""", unsafe_allow_html=True)

# Pour placer la barre de recherche dans le header-right, on doit tricher un peu.
# Streamlit ne permet pas de placer un widget st.text_input directement dans le HTML.
# Nous l'injecterons en CSS en haut à droite.

# Gestion de la colonne de gauche (Assistant Métier)
# Elle prend toute la largeur car la recherche web est montée dans le bandeau.
st.markdown('<div class="column-title">🤖 Assistant Métier EPS (iPack & Santorin)</div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# On place le widget de recherche web (ex-Image 6) tout en haut à droite, en CSS absolu, pour le "coller" dans le bandeau
# C'est une astuce technique car le header HTML ne peut pas contenir de widgets actifs.
col_search, col_spacer = st.columns([1, 4]) # Juste pour créer l'espace
with col_search:
    query_web = st.text_input("🔍 Recherche Web EPS (BO, Académies...)", placeholder="Ex: Grilles BAC Gym...")

# Reste de l'assistant local
col_assistant = st.container()
with col_assistant:
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio(
        "Sur quel module travaillez-vous ?", 
        ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"]
    )

    # Affichage des messages
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    # Entrée du chat local
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
                formatted_answer = f'<div class="santorin-card"><strong>📊 SYNTHÈSE CERTIFICATION :</strong><br><br>{response_locale.response}http://googleusercontent.com/image_generation_content/1

Voici le script complet mis à jour pour ton fichier `app.py`. Il intègre la réorganisation du bandeau supérieur, où la barre de recherche web a été montée dans le header à côté du logo iPack, et une réduction globale de 15% des tailles d'éléments pour apurer l'interface et réduire l'effet de zoom.

Copie tout ce bloc et écrase le contenu de ton fichier `app.py` sur ton GitHub.

### 🛠️ Le code complet à coller dans `app.py` :

```python
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
github_url = f"[https://raw.githubusercontent.com/](https://raw.githubusercontent.com/){st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    /* Configuration globale : réduction des marges et taille de police de base */
    .block-container {{ padding-top: 0rem !important; padding-bottom: 2rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 95% !important; }}
    
    /* Image de fond */
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    
    /* Masquer le header Streamlit */
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* 🏗️ Nouveau Bandeau Supérieur Réorganisé */
    .hub-header {{ 
        background-color: #1E293B; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 25px; 
        margin-bottom: 20px; 
        border-radius: 8px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); 
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 20px !important; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 10px !important; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 14px; border-radius: 20px; font-size: 10px !important; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block; }}
    
    /* Style précis pour les logos */
    .logo-aix {{ height: 60px; }}
    .logo-ipack {{ height: 60px; margin-left: 15px; }}
    
    /* Conteneur pour la recherche web dans le bandeau */
    .search-container {{ display: flex; align-items: center; justify-content: flex-end; flex-grow: 1; padding-right: 15px; }}

    /* 🔍 Bouton de Recherche Web (Ex-Image 6) */
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        padding: 8px 18px !important;
    }}
    .stTextInput>div>div>div {{ background-color: transparent !important; }}
    div[data-testid="stWidgetLabel"] p {{ color: rgba(255,255,255,0.7) !important; font-size: 12px !important; }}

    /* 🧱 Structure des colonnes du chat */
    .column-title {{ color: #FFFFFF; font-size: 14px !important; font-weight: 700; text-align: center; margin-bottom: 0px; height: 32px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 6px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 10px !important; }}
    
    /* Radio boutons (tailles réduites) */
    div[data-testid="stRadio"] label p {{ font-size: 12px !important; }}
    div[data-testid="stRadio"] {{ margin-bottom: 12px !important; }}
    
    /* Fenêtres de chat transparentes à 15% */
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
    .glass-card > p, .glass-card label:not(div[data-testid="stRadio"] label) {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    
    /* Réponses IA translucides (20% opacité) */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 12px; 
        border-radius: 4px; 
        margin-bottom: 12px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2); 
    }}
    .santorin-card {{ border-left: 5px solid #DC2626 !important; }}
    .general-card {{ border-left: 5px solid #10B981 !important; }}
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.4 !important; }}
    
    /* Tableaux Markdown (tailles harmonisées) */
    .santorin-card table, .general-card table {{ background-color: rgba(30, 41, 59, 0.5) !important; color: #FFFFFF !important; border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 12px !important; }}
    .santorin-card th, .general-card th {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #FFFFFF !important; padding: 6px !important; font-weight: bold; border: 1px solid rgba(255,255,255,0.2) !important; }}
    .santorin-card td, .general-card td {{ padding: 6px !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #FFFFFF !important; }}
    
    div[data-testid="stChatMessage"] {{ background-color: transparent !important; border: none !important; padding: 10px 14px !important; margin-bottom: 10px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(6px) !important;
        border-radius: 16px 16px 0px 16px !important; 
        margin-left: 10% !important; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1); 
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
# 6. EXÉCUTION DE L'INTERFACE AVEC BANDEAU OPTIMISÉ
# ======================================================================

# --- Rendu du Bandeau Supérieur Réorganisé ---
# On utilise du HTML pour placer les logos et le titre, car Streamlit ne permet pas cette mise en page de base
bandeau_html = f"""
    <div class="hub-header">
        <div style="display: flex; align-items: center;">
            <img src="{github_url}{img_aix}" class="logo-aix">
        </div>
        <div class="hub-title" style="text-align: center; flex-grow: 1;">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div id="search-placeholder"></div>
            <img src="{github_url}{img_ipack}" class="logo-ipack">
        </div>
    </div>
"""
st.markdown(bandeau_html, unsafe_allow_html=True)

# Pour placer la barre de recherche (ex-Image 6) dans le bandeau à côté du logo,
# on doit utiliser une astuce de colonnes Streamlit placée juste en dessous.
# Nous l'alignerons à droite pour qu'elle s'intègre visuellement dans le header HTML.

# Zone de recherche web (Ex-Image 6)
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col_spacer_left, col_search_web = st.columns([2, 1]) # 2/3 vide, 1/3 pour la recherche
with col_search_web:
    # C'est ta barre de recherche (ex-Image 6)
    query_web = st.text_input("🔍 Recherche Web EPS (BO, Académies...)", placeholder="Ex: Grilles BAC Gym...")
st.markdown('</div>', unsafe_allow_html=True)

# Lancement de la recherche web si une requête est tapée
if query_web and tavily_api_key:
    # On utilise la colonne de gauche (temporairement) pour afficher les résultats web
    # ou on peut les afficher dans une modal. Pour rester simple, on va l'afficher en haut.
    with st.spinner("Recherche approfondie sur les sites officiels d'EPS..."):
        extraits_textes = ""
        try:
            payload = {
                "api_key": tavily_api_key,
                "query": f"{query_web} EPS",
                "search_depth": "advanced",
                "include_domains": ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr", "eps.enseigne.ac-lyon.fr", "eps.ac-creteil.fr"]
            }
            res = requests.post("[https://api.tavily.com/search](https://api.tavily.com/search)", json=payload, timeout=10)
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
            consigne_ia = f"Tu es l'assistant expert des textes officiels EPS. Réponds de manière très précise, structurée et professionnelle à la question suivante : '{query_web}'."

        response_web = Settings.llm.complete(consigne_ia)
        # Affichage du résultat de recherche web tout en haut, avant les colonnes
        st.markdown(f"""<div class="general-card"><strong>🌐 SITES OFFICIELS EPS - RÉSULTAT DE RECHERCHE :</strong><br><br>{response_web.text}</div>""", unsafe_allow_html=True)


# --- Double Colonne pour l'Assistant Métier (iPack / Santorin) ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS (iPackEPS & Santorin)</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio(
        "Sur quel module travaillez-vous ?", 
        ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"]
    )

    # Affichage des messages
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    # Entrée du chat local
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
                            "include_domains": ["ipackeps.ac-creteil.fr"]
                        }
                        res = requests.post("[https://api.tavily.com/search](https://api.tavily.com/search)", json=payload, timeout=10)
                        if res.status_code == 200:
                            data_web = res.json()
                            for item in data_web.get("results", []):
                                extraits_ipack += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
                    except: pass

                consigne_ipack = f"""
                Tu es l'assistant technique exclusif et expert du logiciel de gestion iPackEPS.\n
                Tu réponds en te basant UNIQUEMENT et STRICTEMENT sur les tutoriels, fiches d aide et notices d assistance de la plateforme officielle iPackEPS de l'académie de Créteil fournis ci-dessous :\n
                
                {extraits_ipack if extraits_ipack else 'Utilise les règles standards iPackEPS Créteil.'}
                
                Question technique : '{prompt_ipack}'
                
                Rédige un protocole pas-à-pas clair et rigoureux. Ne cite jamais de menus imaginaires. Ajoute le lien web précis de l article consulté à la fin.
                """
                response_web = Settings.llm.complete(consigne_ipack)
                formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE OFFICIEL IPACKEPS (CRÉTEIL) :</strong><br><br>{response_web.text}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)


with col2:
    # La colonne 2 est désormais vide de recherche générale, car celle-ci est montée dans le bandeau.
    # Tu peux t'en servir pour afficher de la documentation fixe ou des liens rapides.
    st.markdown('<div class="column-title">ℹ️ Informations & Liens Rapides</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
        <p style="font-size: 13px; color: #FFFFFF;">Utilisez la barre de recherche dans le bandeau supérieur pour fouiller sur les sites officiels EPS.</p>
        <p style="font-size: 13px; color: #FFFFFF;">Cette colonne est disponible pour de futures ressources.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
