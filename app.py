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
# Utilisation d'un historique unique partagé pour la fenêtre unique
if "messages_hub" not in st.session_state:
    st.session_state.messages_hub = []
if "current_module" not in st.session_state:
    st.session_state.current_module = "🛠️ iPackEPS (Doc Créteil)"

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
# 3. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (MOBILE FIRST - TRANSPARENCE STANDARD)
# ======================================================================
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 0.5rem !important; 
        padding-bottom: 2rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 800px !important; /* Largeur idéale pour la lecture sur PC et Mobile */
    }}
    
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    /* Structure du Bandeau Supérieur */
    .hub-header {{ 
        background-color: #1E293B; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 15px; 
        margin-bottom: 15px; 
        border-radius: 8px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3); 
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 18px !important; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 9px !important; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 10px; border-radius: 20px; font-size: 9px !important; font-weight: bold; font-family: monospace; margin-top: 4px; display: inline-block; }}
    
    /* Grand Bandeau de Titre Dynamique Unique */
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
    
    /* Bouton Nettoyer */
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 10px !important; padding: 3px 12px !important; }}
    
    /* Bloc de choix des Boutons Modules */
    div[data-testid="stRadio"] {{
        background-color: #1E293B !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: inset 0px 2px 4px rgba(0,0,0,0.3) !important;
        margin-bottom: 15px !important;
    }}
    div[data-testid="stRadio"] label p {{ color: #FFFFFF !important; font-weight: 600 !important; font-size: 12px !important; }}
    
    /* 🏔️ Fenêtre de tchat unique standard transparente à 20% */
    .glass-card {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 8px !important;
        padding: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 15px;
    }}
    
    /* Bulles de réponse IA */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 12px; 
        border-radius: 4px; 
        margin-bottom: 12px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }}
    .santorin-card {{ border-left: 5px solid #38BDF8 !important; }} 
    .general-card {{ border-left: 5px solid #10B981 !important; }} 
    
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; font-size: 13px !important; line-height: 1.4 !important; }}
    .santorin-card strong, .general-card strong {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    .santorin-card a, .general-card a {{ color: #38BDF8 !important; font-weight: bold !important; text-decoration: underline !important; }}
    
    /* Tableaux Markdown */
    .santorin-card table, .general-card table {{ background-color: rgba(30, 41, 59, 0.6) !important; color: #FFFFFF !important; border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 12px !important; }}
    .santorin-card th, .general-card th {{ background-color: rgba(15, 23, 42, 0.85) !important; color: #FFFFFF !important; padding: 8px !important; font-weight: bold !important; font-size: 12px !important; border: 1px solid rgba(255,255,255,0.2) !important; text-align: left; }}
    .santorin-card td, .general-card td {{ padding: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; vertical-align: top !important; }}
    
    /* Bulle message Utilisateur */
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
# 5. RENDU DU BANDEAU SUPERIEUR
# ======================================================================
st.markdown(f"""
    <div class="hub-header">
        <div style="text-align: left;"><img src="{github_url}{img_gauche}" width="85"></div>
        <div class="hub-title" style="text-align: center;">
            <h1>Hub IA - EPS</h1>
            <p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="text-align: right;"><img src="{github_url}{img_droite}" width="55"></div>
    </div>
""", unsafe_allow_html=True)

# ======================================================================
# 6. ZONE DES BOUTONS DE CHOIX DES MODULES (VUE UNIQUE RECONSTRUITE)
# ======================================================================
context_choice = st.radio(
    "Choisissez votre univers d'assistance :", 
    [
        "🛠️ iPackEPS (Documentation Créteil)", 
        "📊 Examens & Santorin (Aix-Marseille & Éduscol)", 
        "🔍 Recherches générales (Multi-sites EPS)"
    ],
    key="radio_hub_unique"
)

# Sécurité mémoire : Si l'utilisateur change de bouton, on nettoie la fenêtre pour éviter les interférences
if context_choice != st.session_state.current_module:
    st.session_state.messages_hub = []
    st.session_state.current_module = context_choice
    st.rerun()

# Affichage du titre dynamique de la fenêtre unique
st.markdown(f'<div class="column-title">💬 Fenêtre Active : {context_choice}</div>', unsafe_allow_html=True)

# --- 🏔️ OUVERTURE DE LA FENÊTRE DE TCHAT UNIQUE ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

if st.button("🧹 Réinitialiser la discussion", key="clear_hub"):
    st.session_state.messages_hub = []
    st.rerun()

# Rendu des messages existants dans la fenêtre
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"], unsafe_allow_html=True)

# Zone de saisie unique tout en bas
if prompt := st.chat_input("Posez votre question ici...", key="input_hub_unique"):
    st.session_state.messages_hub.append({"role": "user", "content": f"**Vous** : {prompt}"})
    
    # Configuration des variables selon le bouton coché
    if "ipackeps" in context_choice.lower():
        domaines_recherche = ["ipackeps.ac-creteil.fr"]
        texte_spinner = "Interrogation de la base technique d'iPackEPS Créteil..."
        color_card = "general-card"
    elif "examens" in context_choice.lower():
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr"]
        texte_spinner = "Fouille des protocoles d'Aix-Marseille et des lois Éduscol..."
        color_card = "santorin-card"
    else:
        domaines_recherche = ["pedagogie.ac-aix-marseille.fr", "eduscol.education.gouv.fr", "eps.enseigne.ac-lyon.fr", "eps.ac-creteil.fr"]
        texte_spinner = "Recherche globale sur les 4 portails officiels EPS..."
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

        # Définition personnalisée des consignes de l'IA selon le contexte
        if "ipackeps" in context_choice.lower():
            consigne_ia = f"""
            Tu es l'assistant technique expert du logiciel iPackEPS. 
            Rédige un protocole pas-à-pas précis (menus, boutons, clics) basé STRICTEMENT sur cette aide de Créteil :
            {extraits_doc if extraits_doc else 'Se référer aux normes iPack.'}
            Ajoute l'URL précise de la fiche consultée à la fin. Ne crée pas de menus fictifs.
            """
            badge_title = "🛠️ PROTOCOLE TECHNIQUE IPACKEPS"
            
        elif "examens" in context_choice.lower():
            consigne_ia = f"""
            Tu es l'assistant de terrain officiel pour l'évaluation et les examens EPS (Aix-Marseille et Éduscol).
            Réponds de façon rigoureuse sur les textes, livrets, dispenses ou grilles d'évaluation en te basant sur ces documents :
            {extraits_doc if extraits_doc else 'Utilise les protocoles officiels d Aix-Marseille.'}
            ⚠️ INTERDICTION DE PARLER d'iPackEPS, de clics informatiques ou de menus logiciels. Reste sur le plan administratif. Ajoute les liens URL exacts à la fin.
            """
            badge_title = "📊 RÉGLEMENTATION EXAMENS & EVALUATIONS"
            
        else:
            consigne_ia = f"""
            Tu es l'assistant de recherche globale pour les enseignants d'EPS.
            Fais une synthèse exhaustive et claire à partir des fiches et textes récoltés sur les portails académiques :
            {extraits_doc if extraits_doc else 'Réponds à partir de tes connaissances institutionnelles EPS.'}
            Ajoute la liste complète des liens web trouvés à la fin.
            """
            badge_title = "🔍 RÉSULTATS DE RECHERCHE EPS"

        # Génération du tchat
        response_web = Settings.llm.complete(consigne_ia)
        formatted_answer = f'<div class="{color_card}"><strong>{badge_title} :</strong><br><br>{response_web.text}</div>'

    st.session_state.messages_hub.append({"role": "assistant", "content": formatted_answer})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
