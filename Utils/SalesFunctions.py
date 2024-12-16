import streamlit as st
import pandas as pd
import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
from barcode.codex import Code128
from barcode.writer import ImageWriter
from fpdf import FPDF
import tempfile
from Utils.LoadDataFrame import load_and_process_data
from Utils.Selectors import select_items_to_ad
from Utils.GoogleSheetManager import GoogleSheetManager
from Utils.LabelCreator import create_labels_from_dataframe_with_barcode

# Função para carregar e processar os dados
data = load_and_process_data()

# Definindo a classe PDF com correção de erro
class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_page()  # Certifique-se de que uma página seja adicionada no início

    def add_label(self, img_buffer, x, y, width, height):
        # Verifique se a página está aberta e, se necessário, adicione uma nova página
        if self.page_no() == 0:
            self.add_page()  # Adiciona a página se não houver página aberta
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
            img_buffer.seek(0)
            temp.write(img_buffer.read())
            temp.flush()
        self.image(temp.name, x, y, width, height)
        os.unlink(temp.name)

# Função para salvar as etiquetas em um arquivo PDF
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
                pdf.add_page()  # Adiciona uma nova página se necessário

            row = index % labels_per_column
            col = index // labels_per_column

            x = (col % labels_per_row) * label_width
            y = row * label_height

            buffer = BytesIO()
            label.save(buffer, format='PNG')
            pdf.add_label(buffer, x, y, label_width, label_height)

        pdf.output(temp_file.name)
        return temp_file.name  # Retorna o caminho do arquivo PDF gerado

# Classe personalizada para gerar código de barras sem o texto numérico
class CustomImageWriter(ImageWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = False  # Desativa o texto no código de barras

# Função para gerar código de barras
def generate_barcode(code_text):
    writer = CustomImageWriter()
    code = Code128(code_text, writer=writer)
    buffer = BytesIO()
    code.write(buffer)
    buffer.seek(0)
    return buffer

# Função para cortar a imagem do código de barras
def crop_barcode_image(barcode_img, crop_percentage_top=0.1, crop_percentage_bottom=0.4):
    img = Image.open(barcode_img)
    width, height = img.size
    top = int(height * crop_percentage_top)
    bottom = int(height * (1 - crop_percentage_bottom))
    return img.crop((0, top, width, bottom))

# Função para gerar QR Code
def generate_qr_code(link):
    img = qrcode.make(link)
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return buffer

# Função para criar uma única etiqueta
def create_single_label(name, qr_code_link, price, sku, universal_code, ad_code, condition, config):
    label_width, label_height = 738, 551
    label = Image.new('RGB', (label_width, label_height), 'white')
    draw = ImageDraw.Draw(label)

    # Tentando carregar as fontes
    fonts = {}
    try:
        fonts['name'] = ImageFont.truetype("arial.ttf", config['name_font_size'])
        fonts['price'] = ImageFont.truetype("arial.ttf", config['price_font_size'])
        fonts['small'] = ImageFont.truetype("arial.ttf", config['small_font_size'])
    except IOError:
        fonts['name'] = ImageFont.load_default()
        fonts['price'] = ImageFont.load_default()
        fonts['small'] = ImageFont.load_default()

    # Adicionando o nome do item
    draw.text((config['name_x'], config['name_y']), name, font=fonts['name'], fill='black')
    
    # Adicionando QR Code
    qr_code_img = Image.open(generate_qr_code(qr_code_link)).resize((config['qr_code_size'], config['qr_code_size']))
    label.paste(qr_code_img, (config['qr_code_x'], config['qr_code_y']))
    
    # Adicionando preço
    draw.text((config['price_x'], config['price_y']), f"{price}", font=fonts['price'], fill='black')

    # Adicionando SKU, código de barras e outros textos
    text_lines = [
        f"SKU: {sku}",
        f"UN: {universal_code}",
        f"ID: {ad_code}",
        f"{condition}"
    ]
    for i, line in enumerate(text_lines):
        draw.text((config['sku_x'], config['sku_y'] + i * config['sku_spacing']), line, font=fonts['small'], fill='black')

    # Adicionando código de barras
    barcode_img = generate_barcode(sku)
    cropped_barcode_img = crop_barcode_image(barcode_img).resize((config['barcode_width'], config['barcode_height']))
    label.paste(cropped_barcode_img, (config['barcode_x'], label_height - config['barcode_height'] - config['barcode_bottom_padding']))

    return label

# Função para selecionar itens
def select_items_to_ad(df):
    """Permite ao usuário selecionar itens do DataFrame, exibindo SKU, ITEM_ID e TITLE."""
    df['item_display'] = df['ITEM_ID'].astype(str) + ' - ' + df['SKU'].astype(str) + ' - ' + df['TITLE']
    item_options = df[['SKU', 'item_display', 'IMG']].set_index('SKU')['item_display'].to_dict()

    st.write("Selecione os itens adicionados para anúncios:")
    selected_display_names = st.multiselect(
        "Nome, SKU ou código Mercado Livre", 
        options=list(item_options.values()), 
        key=1, 
        placeholder="Pesquisar por Nome, SKU ou código Mercado Livre", 
        label_visibility="collapsed"
    )
    
    # Mapeando os itens selecionados para os SKUs
    selected_skus = [key for key, value in item_options.items() if value in selected_display_names]
    selected_items_df = df[df['SKU'].isin(selected_skus)]

    # Exibindo os itens selecionados com URLs e previews de imagens
    if not selected_items_df.empty:
        st.data_editor(
            selected_items_df, 
            column_config={
                "URL": st.column_config.LinkColumn(),
                "ITEM_LINK": st.column_config.LinkColumn(display_text="Editar Anúncio"),
                "IMG": st.column_config.ImageColumn(
                    "Preview", 
                    help="Streamlit app preview screenshots", 
                    width=90
                )
            }
        )
    
    return selected_items_df

# Configurações de layout da etiqueta
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
    'barcode_width': 600,
    'barcode_height': 80,
    'barcode_bottom_padding': 20,
    'name_font_size': 34,
    'price_font_size': 35,
    'small_font_size': 30,
    'margin_top': 80,
    'margin_bottom': 80,
    'margin_left': 40,
    'margin_right': 15,
    'spacing_horizontal': 90,
    'spacing_vertical': 10
}

# Função para criar etiquetas a partir de um arquivo Excel
def create_labels_from_excel(file_path, config):
    labels = []
    for index, row in file_path.iterrows():
        name = row.get('TITLE', '')
        qr_code_link = row.get('URL', '')
        price = row.get('MSHOPS_PRICE', '')
        sku = row.get('SKU', '')
        universal_code = row.get('universal_code', '')
        ad_code = row.get('ITEM_ID', '')
        condition = row.get('CONDITION', '')

        label_image = create_single_label(name, qr_code_link, price, sku, universal_code, ad_code, condition, config)
        labels.append(label_image)

    return labels

# Selecionando os itens a serem incluídos
selected_items = select_items_to_ad(data)

# Gerando as etiquetas e o arquivo PDF
labels = create_labels_from_excel(selected_items, config)
pdf_file_path = save_labels_as_pdf(labels)

# Baixar o PDF gerado
st.download_button("Baixar PDF das Etiquetas", pdf_file_path, file_name="etiquetas.pdf", mime="application/pdf")
