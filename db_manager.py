# db_manager.py
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Inicializa a conexão com o Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- FUNÇÃO ORIGINAL (sem alterações) ---
@st.cache_data(ttl=600)
def carregar_dados():
    """Busca todos os registros da tabela 'registros1' e converte para DataFrame."""
    try:
        response = supabase.table("registros1").select("*").execute()
        df = pd.DataFrame(response.data)
        df['Dia'] = pd.to_datetime(df['Dia'])
        df['valor'] = pd.to_numeric(df['valor'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados principais: {e}")
        return pd.DataFrame()


# --- FUNÇÃO PARA OS DADOS DO CARTÃO (VERSÃO FINAL E CORRETA) ---
@st.cache_data(ttl=3600)
def carregar_dados_cartao(user_id: str):
    """Busca os dados do cartão para um usuário específico."""
    if not user_id:
        return None
    try:
        # CORREÇÃO FINAL: Filtra a tabela pelo 'user_id' fornecido, em vez de tentar ordenar.
        response = supabase.table("DebitoCartao").select("*").eq('user_id', user_id).execute()

        # .eq() retorna uma lista, então pegamos o primeiro (e único) item.
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar dados do cartão: {e}")
        return None