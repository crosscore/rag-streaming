import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import ast

load_dotenv()

POSTGRES_TOC_DB = os.getenv("POSTGRES_TOC_DB")
POSTGRES_TOC_USER = os.getenv("POSTGRES_TOC_USER")
POSTGRES_TOC_PASSWORD = os.getenv("POSTGRES_TOC_PASSWORD")
POSTGRES_TOC_HOST = "localhost"
POSTGRES_TOC_PORT = os.getenv("POSTGRES_TOC_PORT")

# SQLAlchemyエンジンの作成
POSTGRES_TOC_URL = f"postgresql://{POSTGRES_TOC_USER}:{POSTGRES_TOC_PASSWORD}@{POSTGRES_TOC_HOST}:{POSTGRES_TOC_PORT}/{POSTGRES_TOC_DB}"
engine = create_engine(POSTGRES_TOC_URL)

query = "SELECT * FROM toc_table"
df = pd.read_sql(query, engine)

# toc_vectorカラムをリストに変換
df['toc_vector'] = df['toc_vector'].apply(ast.literal_eval)
print(df)
print("---------")

for i in range(10):
    print(len(df['toc_vector'][i]))
