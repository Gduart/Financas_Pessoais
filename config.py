# config.py
import os
from dotenv import load_dotenv
import streamlit as st

# Carrega as variáveis do arquivo .env para o ambiente (útil para outros fins, pode manter)
load_dotenv()

# Acessa as variáveis de segredo do Streamlit usando a sintaxe de dicionário (colchetes)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError as e:
    st.error(f"Erro: A chave secreta {e} não foi encontrada!")
    st.error("Verifique se você criou o arquivo .streamlit/secrets.toml para rodar localmente ou se configurou os segredos no Streamlit Cloud.")
    st.stop()