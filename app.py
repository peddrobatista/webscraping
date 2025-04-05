from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials  # type: ignore

app = Flask(__name__)

# Configuração da API do Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
client = gspread.authorize(credentials)

# ID da planilha e nome da aba
SPREADSHEET_ID = "1eYdX5DbQ_yiTtCzUplsG2G1Pp-mVrjUUHJs5AkNasC8"
SHEET_NAME = "vagas_messejana"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


def buscar_vagas():
    """Faz web scraping no site do IDT e retorna as vagas disponíveis em Fortaleza:U.A. Messejana"""
    url = "https://idt.org.br/vagas-disponiveis"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    site = BeautifulSoup(response.content, 'html.parser')
    vagas = site.find('table', attrs={'class': 'table'})
    
    if not vagas:
        return []

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

                # Verifica se a ocupação é "PESSOA COM DEFICIÊNCIA" (caso esteja separada)
                if "PESSOA COM" in ocupacao and "DEFICIÊNCIA" in quantidade:
                    ocupacao = "PESSOA COM DEFICIÊNCIA"
                    quantidade = "N/A"  # Caso não tenha uma quantidade específica

                dados.append([ocupacao, quantidade])

    return dados


def enviar_para_google_sheets(dados):
    """Envia os dados para a planilha do Google Sheets"""
    if not dados:
        return "Nenhuma vaga encontrada."

    # Atualiza a planilha corrigindo a separação errada
    sheet.update("A1:B{}".format(len(dados) + 1), [["Ocupação", "Quantidade"]] + dados)
    return "Dados enviados com sucesso para o Google Sheets!"


@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')


@app.route('/buscar-vagas', methods=['GET'])
def buscar_e_exibir():
    """Busca as vagas e exibe como JSON"""
    vagas = buscar_vagas()
    if not vagas:
        return jsonify({"mensagem": "Nenhuma vaga encontrada"}), 404

    enviar_para_google_sheets(vagas)
    return jsonify({"vagas": vagas, "mensagem": "Dados atualizados no Google Sheets!"})


if __name__ == '__main__':
    app.run(debug=True)
