import streamlit as st
import os
from openai import OpenAI

# 1. CONFIGURATION DE LA PAGE EN MODE LARGE
st.set_page_config(
    page_title="Tableau de Bord EPS",
    page_icon="🏃‍♂️",
    layout="wide"  # Permet d'occuper tout l'écran pour les deux fenêtres
)

# Initialisation de la clé API OpenAI
if "OPENAI_API_KEY" in os.environ:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
elif "openai" in st.secrets:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
else:
    st.error("⚠️ Clé API OpenAI manquante dans les Secrets Streamlit.")
    st.stop()

# 2. INITIALISATION DES HISTORIQUES DE CHAT
if "messages_ipack" not in st.session_state:
    st.session_state["messages_ipack"] = []
if "messages_examens" not in st.session_state:
    st.session_state["messages_examens"] = []

# 3. CRÉATION DES DEUX FENÊTRES DISTINCTES (CÔTE À CÔTE)
col_ipack, col_examens = st.columns(2)

# --- FENÊTRE DE GAUCHE : IPACK & DOCUMENTS ---
with col_ipack:
    st.header("📱 Fenêtre 1 : iPack & Documents")
    st.caption("Source : https://ipackeps.ac-creteil.fr/ + Vos documents")
    st.write("---")
    
    # Zone d'affichage des messages iPack
    container_ipack = st.container(height=400)
    with container_ipack:
        for msg in st.session_state["messages_ipack"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Saisie pour la fenêtre iPack
    if prompt_ipack := st.chat_input("Question sur iPack ou vos documents...", key="input_ipack"):
        st.session_state["messages_ipack"].append({"role": "user", "content": prompt_ipack})
        with container_ipack:
            with st.chat_message("user"):
                st.markdown(prompt_ipack)
        
        # Prompt système iPack
        sys_ipack = (
            "Tu es un collaborateur IA authentique et direct. Contexte strict : Tu travailles uniquement sur la rubrique iPack. "
            "Base-toi sur les documents de l'utilisateur et sur https://ipackeps.ac-creteil.fr/. "
            "Ne confonds jamais l'application locale avec les serveurs nationaux qui ferment."
        )
        
        # Appel API
        messages_api = [{"role": "system", "content": sys_ipack}] + st.session_state["messages_ipack"]
        response = client.chat.completions.create(model="gpt-4o", messages=messages_api)
        rep_text = response.choices[0].message.content
        
        st.session_state["messages_ipack"].append({"role": "assistant", "content": rep_text})
        st.rerun()

# --- FENÊTRE DE DROITE : EXAMENS ---
with col_examens:
    st.header("📝 Fenêtre 2 : Examens Dédiés")
    st.caption("Sources : Aix-Marseille, Lyon, Grenoble, Créteil")
    st.write("---")
    
    # Zone d'affichage des messages Examens
    container_examens = st.container(height=400)
    with container_examens:
        for msg in st.session_state["messages_examens"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Saisie pour la fenêtre Examens
    if prompt_examens := st.chat_input("Question sur les examens / épreuves...", key="input_examens"):
        st.session_state["messages_examens"].append({"role": "user", "content": prompt_examens})
        with container_examens:
            with st.chat_message("user"):
                st.markdown(prompt_examens)
        
        # Prompt système Examens
        sys_examens = (
            "Tu es un collaborateur IA authentique et direct. Contexte strict : Tu travailles uniquement sur les EXAMENS. "
            "Sources exclusives : https://www.ac-aix-marseille.fr/epreuves-ponctuelles-d-eps-pour-les-examens-du-second-degre-121962, "
            "https://eps.enseigne.ac-lyon.fr/spip/spip.php?rubrique9, https://eps-pedagogie.web.ac-grenoble.fr/examens, "
            "https://eps.ac-creteil.fr/spip.php?rubrique5."
        )
        
        # Appel API
        messages_api = [{"role": "system", "content": sys_examens}] + st.session_state["messages_examens"]
        response = client.chat.completions.create(model="gpt-4o", messages=messages_api)
        rep_text = response.choices[0].message.content
        
        st.session_state["messages_examens"].append({"role": "assistant", "content": rep_text})
        st.rerun()
