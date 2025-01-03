


def generate_report(df, config):
    # Gerar a lista de saída com relatório
    report = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Incluindo data e hora no formato desejado
    
    for idx, row in df.iterrows():
        report.append({
            'Timestamp': current_time,
            'Product Name': row['TITLE'],
            'Ad Code': row['ITEM_ID'],
            'SKU': row['SKU'],
        })
    
    # Criar o relatório com todos os produtos processados
    report_content = f"Timestamp: {current_time}\n"
    for entry in report:
        report_content += f"{entry['Product Name']} | {entry['Ad Code']} | {entry['SKU']}\n"

    # Criar arquivo temporário para o relatório com data no nome
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        report_file_path = temp_file.name
        temp_file.write(report_content.encode())  # Escrever conteúdo no arquivo temporário
    
    return report_file_path


st.write("#### Tabela de Consulta de Produtos")

# Carregar e processar os dados
data = load_and_process_data()

# Seleção de itens para o anúncio
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
            label="Baixar Relatório",
            data=file,
            file_name=f"product_report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            mime="text/plain"
        )
