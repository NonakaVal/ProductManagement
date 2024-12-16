import pandas as pd
import streamlit as st
from Utils.AplyFilters import apply_filters
from Utils.GoogleSheetManager import GoogleSheetManager


def load_and_process_data():
    # Get the URL of Google Sheets
    gs_manager = GoogleSheetManager()
    url = st.secrets["product_url"]

    if url:
        # Set up Google Sheets manager
        gs_manager.set_url(url)

        # Add worksheets
        gs_manager.add_worksheet(url, "ANUNCIOS")
        gs_manager.add_worksheet(url, "CATEGORIAS")
        gs_manager.add_worksheet(url, "CONDITIONS")

        # Read worksheets
        products = gs_manager.read_sheet(url, "ANUNCIOS")
        categorias = gs_manager.read_sheet(url, "CATEGORIAS")

        # Prepare data
        data = products.copy()


        # List of all columns
        all_columns = data.columns.tolist()
        
        # Default columns to always display
        default_columns = [
            "IMG", "ITEM_ID", "SKU", "TITLE", 
            "MSHOPS_PRICE", "QUANTITY", "STATUS", 
            "URL", "ITEM_LINK", "CATEGORY", "DESCRIPTION"
        ]

        # Filter out default columns from the options in the multiselect
        filtered_columns = [col for col in all_columns if col not in default_columns]

        # Widget multiselect for additional columns
        selected_columns = st.sidebar.multiselect(
            "Selecione as colunas adicionais para exibição:",
            options=filtered_columns,
        )

        # Combine default columns with the selected additional columns
        final_columns = default_columns + selected_columns

        # Ensure the final column order is respected
        select_data = data[final_columns]

        # Format currency columns
        if "MSHOPS_PRICE" in select_data.columns:
            select_data["MSHOPS_PRICE"] = select_data["MSHOPS_PRICE"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

        # Apply filters and categorization
        select_data = apply_filters(select_data, categorias)
        

        return select_data
    else:
        st.error("URL do Google Sheets não configurada corretamente!")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error
