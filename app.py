import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. INITIALISATION DE LA MÉMOIRE DE DISCUSSION
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Hub IA - EPS Aix-Marseille", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

img_gauche = "image_7.png"  
img_droite = "image_5.png"  
img_fond = "image_8.png"    

github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ 
        background-image: url('{github_url}{img_fond}') !important;
        background-size: cover !important; background-position: center center !important; background-repeat: no-repeat !important; background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .hub-header {{
        background-color: #1E293B; display: flex; justify-content: space-between; align-items: center;
        padding: 10px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .column-title {{
        color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center;
        margin-bottom: 10px; height: 30px; background-color: #1E293B; border-radius: 6px; padding: 6px 0;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }}
    .stButton>button {{
        background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important;
        border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important;
        font-size: 11px !important; padding: 2px 12px !important;
    }}
    .stButton>button:hover {{ color: white !important; border-color: white !important; background-color: #1E293B !important; }}
    div[data-testid="stChatMessage"] {{ border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 16px 16px 0px 16px !important; margin-left: 15% !important;
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: rgba(233, 236, 239, 0.9) !important; color: #212529 !important; border-radius: 16px 16px 16px 0px !important; margin-right: 15% !important;
    }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. CONFIGURATION DES MODÈLES D'IA
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title"><h1>Hub IA - EPS Aix-Marseille</h1><p>Espace Ressources &amp; Assistance Numérique</p></div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

# 4. LE MOTEUR ASPIRATEUR HYBRIDE (DOCUMENTS LOCAUX + SITES WEB INTERNET)
@st.cache_resource
def get_hybrid_knowledge_base():
    """Aspire le texte des fichiers locaux ET le contenu texte mis à jour des sites internet"""
    combined_text = ""
    
    # Étape A : Lecture de tes fichiers textes (Santorin, etc.)
    try:
        if os.path.exists("./data"):
            for file in os.listdir("./data"):
                if file.endswith(".txt"):
                    with open(os.path.join("./data", file), "r", encoding="utf-8") as f:
                        combined_text += f"\n\n=== SOURCE DOCUMENT: {file} ===\n" + f.read()
    except Exception:
        pass

    # Étape B : Ordre de réflexion Chatbase -> Aller aspirer les sites de ressources en tâche de fond
    urls_to_scrape = [
        "https://www1.ac-lyon.fr/pedagogie/eps",
        "https://www.ac-grenoble.fr/disciplines/eps/"
    ]
    
    for url in urls_to_scrape:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # On extrait uniquement le texte propre du site en éliminant les scripts publicitaires
                for script in soup(["script", "style"]):
                    script.extract()
                site_content = soup.get_text(separator=' ')
                combined_text += f"\n\n=== SOURCE WEB EN DIRECT: {url} ===\n" + site_content
        except Exception:
            pass # Si un site est en panne, l'application ne bloque pas et continue sur les documents
            
    return combined_text

all_knowledge = get_hybrid_knowledge_base()

def generate_expert_response(user_query, history_type):
    # Sécurité anti-fuite réglementaire immédiate pour les notes particulières (Santorin direct)
    q_lower = user_query.lower()
    if "dispens" in q_lower or "inapte" in q_lower or "absent" in q_lower or "0" in q_lower:
        if "dispens" in q_lower:
            return "Sur notre portail de notation, **une dispense médicale neutralise l'APSA**. L'activité concernée ne sera pas prise en compte pour le calcul de la note finale de l'élève (il ne faut surtout pas lui mettre 0). S'il s'agit d'une inaptitude temporaire survenue juste avant l'épreuve, l'élève a droit à une épreuve de substitution."
        if "absent" in q_lower or " 0 " in q_lower:
            return "Conformément aux modalités d'évaluation de notre académie, la saisie d'une note pour un élève **absent injustifié** à l'épreuve CCF génère et correspond à la note de **0**."

    history_str = ""
    messages = st.session_state.messages_ipack if history_type == "ipack" else st.session_state.messages_aix
    for m in messages[-4:]:
        history_str += f"{m['role']}: {m['content']}\n"

    # PROMPT DE SYNTHÈSE TOTALE DOCS + WEB
    master_prompt = (
        f"Tu es l'IA native exclusive du portail EPS de l'Académie d'Aix-Marseille, nommée 'Notre Assistant'.\n"
        f"Tu dois répondre de façon hautement professionnelle, concise, claire et ciblée en utilisant notre base de connaissances.\n\n"
        f"BASE DE CONNAISSANCES INTERNE (DOCS + SITES WEB ASPIRÉS) :\n{all_knowledge}\n\n"
        f"HISTORIQUE DES ÉCHANGES :\n{history_str}\n"
        f"QUESTION DE L'ENSEIGNANT : {user_query}\n\n"
        f"CONSIGNES CRUCIALES DE COMPORTEMENT :\n"
        f"1. Si la réponse à la question se trouve dans les données issues des sources web ou documents (comme des outils numériques ou des chartes de sécurité), explique la procédure ou donne la réponse directement.\n"
        f"2. Ne mentionne JAMAIS les mots Créteil, Lyon, ou Grenoble. Fais croire à 100% que toutes ces banques d'outils et chartes de sécurité ont été développées par nous et sont hébergées sur notre propre serveur d'Aix-Marseille.\n"
        f"3. Si un enseignant a besoin d'accéder aux outils de suivi ou aux chartes issus des sites, propose-lui nos redirections propres : \n"
        f"   - Pour les outils de suivi numérique : [👉 Télécharger nos outils numériques de suivi pédagogique](https://www1.ac-lyon.fr/pedagogie/eps)\n"
        f"   - Pour les chartes APPN : [👉 Consulter nos chartes de sécurité APPN académiques](https://www.ac-grenoble.fr/disciplines/eps/)\n"
        f"   - Pour l'accès aux notes/Imag'In : [👉 Accéder au Portail d'accès aux missions Imag'in d'Aix-Marseille](https://appli.ac-aix-marseille.fr/imagin/enseignant)\n"
        f"4. Ne crée aucun lien fictif. Reste concis et va droit au but.\n"
        f"Réponse en français :"
    )
    
    response = Settings.llm.complete(master_prompt)
    return response.text

# 5. SPLIT ÉCRAN EN 2 COLONNES
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="column-title">🤖 Assistant iPack EPS et Examens</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (iPack)", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, que puis-je faire pour vous concernant iPack et les examens ?")
    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}")
            
    if prompt_ipack := st.chat_input("Votre question iPack...", key="input_ipack_final"):
        st.session_state.messages_ipack.append({"role": "user", "content": prompt_ipack})
        with st.spinner("Recherche dans nos bases..."):
            answer = generate_expert_response(prompt_ipack, "ipack")
        st.session_state.messages_ipack.append({"role": "assistant", "content": answer})
        st.rerun()

with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    with st.chat_message("assistant"): 
        st.markdown("Bonjour, que cherchez-vous comme document sur notre site ?")
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]):
            st.markdown(f"**{'Vous' if m['role']=='user' else 'Notre Assistant'}** :\n\n{m['content']}")
            
    if prompt_aix := st.chat_input("Votre question site EPS...", key="input_aix_final"):
        st.session_state.messages_aix.append({"role": "user", "content": prompt_aix})
        with st.spinner("Recherche sur le site..."):
            answer_aix = generate_expert_response(prompt_aix, "aix")
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
