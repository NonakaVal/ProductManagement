
# import streamlit as st
# from Utils.LoadDataFrame import load_and_process_data
# from Utils.Selectors import select_items_to_ad
# from Utils.GoogleSheetManager import GoogleSheetManager
# from Utils.LabelCreator import create_labels_from_dataframe_with_barcode


# ##############################################################################################
# # Inicializar a conexão com o Google Sheets
# ##############################################################################################

# st.write("#### Tabela de Consulta de Produtos")
# # Em algum lugar no seu código
# data = load_and_process_data()

# select = select_items_to_ad(data)


# st.dataframe(data)


# st.dataframe(select)

from Utils.Selectors import select_items_to_ad
import streamlit as st

import os
import io
from PIL import Image, ImageDraw, ImageFont
import qrcode
from barcode.codex import Code128
from barcode.writer import ImageWriter
from fpdf import FPDF
import tempfile

import streamlit as st

from Utils.LoadDataFrame import load_and_process_data
from Utils.Selectors import select_items_to_ad



##############################################################################################
# Inicializar a conexão com o Google Sheets
##############################################################################################

st.write("#### Tabela de Consulta de Produtos")
# Em algum lugar no seu código
data = load_and_process_data()

# Função mock para carregar dados (substitua com sua função real)
# def load_and_process_data():
#     # Dados fictícios para teste
#     data = {
#         'name': ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5'],
#         'qr_code_link': ['https://example.com/1', 'https://example.com/2', 'https://example.com/3', 'https://example.com/4', 'https://example.com/5'],
#         'price': [10.99, 12.49, 8.99, 15.49, 9.99],
#         'sku': ['12345', '12346', '12347', '12348', '12349'],
#         'universal_code': ['98765', '98766', '98767', '98768', '98769'],
#         'ad_code': ['A001', 'A002', 'A003', 'A004', 'A005'],
#         'condition': ['Novo', 'Novo', 'Usado', 'Novo', 'Usado']
#     }
#     return pd.DataFrame(data)

# Classe PDF customizada
class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_page()

    def add_label(self, img_buffer, x, y, width, height):
        if self.page_no() == 0:
            self.add_page()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
            img_buffer.seek(0)
            temp.write(img_buffer.read())
            temp.flush()
        self.image(temp.name, x, y, width, height)
        os.unlink(temp.name)

# Função para salvar etiquetas como PDF
def save_labels_as_pdf(labels):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        label_width = 65
        label_height = 45
        labels_per_row = int(210 / label_width)
        labels_per_column = int(297 / label_height)

        for index, label in enumerate(labels):
            if index % (labels_per_row * labels_per_column) == 0 and index != 0:
                pdf.add_page()

            row = index % labels_per_column
            col = index // labels_per_column

            x = (col % labels_per_row) * label_width
            y = row * label_height

            buffer = io.BytesIO()
            label.save(buffer, format='PNG')
            pdf.add_label(buffer, x, y, label_width, label_height)

        pdf.output(temp_file.name)
        return temp_file.name  # Retornar o caminho para o arquivo temporário

