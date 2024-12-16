import streamlit as st
from Utils.Get_Link import get_link

def select_items_to_ad(df, key=1):
    """Allow the user to select items from the DataFrame, displaying SKU, ITEM_ID, and TITLE."""
    df['item_display'] = df['ITEM_ID'].astype(str) + ' - ' + df['SKU'].astype(str) + ' - ' + df['TITLE']
    item_options = df[['SKU', 'item_display', 'IMG']].set_index('SKU')['item_display'].to_dict()
    
    st.write("")

    st.write("Selecione os itens adicionados para anúncios:")
    selected_display_names = st.multiselect(
        "Nome, SKU ou código Mercado Livre", 
        options=list(item_options.values()), 
        key=key, 
        placeholder="Pesquisar por Nome, SKU ou código Mercado Livre", 
        label_visibility="collapsed"
    )
    
    # Map selected display names to SKUs
    selected_skus = [key for key, value in item_options.items() if value in selected_display_names]
    selected_items_df = df[df['SKU'].isin(selected_skus)]

    # Apply the get_link function to the selected items
    selected_items_df = get_link(selected_items_df)

    # Display selected items with URLs and image previews
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