# utils.py
from fpdf import FPDF
import pandas as pd
import os
import io


def gerar_pdf(texto_analise: str):
    """
    Gera um arquivo PDF simples a partir de uma string de texto, usando o padrão UTF-8
    e garantindo que a saída seja do tipo 'bytes'. (Função original para compatibilidade).

    Args:
        texto_analise (str): O conteúdo da análise a ser inserido no PDF.

    Returns:
        bytes: O conteúdo do PDF no formato 'bytes', compatível com st.download_button.
    """
    pdf = FPDF()
    pdf.add_page()

    script_dir = os.path.dirname(__file__)
    try:
        font_path = os.path.join(script_dir, 'fontes', 'DejaVuSansCondensed.ttf')
        pdf.add_font('DejaVu', '', font_path)
        pdf.set_font('DejaVu', '', 12)
    except FileNotFoundError:
        # Fallback para fonte padrão caso a customizada não seja encontrada
        pdf.set_font('Arial', '', 12)

    pdf.set_font_size(16)
    pdf.cell(0, 10, 'Relatório de Análise Financeira', ln=True, align='C')
    pdf.ln(10)

    pdf.set_font_size(12)
    # A codificação para 'latin-1' com 'replace' é uma forma de evitar erros com caracteres não suportados pela fonte padrão
    texto_formatado = texto_analise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texto_formatado)

    return bytes(pdf.output())


def gerar_pdf_avancado(titulo: str, texto_analise: str, figura_bytes: io.BytesIO = None, tabela: pd.DataFrame = None):
    """
    Gera um relatório PDF completo com título, texto, um gráfico e uma tabela de dados.

    Args:
        titulo (str): Título do relatório.
        texto_analise (str): Parágrafo introdutório ou de análise.
        figura_bytes (io.BytesIO, optional): Imagem do gráfico já em formato de bytes.
        tabela (pd.DataFrame, optional): DataFrame com os dados a serem exibidos em tabela.

    Returns:
        bytes: O conteúdo do PDF no formato 'bytes'.
    """
    pdf = FPDF()
    pdf.add_page()

    script_dir = os.path.dirname(__file__)
    try:
        font_path = os.path.join(script_dir, 'fontes', 'DejaVuSansCondensed.ttf')
        pdf.add_font('DejaVu', '', font_path)
        pdf.set_font('DejaVu', '', 10)
    except Exception:
        pdf.set_font('Arial', '', 10)

    # Título
    pdf.set_font_size(16)
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.ln(5)

    # Texto de Análise
    pdf.set_font_size(11)
    texto_formatado = texto_analise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, texto_formatado)
    pdf.ln(5)

    # Gráfico
    if figura_bytes:
        pdf.add_page()
        pdf.set_font_size(12)
        pdf.cell(0, 10, "Gráfico da Análise Preditiva", ln=True, align='L')
        pdf.ln(5)
        # Largura da imagem no PDF (190mm para uma página A4 com margens de 10mm)
        pdf.image(figura_bytes, x=10, w=190)
        pdf.ln(5)

    # Tabela
    if tabela is not None and not tabela.empty:
        pdf.add_page()
        pdf.set_font_size(12)
        pdf.cell(0, 10, "Dados Detalhados da Previsão", ln=True, align='L')
        pdf.ln(5)

        pdf.set_font_size(9)
        pdf.set_fill_color(224, 235, 255)  # Cor de fundo para o cabeçalho

        # Renomeia colunas para o relatório
        tabela_pdf = tabela.rename(columns={
            'ds': 'Data',
            'yhat': 'Previsao (R$)',
            'yhat_lower': 'Minimo (R$)',
            'yhat_upper': 'Maximo (R$)'
        })

        # Define a largura das colunas
        col_widths = {'Data': 35, 'Previsao (R$)': 45, 'Minimo (R$)': 50, 'Maximo (R$)': 55}
        header = list(tabela_pdf.columns)

        # Cabeçalho da tabela
        for col_name in header:
            pdf.cell(col_widths.get(col_name, 40), 7, col_name, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # Dados da tabela
        pdf.set_font_size(8)
        pdf.set_fill_color(255, 255, 255)
        fill = False
        for _, row in tabela_pdf.iterrows():
            pdf.cell(col_widths['Data'], 6, row['Data'].strftime('%d/%m/%Y'), border=1, ln=0, align='C', fill=fill)
            pdf.cell(col_widths['Previsao (R$)'], 6, f"{row['Previsao (R$)']:.2f}", border=1, ln=0, align='R',
                     fill=fill)
            pdf.cell(col_widths['Minimo (R$)'], 6, f"{row['Minimo (R$)']:.2f}", border=1, ln=0, align='R', fill=fill)
            pdf.cell(col_widths['Maximo (R$)'], 6, f"{row['Maximo (R$)']:.2f}", border=1, ln=0, align='R', fill=fill)
            pdf.ln()
            fill = not fill

    return bytes(pdf.output())