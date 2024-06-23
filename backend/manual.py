# backend/manual.py

import boto3
import openpyxl
from io import BytesIO
import psycopg2
from psycopg2.extras import execute_values
from langchain_openai import OpenAIEmbeddings
import numpy as np
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENAI_API_KEY,
)

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

def get_xlsx_files_from_s3(bucket_name, prefix='data/xlsx/'):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.xlsx')]

def process_xlsx_file(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read()

    workbook = openpyxl.load_workbook(filename=BytesIO(file_content), read_only=True)

    file_data = []
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        for row in sheet.iter_rows(values_only=True):
            if any(cell for cell in row):
                manual = ','.join(str(cell) if cell is not None else '' for cell in row)
                file_data.append({
                    'file_name': file_key.split('/')[-1],
                    'sheet_name': sheet_name,
                    'manual': manual
                })

    return file_data

def vectorize_and_normalize_text(text):
    try:
        vector = embeddings.embed_query(text)
        return normalize_vector(vector).tolist()
    except Exception as e:
        print(f"Error vectorizing text: {e}")
        return None

def create_table_if_not_exists(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pgvector_manual (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            sheet_name TEXT,
            manual TEXT,
            manual_vector vector(1536)
        )
        """)
    conn.commit()

def save_to_database(conn, data):
    create_table_if_not_exists(conn)

    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO pgvector_manual (file_name, sheet_name, manual, manual_vector)
        VALUES %s
        ON CONFLICT (file_name, sheet_name, manual) DO NOTHING
        """
        values = [
            (item['file_name'], item['sheet_name'], item['manual'], vectorize_and_normalize_text(item['manual']))
            for item in data
            if vectorize_and_normalize_text(item['manual']) is not None
        ]
        execute_values(cur, insert_query, values)

    conn.commit()

def main():
    bucket_name = 'your-s3-bucket-name'
    db_connection_string = "postgresql://user:password@host:port/dbname"

    xlsx_files = get_xlsx_files_from_s3(bucket_name)

    conn = psycopg2.connect(db_connection_string)

    try:
        for file_key in xlsx_files:
            print(f"Processing file: {file_key}")
            file_data = process_xlsx_file(bucket_name, file_key)
            save_to_database(conn, file_data)
            print(f"Processed and saved data from {file_key}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
