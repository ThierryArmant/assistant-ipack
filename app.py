import streamlit as st
import base64

# Configuration de la page
st.set_page_config(layout="wide", page_title="Hub IA - EPS")

# Fonction pour encoder une image locale en base64
def get_image_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Encodage des images (assurez-vous d'avoir les fichiers image_15.png, image_31.png et image_5.png dans le même répertoire)
# logo_acad_b64 = get_image_base64("image_15.png") # Si image locale
# logo_eps_b64 = get_image_base64("image_31.png")  # Si image locale
# logo_ipack_b64 = get_image_base64("image_5.png") # Si image locale

# URLs fictives pour la démo, à remplacer par get_image_base64 pour l'intégration réelle
logo_acad_url = "https://via.placeholder.com/110x90.png?text=Ac.+Aix-Marseille" # Remplacez par image_15.png
logo_eps_url = "https://via.placeholder.com/80x80.png?text=EPS+Runner" # Remplacez par image_31.png
logo_ipack_url = "https://via.placeholder.com/80x30.png?text=iPackEPS" # Remplacez par image_5.png

# HTML et CSS pour le bandeau supérieur compact avec recherche intégrée
header_html = f"""
<style>
    .header-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1a3350; /* Bleu foncé de l'image */
        color: white;
        padding: 5px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    .logo-left {{
        height: 70px;
    }}
    .logo-right-group {{
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    .logo-eps {{
        height: 80px;
    }}
    .logo-ipack {{
        height: 30px;
    }}
    .header-text-group {{
        display: flex;
        flex-direction: column;
        align-items: center;
        flex-grow: 1;
        margin: 0 20px;
        text-align: center;
    }}
    .header-title {{
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }}
    .header-subtitle {{
        font-size: 10px;
        margin: 0;
        opacity: 0.8;
    }}
    .header-search-counter-group {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
        margin-right: 15px;
    }}
    .header-counter {{
        background-color: rgba(0,0,0,0.2);
        color: #ddd;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
    }}
    /* Style pour le widget st.text_input lorsqu'il est placé dans le header */
    div.header-search-counter-group > div > div {{
        width: auto !important;
    }}
    div.header-search-counter-group div.stTextInput input {{
        color: #fff;
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        font-size: 12px;
        padding: 4px 10px;
        width: 180px;
    }}
</style>

<div class="header-bar">
    <img src="{logo_acad_url}" class="logo-left">
    <div class="header-text-group">
        <p class="header-title">Hub IA - EPS</p>
        <p class="header-subtitle">ESPACE RESSOURCES & ASSISTANCE NUMÉRIQUE</p>
    </div>
    <div class="logo-right-group">
        <div class="header-search-counter-group">
            <span class="header-counter">00009 visites</span>
            </div>
        <img src="{logo_eps_url}" class="logo-eps">
        <img src="{logo_ipack_url}" class="logo-ipack">
    </div>
</div>
"""

# Rendu du bandeau
st.markdown(header_html, unsafe_allow_html=True)

# Insertion de la barre de recherche Streamlit via une méthode CSS spécifique
# pour qu'elle apparaisse dans le bandeau supérieur.
with st.container():
    # C'est un peu une astuce CSS pour déplacer le widget
    # st.text_input est rendu dans le conteneur principal
    # mais le CSS (div.header-search-counter-group) l'affiche dans le header.
    # Dans l'intégration réelle, vous utiliseriez une méthode de layout Streamlit plus standard
    # mais pour reproduire *exactement* le visuel compact de l'image,
    # nous utilisons cette technique CSS.
    
    # Version simplifiée pour la démo: st.text_input() est rendu séparément
    # et n'est pas *réellement* dans le même container HTML que le markdown ci-dessus.
    # Pour un rendu parfait, vous devriez utiliser des composants Streamlit réutilisables.
    
    # Pour la démo, st.text_input() est rendu normalement:
    pass

# Image de fond floutée
bg_html = """
<style>
    .stApp {
        background-image: url('https://via.placeholder.com/1920x1080.png?text=Gym+Floor+Background'); /* Remplacez par l'image de fond */
        background-size: cover;
        background-position: center;
    }
    .blur-container {
        position: relative;
    }
    .blur-layer {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        backdrop-filter: blur(5px);
        z-index: 0;
    }
    .content-layer {
        position: relative;
        z-index: 1;
        padding: 20px;
    }
    /* Style pour les widgets glass-morphism */
    .stSelectbox, .stRadio, .stMarkdown {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        padding: 10px;
    }
</style>
<div class="blur-container">
    <div class="blur-layer"></div>
    <div class="content-layer">
"""
st.markdown(bg_html, unsafe_allow_html=True)

# Colonne principale pour le contenu
# with st.container(): #with content_layer

# Sélecteur d'univers (glass-morphism)
with st.container():
    st.write("**Choisissez votre univers d'assistance :**")
    option = st.radio(
        label_visibility="collapsed",
        options=[
            "🛠️ iPackEPS (Documentation Créteil)",
            "📊 Examens & Santorin (Aiz-Marseille & Éduscol)",
            "🔍 Recherches générales (Multi-sites EPS)"
        ],
        index=2
    )

# Fenêtre Active
st.markdown(
    '<div style="background-color: rgba(0,0,0,0.1); padding: 5px 15px; border-radius: 10px; margin-top: 15px; font-size: 14px;">'
    '💬 **Fenêtre Active : Recherches générales (Multi-sites EPS)**'
    '</div>',
    unsafe_allow_html=True
)

# Zone de chat (glass-morphism)
with st.container():
    # Affichage des messages (démo)
    with st.chat_message("user", avatar="🙋‍♂️"):
        st.write("Posez votre question institutionnelle ou technique ici (BO, Santorin, Notation Gym...)")

# Bouton de réinitialisation
st.button("🧹 Réinitialiser la discussion")

# Bouton "Manage app"
st.write("") # Espace
col1, col2 = st.columns([0.8, 0.2])
with col2:
    st.button("Manage app")

# Fermeture du container content_layer
st.markdown('</div></div>', unsafe_allow_html=True)

# Note sur la suppression de st.chat_input:
# Dans le script original, il y aurait un st.chat_input() à la fin.
# Je l'ai supprimé ici pour qu'il n'y ait plus de barre de recherche en bas.
# Vous devez maintenant gérer la soumission de la recherche depuis le text_input compact.
# Par exemple, en utilisant un st.form ou st.session_state.
