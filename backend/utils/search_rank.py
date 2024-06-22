import psycopg2
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
import glob

load_dotenv()

def get_vector_from_csv(csv_file_path, row_number):
    df = pd.read_csv(csv_file_path)
    if row_number < 0 or row_number >= len(df):
        raise ValueError("Invalid row number")
    search_vector = df.iloc[row_number]['search_vector']
    print(f"検索文字列：{df.iloc[row_number]['search_text']}")
    return np.array(eval(search_vector))

def display_results(results):
    if results:
        for rank, result in enumerate(results, start=1):
            file_name, toc, page, toc_vector, distance = result
            print(f"Rank {rank}: file_name: {file_name}, toc: {toc}, page: {page}, distance: {distance}")
    else:
        print("No results found")

SEARCH_INDEX = 0 #検索用のインデックスを指定

# CSVファイルからベクトルを取得
csv_files = glob.glob('../data/csv/search_vector/*.csv')
print(f"CSV file path: {csv_files[0]}")
normalize_search_vector = get_vector_from_csv(csv_files[0], SEARCH_INDEX)
print(f"Normalized Search Vector: {normalize_search_vector}")

# PostgreSQLに接続
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "tocdb"),
    user=os.getenv("POSTGRES_USER", "user"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    host="localhost",
    port=os.getenv("POSTGRES_PORT", "5432")
)
cursor = conn.cursor()

# 類似検索クエリの実行
similarity_search_query = """
SELECT file_name, toc, page, toc_vector, (toc_vector <#> %s::vector) AS distance
FROM toc_table
ORDER BY distance ASC
LIMIT 11;
"""
print("Executing similarity search query...\n")
cursor.execute(similarity_search_query, (normalize_search_vector.tolist(),))
results = cursor.fetchall()

# 検索結果の表示
display_results(results)

cursor.close()
conn.close()
