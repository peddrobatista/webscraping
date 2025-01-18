import requests
from bs4 import BeautifulSoup

# Fazer a requisição à página
response = requests.get('https://idt.org.br/vagas-disponiveis')
content = response.content

# Usar BeautifulSoup para parsear o HTML
site = BeautifulSoup(content, 'html.parser')

# Encontrar a tabela de vagas
vagas = site.find('table', attrs={'class': 'table'})
if vagas:
    # Encontrar todos os elementos <em> na tabela
    local_vagas = vagas.findAll('em')

    # Iterar sobre os elementos encontrados e imprimir o texto
    for vaga in local_vagas:
        print(vaga.text)
else:
    print("Tabela de vagas não encontrada.")
