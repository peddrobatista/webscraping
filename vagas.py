import requests
from bs4 import BeautifulSoup
import gspread # type: ignore
from oauth2client.service_account import ServiceAccountCredentials # type: ignore

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
response = requests.get('https://idt.org.br/vagas-disponiveis', headers=headers)

if response.status_code == 200:
    content = response.content
    site = BeautifulSoup(content, 'html.parser')

    # Procurar a tabela de vagas
    vagas = site.find('table', attrs={'class': 'table'})
    
    if vagas:
        linhas = vagas.find_all('tr')
        capturando = False
        dados = [["Ocupação", "Quantidade de Vagas"]]

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
        sheet.update("A1:B{}".format(len(dados)), dados)
        print("Dados enviados com sucesso para o Google Sheets!")
    else:
        print("Tabela de vagas não encontrada.")
else:
    print(f"Erro ao acessar o site. Status code: {response.status_code}")
