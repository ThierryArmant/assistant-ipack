import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Hub IA - iPackEPS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. TON CSS PERSONNALISÉ (Restauré depuis ta capture d'écran)
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Design du header principal */
    .hub-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        border: 1px solid #334155;
    }
    
    /* Design des messages chat */
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. TON HEADER (Restauré)
st.markdown("""
    <div class="hub-header">
        <h1 style='margin:0; font-size: 2.5em;'>🎓 Assistance Experte iPackEPS</h1>
        <p style='margin-top:10px; color:#94A3B8; font-size:1.1em;'>
            Posez votre question technique, l'IA analyse la documentation officielle pour vous répondre.
        </p>
    </div>
""", unsafe_allow_html=True)

# 4. INITIALISATION DE LA MÉMOIRE
if "messages_hub" not in st.session_state: 
    st.session_state.messages_hub = []

# 5. AFFICHAGE DES ANCIENS MESSAGES
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"])

# 6. MOTEUR "EXTRACTEUR STRICT" (La nouveauté d'aujourd'hui)
prompt = st.chat_input("Ex: Comment déposer un certificat médical ?")

if prompt:
    # Affiche la question de l'utilisateur
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prépare la réponse de l'IA
    with st.chat_message("assistant"):
        with st.spinner("Analyse chirurgicale des tutoriels en cours..."):
            try:
                # REQUÊTE TAVILY
                query_technique = f"site:ipackeps.ac-creteil.fr {prompt} tutoriel guide procédure clics"
                
                res = requests.post("https://api.tavily.com/search", json={
                    "api_key": st.secrets["TAVILY_API_KEY"],
                    "query": query_technique,
                    "include_domains": ["ipackeps.ac-creteil.fr"],
                    "search_depth": "advanced",
                    "include_raw_content": True 
                })
                
                # Extraction du contenu brut pour repérer les liens
                results = res.json().get("results", [])
                raw_data = "\n".join([r.get('raw_content', r.get('content', '')) for r in results])
                
                # SYSTEM EXPERT "EXÉCUTEUR STRICT"
                system_expert = """
                Tu es l'expert technique d'iPackEPS. 
                TON OBJECTIF : Donner uniquement les étapes de manipulation logicielle.
                
                RÈGLES D'EXÉCUTION STRICTES :
                1. PAS D'INTRODUCTION : Interdiction de dire "Voici le tutoriel". Commence directement.
                2. PAS DE RÉSUMÉ : Ne fais pas de sommaire de la page de la commission. 
                3. FORMATAGE "CLIC-BOUTON" :
                   - Étape 1 : [Chemin dans le menu]
                   - Étape 2 : [Clic sur le bouton ou l'onglet précis]
                4. LIEN SOURCE : Si la procédure est dans un lien (ex: "Dépôt des Certificats Médicaux"), donne l'URL de ce lien.
                5. PAS DE BLABLA : Supprime toute mention du Bac ou des circulaires administratives.
                """
                
                Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=1500, api_key=st.secrets["OPENAI_API_KEY"])
                
                full_prompt = f"{system_expert}\n\nCONTENU BRUT DU SITE :\n{raw_data}\n\nQUESTION UTILISATEUR :\n{prompt}"
                response = Settings.llm.complete(full_prompt)
                
                st.markdown(response.text)
                st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Une erreur technique est survenue : {str(e)}")
