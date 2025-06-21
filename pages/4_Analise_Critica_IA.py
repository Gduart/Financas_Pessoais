# pages/4_Analise_Critica_IA.py

# ==============================================================================
# VERSÃO 4.0 - PROMPT APRIMORADO
# - Adicionada análise de categorias de gastos históricos.
# - Prompt da IA atualizado para fornecer insights mais profundos e menos genéricos,
#   correlacionando picos de previsão com as principais categorias de despesas.
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io
import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prophet import Prophet
from config import OPENAI_API_KEY
from datetime import datetime


# --- FUNÇÃO AUXILIAR PARA CARREGAR AS FONTES ---
def add_dejavu_fonts(pdf_instance):
    font_dir = os.path.join(os.getcwd(), 'static', 'fonts')

    if not os.path.isdir(font_dir):
        st.error(f"ERRO CRÍTICO: Diretório de fontes não encontrado: {font_dir}")
        return False

    font_map = {
        '': 'DejaVuSans.ttf',
        'B': 'DejaVuSans-Bold.ttf',
        'I': 'DejaVuSans-Oblique.ttf',
        'BI': 'DejaVuSans-BoldOblique.ttf'
    }

    all_fonts_found = True
    for style, filename in font_map.items():
        font_file_path = os.path.join(font_dir, filename)
        if os.path.exists(font_file_path):
            pdf_instance.add_font('DejaVu', style, font_file_path)
        else:
            st.error(f"ARQUIVO DE FONTE ESSENCIAL NÃO ENCONTRADO: {font_file_path}")
            all_fonts_found = False

    return all_fonts_found


