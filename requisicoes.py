import requests

response = requests.get('https://idt.org.br/vagas-disponiveis')

print('Status code: ', response.status_code)
print('Header: ', response.headers)
print('Conteúdo: ', response.content)