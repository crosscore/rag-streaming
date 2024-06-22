import pandas as pd
import os
import glob
from dotenv import load_dotenv
import psycopg2
import ast
import time
import logging

load_dotenv()

# ロギングの設定
os.makedirs('../../log', exist_ok=True)
logging.basicConfig(filename='../../log/database_connection.log', level=logging.INFO)

max_retries = 10
retry_delay = 2  # 秒

for attempt in range(max_retries):
    try:
        conn = psycopg2.connect(
            dbname="vectordb",
            user="user",
            password="password",
            host="localhost",
            port="5432"
        )
        logging.info("Connected to the database successfully on attempt %d", attempt + 1)
        print("Connected to the database successfully")
        break
    except psycopg2.OperationalError as e:
        logging.error("Attempt %d failed: %s", attempt + 1, e)
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logging.critical("Max retries reached, failed to connect to the database")
            print("Max retries reached, failed to connect to the database")
            raise

print("ログファイルに接続結果が記録されました。")


cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS toc_table (
    id SERIAL PRIMARY KEY,
    file_name TEXT,
    toc TEXT,
    page INTEGER,
    toc_vector vector(3072)
);
"""
cursor.execute(create_table_query)
conn.commit()

input_directory = '../../data/csv/vector/'
csv_files = glob.glob(os.path.join(input_directory, '*.csv'))
print(f"Found CSV files: {csv_files}")

# 全CSVファイルに対してベクトル化の処理を実行
for input_file_path in csv_files:
    df = pd.read_csv(input_file_path)

    # ベクトルデータをPostgreSQLに挿入
    for index, row in df.iterrows():
        try:
            print(f"Inserting row: {row}")

            # ベクトルをリスト形式に変換
            toc_vector = ast.literal_eval(row['toc_vector'])

            # リストの各要素をfloatにキャスト
            toc_vector = [float(x) for x in toc_vector]

            insert_query = """
            INSERT INTO toc_table (file_name, toc, page, toc_vector)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_query, (row['file_name'], row['toc'], row['page'], toc_vector))
            print("Row inserted")
        except Exception as e:
            print(f"Error inserting row: {e}")

    conn.commit()

cursor.close()
conn.close()
