import functions_framework
import pandas as pd
import requests
from google.cloud import bigquery
import json
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

def extract(url, startDate, endDate, websiteId):
    try:
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

        products = [json.loads(line) for line in response.text.splitlines() if line.strip()]

        rows = []

        for product in products:
            product_id = product.get("id")
            product_name = product.get("name")
            programming_list = product.get("programmingList", [])

            for programming in programming_list:
                items_list = programming.get("items", [])

                for items in items_list:
                    Program_dict = items.get("program")   
                    row = {
                        "ITEMS_ID": items.get("id"),
                        "PROGRAM_ID": Program_dict.get("id")
                        if isinstance(Program_dict, dict) 
                        else None,

                        "PROGRAM_NAME": Program_dict.get("name")
                        if isinstance(Program_dict, dict) 
                        else None,

                        "PROGRAM_INITIALS": Program_dict.get("initials")
                        if isinstance(Program_dict, dict)
                        else None,
                    }
                    rows.append(row)

        df = pd.DataFrame(rows)

        return df

    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def transform(df):

    if df is None or df.empty:
        return None
    
    return df

def loadBigquery(df, table_id):
    if df is None or df.empty:
        return "Sem dados carregados."

    try:

        client = bigquery.Client()

        schema = [
            bigquery.SchemaField("ITEMS_ID", "INT64"),
            bigquery.SchemaField("PROGRAM_ID", "INT64"),
            bigquery.SchemaField("PROGRAM_NAME", "STRING"),
            bigquery.SchemaField("PROGRAM_INITIALS", "STRING"),
        ]

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition="WRITE_APPEND"
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
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
    table_id = os.environ.get('TABLE_ID_PROGRAMMING_ITEMS_PROGRAM')

    df = extract(url, startDate, endDate, websiteId)
    if df is None:
        return {"status": "falha", "message": "Extração de dados falhou."}, 500

    df_tratado = transform(df)
    if df_tratado is None:
        return {"status": "falha", "message": "Transformação de dados falhou."}, 500

    load_result = loadBigquery(df_tratado, table_id)
    if load_result is None:
        return {"status": "falha", "message": "Carregamento falhou no BigQuery."}, 500

    return {"status": "success", "message": load_result}, 200
