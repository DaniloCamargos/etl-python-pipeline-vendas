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
                    row = {
                        "PRODUCT_ID": product_id,
                        "PRODUCT_NAME": product_name,
                        "PROGRAMMING_ID": programming.get("id"),
                        "ITEMS_ID": items.get("id"),
                        "ITEMS_REGISTER_DATE": items.get("registerDate"),
                        "ITEMS_LAST_UPDATE_DATE": items.get("lastUpdateDate"),
                        "ITEMS_START": items.get("start"),
                        "ITEMS_END": items.get("end"),
                        "ITEMS_DURATION_SECONDS": items.get("durationSeconds"),
                        "ITEMS_UNITARY_VALUE": items.get("unitaryValue"),
                        "ITEMS_NEGOTIATED_VALUE": items.get("negotiatedValue"),
                        "ITEMS_TABLE_VALUE": items.get("tableValue"),
                        "ITEMS_TOTAL_VALUE": items.get("totalValue"),
                        "ITEMS_DISCOUNT": items.get("discount"),
                        "ITEMS_MARKETING_DISCOUNT": items.get("marketingDiscount"),
                        "ITEMS_IS_LOCK_CHANGES": items.get("isLockChanges"),
                        "ITEMS_QUANTITY": items.get("quantity"),
                        "ITEMS_QUANTITY_TOTAL": items.get("quantityTotal"),
                        "ITEMS_DISTRIBUTION_TYPE": items.get("distributionType"),
                        "ITEMS_IS_PRODUCTION_COST_TO_DEFINE": items.get("isProductionCostToDefine"),
                        "ITEMS_PRODUCTION_COST_VALUE": items.get("productionCostValue"),
                    }
                    rows.append(row)

        df = pd.DataFrame(rows)

        # Converter datas
        date_columns = ["ITEMS_REGISTER_DATE", "ITEMS_START", "ITEMS_END", "ITEMS_LAST_UPDATE_DATE"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Garantir float para valores monetários
        float_cols = [
            "ITEMS_UNITARY_VALUE",
            "ITEMS_NEGOTIATED_VALUE",
            "ITEMS_TABLE_VALUE",
            "ITEMS_TOTAL_VALUE",
            "ITEMS_DISCOUNT",
            "ITEMS_MARKETING_DISCOUNT",
            "ITEMS_PRODUCTION_COST_VALUE",
        ]
        for col in float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

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
            bigquery.SchemaField("PRODUCT_ID", "INT64"),
            bigquery.SchemaField("PRODUCT_NAME", "STRING"),
            bigquery.SchemaField("PROGRAMMING_ID", "INT64"),
            bigquery.SchemaField("ITEMS_ID", "INT64"),
            bigquery.SchemaField("ITEMS_REGISTER_DATE", "TIMESTAMP"),
            bigquery.SchemaField("ITEMS_LAST_UPDATE_DATE", "TIMESTAMP"),
            bigquery.SchemaField("ITEMS_START", "TIMESTAMP"),
            bigquery.SchemaField("ITEMS_END", "TIMESTAMP"),
            bigquery.SchemaField("ITEMS_DURATION_SECONDS", "INT64"),
            bigquery.SchemaField("ITEMS_UNITARY_VALUE", "FLOAT64"),
            bigquery.SchemaField("ITEMS_NEGOTIATED_VALUE", "FLOAT64"),
            bigquery.SchemaField("ITEMS_TABLE_VALUE", "FLOAT64"),
            bigquery.SchemaField("ITEMS_TOTAL_VALUE", "FLOAT64"),
            bigquery.SchemaField("ITEMS_DISCOUNT", "FLOAT64"),
            bigquery.SchemaField("ITEMS_MARKETING_DISCOUNT", "FLOAT64"),
            bigquery.SchemaField("ITEMS_IS_LOCK_CHANGES", "BOOL"),
            bigquery.SchemaField("ITEMS_QUANTITY", "INT64"),
            bigquery.SchemaField("ITEMS_QUANTITY_TOTAL", "INT64"),
            bigquery.SchemaField("ITEMS_DISTRIBUTION_TYPE", "STRING"),
            bigquery.SchemaField("ITEMS_IS_PRODUCTION_COST_TO_DEFINE", "BOOL"),
            bigquery.SchemaField("ITEMS_PRODUCTION_COST_VALUE", "FLOAT64"),
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
    table_id = os.environ.get('TABLE_ID_PROGRAMMING_ITEMS')

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
