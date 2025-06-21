# Financas_Pessoais.py
#streamlit run Financas_Pessoais.py
import streamlit as st
import pandas as pd
from db_manager import carregar_dados, carregar_dados_cartao
from datetime import datetime

st.set_page_config(
    page_title="Finanças Pessoais GDUART",
    page_icon="💰",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>FINANÇAS PESSOAIS GDUART 💰</h1>", unsafe_allow_html=True)
st.markdown("---")

df = carregar_dados()

if df.empty:
    st.error("Falha ao carregar dados.")
    st.stop()

st.sidebar.header("Filtros 🔎")

if 'data_inicio' not in st.session_state:
    st.session_state.data_inicio = df['Dia'].min().date()
if 'data_fim' not in st.session_state:
    st.session_state.data_fim = df['Dia'].max().date()

data_inicio = st.sidebar.date_input('Início', value=st.session_state.data_inicio)
data_fim = st.sidebar.date_input('Fim', value=st.session_state.data_fim)

st.session_state.data_inicio = data_inicio
st.session_state.data_fim = data_fim

categorias_disponiveis = sorted(df['Categoria'].unique().tolist())
fpagam_disponiveis = sorted(df['F.Pagam'].unique().tolist())
tipodespesa_disponiveis = sorted(df['TipoDespesa'].dropna().unique().tolist())

categorias_selecionadas = st.sidebar.multiselect("Categoria", categorias_disponiveis, default=categorias_disponiveis)
fpagam_selecionadas = st.sidebar.multiselect("Forma de Pagamento", fpagam_disponiveis, default=fpagam_disponiveis)
tipodespesa_selecionadas = st.sidebar.multiselect("Tipo de Despesa", tipodespesa_disponiveis, default=tipodespesa_disponiveis)

data_inicio_dt = pd.to_datetime(st.session_state.data_inicio)
data_fim_dt = pd.to_datetime(st.session_state.data_fim)

df_filtrado = df[
    (df['Dia'].between(data_inicio_dt, data_fim_dt)) &
    (df['Categoria'].isin(categorias_selecionadas)) &
    (df['F.Pagam'].isin(fpagam_selecionadas)) &
    (df['TipoDespesa'].isin(tipodespesa_selecionadas))
]

df_despesas = df_filtrado[df_filtrado['TipoMov'] == 'Cx.Out'].copy()
df_receitas = df_filtrado[df_filtrado['TipoMov'] == 'Cx.In'].copy()

st.session_state['df_completo'] = df
st.session_state['df_filtrado'] = df_filtrado
st.session_state['df_despesas'] = df_despesas
st.session_state['df_receitas'] = df_receitas

st.header("Resumo do Período Selecionado")

total_gasto = df_despesas['valor'].sum()
total_recebido = df_receitas['valor'].sum()
user_id_fixo = "b3373108-fd8c-4670-8d4c-11b095a3f803"
dados_cartao = carregar_dados_cartao(user_id=user_id_fixo)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Gasto no Período", f"R$ {total_gasto:,.2f}")
with col2:
    st.metric("Recebido no Período", f"R$ {total_recebido:,.2f}")
if dados_cartao:
    gasto_cartao = dados_cartao.get('total_debitos_periodo', 0)
    saldo_cartao = dados_cartao.get('saldo_final_calculado', 0)
    with col3:
        st.metric(label="Gasto Cartão", value=f"R$ {gasto_cartao:,.2f}")
    with col4:
        st.metric(label="Saldo Cartão", value=f"R$ {saldo_cartao:,.2f}")
else:
    with col3:
        st.metric(label="Gasto Cartão", value="N/A")
    with col4:
        st.metric(label="Saldo Cartão", value="N/A")

if not df_despesas.empty:
    gasto_por_categoria = df_despesas.groupby('Categoria')['valor'].sum().sort_values(ascending=False)
    if not gasto_por_categoria.empty:
        principal_categoria_nome = gasto_por_categoria.index[0]
        principal_categoria_valor = gasto_por_categoria.iloc[0]
        st.info(f"Principal Categoria de Gasto: **{principal_categoria_nome}** (R$ {principal_categoria_valor:,.2f})")
else:
    st.info("Nenhuma despesa registrada no período selecionado.")

st.markdown("### Detalhes das Transações do Período")
st.dataframe(df_filtrado)

#streamlit run Financas_Pessoais.py