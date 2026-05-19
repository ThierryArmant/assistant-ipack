import streamlit as st
import os
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# Configuration
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

if "messages_hub" not in st.session_state: st.session_state.messages_hub = []
if "active_module" not in st.session_state: st.session_state.active_module = "ipack"

# Styles (Design stabilisé)
st.markdown("""
    <style>
    .hub-header { background-color: #1E293B; padding: 20px; border-radius: 8px; color: white; text-align: center; }
    .stButton button { width: 100%; border-radius: 8px; }
    .red-btn button { background-color: rgba(220, 38, 38, 0.45) !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Interface Header
st.markdown('<div class="hub-header"><h1>Hub IA - EPS (Accès Académie de Créteil)</h1></div>', unsafe_allow_html=True)

# Contexte
col1, col2, col3 = st.columns(3)
if col1.button("🛠️ iPackEPS", type="primary" if st.session_state.active_module == "ipack" else "secondary"):
    st.session_state.active_module = "ipack"; st.rerun()
if col2.button("📊 Examens", type="primary" if st.session_state.active_module == "examens" else "secondary"):
    st.session_state.active_module = "examens"; st.rerun()
if col3.button("🔍 Générales", type="primary" if st.session_state.active_module == "general" else "secondary"):
    st.session_state.active_module = "general"; st.rerun()

# Logique de recherche verrouillée
if st.button("🧹 Nettoyer", key="clear"):
    st.session_state.messages_hub = []
    st.rerun()

prompt = st.chat_input("Posez votre question sur iPackEPS (ac-creteil.fr)...")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    # Verrouillage du domaine pour le mode iPack
    if st.session_state.active_module == "ipack":
        domaine = "ipackeps.ac-creteil.fr"
        consigne_stricte = f"""
        Tu es l'assistant technique officiel pour iPackEPS (ac-creteil.fr). 
        RÈGLE ABSOLUE : Tu ne dois puiser tes informations QUE dans le contenu de {domaine}.
        Si la réponse n'est pas dans le contenu trouvé, ne l'invente pas. 
        Donne une procédure pas-à-pas numérotée très détaillée.
        """
    else:
        domaine = "eduscol.education.gouv.fr"
        consigne_stricte = "Tu es l'assistant général EPS."

    with st.spinner(f"Recherche sur {domaine}..."):
        # Appel Tavily avec filtre de domaine strict
        try:
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": prompt,
                "include_domains": [domaine]
            })
            extraits = "\n".join([r['content'] for r in res.json().get("results", [])])
            
            Settings.llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
            response = Settings.llm.complete(consigne_stricte + "\n\nDonnées sources: " + extraits)
            
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Erreur de connexion aux sources.")
    st.rerun()

for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): st.markdown(m["content"])
