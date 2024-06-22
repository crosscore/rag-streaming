import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import ast

load_dotenv()

POSTGRES_NAME = "vectordb"
POSTGRES_USER = "user"
POSTGRES_PASSWORD = "password"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

# SQLAlchemyエンジンの作成
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
engine = create_engine(POSTGRES_URL)

query = "SELECT * FROM toc_table"
df = pd.read_sql(query, engine)

# toc_vectorカラムをリストに変換
df['toc_vector'] = df['toc_vector'].apply(ast.literal_eval)
print(df)
print("---------")

for i in range(10):
    print(len(df['toc_vector'][i]))
