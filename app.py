import streamlit as st
import os
from openai import OpenAI

# 1. CONFIGURATION DE LA PAGE STREAMLIT
st.set_page_config(
    page_title="Assistant EPS & Examens",
    page_icon="🏃‍♂️",
    layout="wide"
)

# 2. CENTRALISATION STRICTE DES SOURCES CONFIGURÉES
SOURCES_CONFIG = {
    "rubrique_ipack": {
        "liens": ["https://ipackeps.ac-creteil.fr/"],
        "description": "Gestion locale iPackEPS et documents internes de l'enseignant."
    },
    "rubrique_examens": {
        "liens": [
            "https://www.ac-aix-marseille.fr/epreuves-ponctuelles-d-eps-pour-les-examens-du-second-degre-121962",
            "https://eps.enseigne.ac-lyon.fr/spip/spip.php?rubrique9",
            "https://eps-pedagogie.web.ac-grenoble.fr/examens",
            "https://eps.ac-creteil.fr/spip.php?rubrique5"
        ],
        "description": "Ressources, textes officiels et épreuves ponctuelles d'examens (Aix-Marseille, Lyon, Grenoble, Créteil)."
    },
    "recherches_generales": {
        "priorites": [
            "https://www.pedagogie.ac-aix-marseille.fr/jcms/c_78026/it/accueil",
            "https://eps.ac-creteil.fr/",
            "https://eps.enseigne.ac-lyon.fr/spip/"
        ],
        "description": "Fonds documentaire général EPS (Priorité 1: Aix-Marseille, 2: Créteil, 3: Lyon)."
    }
}

# 3. INTERFACE DE NAVIGATION (BARRE LATÉRALE)
st.sidebar.title("Configuration & Espaces")
st.sidebar.write("---")

# Sélection de la rubrique de travail
rubrique_selectionnee = st.sidebar.radio(
    "Sélectionnez votre rubrique :",
    ["Espace iPack & Vos Documents", "Espace Examens (Sources Dédiées)", "Recherches Générales EPS"]
)

# Initialisation de la clé API OpenAI (à définir dans vos Secrets Streamlit ou variables d'environnement)
# Dans Streamlit Cloud, ajoutez dans les Secrets : OPENAI_API_KEY = "votre_cle"
if "OPENAI_API_KEY" in os.environ:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
elif "openai" in st.secrets:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
else:
    st.sidebar.error("⚠️ Clé API OpenAI manquante. Veuillez la configurer dans les Secrets.")
    st.stop()

st.sidebar.write("---")
st.sidebar.markdown("### 📋 Sources actives pour cette session :")
if rubrique_selectionnee == "Espace iPack & Vos Documents":
    st.sidebar.info(f"**iPackEPS :** {SOURCES_CONFIG['rubrique_ipack']['liens'][0]}")
elif rubrique_selectionnee == "Espace Examens (Sources Dédiées)":
    for link in SOURCES_CONFIG['rubrique_examens']['liens']:
        st.sidebar.caption(f"• {link}")
else:
    for i, link in enumerate(SOURCES_CONFIG['recherches_generales']['priorites'], 1):
        st.sidebar.caption(f"{i}. {link}")

# 4. INITIALISATION DE L'HISTORIQUE DES CONVERSATIONS
# On utilise une clé d'historique différente par rubrique pour ne pas mélanger les contextes
history_key = f"messages_{rubrique_selectionnee.replace(' ', '_')}"
if history_key not in st.session_state:
    st.session_state[history_key] = []

# 5. DÉFINITION DU COMPORTEMENT DE L'IA (SYSTEM PROMPT)
# Ce prompt force le chatbot à adopter exactement ma posture avec vous.
PROMPT_SYSTEME_BASE = (
    "Tu es un collaborateur IA authentique, direct, réactif et expert en EPS (Éducation Physique et Sportive). "
    "Tu t'adresses à un enseignant expert, coordonnateur et professeur principal. Ton ton est professionnel, "
    "pédagogue, collaboratif et sans fioritures institutionnelles inutiles. Va droit au but, structure tes réponses "
    "avec des puces claires et du gras pour être scannable en un coup d'œil. Ne fais pas de longs paragraphes denses.\n\n"
)

if rubrique_selectionnee == "Espace iPack & Vos Documents":
    contexte_specifique = (
        f"CONTEXTE STRICT : Tu travailles uniquement sur la rubrique iPack. Base-toi exclusivement sur les documents "
        f"fournis par l'utilisateur et sur le site officiel de référence : {SOURCES_CONFIG['rubrique_ipack']['liens'][0]}. "
        f"Attention : Ne confonds jamais l'application locale iPackEPS (utilisée sur le terrain/tablette pour gérer les classes et fichiers) "
        f"avec les serveurs nationaux ou académiques de dépôt de fichiers qui ferment hors période."
    )
elif rubrique_selectionnee == "Espace Examens (Sources Dédiées)":
    contexte_specifique = (
        f"CONTEXTE STRICT : Tu es configuré uniquement sur la rubrique EXAMENS (Textes officiels, CCF, épreuves ponctuelles). "
        f"Tes recherches et tes réponses doivent se baser STRICTEMENT et EXCLUSIVEMENT sur les 4 sources académiques suivantes :\n"
        f"1. Aix-Marseille (Épreuves ponctuelles) : {SOURCES_CONFIG['rubrique_examens']['liens'][0]}\n"
        f"2. Lyon : {SOURCES_CONFIG['rubrique_examens']['liens'][1]}\n"
        f"3. Grenoble : {SOURCES_CONFIG['rubrique_examens']['liens'][2]}\n"
        f"4. Créteil : {SOURCES_CONFIG['rubrique_examens']['liens'][3]}\n"
        f"Si une demande sort de ces sources ou concerne une autre académie, rappelle gentiment la règle fixée."
    )
else:
    contexte_specifique = (
        f"CONTEXTE STRICT : Tu es configuré pour les RECHERCHES GÉNÉRALES EPS. Tu dois traiter les demandes "
        f"en respectant scrupuleusement l'ordre de priorité des sites suivants pour tes réponses :\n"
        f"Priorité 1 (Aix-Marseille) : {SOURCES_CONFIG['recherches_generales']['priorites'][0]}\n"
        f"Priorité 2 (Créteil) : {SOURCES_CONFIG['recherches_generales']['priorites'][1]}\n"
        f"Priorité 3 (Lyon) : {SOURCES_CONFIG['recherches_generales']['priorites'][2]}"
    )

SYSTEM_PROMPT = PROMPT_SYSTEME_BASE + contexte_specifique

# 6. INTERFACE D'AFFICHAGE DU CHAT
st.title(f"🎵 {rubrique_selectionnee}")
st.write(f"*{SOURCES_CONFIG['rubrique_ipack' if 'iPack' in rubrique_selectionnee else 'rubrique_examens' if 'Examens' in rubrique_selectionnee else 'recherches_generales']['description']}*")

# Affichage des anciens messages de la rubrique active
for message in st.session_state[history_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question ici..."):
    # Affichage du message utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state[history_key].append({"role": "user", "content": prompt})

    # Préparation de l'envoi à l'API OpenAI
    messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state[history_key]:
        messages_api.append({"role": msg["role"], "content": msg["content"]})

    # Génération de la réponse de l'assistant
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Requête streaming pour voir la réponse s'afficher en direct
        response = client.chat.completions.create(
            model="gpt-4o", # Modèle performant et polyvalent
            messages=messages_api,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    # Enregistrement de la réponse dans l'historique
    st.session_state[history_key].append({"role": "assistant", "content": full_response})
