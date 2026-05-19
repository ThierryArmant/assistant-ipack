# --- CHARGEMENT DYNAMIQUE ET UNIVERSEL (SANTORIN & EXAMENS) ---
@st.cache_resource
def get_separated_engines_v6():
    index_santorin = VectorStoreIndex.from_documents([])
    documents_list = []
    
    dossier_data = "./data"
    if os.path.exists(dossier_data):
        # 1. On liste tous les fichiers du dossier
        for fichier in os.listdir(dossier_data):
            nom_minuscule = fichier.lower()
            chemin_complet = os.path.join(dossier_data, fichier)
            
            # Cible : les fichiers qui contiennent "santorin" ou "examen"
            if "santorin" in nom_minuscule or "examen" in nom_minuscule:
                
                # 📊 CAS A : C'est un fichier Excel (.xlsx ou .xls)
                if fichier.endswith(('.xlsx', '.xls')):
                    try:
                        # xl = pd.ExcelFile(chemin_complet) lira TOUTES les feuilles du fichier excel
                        xl = pd.ExcelFile(chemin_complet)
                        for sheet_name in xl.sheet_names:
                            df = xl.parse(sheet_name)
                            for idx, row in df.iterrows():
                                texte_ligne = f"[Feuille: {sheet_name}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                                documents_list.append(Document(text=texte_ligne))
                    except Exception as e:
                        st.error(f"Erreur Excel ({fichier}) : {str(e)}")
                        
                # 📊 CAS B : C'est un fichier CSV (.csv)
                elif fichier.endswith('.csv'):
                    try:
                        # Lecture robuste avec séparateur point-virgule
                        df = pd.read_csv(chemin_complet, sep=";", encoding="utf-8", on_bad_lines='skip')
                        for idx, row in df.iterrows():
                            texte_ligne = f"[Fichier: {fichier}] " + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                            documents_list.append(Document(text=texte_ligne))
                    except Exception as e:
                        st.error(f"Erreur CSV ({fichier}) : {str(e)}")

        # S'il y a des documents trouvés, on crée l'index global pour l'IA
        if documents_list:
            index_santorin = VectorStoreIndex.from_documents(documents_list)
        
    # 🛠️ MOTEUR IPACKEPS : Chargement des PDF de cartes mentales
    index_ipack = VectorStoreIndex.from_documents([])
    if os.path.exists(dossier_data):
        ipack_files = [os.path.join(dossier_data, f) for f in os.listdir(dossier_data) if "ipack" in f.lower() and f.endswith(".pdf")]
        if ipack_files:
            try:
                docs_i = SimpleDirectoryReader(input_files=ipack_files).load_data()
                index_ipack = VectorStoreIndex.from_documents(docs_i)
            except Exception as e:
                st.error(f"Erreur iPack PDF : {str(e)}")
    
    return index_ipack, index_santorin

# Ligne d'activation à mettre à jour juste en dessous de la fonction
if openai_api_key:
    index_ipack, index_santorin = get_separated_engines_v6()
