import streamlit as st
import os
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# ======================================================================
# 1. CONFIGURATION
# ======================================================================
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

# 2. GESTION ÉTAT
if "messages_hub" not in st.session_state: st.session_state.messages_hub = []
if "active_module" not in st.session_state: st.session_state.active_module = "ipack"

# 3. INTERFACE & CSS (Design stable)
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem !important; max-width: 920px !important; }
    .hub-header { background-color: #1E293B; padding: 20px; border-radius: 8px; color: white; text-align: center; margin-bottom: 20px; }
    .context-container { background-color: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .stButton button { width: 100%; border-radius: 8px; }
    .assistant-card { background: #1E293B; padding: 15px; border-radius: 8px; border-left: 6px solid #10B981; color: white; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="hub-header"><h1>Hub IA - EPS (Académie de Créteil)</h1></div>', unsafe_allow_html=True)

# 4. CONTEXTE
st.markdown('<div class="context-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="small")
if col1.button("🛠️ iPackEPS", type="primary" if st.session_state.active_module == "ipack" else "secondary"):
    st.session_state.active_module = "ipack"; st.rerun()
if col2.button("📊 Examens", type="primary" if st.session_state.active_module == "examens" else "secondary"):
    st.session_state.active_module = "examens"; st.rerun()
if col3.button("🔍 Générales", type="primary" if st.session_state.active_module == "general" else "secondary"):
    st.session_state.active_module = "general"; st.rerun()

if st.button("🧹 Nettoyer"):
    st.session_state.messages_hub = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 5. CHAT ET LOGIQUE IA (Bloc iPack corrigé)
prompt = st.chat_input("Posez votre question...")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    with st.spinner("Analyse approfondie..."):
        
        # Logique Recherche
        extraits_doc = ""
        domaine = "ipackeps.ac-creteil.fr"
        
        # Appel Tavily
        res = requests.post("https://api.tavily.com/search", json={
            "api_key": st.secrets["TAVILY_API_KEY"],
            "query": prompt + " iPackEPS",
            "include_domains": [domaine] if st.session_state.active_module == "ipack" else None,
            "search_depth": "advanced"
        })
        raw_data = "\n".join([r['content'] for r in res.json().get("results", [])])

        # Consigne IA
        if st.session_state.active_module == "ipack":
            consigne = f"""
            Tu es l'assistant expert pour iPackEPS (ac-creteil.fr).
            1. RÈGLE : JAMAIS tu ne parles de palettes, de logistique ou de colis.
            2. SOURCE : Utilise EXCLUSIVEMENT les données extraites : {raw_data}
            3. FORMAT : Rédige UN TUTORIEL PAS-À-PAS NUMÉROTÉ très détaillé.
            4. LIENS : Termine par '🔗 Sources de référence :' en listant les URLs.
            5. VÉRIFICATION : Si l'info n'est pas dans les données, dis-le sans inventer.
            Question : {prompt}
            """
        else:
            consigne = f"Analyse : {raw_data}. Rédige une synthèse structurée. Question : {prompt}"

        Settings.llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
        resp = Settings.llm.complete(consigne)
        st.session_state.messages_hub.append({"role": "assistant", "content": resp.text})
    st.rerun()

for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="assistant-card">{m["content"]}</div>' if m["role"]=="assistant" else m["content"], unsafe_allow_html=True)
