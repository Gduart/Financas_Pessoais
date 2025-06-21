# pages/2_Central_do_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_manager import carregar_dados
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Central do Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central do Dashboard")
st.markdown("---")

# --- Validação e Recuperação de Dados do st.session_state ---
# A base para toda a página: os dados de despesas filtrados na página principal.
if 'df_despesas' not in st.session_state or st.session_state.df_despesas.empty:
    st.warning("Nenhuma despesa encontrada para o período e filtros selecionados na página principal.")
    st.stop()

df_despesas = st.session_state['df_despesas'].copy()

# --- Visualização 1: Análise de Despesas por Categoria ---
st.header("Visão Geral das Despesas por Categoria")

with st.container(border=True):
    col1, col2 = st.columns(2)

    # Preparação dos dados para esta seção
    gastos_por_categoria = df_despesas.groupby('Categoria')['valor'].sum().sort_values(ascending=False).reset_index()

    with col1:
        # Gráfico de Rosca (Plotly Express)
        st.subheader("Distribuição Percentual")
        fig_pie = px.pie(
            gastos_por_categoria,
            values='valor',
            names='Categoria',
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Gráfico de Barras Horizontais (Plotly Express)
        st.subheader("Ranking de Gastos")
        fig_bar = px.bar(
            gastos_por_categoria,
            x='valor',
            y='Categoria',
            orientation='h',
            text_auto='.2s'
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        fig_bar.update_traces(textposition='outside', marker_color='#1DB954')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabela 2: Resumo Agregado de Despesas por Categoria
    st.subheader("Resumo Agregado por Categoria")
    resumo_agregado = df_despesas.groupby('Categoria')['valor'].agg(['sum', 'mean', 'count']).rename(
        columns={'sum': 'Soma Total', 'mean': 'Gasto Médio', 'count': 'Nº de Transações'}
    ).sort_values(by='Soma Total', ascending=False)
    st.dataframe(resumo_agregado.style.format({
        'Soma Total': 'R${:,.2f}',
        'Gasto Médio': 'R${:,.2f}'
    }), use_container_width=True)

# --- Visualização 2: Tendência de Gastos ao Longo do Tempo ---
st.markdown("---")
st.header("Tendência de Gastos ao Longo do Tempo")

with st.container(border=True):
    # Prepara os dados com uma coluna 'Mes_Ano'
    df_despesas['Mes_Ano'] = df_despesas['Dia'].dt.to_period('M').astype(str)

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de Linha do total de gastos mensais
        st.subheader("Total de Despesas Mensais")
        gastos_mensais = df_despesas.groupby('Mes_Ano')['valor'].sum().reset_index()
        fig_line = px.line(
            gastos_mensais.sort_values('Mes_Ano'),
            x='Mes_Ano',
            y='valor',
            title='Evolução do Gasto Total',
            labels={'valor': 'Valor Total (R$)', 'Mes_Ano': 'Mês'},
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        # Gráfico de Área Empilhada por Categoria
        st.subheader("Composição Mensal das Despesas")
        gastos_mensais_categoria = df_despesas.groupby(['Mes_Ano', 'Categoria'])['valor'].sum().reset_index()
        fig_area_stack = px.area(
            gastos_mensais_categoria.sort_values('Mes_Ano'),
            x='Mes_Ano',
            y='valor',
            color='Categoria',
            title='Composição dos Gastos por Categoria',
            labels={'valor': 'Valor Total (R$)', 'Mes_Ano': 'Mês'}
        )
        st.plotly_chart(fig_area_stack, use_container_width=True)

# --- Visualização 3: Comparativo Fixo vs. Variável ---
st.markdown("---")
st.header("Análise de Despesas Fixas vs. Variáveis")

with st.container(border=True):
    # Prepara os dados agrupando por mês e Tipo de Despesa
    df_fixo_variavel = df_despesas.groupby(['Mes_Ano', 'TipoDespesa'])['valor'].sum().reset_index()

    st.subheader("Comparativo Mensal")
    fig_fv_bar = px.bar(
        df_fixo_variavel,
        x='Mes_Ano',
        y='valor',
        color='TipoDespesa',
        title='Despesas Fixas vs. Variáveis por Mês',
        labels={'valor': 'Valor Total (R$)', 'Mes_Ano': 'Mês', 'TipoDespesa': 'Tipo de Despesa'},
        barmode='stack'  # Empilha as barras
    )
    st.plotly_chart(fig_fv_bar, use_container_width=True)

# --- Visualização 4: Distribuição de Valores por Tipo de Pagamento ---
st.markdown("---")
st.header("Análise por Forma de Pagamento")

with st.container(border=True):
    st.subheader("Composição dos Gastos")
    # Treemap para Tipo de Pagamento e Categoria
    fig_treemap = px.treemap(
        df_despesas,
        path=[px.Constant("Todos os Gastos"), 'F.Pagam', 'Categoria'],  # Hierarquia: Forma de Pagamento -> Categoria
        values='valor',
        title='Distribuição por Forma de Pagamento e Categoria'
    )
    fig_treemap.update_traces(root_color="lightgrey")
    fig_treemap.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig_treemap, use_container_width=True)

# --- SEÇÃO FINAL: Análise Comparativa de Períodos (CÓDIGO MANTIDO) ---
st.markdown("---")
st.header("Análise Comparativa de Períodos")

with st.expander("Clique aqui para selecionar os períodos e comparar", expanded=False):
    df_completo = carregar_dados()
    df_despesas_completo = df_completo[df_completo['TipoMov'] == 'Cx.Out'].copy()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Período A")
        pa_inicio = st.date_input("Início A", value=datetime(2025, 4, 1), key="pa_inicio")
        pa_fim = st.date_input("Fim A", value=datetime(2025, 4, 30), key="pa_fim")
    with col_b:
        st.subheader("Período B")
        pb_inicio = st.date_input("Início B", value=datetime(2025, 5, 1), key="pb_inicio")
        pb_fim = st.date_input("Fim B", value=datetime(2025, 5, 31), key="pb_fim")

    if st.button("Comparar Períodos"):
        df_pa = df_despesas_completo[
            df_despesas_completo['Dia'].between(pd.to_datetime(pa_inicio), pd.to_datetime(pa_fim))]
        df_pb = df_despesas_completo[
            df_despesas_completo['Dia'].between(pd.to_datetime(pb_inicio), pd.to_datetime(pb_fim))]

        gastos_pa = df_pa.groupby('Categoria')['valor'].sum().rename("Gasto Período A")
        gastos_pb = df_pb.groupby('Categoria')['valor'].sum().rename("Gasto Período B")

        df_merged = pd.merge(gastos_pa, gastos_pb, on='Categoria', how='outer').fillna(0)
        df_merged['Variacao Absoluta'] = df_merged['Gasto Período B'] - df_merged['Gasto Período A']
        df_merged['Variacao Percentual'] = (df_merged['Variacao Absoluta'] / df_merged['Gasto Período A'].replace(0,
                                                                                                                  pd.NA)) * 100
        df_merged = df_merged[(df_merged['Gasto Período A'] > 0) | (df_merged['Gasto Período B'] > 0)]

        if df_merged.empty:
            st.warning("Nenhuma despesa encontrada para comparação.")
        else:
            st.subheader("Tabela Comparativa Detalhada")
            st.dataframe(df_merged.style.format({
                'Gasto Período A': 'R${:,.2f}', 'Gasto Período B': 'R${:,.2f}',
                'Variacao Absoluta': 'R${:,.2f}', 'Variacao Percentual': '{:,.2f}%'
            }).background_gradient(cmap='RdYlGn_r', subset=['Variacao Absoluta']), use_container_width=True)

            st.subheader("Variação de Gastos por Categoria (Período B vs. A)")
            df_variacao = df_merged[df_merged['Variacao Absoluta'] != 0].reset_index()

            if not df_variacao.empty:
                fig_variacao = px.bar(
                    df_variacao, x='Variacao Absoluta', y='Categoria', orientation='h',
                    title='Aumento/Redução de Gastos por Categoria', text='Variacao Absoluta',
                    labels={'Variacao Absoluta': 'Variação em Reais (R$)', 'Categoria': 'Categoria'}
                )
                fig_variacao.update_traces(texttemplate='R$%{text:,.2f}', textposition='outside')
                fig_variacao.update_layout(yaxis={'categoryorder': 'total ascending'}, title_x=0.5)
                st.plotly_chart(fig_variacao, use_container_width=True)
            else:
                st.info("Não houve variação de gastos entre os períodos selecionados.")