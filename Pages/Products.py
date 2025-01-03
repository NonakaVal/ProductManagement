
import streamlit as st
from Utils.LoadDataFrame import load_and_process_data
from Utils.Selectors import select_items_to_ad
from Utils.GoogleSheetManager import GoogleSheetManager
from Utils.LabelCreator import create_labels_from_dataframe_with_barcode
from Utils.QRcodeLabelCreator import create_qrcode_labels
from Utils.Reports import generate_report
import datetime


st.write("#### Tabela de Consulta de Produtos")
st.write("Em caso de erro apenas atualize a página. F5")

# Em algum lugar no seu código
data = load_and_process_data()

##############################################################################################
# Função de Pesquisa por Correspondência de Palavras
##############################################################################################


def search_items(data, search_term):
    """
    Filtra o DataFrame para itens que contenham o termo de pesquisa em qualquer coluna de texto.
    """
    if search_term:
        # Filtra o DataFrame baseado na correspondência do termo de pesquisa nas colunas 'TITLE' e 'SKU'
        filtered_data = data[data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        # Se não houver termo de pesquisa, retorna o DataFrame completo
        filtered_data = data
    return filtered_data

search_term = st.text_input("Pesquisar por palavra-chave")

# Filtra os dados com base no termo de pesquisa
searched_data = search_items(data, search_term)

st.dataframe(
searched_data,
column_config={
    "URL": st.column_config.LinkColumn(display_text="Link do Produto"),
    "ITEM_LINK": st.column_config.LinkColumn(display_text="Editar Anúncio"),
    "IMG": st.column_config.ImageColumn(
        "Preview", help="Preview da imagem", width=130
    )
}
)

shape = data.shape

st.write(f"Total de Itens: {shape[0]}")

##############################################################################################
# Inicializar a conexão com o Google Sheets
##############################################################################################
st.divider()
gs_manager = GoogleSheetManager()
url = st.secrets["product_url"]

if url:
    # Configura o gerenciador de Google Sheets
    gs_manager.set_url(url)
    gs_manager.add_worksheet(url, "ANUNCIOS")
    products = gs_manager.read_sheet(url, "ANUNCIOS")


##############################################################################################
# Função para selecionar itens do Google Sheets
##############################################################################################

def select_items(data):
    # Criar uma coluna para exibição combinada de SKU e TITLE
    data['item_display'] = data['ITEM_ID'].astype(str) + ' - ' + data['SKU'].astype(str) + ' - ' + data['TITLE']

    # Criar uma caixa de seleção múltipla para escolher itens
    item_options = data[['SKU', 'item_display']].set_index('SKU')['item_display'].to_dict()
    selected_display_names = st.multiselect("Selecione os itens (SKU - Nome)", options=list(item_options.values()))

    # Mapear nomes de exibição selecionados de volta para SKU
    selected_skus = [key for key, value in item_options.items() if value in selected_display_names]

    # Filtrar o DataFrame para obter as linhas correspondentes
    selected_items_df = data[data['SKU'].isin(selected_skus)]

    # Exibir o DataFrame dos itens selecionados
    if not selected_items_df.empty:
        st.write("Itens selecionados:")
        st.dataframe(selected_items_df[['ITEM_ID', 'SKU', 'TITLE']])

    return selected_items_df


##############################################################################################
# Função principal do Streamlit
##############################################################################################

# st.write("#### Criar lista de itens com links encurtados")

select = select_items_to_ad(data)



##############################################################################################
##############################################################################################

if not select.empty:

    # Calcula o número total de itens
    total_items = select['CATEGORY'].value_counts().sum()
    
    # Remover formatação do preço e convertê-lo para inteiro
    select['MSHOPS_PRICE'] = select['MSHOPS_PRICE'].str.replace('R$', '', regex=False).str.replace(',00', '', regex=False).str.replace('.', '', regex=False).str.strip()
    select['MSHOPS_PRICE'] = select['MSHOPS_PRICE'].astype(int)

    # Soma total dos preços e formatação
    price_counts = select["MSHOPS_PRICE"].sum()
    formatted_price = f"R$ {price_counts:,.2f}"

    st.write(f"Total de Itens: {total_items}")
    st.write(f"Valor Total: {formatted_price}")

    # Gerar o relatório de saída
    report_path = generate_report(select, config={})  # Configurar conforme necessário
    st.write(f"Relatório de Saída gerado em: {report_path}")

    # Criar o botão de download
    with open(report_path, "rb") as file:
        st.download_button(
            label="Gerar Registro de Saída",
            data=file,
            file_name=f"Registro_de_saida_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            mime="text/plain"
        )


# if not select.empty:

#     # Calcula o número total de itens
#     total_items = select['CATEGORY'].value_counts().sum()
      
#     # Aplicando a função nas colunas 'VALOR' e 'PAGO'
#     select['MSHOPS_PRICE'] = select['MSHOPS_PRICE'].str.replace('R$', '', regex=False).str.replace(',00', '', regex=False).str.replace('.', '', regex=False).str.strip()
#     # Soma total dos preços e formatação
#     select['MSHOPS_PRICE'] = select['MSHOPS_PRICE'].astype(int)
#     price_counts = select["MSHOPS_PRICE"].sum()
#     formatted_price = f"R$ {price_counts:,.2f}"
#     st.write(f"Total de Itens: {total_items}")
#     st.write(f"Valor Total: {formatted_price}")


st.divider()
st.divider()

def main():
    st.write("#### Selecione os itens para gerar etiquetas.")
    # Selecionar itens


    tab1, tab2 = st.tabs(["Etiqueta com Barra de Código", "Etiqueta com QRCODE"])

    with tab1:
                
        df = select_items(products)

        
        # Configurações para etiquetas
        config = {
            'margin_top': 70,
            'margin_bottom': 50,
            'margin_left': 70,
            'margin_right': 50,
            'spacing_horizontal': 40,
            'spacing_vertical': 55,
            'name_font_size': 25,
            'small_font_size': 25,
            'name_x': 55,
            'name_y': 50,
            'ad_code_x': 55,
            'ad_code_y': 100,
            'barcode_x': 10,
            'barcode_bottom_padding': 10,
            'barcode_width': 650,
            'barcode_height': 100
        }
        if st.button("Gerar PDF e Baixar"):
            if df.empty:
                st.warning("Por favor, selecione pelo menos um item!")
            else:
                pdf_path = create_labels_from_dataframe_with_barcode(df, config)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_file,
                        file_name="etiquetas_barcode_33_a4.pdf",
                        mime="application/pdf"
                    )
    with tab2:
        create_qrcode_labels()
    
main()





st.sidebar.markdown("""

            [Acessar Tabela Google Sheets](https://docs.google.com/spreadsheets/d/11gOfqJdk1Q49MLDQA-DeEH7YiGIf_kWdkp6CORk8t4A/edit?gid=1238567357#gid=1238567357)
                    
            [Baixar Tabela Mercado Livre](https://www.mercadolivre.com.br/anuncios/edicao-em-excel?filters=OMNI_ACTIVE%7COMNI_INACTIVE%7CCHANNEL_NO_PROXIMITY_AND_NO_MP_MERCHANTS&order=DEFAULT&excelType=MARKETPLACE&channel=marketplace&callback_url=https%3A%2F%2Fwww.mercadolivre.com.br%2Fanuncios%2Flista%3Ffilters%3DOMNI_ACTIVE%257COMNI_INACTIVE%257CCHANNEL_NO_PROXIMITY_AND_NO_MP_MERCHANTS%26page%3D1%26sort%3DDEFAULT#from%3Dlistings)

""")