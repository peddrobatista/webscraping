import requests
from bs4 import BeautifulSoup

url_base = 'https://lista.mercadolivre.com.br/'
produto_nome = input('Buscar produto: ')

# Adicionando cabeçalho para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url_base + produto_nome, headers=headers)

if response.status_code == 200:
    site = BeautifulSoup(response.text, 'html.parser')

    # Tentando buscar produtos em diferentes estruturas HTML
    produtos = site.find_all('li', {'class': 'ui-search-layout__item'})

    if produtos:
        print(f'Foram encontrados {len(produtos)} produtos:')
        for i, produto in enumerate(produtos[:5]):  # Exibindo os 5 primeiros produtos
            # Tentativas de captura de título e preço
            titulo = produto.find('h2')
            preco = produto.find('span', {'class': 'price-tag-fraction'})

            if not titulo:
                titulo = produto.find('h2', {'class': 'ui-search-item__title'})

            if not preco:
                preco = produto.find('span', {'class': 'ui-search-price__second-line'})

            if titulo and preco:
                print(f"{i + 1}. {titulo.text.strip()} - R$ {preco.text.strip()}")
            else:
                print(f"{i + 1}. Detalhes do produto não disponíveis.")
    else:
        print('Nenhum produto encontrado.')
else:
    print(f'Erro ao acessar o site: {response.status_code}')
