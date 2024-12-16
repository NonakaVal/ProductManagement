import streamlit as st
import pandas as pd
import os


# Mapeamento de extensões de arquivo para funções de carregamento do pandas
# Mapeamento de extensões de arquivo para funções de carregamento do pandas
file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}


def load_data(uploaded_file, sheet_name, header=0):
    """
    Carrega o arquivo e retorna um DataFrame do Pandas, com opções específicas para planilhas do Excel.
    """
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()  # Extrai a extensão do arquivo
    except:
        ext = uploaded_file.split(".")[-1]  # Em caso de erro, extrai pela string do nome

    # Verifica se o formato é suportado
    if ext in file_formats:
        if ext in ['xls', 'xlsx', 'xlsm', 'xlsb']:
            # Para planilhas Excel, carrega a aba específica e ignora as primeiras 5 linhas
            return pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header)
        else:
            return file_formats[ext](uploaded_file)  # Para outros formatos, usa o mapeamento padrão
    else:
        st.error(f"Formato de arquivo não suportado: {ext}")
        return None