# Funções de geração de etiquetas e códigos
class CustomImageWriter(ImageWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = False  # Desabilitar texto no código de barras

def generate_barcode(code_text):
    writer = CustomImageWriter()
    code = Code128(code_text, writer=writer)
    buffer = io.BytesIO()
    code.write(buffer)
    buffer.seek(0)
    return buffer

def crop_barcode_image(barcode_img, crop_percentage_top=0.1, crop_percentage_bottom=0.4):
    img = Image.open(barcode_img)
    width, height = img.size
    top = int(height * crop_percentage_top)
    bottom = int(height * (1 - crop_percentage_bottom))
    return img.crop((0, top, width, bottom))

def generate_qr_code(link):
    img = qrcode.make(link)
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return buffer

# Função para criar uma única etiqueta
def create_single_label(name, qr_code_link, price, sku, ad_code,  config):
    label_width, label_height = 738, 551
    label = Image.new('RGB', (label_width, label_height), 'white')
    draw = ImageDraw.Draw(label)

    fonts = {}
    try:
        fonts['name'] = ImageFont.truetype("arial.ttf", config['name_font_size'])
        fonts['price'] = ImageFont.truetype("arial.ttf", config['price_font_size'])
        fonts['small'] = ImageFont.truetype("arial.ttf", config['small_font_size'])
    except IOError:
        fonts['name'] = ImageFont.load_default()
        fonts['price'] = ImageFont.load_default()
        fonts['small'] = ImageFont.load_default()

    # Adiciona texto
    draw.text((config['name_x'], config['name_y']), name, font=fonts['name'], fill='black')
    
    # Adiciona QR Code
    qr_code_img = Image.open(generate_qr_code(qr_code_link)).resize((config['qr_code_size'], config['qr_code_size']))
    label.paste(qr_code_img, (config['qr_code_x'], config['qr_code_y']))
    
    # Adiciona preço
    draw.text((config['price_x'], config['price_y']), f"{price}", font=fonts['price'], fill='black')

    # Adiciona SKUs e códigos
    text_lines = [
        f"SKU: {sku}",
        f"ID: {ad_code}"

    ]
    for i, line in enumerate(text_lines):
        draw.text((config['sku_x'], config['sku_y'] + i * config['sku_spacing']), line, font=fonts['small'], fill='black')

    # Adiciona código de barras
    barcode_img = generate_barcode(sku)
    cropped_barcode_img = crop_barcode_image(barcode_img).resize((config['barcode_width'], config['barcode_height']))
    label.paste(cropped_barcode_img, (config['barcode_x'], label_height - config['barcode_height'] - config['barcode_bottom_padding']))

    return label


# Função para criar etiquetas a partir do dataframe 'data'
def create_labels_from_dataframe(data, config):
    labels = []
    for index, row in data.iterrows():
        name = row.get('TITLE', '')
        qr_code_link = row.get('URL', '')
        price = row.get('MSHOPS_PRICE', '')
        sku = row.get('SKU', '')
        ad_code = row.get('ITEM_ID', '')


        label_image = create_single_label(name, qr_code_link, price, sku, ad_code, config)
        labels.append(label_image)

    return labels

# Interface do Streamlit
st.markdown('Baixe a tabela com o botão de download e carregue o arquivo CSV.')




def create_qrcode_labels():


    # Selecionar itens
    
    df = select_items_to_ad(data, key=2)
    df = df[['TITLE', 'URL', 'MSHOPS_PRICE', 'SKU', 'ITEM_ID']]

# Configuração de layout das etiquetas
    config = {
        'name_x': 90,
        'name_y': 110,
        'qr_code_x': 60,
        'qr_code_y': 160,
        'qr_code_size': 260,
        'price_x': 320,
        'price_y': 190,
        'sku_x': 320,
        'sku_y': 240,
        'sku_spacing': 45,
        'barcode_x': 50,
        'barcode_width': 650,
        'barcode_height': 80,
        'barcode_bottom_padding': 20,
        'name_font_size': 28,
        'price_font_size': 35,
        'small_font_size': 30,
        'margin_top': 80,
        'margin_bottom': 80,
        'margin_left': 40,
        'margin_right': 15,
        'spacing_horizontal': 90,
        'spacing_vertical': 10
    }
    
    if st.button("Gerar PDF e Baixar", key=3):
        if df.empty:
            st.warning("Por favor, selecione pelo menos um item!")
        else:
            # Gera as etiquetas a partir do dataframe
            labels = create_labels_from_dataframe(df, config)
            
            # Salva as etiquetas como PDF
            pdf_path = save_labels_as_pdf(labels)
            
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_file,
                    file_name="etiquetas_barcode_33_a4.pdf",
                    mime="application/pdf"
                )

