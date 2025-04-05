import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da API do Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
client = gspread.authorize(credentials)

# ID da planilha e nome da aba
spreadsheet_id = "1eYdX5DbQ_yiTtCzUplsG2G1Pp-mVrjUUHJs5AkNasC8"
sheet_name = "vagas_messejana"
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Fazer a requisição com cabeçalho User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

try:
    response = requests.get('https://idt.org.br/vagas-disponiveis', headers=headers)
    response.raise_for_status()  # Lança uma exceção se a resposta não for bem-sucedida
except requests.exceptions.RequestException as e:
    print(f"Erro ao fazer a requisição: {e}")
    exit(1)

# Parsear o conteúdo HTML da página
site = BeautifulSoup(response.content, 'html.parser')

# Procurar a tabela de vagas
vagas = site.find('table', attrs={'class': 'table'})

if vagas is None:
    print("Tabela de vagas não encontrada.")
    exit(1)

# Coletar as informações de cada linha da tabela
linhas = vagas.find_all('tr')
capturando = False
dados = []

for linha in linhas:
    texto = linha.get_text(separator=' ').strip()

    if "FORTALEZA:U.A. MESSEJANA" in texto:
        capturando = True
        continue

    if capturando:
        if "FORTALEZA:" in texto and "MESSEJANA" not in texto:
            break

        dados_linha = texto.split()
        if len(dados_linha) > 1:
            ocupacao = " ".join(dados_linha[:-1])
            quantidade = dados_linha[-1]
            dados.append([ocupacao, quantidade])

# Atualizar a planilha
try:
    sheet.update("A1:B{}".format(len(dados)), dados)
    print("Dados enviados com sucesso para o Google Sheets!")
except gspread.exceptions.GSpreadException as e:
    print(f"Erro ao atualizar a planilha: {e}")