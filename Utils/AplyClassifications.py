import pandas as pd
import json
import re
import streamlit as st

with open('utils/json/editions_keywords.json', 'r') as json_file:
    edition_keywords = json.load(json_file)

with open('utils/json/detailed_keywords.json', 'r') as json_file:
    detailed_keywords = json.load(json_file)

def classify_items(df):
    """
    Classifies items into subcategories based on provided keywords,
    ignoring case differences, using regular expressions.

    :param df: DataFrame containing item data.
    :param detailed_keywords: Detailed dictionary with categories, subcategories, and keywords.
    :return: Updated DataFrame with a new column 'SUBCATEGORY'.
    """
    # Flattening the detailed keywords into a single dictionary mapping subcategory names to keywords
    flat_keywords = {}
    for category, subcategories in detailed_keywords.items():
        for subcategory, words in subcategories.items():
            flat_subcategory = f"{category}-{subcategory}"
            if flat_subcategory not in flat_keywords:
                flat_keywords[flat_subcategory] = []
            flat_keywords[flat_subcategory].extend(words)

    # Function to classify a single item
    def classify_item(item):
        if isinstance(item, str):
            item_lower = item.lower()
            matched_subcategories = []
            
            # Check each subcategory's keywords
            for subcategory, words in flat_keywords.items():
                # Create a pattern that ensures we are matching whole words
                pattern = r'\b(?:' + '|'.join(re.escape(word.lower()) for word in words) + r')\b'  # Match whole words
                if re.search(pattern, item_lower):
                    matched_subcategories.append(subcategory)

            # If matches were found, return the most specific match
            if matched_subcategories:
                # Here you can choose how to determine the "most specific" match.
                # For example, you could sort by length of subcategory name.
                return max(matched_subcategories, key=len)

        return "Outros"  # Return "Outros" if no keywords match

    # Applying the classification function to the 'TITLE' column
    df['SUBCATEGORY'] = df['TITLE'].apply(classify_item)

    return df

def classify_editions(df):
    """
    Classifies items into editions based on provided keywords.

    :param df: DataFrame containing item data.
    :param edition_keywords: Dictionary with edition keywords.
    :return: Updated DataFrame with a new column 'EDITION'.
    """
    # Flattening the edition keywords into a single dictionary
    flat_keywords = {}
    for edition, words in edition_keywords.items():
        flat_keywords[edition] = words

    # Function to classify a single item
    def classify_edition(item):
        if isinstance(item, str):
            item_lower = item.lower()
            for edition, words in flat_keywords.items():
                pattern = '|'.join(re.escape(word.lower()) for word in words)  # Escape special characters
                if re.search(pattern, item_lower):
                    return edition.upper()  # Return the edition ID in uppercase
        return "Outros"  # Return "OUTROS" if no keywords match

    # Applying the classification function to the 'TITLE' column
    df['EDITION'] = df['TITLE'].apply(classify_edition)
    
    return df

def get_condition(data, cat):
    # Assuming `cat` contains ITEM_ID and CONDITION columns
    # Merge based on ITEM_ID to bring in the CONDITION column from cat DataFrame
    merged = pd.merge(data, cat[['ITEM_ID', 'CONDITION']], on='ITEM_ID', how='left')
    merged['CONDITION'] = merged['CONDITION'].fillna('-')
    
    # Optionally, you can rename the CONDITION column from cat if needed
    # merged.rename(columns={'CONDITION': 'CONDITION'}, inplace=True)

    # Ensure the data still keeps the original columns along with the new condition
    return merged

# def get_imgs(data, imgs):
    
#     # Merge based on ITEM_ID to bring in the IMG column from imgs DataFrame
#     merged = pd.merge(data, imgs[['ITEM_ID', 'IMG']], on='ITEM_ID', how='left')
    
#     # Fill any missing values in the IMG column
#     merged['IMG'] = merged['IMG'].fillna('-')
    
#     return merged

def get_categories_ID(data, categorias_data):
    categorias_data['ID'] = categorias_data['ID'].apply(lambda x: f'{int(x):03d}') 
    # Converter a tabela de categorias em um dicionário
    categorias_dict = categorias_data.set_index('CATEGORY')['ID'].to_dict()

    # Verificar se a coluna 'CATEGORY' existe nos anúncios e fazer o mapeamento
    if 'CATEGORY' in data.columns:
        data['CATEGORY_ID'] = data['CATEGORY'].map(categorias_dict)

    return data

def display_column_data(filtered, column_name, title):
    st.write(title)
    if column_name in filtered.columns:
        counts = filtered[column_name].dropna().value_counts()
        counts_df = counts.reset_index()
        counts_df.columns = [column_name.capitalize(), 'Contagem']
        counts_html = counts_df.to_html(index=False, escape=False, header=False)
        st.markdown(counts_html, unsafe_allow_html=True)
    else:
        st.error(f"Coluna '{column_name}' não encontrada no DataFrame filtrado!")
