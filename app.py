import streamlit as st
import requests
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Expert iPackEPS", layout="wide", initial_sidebar_state="collapsed")

# 2. STYLE ET DESIGN (CSS)
st.markdown("""
    <style>
    .hub-header { background-color: #1E293B; padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="hub-header"><h1>Assistant Support iPackEPS</h1></div>', unsafe_allow_html=True)

# Initialisation de l'historique
if "messages_hub" not in st.session_state:
    st.session_state.messages_hub = []

# 3. INTERFACE DE SAISIE
prompt = st.chat_input("Ex: Comment déposer un certificat médical ?")

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    with st.spinner("Analyse chirurgicale des tutoriels en cours..."):
        try:
            # REQUÊTE TAVILY : On force l'extraction du contenu brut (raw) pour voir les liens
            query_technique = f"site:ipackeps.ac-creteil.fr {prompt} tutoriel guide procédure clics"
            
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": query_technique,
                "include_domains": ["ipackeps.ac-creteil.fr"],
                "search_depth": "advanced",
                "include_raw_content": True 
            })
            
            # Récupération du contenu brut des pages
            results = res.json().get("results", [])
            raw_data = "\n".join([r.get('raw_content', r.get('content', '')) for r in results])
            
            # SYSTEM EXPERT : "AGENT EXTRACTEUR DE LIENS & ÉTAPES"
            system_expert = """
            Tu es l'expert technique d'iPackEPS. 
            TON OBJECTIF : Donner uniquement les étapes de manipulation logicielle.
            
            RÈGLES D'EXÉCUTION STRICTES :
            1. PAS D'INTRODUCTION : Interdiction de dire "Voici le tutoriel" ou "Bonjour". Commence directement par l'action.
            2. PAS DE RÉSUMÉ : Ne fais pas de sommaire de la page. Si l'utilisateur demande le dépôt de certificats, ignore la fiche établissement ou le TASA.
            3. DÉTECTION DE LIEN : Si tu vois un lien ou un titre nommé "Dépôt des Certificats Médicaux", c'est ta cible prioritaire.
            4. FORMATAGE "CLIC-BOUTON" :
               - Étape 1 : [Chemin dans le menu]
               - Étape 2 : [Clic sur le bouton ou l'onglet précis]
               - Étape 3 : [Validation finale]
            5. LIEN SOURCE : Si la procédure complète est dans un sous-article, cite le titre du lien et son URL.
            6. PAS DE BLABLA : Supprime toute mention du Bac, de l'UNSS ou des circulaires administratives.
            """
            
            # Configuration du LLM
            Settings.llm = OpenAI(
                model="gpt-4o-mini", 
                temperature=0, 
                max_tokens=1500, 
                api_key=st.secrets["OPENAI_API_KEY"]
            )
            
            # Génération de la réponse
            full_prompt = f"{system_expert}\n\nCONTENU BRUT DU SITE :\n{raw_data}\n\nQUESTION UTILISATEUR :\n{prompt}"
            response = Settings.llm.complete(full_prompt)
            
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Une erreur technique est survenue : {str(e)}")
            
    st.rerun()

# 4. AFFICHAGE DES MESSAGES
for m in st.session_state.messages_hub:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
