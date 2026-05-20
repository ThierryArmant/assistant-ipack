import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# Configuration
st.set_page_config(page_title="Hub IA - iPackEPS", layout="wide")

st.markdown('<div style="background-color: #1E293B; padding: 20px; border-radius: 12px; color: white; text-align: center;"><h1>Expert Support iPackEPS</h1></div>', unsafe_allow_html=True)

if "messages_hub" not in st.session_state: st.session_state.messages_hub = []

prompt = st.chat_input("Quelle procédure cherchez-vous ?")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    with st.spinner("Analyse..."):
        try:
            query = f"{prompt} site:ipackeps.ac-creteil.fr/spip.php?rubrique2"
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": query,
                "include_domains": ["ipackeps.ac-creteil.fr"],
                "search_depth": "advanced"
            })
            
            data = "\n".join([r.get('content', '') for r in res.json().get("results", [])])
            
            system_expert = "Tu es l'expert iPackEPS. Réponds en utilisant uniquement les infos trouvées. Sois concis, technique et pas-à-pas."
            Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
            
            response = Settings.llm.complete(system_expert + "\n\nDonnées : " + data + "\n\nQuestion : " + prompt)
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages_hub.append({"role": "assistant", "content": f"Erreur : {str(e)}"})
    st.rerun()

for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): st.markdown(m["content"])