# --- FUNÇÃO DE PDF COM CORREÇÃO FINAL ---
def gerar_pdf_completo(titulo, texto_analise, chart=None, table=None):
    pdf = FPDF()

    if not add_dejavu_fonts(pdf):
        st.error("Geração do PDF cancelada: falha ao carregar fontes customizadas.")
        return None

    pdf.add_page()

    pdf.set_font('DejaVu', 'B', 16)
    pdf.multi_cell(0, 10, titulo, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # A análise de texto agora é tratada de forma mais robusta para UTF-8
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 8, texto_analise)
    pdf.ln(10)

    if chart:
        try:
            pdf.add_page()
            pdf.set_font('DejaVu', "B", 12)
            pdf.cell(0, 10, "Gráfico da Análise", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            img_bytes = io.BytesIO()
            chart.write_image(img_bytes, format="png", width=900, height=400, scale=2)
            img_bytes.seek(0)
            pdf.image(img_bytes, x=10, w=190)
        except Exception as e:
            pdf.set_text_color(255, 0, 0)
            pdf.multi_cell(0, 10,
                           f"ATENÇÃO: Erro ao renderizar o gráfico. Verifique se 'kaleido' está instalado. Erro: {e}")
            pdf.set_text_color(0, 0, 0)

    if table is not None and not table.empty:
        pdf.add_page()
        pdf.set_font('DejaVu', "B", 12)
        pdf.cell(0, 10, "Dados Detalhados da Previsão", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        df_table_str = table.copy().rename(
            columns={'ds': 'Data', 'yhat': 'Previsao_R', 'yhat_lower': 'Minimo_R', 'yhat_upper': 'Maximo_R'})
        df_table_str['Data'] = df_table_str['Data'].dt.strftime('%d/%m/%Y')

        col_widths = {'Data': 35, 'Previsao_R': 45, 'Minimo_R': 50, 'Maximo_R': 55}
        header = ['Data', 'Previsao_R', 'Minimo_R', 'Maximo_R']

        pdf.set_font('DejaVu', 'B', 9)
        for col_name in header:
            pdf.cell(col_widths.get(col_name, 40), 10, col_name.replace('_', ' '), border=1, align='C')
        pdf.ln()

        pdf.set_font('DejaVu', '', 8)
        for _, row in df_table_str.iterrows():
            pdf.cell(col_widths['Data'], 10, str(row['Data']), border=1, align='C')
            pdf.cell(col_widths['Previsao_R'], 10, f"R$ {row['Previsao_R']:,.2f}", border=1, align='R')
            pdf.cell(col_widths['Minimo_R'], 10, f"R$ {row['Minimo_R']:,.2f}", border=1, align='R')
            pdf.cell(col_widths['Maximo_R'], 10, f"R$ {row['Maximo_R']:,.2f}", border=1, align='R', new_x=XPos.LMARGIN,
                     new_y=YPos.NEXT)

    return bytes(pdf.output())


# --- O RESTANTE DO CÓDIGO PERMANECE IDÊNTICO ATÉ O BOTÃO ---

st.set_page_config(page_title="Análise com IA", page_icon="🤖", layout="wide")
st.title("🤖 Análise Avançada com Inteligência Artificial")
st.markdown("---")


@st.cache_resource
def get_llm():
    return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4.1-mini", temperature=0.3, max_tokens=2000)


llm = get_llm()
st.header("Análise Preditiva de Gastos")

if 'df_completo' not in st.session_state:
    try:
        from db_manager import carregar_dados

        st.session_state.df_completo = carregar_dados()
    except ImportError:
        st.error("Arquivo 'db_manager.py' não encontrado.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")
        st.stop()

if 'df_completo' not in st.session_state or st.session_state.df_completo.empty:
    st.error("Falha ao carregar dados. Verifique a conexão com o banco de dados.")
    st.stop()

df_despesas_completo = st.session_state.df_completo[st.session_state.df_completo['TipoMov'] == 'Cx.Out'].copy()
df_despesas_completo['Dia'] = pd.to_datetime(df_despesas_completo['Dia'])
dias_para_prever = st.slider("Selecione quantos dias você quer prever no futuro:", 30, 365, 90, key="dias_predicao")

if st.button("Gerar Análise Preditiva Completa", type="primary", use_container_width=True):
    with st.spinner("Analisando seu histórico e construindo a previsão... Isso pode levar um minuto."):
        df_preditivo = df_despesas_completo[['Dia', 'valor']].rename(columns={'Dia': 'ds', 'valor': 'y'})
        df_preditivo_diario = df_preditivo.groupby('ds').sum().reset_index()

        if len(df_preditivo_diario) < 10:
            st.error(
                "Histórico de dados insuficiente para uma previsão confiável. São necessários pelo menos 10 dias de gastos registrados.")
        else:
            modelo = Prophet(daily_seasonality=True)
            modelo.add_country_holidays(country_name='BR')
            modelo.fit(df_preditivo_diario)
            futuro = modelo.make_future_dataframe(periods=dias_para_prever)
            previsao = modelo.predict(futuro)

            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_upper'], fill=None, mode='lines',
                                          line_color='rgba(0,176,246,0.2)', name='Máximo Previsto'))
            fig_pred.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_lower'], fill='tonexty', mode='lines',
                                          line_color='rgba(0,176,246,0.2)', name='Mínimo Previsto'))
            fig_pred.add_trace(
                go.Scatter(x=previsao['ds'], y=previsao['yhat'], mode='lines', line=dict(color='cyan', width=3),
                           name='Previsão'))
            fig_pred.add_trace(go.Scatter(x=df_preditivo_diario['ds'], y=df_preditivo_diario['y'], mode='markers',
                                          marker=dict(color='yellow', size=5), name='Gastos Reais'))
            fig_pred.update_layout(title_text="Projeção de Gastos Futuros vs. Histórico", xaxis_title="Data",
                                   yaxis_title="Valor Gasto (R$)",
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

            st.session_state.analise_pred_fig = fig_pred
            df_previsao_tabela = previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(dias_para_prever)
            st.session_state.analise_pred_tabela = df_previsao_tabela

            if 'analise_pred_texto' in st.session_state:
                del st.session_state['analise_pred_texto']

            with st.spinner("IA parceira gerando a análise explicativa dos resultados..."):
                try:
                    # ==================================================================
                    # NOVA SEÇÃO: ANÁLISE DE CATEGORIAS PARA ENRIQUECER O PROMPT
                    # ==================================================================
                    # Verifica se a coluna 'Categoria' existe no dataframe.
                    # Adapte 'Categoria' para o nome real da sua coluna.
                    if 'Categoria' in df_despesas_completo.columns:
                        top_categorias = df_despesas_completo.groupby('Categoria')['valor'].sum().nlargest(5)
                        analise_historica_categorias = "\n\nAnálise do Histórico de Gastos por Categoria:\n"
                        analise_historica_categorias += "As 5 categorias com maiores gastos no seu histórico foram:\n"
                        for categoria, total in top_categorias.items():
                            analise_historica_categorias += f"- {categoria}: Total de R$ {total:,.2f}\n"
                    else:
                        analise_historica_categorias = "\n\n(Não foi possível analisar as categorias pois a coluna 'Categoria' não foi encontrada no histórico de dados.)"

                    total_previsto = df_previsao_tabela['yhat'].sum()

                    # ==================================================================
                    # PROMPT ATUALIZADO E MAIS ROBUSTO
                    # ==================================================================
                    contexto_preditivo = (
                        f"Você é um analista financeiro sênior, especialista em finanças pessoais e análise de dados. Sua tarefa é criar um relatório detalhado e acionável para um usuário.\n\n"
                        f"**DADOS PARA ANÁLISE:**\n"
                        f"1.  **Previsão de Gastos:** A previsão para os próximos {dias_para_prever} dias indica um gasto total de aproximadamente **R$ {total_previsto:,.2f}**. O usuário está vendo um gráfico com a projeção diária, os picos e os vales.\n"
                        f"2.  **Contexto Histórico:** {analise_historica_categorias}\n\n"
                        f"**SUA TAREFA (siga esta estrutura rigorosamente):**\n\n"
                        f"### **1. Resumo Executivo da Projeção**\n"
                        f"Comece com um parágrafo claro e direto sobre o que o valor total previsto significa para o planejamento financeiro do usuário no período.\n\n"
                        f"### **2. Análise Detalhada dos Picos de Gastos**\n"
                        f"Identifique no gráfico de previsão as semanas ou dias específicos com os maiores picos de despesas. Usando a análise do histórico de categorias, **faça uma inferência educada sobre QUAIS CATEGORIAS provavelmente estão causando esses picos**. Por exemplo: 'O pico na primeira semana do mês provavelmente está ligado a despesas de 'Aluguel' e 'Contas', que são suas maiores categorias de gasto'. Seja específico.\n\n"
                        f"### **3. Tendências e Padrões Ocultos**\n"
                        f"Além dos picos óbvios, identifique padrões mais sutis. Os gastos aumentam em dias de semana específicos? Há uma queda consistente nos fins de semana? Existe alguma tendência geral de aumento ou diminuição dos gastos ao longo do período? Comente sobre a volatilidade da previsão (a distância entre o mínimo e o máximo previsto).\n\n"
                        f"### **4. Recomendações Estratégicas e Acionáveis**\n"
                        f"Com base em TUDO o que foi analisado (picos, categorias, tendências), forneça pelo menos 3 recomendações práticas e personalizadas. Não dê conselhos genéricos. Por exemplo:\n"
                        f"- 'Para a categoria de **{top_categorias.index[0]}**, que é sua maior despesa, sugiro revisar X ou Y para reduzir o impacto no pico da semana Z.'\n"
                        f"- 'Dado que seus gastos caem nos fins de semana, considere criar um 'desafio de economia' nesses dias para potencializar ainda mais essa tendência.'\n\n"
                        f"Use uma linguagem profissional, mas encorajadora. O objetivo é dar ao usuário clareza, controle e insights que ele não conseguiria ver sozinho."
                    )

                    chain = get_llm() | StrOutputParser()
                    st.session_state.analise_pred_texto = chain.invoke(contexto_preditivo)

                except Exception as e:
                    st.session_state.analise_pred_texto = None
                    st.error(
                        f"Ocorreu um erro ao gerar a análise de texto com a IA. Verifique sua chave de API ou tente novamente. Detalhe do Erro: {e}")

# --- O código de exibição dos resultados permanece o mesmo ---
if 'analise_pred_fig' in st.session_state:
    st.markdown("### Gráfico da Previsão")
    st.plotly_chart(st.session_state.analise_pred_fig, use_container_width=True)

if 'analise_pred_texto' in st.session_state and st.session_state.analise_pred_texto:
    st.markdown("### Análise Explicativa da IA")
    st.markdown(st.session_state.analise_pred_texto)
    if 'analise_pred_tabela' in st.session_state:
        st.markdown("### Detalhes da Previsão")
        df_para_exibir = st.session_state.analise_pred_tabela.copy()
        df_para_exibir = df_para_exibir.rename(
            columns={'ds': 'Data', 'yhat': 'Previsão (R$)', 'yhat_lower': 'Mínimo Estimado (R$)',
                     'yhat_upper': 'Máximo Estimado (R$)'})
        st.dataframe(df_para_exibir.style.format(
            {'Previsão (R$)': "R$ {:,.2f}", 'Mínimo Estimado (R$)': "R$ {:,.2f}", 'Máximo Estimado (R$)': "R$ {:,.2f}",
             'Data': '{:%d/%m/%Y}'}))

if 'analise_pred_fig' in st.session_state:
    st.markdown("---")
    st.subheader("📥 Baixar Relatório Completo")

    pdf_bytes = gerar_pdf_completo("Relatório de Análise Preditiva de Gastos",
                                   st.session_state.get('analise_pred_texto', "A análise textual não pôde ser gerada."),
                                   chart=st.session_state.analise_pred_fig, table=st.session_state.analise_pred_tabela)

    if pdf_bytes:
        st.download_button(label="Gerar Relatório em PDF", data=pdf_bytes,
                           file_name=f"Relatorio_Preditivo_GDUART_{datetime.now().strftime('%Y%m%d')}.pdf",
                           mime="application/pdf", use_container_width=True)
    else:
        st.error(
            "O botão de download não foi renderizado porque a geração do arquivo PDF falhou. Verifique os erros de carregamento de fonte acima.")