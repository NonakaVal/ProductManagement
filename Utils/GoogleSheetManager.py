import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit as st

conn = st.connection("gsheets", type=GSheetsConnection)

def update_worksheet(df, worksheet_title, key, url, button_text="Enviar lista"):
    if st.button(button_text, key=key):
        # url = st.secrets["url"]
        conn.update(spreadsheet=url, worksheet=worksheet_title, data=df)
        st.success("Tabela Atualizada com sucesso 🤓")
    
class GoogleSheetManager:
    def __init__(self, connection_type="gsheets"):
        self.conn = st.connection(connection_type, type=GSheetsConnection)
        self.spreadsheets = {}  # Dicionário para armazenar URLs e suas worksheets

    def set_url(self, url):
        """Define a URL de uma planilha e inicializa suas worksheets."""
        if url not in self.spreadsheets:
            self.spreadsheets[url] = []  # Cria uma lista para armazenar as worksheets

    def add_worksheet(self, url, worksheet_name):
        """Adiciona uma nova worksheet à planilha especificada pela URL."""
        if url in self.spreadsheets:
            self.spreadsheets[url].append(worksheet_name)
        else:
            st.error("URL não encontrada. Adicione a URL primeiro.")

    def read_sheet(self, url, worksheet):
        """Lê dados de uma worksheet específica de uma URL."""
        if url in self.spreadsheets and worksheet in self.spreadsheets[url]:
            data = self.conn.read(spreadsheet=url, worksheet=worksheet)
            return data.copy()
        else:
            st.error("Worksheet não encontrada para esta URL.")
            return None
            
    def update_sheet(self, url, worksheet, data):
        """Atualiza uma worksheet específica de uma URL."""
        if url in self.spreadsheets and worksheet in self.spreadsheets[url]:
            self.conn.update(spreadsheet=url, worksheet=worksheet, data=data)
            st.success("Worksheet Atualizada 🤓")
        else:
            st.error("Worksheet não encontrada para esta URL.")


