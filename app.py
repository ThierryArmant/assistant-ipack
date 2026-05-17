# ----------------------------------------------------------------------
# 🗂️ CARTOGRAPHIE MULTI-NIVEAUX : DISTINCTION COLLÈGE / LYCÉE
# ----------------------------------------------------------------------
def get_map_video_support(query_text):
    text = query_text.lower()
    fallback_url = "https://eps.ac-creteil.fr/spip.php?rubrique5"
    
    # 1. DÉTERMINATION DU NIVEAU (DÉTECTION AUTOMATIQUE)
    is_lycee = any(w in text for w in ["lycée", "lycee", "2de", "seconde", "1ere", "premiere", "terminale", "lycéen"])
    is_college = any(w in text for w in ["collège", "college", "6eme", "5eme", "4eme", "3eme", "brevet"])
    
    # Si l'utilisateur pose une question générique sans préciser le niveau, on affiche un choix
    if ("section" in text or "classe" in text or "import" in text) and not (is_lycee or is_college):
        return """<div class="video-card" style="background-color: rgba(234, 179, 8, 0.1) !important; border-left: 6px solid #EAB308 !important;">
            <strong>🔍 Précision requise (Collège ou Lycée ?) :</strong><br>
            Pour vous donner le bon parcours fléché, précisez votre niveau dans votre question (ex: <em>"comment importer mes classes en lycée ?"</em> ou <em>"les sections sportives en collège"</em>).
        </div>"""

    # ------------------------------------------------------------------
    # PARCOURS LYCÉE (Basé sur ta nouvelle carte mentale Lycée)
    # ------------------------------------------------------------------
    if is_lycee:
        # Étape 3.4 : Sections Sportives Lycée
        if "section" in text or "sss" in text or "sportive" in text:
            url = "https://www.youtube.com/watch?v=QPhqFI4czhA" # Lien vidéo SSS Lycée
            active_url = url if check_link_status(url) else fallback_url
            return f"""<div class="video-card"><strong>📍 CARTE MENTALE LYCÉE – Étape 3.4 (Sections Sportives) :</strong><br>
                Voici le parcours de configuration spécifique pour les Lycées :<br>
                <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Vidéo SSS Lycée</a><br>
                <small>💡 <em>Rappel Lycée :</em> Pensez à lier le projet annuel SSS avant la validation finale.</small></div>"""
        
        # Étape 3.1 : Configuration Classes et Groupes Lycée
        if "classe" in text or "import" in text or "eleve" in text or "groupe" in text:
            url = "https://www.youtube.com/watch?v=tu8J1RBUTwk"
            active_url = url if check_link_status(url) else fallback_url
            return f"""<div class="video-card"><strong>📍 CARTE MENTALE LYCÉE – Étape 3.1 (Classes &amp; Groupes) :</strong><br>
                Procédure d'importation des divisions de Lycée (STSWEB) :<br>
                <a href="{active_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel Classes Lycée</a></div>"""

        # Étape 3.6 : Dossiers APPN (Spécifique Lycée - Environnement spécifique)
        if "appn" in text or "pleine nature" in text:
            return f"""<div class="video-card"><strong>📍 CARTE MENTALE LYCÉE – Étape 3.6 (Dossiers APPN) :</strong><br>
                Attention, la déclaration en Lycée requiert la validation de l'environnement spécifique.<br>
                <a href="{fallback_url}" target="_blank" style="color:#4F46E5; font-weight:bold; text-decoration:underline;">📄 Consulter la note technique APPN Lycée</a></div>"""

    # ------------------------------------------------------------------
    # PARCOURS COLLÈGE
    # ------------------------------------------------------------------
    if is_college:
        if "section" in text or "sss" in text or "sportive" in text:
            return f"""<div class="video-card" style="background-color: rgba(14, 165, 233, 0.1) !important; border-left: 6px solid #0EA5E9 !important;">
                <strong>📍 CARTE MENTALE COLLÈGE – Étape 3.4 :</strong><br>
                Voici le protocole de reconduction SSS pour les Collèges :<br>
                <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Tutoriel SSS Collège</a></div>"""
                
        if "classe" in text or "import" in text or "eleve" in text or "groupe" in text:
            return f"""<div class="video-card" style="background-color: rgba(14, 165, 233, 0.1) !important; border-left: 6px solid #0EA5E9 !important;">
                <strong>📍 CARTE MENTALE COLLÈGE – Étape 3.1 :</strong><br>
                Synchronisation des classes et des cycles du socle commun (Collège) :<br>
                <a href="{fallback_url}" target="_blank" style="color:#0EA5E9; font-weight:bold; text-decoration:underline;">🎬 Ouvrir le Guide d'importation Collège</a></div>"""

    return ""
