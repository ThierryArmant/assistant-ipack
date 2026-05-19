# Remplace uniquement ton bloc "if prompt:" existant par celui-ci :

if prompt:
    st.session_state.messages_hub.append({"role": "user", "content": prompt})
    
    # Consigne ultra-stricte et isolée
    domaine = "ipackeps.ac-creteil.fr"
    system_instruction = f"""
    Tu es l'expert iPackEPS. Analyser : {prompt}. 
    RÈGLE ABSOLUE : Utilise EXCLUSIVEMENT le site {domaine}.
    JAMAIS de logistique, palettes ou colis.
    Tu DOIS rédiger un tutoriel PAS-À-PAS numéroté (Étape 1, Étape 2...) très précis.
    Si l'étape n'est pas sur le site, dis que tu ne peux pas l'inventer.
    """

    with st.spinner("Analyse approfondie..."):
        try:
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": st.secrets["TAVILY_API_KEY"],
                "query": prompt,
                "include_domains": [domaine],
                "search_depth": "advanced"
            })
            raw_data = "\n".join([r['content'] for r in res.json().get("results", [])])
            
            Settings.llm = OpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])
            response = Settings.llm.complete(system_instruction + "\n\nSources: " + raw_data)
            
            st.session_state.messages_hub.append({"role": "assistant", "content": response.text})
        except Exception:
            st.session_state.messages_hub.append({"role": "assistant", "content": "Erreur de connexion."})
    st.rerun()
