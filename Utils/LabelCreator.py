import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from barcode.codex import Code128
from barcode.writer import ImageWriter
import tempfile


class CustomImageWriter(ImageWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = False  # Remove o texto do código de barras


def generate_barcode(code_text):
    writer = CustomImageWriter()
    code = Code128(code_text, writer=writer)
    buffer = BytesIO()
    code.write(buffer)
    buffer.seek(0)
    return buffer


def crop_barcode_image(barcode_img, crop_percentage_top=0.1, crop_percentage_bottom=0.4):
    img = Image.open(barcode_img)
    width, height = img.size
    top = int(height * crop_percentage_top)
    bottom = int(height * (1 - crop_percentage_bottom))
    return img.crop((0, top, width, bottom))


def create_single_label_with_barcode(name, ad_code, sku, config):
    label_width, label_height = 738, 250  # Ajustado para 33 etiquetas por página
    label = Image.new('RGB', (label_width, label_height), 'white')
    draw = ImageDraw.Draw(label)

    fonts = {}
    try:
        fonts['name'] = ImageFont.truetype("arial.ttf", config['name_font_size'])
        fonts['small'] = ImageFont.truetype("arial.ttf", config['small_font_size'])
    except IOError:
        fonts['name'] = ImageFont.load_default()
        fonts['small'] = ImageFont.load_default()

    # Adicionar o nome
    draw.text((config['name_x'], config['name_y']), name, font=fonts['name'], fill='black')

    # Adicionar o código do anúncio
    draw.text((config['ad_code_x'], config['ad_code_y']), f"ID: {ad_code}", font=fonts['small'], fill='black')
    
    # Adicionar o código de barras
    barcode_img = generate_barcode(sku)
    cropped_barcode_img = crop_barcode_image(barcode_img).resize((config['barcode_width'], config['barcode_height']))
    label.paste(cropped_barcode_img, (config['barcode_x'], label_height - config['barcode_height'] - config['barcode_bottom_padding']))

    return label


def create_labels_from_dataframe_with_barcode(df, config):
    page_width, page_height = 2480, 3508  # Tamanho A4 em DPI 300
    label_width, label_height = 738, 250  # Tamanho ajustado das etiquetas
    labels_per_row = 3  # 3 etiquetas por linha
    labels_per_column = 11  # 11 etiquetas por coluna
    labels_per_page = labels_per_row * labels_per_column  # Total de etiquetas por página

    num_pages = -(-len(df) // labels_per_page)  # Arredonda para cima
    pdf_images = []

    x_offset = 60  # Deslocamento horizontal

    for page_num in range(num_pages):
        sheet = Image.new('RGB', (page_width, page_height), 'white')
        current_x = config['margin_left'] + x_offset
        current_y = config['margin_top']
        start_idx = page_num * labels_per_page
        end_idx = min(start_idx + labels_per_page, len(df))

        for idx in range(start_idx, end_idx):
            row = df.iloc[idx]

            label = create_single_label_with_barcode(
                row['TITLE'], row['ITEM_ID'], row['SKU'], config
            )
            sheet.paste(label, (current_x, current_y))
            current_x += label_width + config['spacing_horizontal']

            if (idx + 1) % labels_per_row == 0:
                current_x = config['margin_left'] + x_offset
                current_y += label_height + config['spacing_vertical']

        pdf_images.append(sheet.convert('RGB'))

    # Criar arquivo PDF em um diretório temporário
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        pdf_path = temp_file.name
        pdf_images[0].save(pdf_path, save_all=True, append_images=pdf_images[1:], resolution=300)

    return pdf_path
