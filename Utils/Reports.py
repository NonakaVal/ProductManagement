

import tempfile
import datetime



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
    report_content = f"Data-Hora-sáida: {current_time}\n"
    for entry in report:
        report_content += f"- {entry['Product Name']} | {entry['Ad Code']} | {entry['SKU']}\n"

    # Criar arquivo temporário para o relatório com data no nome
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        report_file_path = temp_file.name
        temp_file.write(report_content.encode())  # Escrever conteúdo no arquivo temporário
    
    return report_file_path
