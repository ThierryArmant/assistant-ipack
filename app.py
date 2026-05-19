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
# 3. INTERFACE GRAPHIQUE ET STYLE (INTEGRATION RECHERCHE & BOUTONS HORIZONTAUX)
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
        max-width: 96% !important; 
    }}
    
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* 🏗️ BANDEAU SUPERIEUR : Intègre désormais le Titre, la Recherche (Image 6) et le Logo (Image 5) */
    .hub-header {{ 
        background-color: #1E293B; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 20px; 
        margin-bottom: 20px; 
        border-radius: 8px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); 
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 20px !important; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 10px !important; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 12px; border-radius: 20px; font-size: 10px !important; font-weight: bold; font-family: monospace; margin-top: 5px; display: inline-block; }}
    
    /* Titre de la zone active */
    .column-title {{ 
        color: #FFFFFF; 
        font-size: 13px !important; 
        font-weight: 700; 
        text-align: center; 
        margin-top: 10px;
        margin-bottom: 15px !important; 
        height: 32px; 
        background-color: #1E293B; 
        border-radius: 6px !important; 
        padding: 6px 0; 
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }}

    /* Personnalisation esthétique de l'input de recherche inséré dans le bandeau */
    div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 6px !important;
        font-size: 13px !important;
    }}

    /* Fenêtre de tchat transparente */
    .glass-card {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }}
    
    /* Réponses IA */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        padding: 14px; 
        border-radius: 4px; 
        margin-bottom: 14px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }}
    .santorin-card {{ border-left: 5px solid #38BDF8 !important; }} 
    .general-card {{ border-left: 5px solid #10B981 !important; }} 
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; }}
    
    /* Messages Utilisateur */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(6px) !important;
        border-radius: 14px 14px 0px 14px !important; 
        margin-left: 15% !important; 
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
# 5. RENDU DU BANDEAU SUPÉRIEUR ET BARRE DE RECHERCHE INTEGRÉE
# ======================================================================
# On crée une grille à 3 colonnes pour le bandeau supérieur pour y insérer l'input au millimètre
grid_head = st.container()
with grid_head:
    col_h1, col_h2, col_h3 = st.columns([1.2, 2, 1.8], gap="small")
    
    with col_h1:
        # Académie d'Aix-Marseille (Image 7)
        st.markdown(f'<div style="padding-top:10px;"><img src="{github_url}{img_gauche}" width="110"></div>', unsafe_allow_html=True)
        
    with col_h2:
        # Titre central et compteur
        st.markdown(f"""
            <div style="text-align: center; color: white; padding-top: 5px;">
                <h1 style="margin:0; font-size:22px; font-weight:bold;">Hub IA - EPS</h1>
                <p style="margin:0; color:#94A3B8; font-size:10px; text-transform:uppercase;">Espace Ressources &amp; Assistance Numérique</p>
                <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_h3:
        # Alignement horizontal de l'Input de Recherche (Image 6) + Logo iPackEPS (Image 5)
        st.markdown('<div style="display:flex; align-items:center; justify-content:flex-end; gap:10px; padding-top:12px;">', unsafe_allow_html=True)
        col_sub_search, col_sub_logo = st.columns([2.5, 1])
        with col_sub_search:
            query_web = st.text_input("", placeholder="🔍 Recherche Web EPS (BO, Académies...)", label_visibility="collapsed", key="search_bar_top")
        with col_sub_logo:
            st.markdown(f'<img src="{github_url}{img_droite}" width="60">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Barre de séparation esthétique pour fermer le bandeau
st.markdown('<div style="margin-bottom:20px;"></div>', unsafe_allow_html=True)

# Déploiement de la recherche générale si elle est activée depuis le bandeau
if query_web and tavily_api_key:
    with st.spinner("Recherche globale sur les serveurs académiques..."):
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

        consigne_ia = f"Tu es l'assistant expert des textes officiels EPS. Réponds précisément à la question suivante : '{query_web}' en utilisant ces sources : {extraits_textes}. Ajoute les liens URL complets trouvés à la fin."
        response_web = Settings.llm.complete(consigne_ia)
        st.markdown(f"""<div class="general-card"><strong>🔍 RÉSULTAT DE LA RECHERCHE SUPERIEURE :</strong><br><br>{response_web.text}</div>""", unsafe_allow_html=True)


# ======================================================================
# 6. SÉPARATEUR DE MODULES : 3 PETITES CARTES BOUTONS HORIZONTAUX CÔTE À CÔTE
# ======================================================================
col_b1, col_b2, col_b3 = st.columns(3, gap="small")

with col_b1:
    btn_ipack = st.button(
        "🛠️ iPackEPS\n(Documentation Créteil)", 
        use_container_width=True, 
        key="btn_module_ipack",
        type="primary" if st.session_state.active_module == "ipack" else "secondary"
    )
    if btn_ipack:
        st.session_state.active_module = "ipack"
        st.session_state.messages_hub = []
        st.rerun()

with col_b2:
    btn_exams = st.button(
        "📊 Examens & Santorin\n(Aix-Marseille & Éduscol)", 
        use_container_width=True, 
        key="btn_module_exams",
        type="primary" if st.session_state.active_module == "examens" else "secondary"
    )
    if btn_exams:
        st.session_state.active_module = "examens"
        st.session_state.messages_hub = []
        st.rerun()

with col_b3:
    btn_general = st.button(
        "🔍 Recherches Générales\n(Multi-sites EPS)", 
        use_container_width=True, 
        key="btn_module_general",
        type="primary" if st.session_state.active_module == "general" else "secondary"
    )
    if btn_general:
        st.session_state.active_module = "general"
        st.session_state.messages_hub = []
        st.rerun()


# ======================================================================
# 7. FENÊTRE DE DISCUSSION UNIQUE NETTOYÉE ET INTEGRÉE
# ======================================================================
label_titres = {
    "ipack": "🛠️ Assistant iPackEPS connecté sur l'Assistance de Créteil",
    "examens": "📊 Assistant Examens connecté sur Aix-Marseille & Éduscol",
    "general": "🔍 Assistant de Fouille Multitâches (Tous serveurs EPS)"
}

st.markdown(f'<div class="column-title">{label_titres[st.session_state.active_module]}</div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

if st.button("🧹 Nettoyer le chat", key="clear_hub_unique"):
    st.session_state.messages_hub = []
    st.rerun()

# Rendu du fil de discussion unique
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"], unsafe_allow_html=True)

# Zone d'écriture unique
if prompt := st.chat_input("Votre question (iPack, Règlements, Notation...) ?", key="chat_input_unique"):
    st.session_state.messages_hub.append({"role": "user", "content": f"**Vous** : {prompt}"})
    
    # Configuration des domaines selon le bouton carte sélectionné
    if st.session_state.active_module == "ipack":
        domaines_recherche = ["ipackeps.ac-creteil.fr"]
        texte_spinner = "Fouille du serveur d'assistance de Créteil..."
        color_card = "general-card"
    elif st.session_state.active_module == "examens":
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr"]
        texte_spinner = "Analyse réglementaire Aix-Marseille & Éduscol..."
        color_card = "santorin-card"
    else:
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr", "eps.enseigne.ac-lyon.fr", "eps.ac-creteil.fr"]
        texte_spinner = "Fouille de l'ensemble des serveurs EPS..."
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

        # Rédaction des consignes spécifiques à l'IA
        if st.session_state.active_module == "ipack":
            consigne_ia = f"Tu es l'assistant technique expert d'iPackEPS. Crée un tutoriel pas-à-pas basé sur ces manuels : {extraits_doc}. Ajoute l'URL de la fiche consultée à la fin. Ne crée pas d'onglets imaginaires."
            badge_title = "🛠️ PROTOCOLE TECHNIQUE IPACKEPS"
        elif st.session_state.active_module == "examens":
            consigne_ia = f"Tu es l'assistant de terrain officiel d'Aix-Marseille et Éduscol. Réponds de manière purement institutionnelle et administrative sur les textes, livrets ou dispenses à partir de ces documents : {extraits_doc}. ⚠️ INTERDICTION ABSOLUE de parler d'interface de clics logiciels. Ajoute les liens URL exacts consultés."
            badge_title = "📊 REGLEMENTATION EXAMENS & EVALUATIONS"
        else:
            consigne_ia = f"Tu es l'assistant de recherche globale EPS. Synthétise clairement les informations trouvées sur les serveurs institutionnels : {extraits_doc}. Donne la liste complète des liens URL trouvés."
            badge_title = "🔍 RÉSULTATS DE RECHERCHE GLOBALE"

        response_web = Settings.llm.complete(consigne_ia)
        formatted_answer = f'<div class="{color_card}"><strong>{badge_title} :</strong><br><br>{response_web.text}</div>'

    st.session_state.messages_hub.append({"role": "assistant", "content": formatted_answer})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
