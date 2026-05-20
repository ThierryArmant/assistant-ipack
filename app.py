import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# 1. CONFIGURATION
st.set_page_config(page_title="Hub IA - EPS", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN (CSS stable)
st.markdown("""
    <style>
    .hub-header { background-color: #1E293B; padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .context-box { background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
    .stChatMessage { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# 3. INTERFACE
st.markdown('<div class="hub-header"><h1>Expert Support iPackEPS (Académie de Créteil)</h1></div>', unsafe_allow_html=True)

if "messages_hub" not in st.session_state: st.session_state.messages_hub = []

st.markdown('<div class="context-box">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
if col1.button("🛠️ iPackEPS"): st.session_state.active_module = "ipack"
if col2.button("📊 Examens"): st.session_state.active_module = "examens"
if col3.button("🔍 Générales"): st.session_state.active_module = "general"

if st.button("🧹 Nettoyer"):
    st.session_state.messages_hub = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIQUE "BACKDOOR" EXPERT MÉTIER
prompt = st.chat_input("Ex: Comment déposer un certificat médical ?")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    with st.spinner("Analyse approfondie des tutoriels..."):
        try:
            # QUERY TECHNIQUE FORCÉE sur la rubrique tutoriels
            # On demande d'inclure le contenu brut pour que l'IA puisse "lire" les guides
            query_technique = f"{prompt} procédure détaillée dépôt certificat médical iPackEPS"
            
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": query_technique,
                "include_domains": ["ipackeps.ac-creteil.fr"],
                "search_depth": "advanced",
                "include_raw_content": True 
            })
            
            # On agrège le contenu brut pour fournir le maximum de détails techniques à l'IA
            raw_data = "\n".join([r.get('raw_content', r.get('content', '')) for r in res.json().get("results", [])])
            
            # INSTRUCTION "EXPERT MÉTIER & TECHNIQUE"
            system_expert = """
            Tu es l'expert support technique d'iPackEPS.
            MISSION : Guider l'utilisateur pour déposer un certificat médical.
            
            RÈGLES D'EXCELLENCE :
            1. PAS DE THÉORIE : Ignore les circulaires, les définitions et le blabla administratif.
            2. FOCUS TUTORIEL : Si les données contiennent une procédure, extrais les étapes techniques (boutons, menus, clics).
            3. NAVIGATION : Chemin exact : Menu > Sous-menu > Action (Numéroté 1, 2, 3...).
            4. MÉTIER : Précise les contextes (ex: certificat longue durée ou ponctuel) si mentionnés.
            5. FORMAT : Markdown pur, numéroté, sans aucune div HTML.
            """
            
            Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=1500, api_key=st.secrets["OPENAI_API_KEY"])
            
            response = Settings.llm.complete(system_expert + "\n\nContenu technique extrait : " + raw_data + "\n\nQuestion utilisateur : " + prompt)
            
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages_hub.append({"role": "assistant", "content": f"Erreur de connexion : {str(e)}"})
    st.rerun()

# 5. AFFICHAGE
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"])
