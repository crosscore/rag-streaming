import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv
import ast

load_dotenv()

conn = psycopg2.connect(
    dbname="vectordb",
    user="user",
    password="password",
    host="localhost",
    port="5432"
)

query = "SELECT * FROM toc_table;"
df = pd.read_sql_query(query, conn)
print(df)

# toc_vectorカラムをリストに変換
df['toc_vector'] = df['toc_vector'].apply(ast.literal_eval)

print("------")

for i in range(10):
    print(len(df['toc_vector'][i]))

conn.close()
