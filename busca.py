# Obter produtos do mercado livre a partir de uma busca realizada pelo usuário
# extensão coderunner
import requests
from bs4 import BeautifulSoup

url_base = 'https://lista.mercadolivre.com.br/'
produto_nome = input('Buscar produto: ')

response = requests.get(url_base + produto_nome)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    site = BeautifulSoup(response.text, 'html.parser')

    # Ajustando o seletor para obter a lista de resultados
    produtos = site.find_all('div', attrs={'class': 'ui-search-result__wrapper'})

    if produtos:
        print(f'Foram encontrados {len(produtos)} produtos:')
        for i, produto in enumerate(produtos[:5]):  # Exibe os 5 primeiros produtos
            titulo = produto.find('h2', attrs={'class': 'poly-component__title-wrapper'})
            preco = produto.find('span', attrs={'class': 'andes-money-amount andes-money-amount--cents-superscript'})
            
            if titulo and preco:
                print(f"{i+1}. {titulo.text.strip()} - {preco.text.strip()}")
            else:
                print(f"{i+1}. Detalhes do produto não disponíveis.")
    else:
        print('Nenhum produto encontrado.')
else:
    print(f'Erro ao acessar o site: {response.status_code}')