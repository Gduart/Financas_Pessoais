# pages/3_Metas.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # Usaremos o graph_objects para o gráfico de Gauge

# --- Configuração da Página ---
st.set_page_config(
    page_title="Metas de Gastos",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Acompanhamento de Metas de Gastos")
st.markdown("---")

# --- Validação e Recuperação de Dados do st.session_state ---
# Verifica se os dados de despesas existem para fazer os cálculos.
if 'df_despesas' not in st.session_state or st.session_state.df_despesas.empty:
    st.warning("Nenhuma despesa encontrada. Por favor, selecione um período com dados na página principal.")
    st.stop()

# Recupera o DataFrame de despesas
df_despesas = st.session_state['df_despesas']
total_gasto_periodo = df_despesas['valor'].sum()

# --- Definição da Meta de Gastos ---
st.header("Defina sua Meta")

# Campo para o usuário inserir a meta. O valor padrão é 6400, como solicitado.
meta_gastos = st.number_input(
    "Defina sua meta máxima de gastos para o período selecionado (R$):",
    min_value=0.0,
    value=6000.0,
    step=100.0,
    format="%.2f"
)

# --- Cálculos de Progresso ---
if meta_gastos > 0:
    percentual_atingido = (total_gasto_periodo / meta_gastos) * 100
    valor_restante = meta_gastos - total_gasto_periodo
else:
    percentual_atingido = 0
    valor_restante = 0

# --- Visualização com Gráfico de Gauge e KPIs ---
st.markdown("---")
st.header("Progresso da Meta")

# Layout para o gráfico e os KPIs
col1, col2 = st.columns([2, 1.5])  # A primeira coluna é maior para o gráfico

with col1:
    # Gráfico de Gauge do Plotly
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_gasto_periodo,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Progresso de Gastos", 'font': {'size': 24}},
        delta={'reference': meta_gastos, 'increasing': {'color': "#FF4136"}},  # Vermelho se passar da meta
        gauge={
            'axis': {'range': [None, meta_gastos], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#1DB954"},  # Cor da barra de progresso
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_gastos * 0.5], 'color': 'lightgreen'},  # Até 50%
                {'range': [meta_gastos * 0.5, meta_gastos * 0.8], 'color': 'yellow'},  # Até 80%
                {'range': [meta_gastos * 0.8, meta_gastos], 'color': 'orange'}  # Acima de 80%
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meta_gastos
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.subheader("Análise da Meta")
    st.metric(label="Total Gasto no Período", value=f"R$ {total_gasto_periodo:,.2f}")

    if valor_restante >= 0:
        st.metric(
            label="Valor Restante para Atingir a Meta",
            value=f"R$ {valor_restante:,.2f}",
            delta=f"-{100 - percentual_atingido:,.2f}% do orçamento restante",
            delta_color="normal"
        )
        st.success(f"Você está dentro do orçamento! Já utilizou {percentual_atingido:,.2f}% da sua meta.")
    else:
        st.metric(
            label="Valor Acima da Meta",
            value=f"R$ {abs(valor_restante):,.2f}",
            delta=f"{percentual_atingido - 100:,.2f}% acima do orçamento",
            delta_color="inverse"
        )
        st.error(f"Atenção! Você ultrapassou a sua meta em {abs(valor_restante):,.2f} reais.")