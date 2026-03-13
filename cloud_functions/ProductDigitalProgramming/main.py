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
        # Fusos horários
        fuso_horario = pytz.timezone('America/Sao_Paulo')

        # Parâmetros da API
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
            product_id = product.get("id")
            product_name = product.get("name")
            digitalprogramming_list = product.get("digitalProgrammingList", [])

            for programming in digitalprogramming_list:
                row = {
                    "PRODUCT_ID": product_id,
                    "PRODUCT_NAME": product_name,
                    "DIGITAL_PROGRAMMING_ID": programming.get("id"),
                    "DIGITAL_PROGRAMMING_REGISTER_DATE": programming.get("registerDate"),
                    "DIGITAL_PROGRAMMING_ITEMS_COUNT": len(programming.get("items", []))
                }
                rows.append(row)

        df = pd.DataFrame(rows)

        # Converter datas para datetime do pandas
        date_columns = ["DIGITAL_PROGRAMMING_REGISTER_DATE"]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')  # 'coerce' evita erro se houver valor inválido

        return df

    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def transform(df):
    if df is None or df.empty:
        return None

    # Retorna df pronto, datas já convertidas
    return df

def loadBigquery(df, table_id):
    if df is None or df.empty:
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
    table_id = os.environ.get('TABLE_ID_DIGITAL_PROGRAMMING')

    # Extract
    df = extract(url, startDate, endDate, websiteId)
    if df is None:
        return {"status": "falha", "message": "Extração de dados falhou."}, 500

    # Transform
    df_tratado = transform(df)
    if df_tratado is None:
        return {"status": "falha", "message": "Transformação de dados falhou."}, 500

    # Load
    load_result = loadBigquery(df_tratado, table_id)
    if load_result is None:
        return {"status": "falha", "message": "Carregamento falhou no BigQuery."}, 500

    return {"status": "success", "message": load_result}, 200
