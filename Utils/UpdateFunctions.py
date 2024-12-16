# Funções utilitárias
import pandas as pd

def data_normalization(data):
    """Normaliza os dados, ajustando tipos e colunas relevantes."""
    data = data[["ITEM_ID", "SKU", "TITLE", 'MSHOPS_PRICE', 'MARKETPLACE_PRICE', "DESCRIPTION",'CATEGORY', 'STATUS', 'QUANTITY']]
    data['MSHOPS_PRICE'] = pd.to_numeric(data['MSHOPS_PRICE'], errors='coerce')
    data['MARKETPLACE_PRICE'] = pd.to_numeric(data['MARKETPLACE_PRICE'], errors='coerce')
    data['STATUS'] = data['STATUS'].str.strip()
    data['QUANTITY'] = pd.to_numeric(data['QUANTITY'], errors='coerce').fillna(0).astype(int)
    data = data.drop_duplicates(subset='ITEM_ID', keep='first')
    return data

# def compare_dataframes(new_data, old_data):
#     """Compara dois DataFrames e retorna as diferenças (itens adicionados, mudanças de preço, quantidade e status)."""
#     items_added = new_data[~new_data['ITEM_ID'].isin(old_data['ITEM_ID'])]
#     common_items = pd.merge(new_data, old_data, on=['ITEM_ID', "TITLE"], suffixes=('_novo', '_antigo'))
    
#     price_changes = common_items[
#         (common_items['MSHOPS_PRICE_novo'] != common_items['MSHOPS_PRICE_antigo']) |
#         (common_items['MARKETPLACE_PRICE_novo'] != common_items['MARKETPLACE_PRICE_antigo'])
#     ]
    
#     quantity_changes = common_items[common_items['QUANTITY_novo'] != common_items['QUANTITY_antigo']]
#     status_changes = common_items[common_items['STATUS_novo'] != common_items['STATUS_antigo']]
    
#     return items_added, price_changes, quantity_changes, status_changes

def compare_dataframes(new_data, old_data):
    """Compara dois DataFrames e retorna as diferenças: itens adicionados, removidos, mudanças de preço, quantidade e status, além de totais."""
    # Itens adicionados e removidos
    items_added = new_data.loc[~new_data['ITEM_ID'].isin(old_data['ITEM_ID'])]
    items_removed = old_data.loc[~old_data['ITEM_ID'].isin(new_data['ITEM_ID'])]

    # Itens em comum
    common_items = new_data.merge(old_data, on=['ITEM_ID', 'TITLE'], suffixes=('_novo', '_antigo'))

    # Mudanças de preço, quantidade e status
    price_changes = common_items.query('MSHOPS_PRICE_novo != MSHOPS_PRICE_antigo or MARKETPLACE_PRICE_novo != MARKETPLACE_PRICE_antigo')
    quantity_changes = common_items.query('QUANTITY_novo != QUANTITY_antigo')
    status_changes = common_items.query('STATUS_novo != STATUS_antigo')

    # Cálculo de totais apenas para itens ativos
    active_items = new_data[new_data['STATUS'] == "Ativo"]
    total_price_active = active_items['MSHOPS_PRICE'].sum()
    total_quantity_active = active_items['QUANTITY'].sum()

    return items_added, items_removed, price_changes, quantity_changes, status_changes, total_price_active, total_quantity_active



def fill_sku_from_df1(df_with_sku, df_without_sku):
    """Preenche os SKUs em df_without_sku com base em df_with_sku (usando ITEM_ID como chave)."""
    merged_data = df_without_sku.merge(df_with_sku[['ITEM_ID', 'SKU']], on='ITEM_ID', how='left', suffixes=('', '_from_df1'))
    merged_data['SKU'] = merged_data['SKU_from_df1']
    merged_data.drop(columns=['SKU_from_df1'], inplace=True)
    return merged_data

def calculate_totals(data):
    """Calcula os totais de MSHOPS_PRICE e QUANTITY para um DataFrame com STATUS 'Ativo'."""
    # Filtrando dados com STATUS igual a "Ativo"
    active_data = data[data['STATUS'] == "Ativo"]
    
    # Calculando totais
    total_price = active_data['MSHOPS_PRICE'].sum()
    total_quantity = active_data['QUANTITY'].sum()
    
    # Contando itens adicionados (assumindo que 'itens adicionados' se refere a novos registros)
    items_added_count = len(data[~data['ITEM_ID'].isin(active_data['ITEM_ID'])])
    
    return total_price, total_quantity, items_added_count
