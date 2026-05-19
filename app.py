import streamlit as st
import os
import pandas as pd
import requests
import urllib.parse
import re
from bs4 import BeautifulSoup
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import Document

# ======================================================================
# 1. CONFIGURATION DE L'APPLICATION (IMPÉRATIVEMENT EN PREMIER)
# ======================================================================
st.set_page_config(
    page_title="Hub IA - EPS", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ======================================================================
# 2. GESTION DE LA MÉMOIRE ET DU COMPTEUR DE VISITES
# ======================================================================
if "messages_ipack" not in st.session_state:
    st.session_state.messages_ipack = []
if "messages_aix" not in st.session_state:
    st.session_state.messages_aix = []

def incrementer_et_recuperer_compteur():
    fichier_compteur = "compteur.txt"
    if not os.path.exists(fichier_compteur):
        with open(fichier_compteur, "w", encoding="utf-8") as f: 
            f.write("0")
            
    with open(fichier_compteur, "r", encoding="utf-8") as f:
        try: 
            total_visites = int(f.read().strip())
        except ValueError: 
            total_visites = 0
            
    if "visite_comptabilisee" not in st.session_state:
        total_visites += 1
        st.session_state.visite_comptabilisee = True
        with open(fichier_compteur, "w", encoding="utf-8") as f: 
            f.write(str(total_visites))
            
    return total_visites

nb_visites = incrementer_et_recuperer_compteur()

# ======================================================================
# 3. INTERFACE GRAPHIQUE ET FEUILLES DE STYLE (15% TRANSPARENCE ACCENTUÉE)
# ======================================================================
img_gauche, img_droite, img_fond = "image_7.png", "image_5.png", "image_8.png"    
github_url = f"https://raw.githubusercontent.com/{st.secrets.get('GITHUB_USERNAME')}/{st.secrets.get('GITHUB_REPO')}/main/"

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }}
    .stApp {{ background-image: url('{github_url}{img_fond}') !important; background-size: cover !important; background-attachment: fixed !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    
    .hub-header {{ background-color: #1E293B; display: flex; justify-content: space-between; align-items: center; padding: 12px 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }}
    .hub-title h1 {{ color: white !important; margin: 0; font-size: 22px; font-weight: bold; }}
    .hub-title p {{ color: #94A3B8 !important; margin: 0; font-size: 11px; text-transform: uppercase; }}
    .visitor-badge {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 14px; border-radius: 20px; font-size: 11px; font-weight: bold; font-family: monospace; margin-top: 8px; display: inline-block; }}
    
    .column-title {{ color: #FFFFFF; font-size: 15px; font-weight: 700; text-align: center; margin-bottom: 0px; height: 35px; background-color: #1E293B; border-radius: 8px 8px 0px 0px; padding: 6px 0; }}
    .stButton>button {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #94A3B8 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 20px !important; font-size: 11px !important; }}
    
    div[data-testid="stRadio"] {{
        background-color: #1E293B !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: inset 0px 2px 4px rgba(0,0,0,0.3) !important;
        margin-bottom: 15px !important;
    }}
    div[data-testid="stRadio"] label p {{ color: #FFFFFF !important; font-weight: 600 !important; font-size: 13px !important; }}
    
    /* 🖼️ Conteneurs principaux (Transparence à 15% pour voir la Sainte-Victoire) */
    .glass-card {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border-radius: 0px 0px 8px 8px;
        padding: 18px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
        border-left: 1px solid rgba(255, 255, 255, 0.15);
        border-right: 1px solid rgba(255, 255, 255, 0.15);
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 20px;
    }}
    .glass-card > p, .glass-card label:not(div[data-testid="stRadio"] label) {{ color: #FFFFFF !important; font-weight: 700 !important; }}
    
    /* 🏔️ Cartes des réponses IA translucides à 20% (Disparition complète des blocs opaques) */
    .santorin-card, .general-card {{ 
        background-color: rgba(255, 255, 255, 0.20) !important; 
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        padding: 16px; 
        border-radius: 4px; 
        margin-bottom: 18px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.25); 
    }}
    .santorin-card {{ border-left: 6px solid #DC2626 !important; }}
    .general-card {{ border-left: 6px solid #10B981 !important; }}
    
    /* Forçage de lisibilité blanc sur transparent */
    .santorin-card *, .general-card * {{ color: #FFFFFF !important; }}
    .santorin-card a, .general-card a {{ color: #38BDF8 !important; text-decoration: underline !important; font-weight: bold; }}
    
    /* Tableaux Markdown transparents */
    .santorin-card table, .general-card table {{ background-color: rgba(30, 41, 59, 0.5) !important; color: #FFFFFF !important; border-collapse: collapse; width: 100%; margin-top: 10px; }}
    .santorin-card th, .general-card th {{ background-color: rgba(30, 41, 59, 0.8) !important; color: #FFFFFF !important; padding: 8px !important; font-weight: bold !important; border: 1px solid rgba(255,255,255,0.2) !important; }}
    .santorin-card td, .general-card td {{ padding: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #FFFFFF !important; }}
    
    /* Zone de dialogue utilisateur */
    div[data-testid="stChatMessage"] {{ background-color: transparent !important; border: none !important; padding: 12px 16px !important; margin-bottom: 12px !important; }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(6px) !important;
        border-radius: 16px 16px 0px 16px !important; 
        margin-left: 10% !important; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1); 
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p {{ color: #FFFFFF !important; }}
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ======================================================================
# 4. CONFIGURATION DE L'INTELLIGENCE ARTIFICIELLE
# ======================================================================
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.0, api_key=openai_api_key)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=openai_api_key)

# bandeau titre
st.markdown(f"""
    <div class="hub-header">
        <div style="width: 150px; text-align: left;"><img src="{github_url}{img_gauche}" width="110"></div>
        <div class="hub-title" style="text-align: center; flex-grow: 1;">
            <h1>Hub IA - EPS</h1><p>Espace Ressources &amp; Assistance Numérique</p>
            <div class="visitor-badge">👁️ {nb_visites:05d} visites</div>
        </div>
        <div style="width: 150px; text-align: right;"><img src="{github_url}{img_droite}" width="75"></div>
    </div>
""", unsafe_allow_html=True)

# ======================================================================
# 5. MOTEURS D'INDEXATION DES DOCUMENTS LOCAUX (IPACK & SANTORIN)
# ======================================================================
@st.cache_resource
def get_separated_engines_final():
    index_santorin = VectorStoreIndex.from_documents([])
    documents_list = []
    base_dir = "./data"
    
    if os.path.exists(base_dir):
        for fichier in os.listdir(base_dir):
            nom_f = fichier.lower()
            chemin = os.path.join(base_dir, fichier)
            if "santorin" in nom_f or "notation" in nom_f:
                if nom_f.endswith('.csv'):
                    try:
                        df = pd.read_csv(chemin, sep=";", encoding="utf-8", on_bad_lines='skip')
                        for idx, row in df.iterrows():
                            texte_ligne = f"[Source: {fichier}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                            documents_list.append(Document(text=texte_ligne))
                    except:
                        pass
                else:
                    try:
                        xl = pd.ExcelFile(chemin)
                        for sheet_name in xl.sheet_names:
                            df = xl.parse(sheet_name)
                            for idx, row in df.iterrows():
                                texte_ligne = f"[Onglet: {sheet_name}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                                documents_list.append(Document(text=texte_ligne))
                    except:
                        pass
        if documents_list:
            index_santorin = VectorStoreIndex.from_documents(documents_list)
        
    index_ipack = VectorStoreIndex.from_documents([])
    if os.path.exists(base_dir):
        fichiers_ipack = []
        for f in os.listdir(base_dir):
            nom_f = f.lower()
            if "ipack" in nom_f and not nom_f.endswith('.csv') and "santorin" not in nom_f:
                fichiers_ipack.append(os.path.join(base_dir, f))
        if fichiers_ipack:
            try:
                docs_i = SimpleDirectoryReader(input_files=fichiers_ipack).load_data()
                index_ipack = VectorStoreIndex.from_documents(docs_i)
            except:
                pass
                
    return index_ipack, index_santorin

if openai_api_key:
    index_ipack, index_santorin = get_separated_engines_final()

# ======================================================================
# 6. EXÉCUTION DOUBLE COLONNE INDÉPENDANTE
# ======================================================================
col1, col2 = st.columns(2, gap="large")

# --- COLONNE 1 : ASSISTANT MÉTIER (IPACK / EXAMENS) ---
with col1:
    st.markdown('<div class="column-title">🤖 Assistant Métier EPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nettoyer le chat", key="clear_ipack"):
        st.session_state.messages_ipack = []
        st.rerun()
        
    context_choice = st.radio(
        "Sur quel module travaillez-vous ?", 
        ["🛠️ iPackEPS (Configuration, Classes, SSS)", "📊 Examens & Santorin (Notes, Absences, Dispenses)"]
    )

    for m in st.session_state.messages_ipack:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_ipack := st.chat_input("Votre question (iPack, Santorin...) ?", key="input_ipack"):
        st.session_state.messages_ipack.append({"role": "user", "content": f"**Vous** : {prompt_ipack}"})
        
        with st.spinner("Analyse des fichiers..."):
            if "examens" in context_choice.lower():
                system_prompt = (
                    "Tu es l'assistant expert EXAMENS & SANTORIN pour les professeurs d'EPS.\n"
                    "Tu traites STRICTEMENT de la réglementation des examens (DNB, BAC, CAP) et de la remontée des notes.\n\n"
                    "⚠️ CONSIGNE ABSOLUE SUR L'INTENTION DE SANTÉ :\n"
                    "Si l'utilisateur pose une question relative à un certificat médical, une dispense ou une inaptitude, "
                    "tu dois l'analyser SOUS L'ANGLE DE L'EXAMEN (Le Certificatif).\n"
                    "Format de réponse obligatoire : Présente TOUJOURS tes résultats sous la forme d'un tableau Markdown comparatif "
                    "détaillant le protocole précis pour chaque niveau (Collège DNB, Lycée GT Bac, Lycée Pro, etc.)."
                )
                chosen_index = index_santorin
            else:
                system_prompt = (
                    "Tu es l'assistant informatique et technique exclusif du logiciel de saisie iPackEPS.\n"
                    "Ton unique rôle est d'expliquer comment configurer et manipuler l'application.\n\n"
                    "⚠️ CLOISONNEMENT STRICT : Reste purement technique, pas-à-pas (clics, menus, onglets). "
                    "Interdiction de parler des examens nationaux ou de Santorin."
                )
                chosen_index = index_ipack
            
            chat_engine = chosen_index.as_chat_engine(
                chat_mode="context", 
                memory=ChatMemoryBuffer.from_defaults(token_limit=4000), 
                system_prompt=system_prompt
            )
            response_locale = chat_engine.chat(prompt_ipack)
            answer = response_locale.response

        if "examens" in context_choice.lower():
            formatted_answer = f'<div class="santorin-card"><strong>📊 SYNTHÈSE CERTIFICATION :</strong><br><br>{answer}</div>'
        else:
            formatted_answer = f'<div class="general-card"><strong>🛠️ PROTOCOLE TECHNIQUE IPACKEPS :</strong><br><br>{answer}</div>'

        st.session_state.messages_ipack.append({"role": "assistant", "content": formatted_answer})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLONNE 2 : ASSISTANT RECHERCHES SITES ACADÉMIQUES PROFONDES ---
with col2:
    st.markdown('<div class="column-title">🔍 Assistant Recherches Site EPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("🧹 Nouveau chat (Site)", key="clear_aix"):
        st.session_state.messages_aix = []
        st.rerun()
        
    for m in st.session_state.messages_aix:
        with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)
            
    if prompt_aix := st.chat_input("Votre recherche officielle...", key="input_aix"):
        st.session_state.messages_aix.append({"role": "user", "content": f"**Vous** : {prompt_aix}"})
        
        with st.spinner("Recherche et lecture approfondie des directives académiques..."):
            # Requête ciblée restreinte aux 4 portails académiques officiels
            terme_recherche = f"{prompt_aix} (site:pedagogie.ac-aix-marseille.fr OR site:eduscol.education.gouv.fr OR site:eps.enseigne.ac-lyon.fr OR site:eps.ac-creteil.fr)"
            url_moteur = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(terme_recherche)}"
            
            contenu_profond = ""
            liens_trouves = []
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            try:
                res_moteur = requests.get(url_moteur, headers=headers, timeout=6)
                if res_moteur.status_code == 200:
                    soup_moteur = BeautifulSoup(res_moteur.text, "html.parser")
                    # On extrait les 3 premiers vrais liens profonds des résultats
                    blocs_liens = soup_moteur.find_all("a", class_="result__url")[:3]
                    for b in blocs_liens:
                        href = b.get("href")
                        if href and "duckduckgo" not in href:
                            # Extraction de la vraie URL propre
                            vraie_url = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get('uddg', [None])[0]
                            if vraie_url:
                                liens_trouves.append(vraie_url)
                            else:
                                liens_trouves.append(href)
            except:
                pass

            # 🚀 LE CORRECTIF : On va lire le CONTENU RÉEL de ces liens profonds en direct
            if liens_trouves:
                for url in liens_trouves:
                    try:
                        res_page = requests.get(url, headers=headers, timeout=5)
                        if res_page.status_code == 200:
                            soup_page = BeautifulSoup(res_page.text, "html.parser")
                            # Nettoyage des balises inutiles pour isoler le texte de la circulaire
                            for tag in soup_page(["script", "style", "nav", "footer", "header"]):
                                tag.extract()
                            
                            # On ne prend que les paragraphes significatifs pour ne pas surcharger l'IA
                            paragraphes = [p.get_text().strip() for p in soup_page.find_all(["p", "li", "td"]) if len(p.get_text().strip()) > 40]
                            texte_page = " ".join(paragraphes[:15]) # Analyse des 15 premiers blocs de texte profonds
                            contenu_profond += f"\n--- CONTENU DE LA PAGE ({url}) ---\n{texte_page}\n"
                    except:
                        pass

            # Formulation de l'instruction finale pour le modèle de langage
            if contenu_profond.strip():
                consigne_analyse = f"""
                Tu es l'assistant expert des textes officiels et protocoles EPS de l'Éducation Nationale.
                Tu dois répondre de façon claire, structurée et exhaustive à la demande de l'enseignant.
                
                Voici le texte extrait des documents profonds trouvés sur les sites officiels :
                {contenu_profond}
                
                Question de l'enseignant : '{prompt_aix}'
                
                Rédige une synthèse immédiate du protocole ou de la directive trouvée (par exemple s'il s'agit du protocole TASA ou d'une fiche d'évaluation). 
                À la fin de ta réponse, ajoute explicitement les liens internet consultés sous cette forme Markdown pour permettre au collègue de télécharger les PDF d'origine :
                - [Lien vers la ressource officielle](adresse_url)
                """
            else:
                consigne_analyse = f"Tu es l'assistant expert des textes officiels EPS. Réponds au mieux de tes connaissances sur : '{prompt_aix}' car les serveurs académiques profonds n'ont pas renvoyé de texte lisible."

            response_web = Settings.llm.complete(consigne_analyse)
            answer_aix = f"""<div class="general-card"><strong>🌐 DOSSIER RÉGLEMENTAIRE ET LIENS :</strong><br><br>{response_web.text}</div>"""
                
        st.session_state.messages_aix.append({"role": "assistant", "content": answer_aix})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
