# ProductManagement

## Visão Geral

O projeto consiste em uma aplicação desenvolvida com **Streamlit**, que permite a consulta e gestão de produtos por meio de uma interface interativa. Ele integra diversas funcionalidades para facilitar a seleção, visualização e processamento de dados de produtos, incluindo a geração de relatórios e etiquetas. Além disso, o aplicativo tem a capacidade de se conectar com o Google Sheets para importação e exportação de dados de produtos.

![Imgur](https://i.imgur.com/dZsSrBk.png)

## Funcionalidades

1. **Consulta e Pesquisa de Produtos**:
   - O aplicativo permite a consulta de produtos a partir de uma tabela, com suporte a filtros por palavras-chave (como SKU ou título).
   - Os dados exibidos incluem informações como links para edição do anúncio e pré-visualização das imagens dos produtos.

2. **Integração com Google Sheets**:
   - O aplicativo se conecta a uma planilha do Google Sheets para ler e gerenciar os dados dos produtos.
   - Os dados da planilha podem ser usados para gerar relatórios e etiquetas automaticamente a partir das informações de cada produto.

3. **Seleção de Itens**:
   - O usuário pode selecionar múltiplos itens de uma lista para gerar relatórios de saída ou etiquetas com base em suas seleções.

4. **Geração de Relatórios**:
   - O aplicativo permite gerar um relatório de saída que detalha o total de itens e o valor total dos produtos selecionados.
   - O relatório é gerado em formato `.txt` e está disponível para download.

5. **Criação de Etiquetas**:
   - **Etiquetas com Código de Barras**: O aplicativo permite gerar etiquetas com código de barras para os produtos selecionados, com a possibilidade de gerar um PDF contendo todas as etiquetas.
   - **Etiquetas com QR Code**: Alternativamente, também é possível criar etiquetas com QR Code para os itens selecionados.

6. **Visualização e Interação com Tabela**:
   - A tabela de produtos pode ser filtrada dinamicamente com base em palavras-chave. A visualização inclui dados como SKU, título e preço, além de links para acessar os detalhes do produto.

## Tecnologias Utilizadas

- **Streamlit**: Biblioteca Python usada para construir a interface interativa e visual.
- **Pandas**: Para manipulação de dados e filtragem de produtos.
- **Google Sheets API**: Para integrar a aplicação com planilhas do Google, facilitando a importação e exportação de dados.
- **QR Code e Código de Barras**: Bibliotecas específicas para gerar códigos de barras e QR Codes nas etiquetas.

## Como Funciona

### Fluxo de Dados

1. **Carregamento dos Dados**: O aplicativo carrega os dados de uma planilha do Google Sheets através da integração com a API do Google. Os dados incluem informações como SKU, título, preço e outros detalhes relevantes sobre os produtos.
   
2. **Pesquisa de Produtos**: Através de uma caixa de pesquisa, o usuário pode filtrar a tabela de produtos por palavras-chave, como SKU ou título, para encontrar rapidamente os itens desejados.

3. **Seleção de Produtos**: Após filtrar os produtos, o usuário pode selecionar os itens que deseja incluir em um relatório ou em um conjunto de etiquetas. Os itens selecionados são exibidos para visualização.

4. **Geração de Relatórios**: Quando o usuário seleciona itens, a aplicação calcula o total de produtos e o valor total dos itens. Um relatório é gerado com essa informação, e o usuário pode baixá-lo.

5. **Criação de Etiquetas**: O usuário pode gerar etiquetas com códigos de barras ou QR Codes. O layout das etiquetas pode ser configurado, e o arquivo gerado é disponibilizado para download.

## Objetivo

Este projeto visa simplificar o processo de gerenciamento e criação de documentos para produtos de e-commerce. Ele oferece uma maneira eficiente de consultar, selecionar e gerar relatórios e etiquetas, tudo dentro de uma interface de fácil uso. A integração com o Google Sheets torna o gerenciamento de dados ainda mais fluido e acessível, permitindo que os usuários atualizem e sincronizem informações em tempo real.
