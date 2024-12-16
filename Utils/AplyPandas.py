import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def format_data(data):
    # Transformações de tipo
    # data['CONDITION'] = data['CONDITION'].fillna('-')
    data['QUANTITY'] = data['QUANTITY'].fillna(0).astype(int)
    data['MSHOPS_PRICE'] = data["MSHOPS_PRICE"].astype(int)
    data['SKU'] = data['SKU'].str.replace('-', '').astype(str)
    # Criação da coluna de links clicáveis

    # Ordenação das colunas
    var_order = ["IMG",'ITEM_ID', 'SKU', 'TITLE', 'DESCRIPTION', 'MSHOPS_PRICE', 'MARKETPLACE_PRICE',  'CATEGORY', 'STATUS', 'QUANTITY', "ITEM_LINK", "CONDITION","URL"]
    data = data.reindex(columns=var_order)

    # Remoção de duplicatas
    data = data.drop_duplicates(subset='ITEM_ID', keep='first')

    return data

def update_product_skus(data):
    current_year_month = datetime.now().strftime("%y%m")

    # Preparando para rastrear informações adicionais sobre novos SKUs
    existing_skus_list = []
    new_skus_list = []
    new_skus_details = []  # Lista para armazenar detalhes para novos SKUs incluindo ITEM_ID e TITLE

    # Certifique-se de que CATEGORY_id tenha 3 dígitos
    data['CATEGORY_ID'] = data['CATEGORY_ID'].str.zfill(3)

    for category_id in data['CATEGORY_ID'].unique():
        category_mask = data['CATEGORY_ID'] == category_id

        existing_skus = data.loc[category_mask & data['SKU'].notna(), 'SKU']
        existing_skus_list.extend(existing_skus)

        year_month = current_year_month

        # Extrai contadores e valida
        counters = existing_skus.str.extract(f"^{category_id}-\d{{4}}-(\d{{4}})$")[0]
        valid_counters = pd.to_numeric(counters, errors='coerce').dropna().astype(int)
        
        next_counter = valid_counters.max() + 1 if not valid_counters.empty else 1

        null_skus_indices = data.index[category_mask & data['SKU'].isna()]
        for idx in null_skus_indices:
            new_sku = f"{category_id}-{year_month}-{next_counter:04d}"
            data.at[idx, 'SKU'] = new_sku
            new_skus_list.append(new_sku)
            new_skus_details.append({
                'TITLE': data.at[idx, 'TITLE'],
                'SKU': new_sku,
                'ITEM_ID': data.at[idx, 'ITEM_ID'],
            })
            next_counter += 1


        # Converte a lista de dicionários em DataFrame
        new_skus_data = pd.DataFrame(new_skus_details)  # Agora inclui ITEM_ID e TITLE

    return data, new_skus_data

def format_prices(data):
    if 'MSHOPS_PRICE' in data.columns:
        data['MSHOPS_PRICE'] = pd.to_numeric(data['MSHOPS_PRICE'], errors='coerce')
        data['MSHOPS_PRICE'] = data['MSHOPS_PRICE'].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else 'R$ 0.00')
    # Formatação de MARKETPLACE_PRICE
    if 'MARKETPLACE_PRICE' in data.columns:
        data['MARKETPLACE_PRICE'] = pd.to_numeric(data['MARKETPLACE_PRICE'], errors='coerce')
        data['MARKETPLACE_PRICE'] = data['MARKETPLACE_PRICE'].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else 'R$ 0.00')
    return data



def compare_dataframes(data1, data2):
    """
    Compara dois DataFrames e retorna as diferenças, incluindo:
    - Itens adicionados
    - Mudanças de preço (MSHOPS_PRICE e MARKETPLACE_PRICE)
    - Alterações de quantidade (QUANTITY)
    """
    
    data1['QUANTITY'] = data1['QUANTITY'].fillna(0).astype(int)
    data1['QUANTITY'] = data2['QUANTITY'].fillna(0).astype(int)

    # Itens adicionados: presentes na tabela 1 (data1), mas não na tabela 2 (data2)
    items_added = data1[~data1['ITEM_ID'].isin(data2['ITEM_ID'])]
    
    # Itens comuns: presentes em ambas as tabelas, para comparação de preços e quantidade
    common_items = pd.merge(data1, data2, on='ITEM_ID', suffixes=('_new', '_old'))
    
    # Mudanças de preço: verifica se os preços (MSHOPS_PRICE e MARKETPLACE_PRICE) mudaram
    price_changes = common_items[
        (common_items['MSHOPS_PRICE_new'] != common_items['MSHOPS_PRICE_old']) | 
        (common_items['MARKETPLACE_PRICE_new'] != common_items['MARKETPLACE_PRICE_old'])
    ]

    # Alterações de quantidade: verifica se a quantidade mudou
    quantity_changes = common_items[common_items['QUANTITY_new'] != common_items['QUANTITY_old']]
    
    return items_added, price_changes, quantity_changes

