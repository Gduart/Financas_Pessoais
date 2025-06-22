# pages/3_Metas.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Metas de Gastos",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Acompanhamento de Metas de Gastos")
st.markdown("---")

# --- Validação e Recuperação de Dados do st.session_state ---
if 'df_despesas' not in st.session_state or st.session_state.df_despesas.empty:
    st.warning("Nenhuma despesa encontrada. Por favor, selecione um período com dados na página principal para análise.")
    st.stop()

df_despesas = st.session_state['df_despesas']
total_gasto_periodo = df_despesas['valor'].sum()

# --- Definição da Meta de Gastos ---
st.header("Defina sua Meta")
meta_gastos = st.number_input(
    "Defina sua meta máxima de gastos para o período selecionado (R$):",
    min_value=0.01,  # Evita divisão por zero
    value=6000.0,
    step=100.0,
    format="%.2f"
)

# --- Cálculos de Progresso ---
# CORREÇÃO: Garantindo que não haja divisão por zero
percentual_atingido = (total_gasto_periodo / meta_gastos) * 100 if meta_gastos > 0 else 0
valor_restante = meta_gastos - total_gasto_periodo

# --- Visualização com Gráfico de Gauge e KPIs ---
st.markdown("---")
st.header("Progresso da Meta")

col1, col2 = st.columns([2, 1.5])

with col1:
    # CORREÇÃO: Simplificação do Gauge para maior clareza e consistência
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_gasto_periodo,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Progresso de Gastos (R$)", 'font': {'size': 20}},
        number={'prefix': "R$ ", 'font': {'size': 48}},
        delta={
            'reference': meta_gastos,
            'increasing': {'color': "#d62728"}, # Vermelho forte quando ultrapassa
            'decreasing': {'color': "#2ca02c"}  # Verde quando está abaixo
        },
        gauge={
            'axis': {'range': [0, meta_gastos], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#1f77b4"},  # Azul padrão, mais neutro
            'bgcolor': "rgba(0,0,0,0.1)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_gastos * 0.75], 'color': 'green'},
                {'range': [meta_gastos * 0.75, meta_gastos * 0.9], 'color': 'yellow'},
                {'range': [meta_gastos * 0.9, meta_gastos], 'color': 'orange'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.9,
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
    st.metric(
        label="Total Gasto no Período",
        value=f"R$ {total_gasto_periodo:,.2f}"
    )

    # CORREÇÃO: Lógica de UX clara e sem contradições
    if valor_restante >= 0:
        st.metric(
            label="Valor Restante para Atingir a Meta",
            value=f"R$ {valor_restante:,.2f}"
            # O delta aqui foi removido por ser confuso. O valor principal já passa a informação.
        )
        # Mensagem de sucesso, consistente com a situação.
        st.success(f"Você está dentro do orçamento! Já utilizou {percentual_atingido:.2f}% da sua meta.")
    else:
        # A lógica para quando a meta é ultrapassada
        st.metric(
            label="Valor ACIMA da Meta",
            value=f"R$ {abs(valor_restante):,.2f}",
            delta=f"{(percentual_atingido - 100):.2f}% acima do orçamento",
            delta_color="inverse" # "inverse" mostra vermelho para valores positivos (ruim neste caso)
        )
        # Mensagem de erro, consistente com a situação.
        st.error(f"Atenção! Você ultrapassou sua meta em R$ {abs(valor_restante):,.2f}.")
    #versao3