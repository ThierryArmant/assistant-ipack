if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    with st.spinner("Analyse approfondie..."):
        # 🚀 CONSIGNES IA EXPERTES - VERROUILLÉES
        if st.session_state.active_module == "ipack":
            # On force le domaine et on interdit toute digression logistique
            domaine = "ipackeps.ac-creteil.fr"
            consigne = f"""
            Tu es l'assistant technique officiel pour iPackEPS (ac-creteil.fr).
            1. CONTEXTE : Tu es un outil de l'Éducation Nationale. JAMAIS tu ne parles de palettes, de logistique ou de colis.
            2. SOURCE : Tu puises tes informations EXCLUSIVEMENT dans les résultats de recherche venant de {domaine}.
            3. FORMAT : Rédige TOUJOURS un tutoriel PAS-À-PAS numéroté et détaillé (Étape 1, Étape 2...).
            4. VÉRIFICATION : Si l'information technique exacte (boutons, menus) n'est pas présente dans les données sources, ne l'invente pas, dis-le clairement.
            
            Analyse ces données : {{extraits_doc}}
            Réponds à la question : {prompt}
            """
        else:
            consigne = f"Analyse : {{extraits_doc}}. Rédige une synthèse structurée. URL à la fin. Question : {prompt}"

        # Exécution Tavily + LLM
        res = requests.post("https://api.tavily.com/search", json={
            "api_key": st.secrets["TAVILY_API_KEY"],
            "query": prompt + " iPackEPS Créteil",
            "include_domains": ["ipackeps.ac-creteil.fr"] if st.session_state.active_module == "ipack" else None,
            "search_depth": "advanced"
        })
        raw_data = "\n".join([r['content'] for r in res.json().get("results", [])])
        
        # Appel final
        final_consigne = consigne.replace("{extraits_doc}", raw_data)
        resp = Settings.llm.complete(final_consigne)
        
        st.session_state.messages_hub.append({"role": "assistant", "content": resp.text})
    st.rerun()
