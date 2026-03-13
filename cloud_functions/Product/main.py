import functions_framework
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
from google.cloud import bigquery
import json
import os
from dotenv import load_dotenv

load_dotenv()

def extract(url, startDate, endDate, websiteId):
    try:
        fuso_horario = pytz.timezone('America/Sao_Paulo')
        atual = datetime.now(fuso_horario)
        anterior = atual - timedelta(hours=1, minutes=50)
        data_atual = atual.strftime("%Y-%m-%d %H:%M:%S")
        data_anterior = anterior.strftime("%Y-%m-%d %H:%M:%S")

        params = {
            "startDate": startDate,
            "endDate": endDate,
            "channelId": int(os.environ.get('CHANNEL_ID')),
            "websiteId": websiteId
        }

        headers = {
            "accept": os.environ.get('ACCEPT_HEADER'),
            "Authorization": f"Bearer {os.environ.get('API_TOKEN')}"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Cada linha do NDJSON é um produto
        products = [json.loads(line) for line in response.text.splitlines() if line.strip()]

        rows = []
        for product in products:
            row = {
                "id": product.get("id"),
                "name": product.get("name"),
                "notes": product.get("notes"),
                "value": product.get("value"),
                "isActive": product.get("isActive"),
                "isDeleted": product.get("isDeleted"),
                "isControlQuotas": product.get("isControlQuotas"),
                "isControlBalance": product.get("isControlBalance"),
                "isAutomaticDistributedScheduling": product.get("isAutomaticDistributedScheduling"),
                "isProposalAddItems": product.get("isProposalAddItems"),
                "isDigitalProposalAddItems": product.get("isDigitalProposalAddItems"),
                "startDate": product.get("startDate"),
                "endDate": product.get("endDate"),
                "companyId": product.get("companyId"),
                "companyGroupId": product.get("companyGroupId"),
                "tags": product.get("tags"),
                "externalCode": product.get("externalCode"),
                "origin": product.get("origin"),
                "registerDate": product.get("registerDate"),
                "lastUpdateDate": product.get("lastUpdateDate"),
                "isAvailableOnEmidiaPortal": product.get("isAvailableOnEmidiaPortal"),
            }
            rows.append(row)

        return pd.DataFrame(rows)

    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    

def transform(data):
    if data is None or data.empty:
        return None

    data.rename(columns={
        "id": "ID_PRODUTO",
        "name": "NAME_PRODUTO",
        "notes": "NOTAS",
        "registerDate": "DATA_REGISTRO",
        "lastUpdateDate": "ULTIMADATA_ATUALIZACAO",
        "value": "VALOR_PRODUTO",
        "isActive": "STATUS",
        "isDeleted": "DELETADO",
        "isControlQuotas": "CONTROLA_COTAS",
        "isControlBalance": "CONSUMO_SALDO_VEICULACAO",
        "isAvailableOnEmidiaPortal": "PORTAL_E-MIDIA",
        "tags": "TAGS",
        "externalCode": "CODIGO_EXTERNO",
        "companyId": "ID_COMPANHIA",
        "companyGroupId": "ID_GRUPO_COMPANHIA",
        "startDate": "DATA_INICIO",
        "endDate": "DATA_FINAL",
        "origin": "ORIGEM_PRODUTO"
    }, inplace=True)

    # Conversões seguras
    for col in ["DATA_REGISTRO", "ULTIMADATA_ATUALIZACAO", "DATA_INICIO", "DATA_FINAL"]:
        data[col] = pd.to_datetime(data[col], errors='coerce')

    if "VALOR_PRODUTO" in data.columns:
        data["VALOR_PRODUTO"] = pd.to_numeric(data["VALOR_PRODUTO"], errors='coerce')

    return data


def loadBigquery(df, table_id):
    if df is None:
        return "Sem dados carregados."

    try:
        client = bigquery.Client()
        job = client.load_table_from_dataframe(df, table_id)
        job.result()
        return f"Loaded {job.output_rows} rows into {table_id}"

    except Exception as e:
        print(f"Erro ao carregar no BigQuery: {e}")
        return None
    

@functions_framework.http
def main(request):
    url = os.environ.get('API_URL')
    startDate = os.environ.get('START_DATE')
    endDate = os.environ.get('END_DATE')
    websiteId = os.environ.get('WEBSITE_ID')
    table_id = os.environ.get('TABLE_ID_PRODUCT')

    # Extract
    data = extract(url, startDate, endDate, websiteId)
    if data is None:
        return {
            "status": "falha", 
            "message": "Extração de dados falhou."
        }, 500

    # Transform
    df_tratado = transform(data)
    if df_tratado is None:
        return {
            "status": "falha", 
            "message": "Transformação de dados falhou."
        }, 500
    
    # Load
    load_result = loadBigquery(df_tratado, table_id)
    if load_result is None:
        return {
            "status": "falha", 
            "message": "Carregamento falhou no BigQuery."
        }, 500

    return {
        "status": "success", 
        "message": load_result
    }, 200
