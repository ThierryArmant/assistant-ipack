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
if "messages_hub" not in st.session_state:
    st.session_state.messages_hub = []
if "active_module" not in st.session_state:
    st.session_state.active_module = "ipack"  # 'ipack', 'examens', ou 'general'

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
# 3. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (Boutons Verts & Explications)
# ======================================================================
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 0.5rem !important; 
        padding-bottom: 2rem !important; 
        padding-left: 1.5rem !important; 
        padding-right: 1.5rem !important; 
        max-width: 900px !important; 
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
    
    /* Texte d'explication "Choix du contexte" */
    .context-label {{
        color: #94A3B8;
        font-size: 12px !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        margin-left: 2px;
    }}

    /* Grand Bandeau de Titre de la zone de tchat active */
    .column-title {{ 
        color: #FFFFFF; 
        font-size: 13px !important; 
        font-weight: 700; 
        text-align: center; 
        margin-bottom: 15px !important; 
        height: 32px; 
        background-color: #1E293B; 
        border-radius: 6px !important; 
        padding: 6px 0; 
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Boutons Neutres par défaut (Inactifs) */
    .stButton>button {{ 
        background-color: rgba(30, 41, 59, 0.75) !important; 
        color: #94A3B8 !important; 
        border: 1px solid rgba(255,255,255,0.1) !important; 
        border-radius: 8px !important; 
        font-size: 11px !important; 
        padding: 8px 10px !important; 
        line-height: 1.4 !important;
        transition: all 0.2s ease;
    }}

    /* 🟢 Passage au vert fluo/lumineux pour le bouton actif unique via détection d'index */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div:nth-of-type(1) button {{
        background-color: { 'rgba(16, 185, 129, 0.25)' if st.session_state.active_module == 'ipack' else 'rgba(30, 41, 59, 0.75)' } !important;
        color: { '#10B981' if st.session_state.active_module == 'ipack' else '#94A3B8' } !important;
        border: 1px solid { 'rgba(16, 185, 129, 0.5)' if st.session_state.active_module == 'ipack' else 'rgba(255,255,255,0.1)' } !important;
        box-shadow: { '0px 0px 10px rgba(16, 185, 129, 0.3)' if st.session_state.active_module == 'ipack' else 'none' };
        font-weight: { '700' if st.session_state.active_module == 'ipack' else 'normal' };
    }}
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div:nth-of-type(2) button {{
        background-color: { 'rgba(16, 185, 129, 0.25)' if st.session_state.active_module == 'examens' else 'rgba(30, 41, 59, 0.75)' } !important;
        color: { '#10B981' if st.session_state.active_module == 'examens' else '#94A3B8' } !important;
        border: 1px solid { 'rgba(16, 185, 129, 0.5)' if st.session_state.active_module == 'examens' else 'rgba(255,255,255,0.1)' } !important;
        box-shadow: { '0px 0px 10px rgba(16, 185, 129, 0.3)' if st.session_state.active_module == 'examens' else 'none' };
        font-weight: { '700' if st.session_state.active_module == 'examens' else 'normal' };
    }}
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div:nth-of-type(3) button {{
        background-color: { 'rgba(16, 185, 129, 0.25)' if st.session_state.active_module == 'general' else 'rgba(30, 41, 59, 0.75)' } !important;
        color: { '#10B981' if st.session_state.active_module == 'general' else '#94A3B8' } !important;
        border: 1px solid { 'rgba(16, 185, 129, 0.5)' if st.session_state.active_module == 'general' else 'rgba(255,255,255,0.1)' } !important;
        box-shadow: { '0px 0px 10px rgba(16, 185, 129, 0.3)' if st.session_state.active_module == 'general' else 'none' };
        font-weight: { '700' if st.session_state.active_module == 'general' else 'normal' };
    }}
    
    /* Bouton Nettoyer le chat */
    div.clear-btn-align {{ padding-top: 3px !important; }}
    div.clear-btn-align .stButton>button {{
        background-color: rgba(220, 38, 38, 0.15) !important;
        color: #EF4444 !important;
        border: 1px solid rgba(220, 38, 38, 0.3) !important;
        border-radius: 8px !important;
        padding: 7px 10px !important;
        font-size: 12px !important;
        width: 100% !important;
        box-shadow: none !important;
    }}
    
    /* Conteneur de tchat sans boîte opaque */
    .glass-card {{ background-color: transparent !important; border: none !important; box-shadow: none !important; padding: 0px !important; margin-top: 15px; }}
    
    /* Bulles de réponse de l'IA */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 14px; 
        border-radius: 6px; 
        margin-bottom: 14px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }}
    .santorin-card {{ border-left: 5px solid #38BDF8 !important; }} 
    .general-card {{ border-left: 5px solid #10B981 !important; }} 
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.4 !important; }}
    .santorin-card strong, .general-card strong {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    .santorin-card a, .general-card a {{ color: #38BDF8 !important; font-weight: bold !important; text-decoration: underline !important; }}
    
    /* Style de la bulle utilisateur */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(6px) !important;
        border-radius: 14px 14px 0px 14px !important; 
        margin-left: 20% !important; 
    }}
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
# 5. RENDU DU BANDEAU SUPERIEUR STANDARD
# ======================================================================
st.markdown(f"""
    <div class="hub-header">
        <div style="text-align: left;"><img src="{github_url}{img_gauche}" width="95"></div>
        <div class="hub-title" style="text-align: center;">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="text-align: right;"><img src="{github_url}{img_droite}" width="60"></div>
    </div>
""", unsafe_allow_html=True)

# ======================================================================
# 6. COMMUTATION HORIZONTALE NEUTRE ➔ VERT (AVEC EXPLICATION)
# ======================================================================
# Ajout du titre d'explication juste au-dessus des boutons
st.markdown('<div class="context-label">⚙️ Choix du contexte :</div>', unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns(3, gap="small")

with col_b1:
    btn_ipack = st.button(
        "🛠️ iPackEPS\n(Documentation Créteil)", 
        use_container_width=True, 
        key="btn_module_ipack"
    )
    if btn_ipack:
        st.session_state.active_module = "ipack"
        st.session_state.messages_hub = []
        st.rerun()

with col_b2:
    btn_exams = st.button(
        "📊 Examens & Santorin\n(Aix-Marseille & Éduscol)", 
        use_container_width=True, 
        key="btn_module_exams"
    )
    if btn_exams:
        st.session_state.active_module = "examens"
        st.session_state.messages_hub = []
        st.rerun()

with col_b3:
    btn_general = st.button(
        "🔍 Recherches Générales\n(Multi-sites EPS)", 
        use_container_width=True, 
        key="btn_module_general"
    )
    if btn_general:
        st.session_state.active_module = "general"
        st.session_state.messages_hub = []
        st.rerun()

# ======================================================================
# 7. ZONE DE DIALOGUE ACTIVE UNIQUE CONSOLIDÉE
# ======================================================================
label_titres = {
    "ipack": "🛠️ Mode : Assistance Technique iPackEPS (Serveur de Créteil)",
    "examens": "📊 Mode : Textes Officiels Examens (Aix-Marseille & Éduscol)",
    "general": "🔍 Mode : Recherche Transversale Globale (Tous serveurs EPS)"
}

st.markdown(f'<div class="column-title">{label_titres[st.session_state.active_module]}</div>', unsafe_allow_html=True)

# Couplage horizontal : Alignement du bouton Nettoyer et de la barre de saisie
col_action_clear, col_action_input = st.columns([1, 4.5], gap="small")

with col_action_clear:
    st.markdown('<div class="clear-btn-align">', unsafe_allow_html=True)
    clear_clicked = st.button("🧹 Nettoyer", key="clear_hub_unique")
    st.markdown('</div>', unsafe_allow_html=True)
    if clear_clicked:
        st.session_state.messages_hub = []
        st.rerun()

with col_action_input:
    prompt = st.chat_input("Posez votre question ici (iPack, Règlements, Grilles...)...", key="chat_input_unique")

# Conteneur d'affichage du flux de messages (Sous le bloc d'action)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# Rendu du fil de discussion
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"], unsafe_allow_html=True)

# Traitement de la requête utilisateur
if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": f"**Vous** : {prompt}"})
    
    if st.session_state.active_module == "ipack":
        domaines_recherche = ["ipackeps.ac-creteil.fr"]
        texte_spinner = "Fouille de la base d'assistance technique de Créteil..."
        color_card = "general-card"
    elif st.session_state.active_module == "examens":
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr"]
        texte_spinner = "Recherche dans les archives d'Aix-Marseille & Éduscol..."
        color_card = "santorin-card"
    else:
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr", "eps.enseigne.ac-lyon.fr", "eps.ac-creteil.fr"]
        texte_spinner = "Lancement de la recherche globale multi-académies..."
        color_card = "general-card"

    with st.spinner(texte_spinner):
        extraits_doc = ""
        if tavily_api_key:
            try:
                payload = {
                    "api_key": tavily_api_key,
                    "query": f"{prompt} EPS",
                    "search_depth": "advanced",
                    "include_domains": domaines_recherche
                }
                res = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
                if res.status_code == 200:
                    data_web = res.json()
                    for item in data_web.get("results", []):
                        extraits_doc += f"Source: {item['title']} ({item['url']})\nContenu: {item['content']}\n\n"
            except: pass

        if st.session_state.active_module == "ipack":
            consigne_ia = f"Tu es l'assistant technique expert d'iPackEPS. Génère un protocole pas-à-pas précis (onglets, clics) basé STRICTEMENT sur cette aide : {extraits_doc}. Ajoute l'URL exacte à la fin. Ne mentionne aucun menu imaginaire."
            badge_title = "🛠️ PROTOCOLE TECHNIQUE IPACKEPS"
        elif st.session_state.active_module == "examens":
            consigne_ia = f"Tu es l'assistant de terrain officiel d'Aix-Marseille et Éduscol. Réponds de façon purement administrative sur les textes, livrets ou dispenses à partir de ces documents : {extraits_doc}. ⚠️ INTERDICTION STRICTE de parler d'interface logicielle, d'onglets ou de clics (pas de mention d'iPack). Reste sur le règlement. Ajoute les liens URL exacts consultés à la fin."
            badge_title = "📊 REGLEMENTATION EXAMENS & EVALUATIONS"
        else:
            consigne_ia = f"Tu es l'assistant de recherche globale EPS. Synthétise clairement les informations institutionnelles récoltées : {extraits_doc}. Donne la liste complète des URL sources trouvées à la fin."
            badge_title = "🔍 RÉSULTATS DE RECHERCHE GLOBALE"

        response_web = Settings.llm.complete(consigne_ia)
        formatted_answer = f'<div class="{color_card}"><strong>{badge_title} :</strong><br><br>{response_web.text}</div>'

    st.session_state.messages_hub.append({"role": "assistant", "content": formatted_answer})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
