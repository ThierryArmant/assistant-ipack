import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# 1. CONFIGURATION (Stable)
st.set_page_config(page_title="Assistance Expert iPackEPS", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN ARCHITECTURAL (Restauré)
st.markdown("""
    <style>
    .stApp { background: url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2000'); background-size: cover; }
    .main-box { background: rgba(15, 23, 42, 0.85); padding: 25px; border-radius: 15px; color: white; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# 3. INTERFACE
with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🎓 Assistance Expert iPackEPS")
    
    # Boutons de contexte
    c1, c2, c3 = st.columns(3)
    if c1.button("🛠️ iPackEPS"): st.session_state.context = "iPackEPS"
    if c2.button("📊 Examens"): st.session_state.context = "Examen"
    if c3.button("🔍 Générales"): st.session_state.context = "Generales"
    
    st.markdown('</div>', unsafe_allow_html=True)

# 4. MOTEUR D'EXTRACTION STRICT
if "messages" not in st.session_state: st.session_state.messages = []
prompt = st.chat_input("Posez votre question institutionnelle ou technique...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Analyse chirurgicale..."):
        try:
            # Recherche ciblée
            query = f"{prompt} mode d'emploi clic étape par étape site:ipackeps.ac-creteil.fr"
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": query,
                "include_raw_content": True
            })
            raw = "\n".join([r.get('raw_content', '') for r in res.json().get("results", [])])
            
            # IA Directrice
            system = "Tu es l'expert technique. Donne uniquement des étapes numérotées, claires et courtes. Pas d'intro."
            llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
            resp = llm.complete(system + "\n\nDonnées : " + raw + "\n\nQuestion : " + prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
        except Exception as e:
            st.error(str(e))
    st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])
