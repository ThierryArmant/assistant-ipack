import streamlit as st
import os
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# Configuration
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

if "messages_hub" not in st.session_state: st.session_state.messages_hub = []
if "active_module" not in st.session_state: st.session_state.active_module = "ipack"

# ======================================================================
# STYLE CSS COMPLET (Restauration du design Hub IA)
# ======================================================================
st.markdown("""
    <style>
    /* Structure principale */
    .block-container { padding: 2rem; max-width: 1000px; }
    
    /* Header bleu */
    .hub-header { background-color: #1E293B; padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* Bloc contexte */
    .context-box { background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
    
    /* Boutons */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .clean-btn button { background-color: #EF4444 !important; color: white !important; }
    
    /* Chat */
    .assistant-card { background: #1E293B; padding: 15px; border-radius: 8px; border-left: 5px solid #10B981; color: white; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# INTERFACE
# ======================================================================
st.markdown('<div class="hub-header"><h1>Hub IA - EPS (Académie de Créteil)</h1></div>', unsafe_allow_html=True)

st.markdown('<div class="context-box">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
if col1.button("🛠️ iPackEPS", type="primary" if st.session_state.active_module == "ipack" else "secondary"):
    st.session_state.active_module = "ipack"; st.rerun()
if col2.button("📊 Examens", type="primary" if st.session_state.active_module == "examens" else "secondary"):
    st.session_state.active_module = "examens"; st.rerun()
if col3.button("🔍 Générales", type="primary" if st.session_state.active_module == "general" else "secondary"):
    st.session_state.active_module = "general"; st.rerun()

if st.button("🧹 Nettoyer la discussion", use_container_width=True):
    st.session_state.messages_hub = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ======================================================================
# LOGIQUE IA (Verrouillée sur Créteil)
# ======================================================================
prompt = st.chat_input("Posez votre question sur iPackEPS (ac-creteil.fr)...")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    domaine = "ipackeps.ac-creteil.fr"
    system_instruction = f"""
    Tu es l'assistant technique expert pour iPackEPS (ac-creteil.fr).
    1. CONTEXTE : Tu travailles pour l'Éducation Nationale. JAMAIS tu ne parles de logistique, de colis ou de palettes.
    2. SOURCE : Tu utilises EXCLUSIVEMENT le contenu de {domaine}.
    3. FORMAT : Si la question concerne une procédure, rédige un tutoriel PAS-À-PAS numéroté.
    4. SÉCURITÉ : Si l'information ne se trouve pas sur le site, dis-le clairement sans inventer.
    """

    with st.spinner("Analyse du site de Créteil..."):
        try:
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": prompt,
                "include_domains": [domaine],
                "search_depth": "advanced"
            })
            raw_data = "\n".join([r['content'] for r in res.json().get("results", [])])
            Settings.llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
            response = Settings.llm.complete(system_instruction + "\n\nDonnées sources: " + raw_data + "\n\nQuestion: " + prompt)
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception:
            st.error("Erreur de connexion.")
    st.rerun()

# Rendu des messages
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(f'<div class="assistant-card">{m["content"]}</div>' if m["role"]=="assistant" else m["content"], unsafe_allow_html=True)
