import streamlit as st
import os
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# Configuration
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

# Initialisation
if "messages_hub" not in st.session_state: st.session_state.messages_hub = []
if "active_module" not in st.session_state: st.session_state.active_module = "ipack"

# ======================================================================
# STYLE CSS STABLE (LE DESIGN PROPRE)
# ======================================================================
st.markdown("""
    <style>
    .block-container { padding: 20px; max-width: 900px; }
    .hub-header { background-color: #1E293B; padding: 20px; border-radius: 8px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .context-box { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2); }
    .stButton button { width: 100%; border-radius: 8px; }
    .red-btn button { background-color: rgba(220, 38, 38, 0.25) !important; color: white !important; border: 1px solid #EF4444 !important; }
    .assistant-card { background: #1E293B; padding: 20px; border-radius: 10px; border-left: 5px solid #10B981; color: white; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# Interface
st.markdown('<div class="hub-header"><h1>Hub IA - EPS (Académie de Créteil)</h1></div>', unsafe_allow_html=True)

st.markdown('<div class="context-box">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
if col1.button("🛠️ iPackEPS", type="primary" if st.session_state.active_module == "ipack" else "secondary"):
    st.session_state.active_module = "ipack"; st.rerun()
if col2.button("📊 Examens", type="primary" if st.session_state.active_module == "examens" else "secondary"):
    st.session_state.active_module = "examens"; st.rerun()
if col3.button("🔍 Générales", type="primary" if st.session_state.active_module == "general" else "secondary"):
    st.session_state.active_module = "general"; st.rerun()

if st.button("🧹 Nettoyer", key="clear", use_container_width=True):
    st.session_state.messages_hub = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Chat
prompt = st.chat_input("Posez votre question sur iPackEPS (ac-creteil.fr)...")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    # Consigne ultra-stricte
    domaine = "ipackeps.ac-creteil.fr"
    system_instruction = f"""
    Tu es l'assistant technique expert pour iPackEPS (Académie de Créteil).
    1. CONTEXTE : Tu travailles pour l'Éducation Nationale. JAMAIS tu ne parles de palettes, de logistique ou de colis.
    2. SOURCE : Tu utilises EXCLUSIVEMENT le contenu de {domaine}.
    3. FORMAT : Si la question est technique, rédige un tutoriel PAS-À-PAS numéroté et détaillé.
    4. VÉRIFICATION : Si l'info n'est pas sur le site, dis que tu ne sais pas.
    """

    with st.spinner("Analyse du site de Créteil..."):
        try:
            # Recherche ciblée
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": prompt,
                "include_domains": [domaine],
                "search_depth": "advanced"
            })
            
            # Extraction propre
            raw_data = "\n".join([r['content'] for r in res.json().get("results", [])])
            
            Settings.llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
            response = Settings.llm.complete(system_instruction + "\n\nSource: " + raw_data + "\n\nQuestion: " + prompt)
            
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages_hub.append({"role": "assistant", "content": "Erreur : Je n'arrive pas à lire le site de Créteil pour le moment."})
    st.rerun()

for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): st.markdown(f'<div class="assistant-card">{m["content"]}</div>' if m["role"]=="assistant" else m["content"], unsafe_allow_html=True)
