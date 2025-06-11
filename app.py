import re
from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials  # type: ignore
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


app = Flask(__name__)

# Configuração da API do Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
client = gspread.authorize(credentials)

# ID da planilha e nome da aba
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "vagas_messejana"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


def buscar_vagas():
    """Faz web scraping no site do IDT e retorna as vagas e a data de atualização"""
    url = "https://idt.org.br/vagas-disponiveis"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return [], "Data de atualização indisponível"

    site = BeautifulSoup(response.content, 'html.parser')
    vagas = site.find('table', attrs={'class': 'table'})

    # Captura a primeira data no <strong> que bate com o formato DD/MM/YYYY HH:MM
    data_atualizacao = "Data de atualização não encontrada"
    for strong in site.find_all('strong'):
        texto = strong.get_text().strip()
        if re.match(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", texto):
            data_atualizacao = texto
            break

    if not vagas:
        return [], data_atualizacao

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

                # Corrige separação indevida de "PESSOA COM DEFICIÊNCIA"
                if ocupacao == "PESSOA COM" and quantidade == "DEFICIÊNCIA":
                    ocupacao = "PESSOA COM DEFICIÊNCIA"
                    quantidade = "N/A"

                dados.append([ocupacao, quantidade])

    return dados, data_atualizacao

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
    vagas, data_atualizacao = buscar_vagas()
    if not vagas:
        return jsonify({"mensagem": "Nenhuma vaga encontrada", "data": data_atualizacao}), 404

    enviar_para_google_sheets(vagas)
    return jsonify({
        "vagas": vagas,
        "mensagem": "Dados atualizados no Google Sheets!",
        "data": data_atualizacao
    })



if __name__ == '__main__':
    app.run(debug=True)
