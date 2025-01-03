import requests

def shorten_url_with_requests(url, timeout=10):
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    try:
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Erro ao encurtar a URL: {str(e)}"
def shorten_links_in_df(df, link_column="URL"):
    # Verifica se a coluna existe antes de aplicar
    if link_column in df.columns:
        df[link_column] = df[link_column].apply(lambda x: shorten_url_with_requests(x))
    return df[[link_column]]  # Retorna apenas a coluna que foi encurtada

def get_link(data):
    # Verifica se o DataFrame está vazio
    if data.empty:
        return data 
    data['URL'] = data.apply(
        lambda row: f"https://www.collectorsguardian.com.br/{row['ITEM_ID'][:3]}-{row['ITEM_ID'][3:]}-{row['TITLE'].replace(' ', '-').lower()}-_JM#item_id={row['ITEM_ID']}", 
        axis=1
    )
    # por algum motivo inexplicável isso aqui ta sendo aplicado em todos os df
    
    selected_columns = ["IMG",'ITEM_ID', 'SKU','TITLE', 'MSHOPS_PRICE', 'URL','ITEM_LINK', "DESCRIPTION","CATEGORY"]

    data = data[selected_columns]

    # Encurtando os links na coluna 'URL'
    shortened_data = shorten_links_in_df(data, link_column='URL')

    # Aqui estamos atribuindo a coluna 'URL' do DataFrame encurtado de volta ao data
    data['URL'] = shortened_data['URL']

    return data



def get_link_edit(data):
    # Verifica se o DataFrame está vazio
    if data.empty:
        return data 
    data['URL'] = data['ITEM_ID'].apply(
        lambda item_id: f"https://www.mercadolivre.com.br/anuncios/lista?filters=OMNI_ACTIVE|OMNI_INACTIVE|CHANNEL_NO_PROXIMITY_AND_NO_MP_MERCHANTS&page=1&search={item_id}"
    )

    # # Selecionando apenas as colunas desejadas
    # selected_columns = ['ITEM_ID', 'TITLE', 'MSHOPS_PRICE', 'URL', "DESCRIPTION","CATEGORY","SUBCATEGORY",  "EDITION", "CONDITION"]
    

    # data = data[selected_columns]


    # # Encurtando os links na coluna 'URL'
    # shortened_data = shorten_links_in_df(data, link_column='URL')

    # # Aqui estamos atribuindo a coluna 'URL' do DataFrame encurtado de volta ao data
    # data['URL'] = shortened_data['URL'] 
    


    # Aqui estamos atribuindo a coluna 'URL' do DataFrame encurtado de volta ao data
   

    return data