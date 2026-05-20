import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

st.set_page_config(page_title="Expert iPackEPS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .hub-header { background-color: #1E293B; padding: 25px; border-radius: 15px; color: white; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="hub-header"><h1>Expert Support iPackEPS</h1></div>', unsafe_allow_html=True)

if "messages_hub" not in st.session_state: st.session_state.messages_hub = []

prompt = st.chat_input("Quelle procédure cherchez-vous ?")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    with st.spinner("Analyse en cours..."):
        try:
            query = f"{prompt} mode d'emploi clic bouton site:ipackeps.ac-creteil.fr"
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": query,
                "include_domains": ["ipackeps.ac-creteil.fr"],
                "search_depth": "advanced",
                "include_raw_content": True 
            })
            raw = "\n".join([r.get('raw_content', r.get('content', '')) for r in res.json().get("results", [])])
            
            system = "Tu es l'expert iPackEPS. Donne uniquement les étapes (clics, menus) de façon concise. Pas d'intro, pas de résumé."
            Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
            response = Settings.llm.complete(system + "\n\nDonnées : " + raw + "\n\nQuestion : " + prompt)
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages_hub.append({"role": "assistant", "content": f"Erreur : {str(e)}"})
    st.rerun()

for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): st.markdown(m["content"])
