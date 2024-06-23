import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import ast

load_dotenv()

POSTGRES_MANUAL_NAME = os.getenv("POSTGRES_MANUAL_NAME")
POSTGRES_MANUAL_USER = os.getenv("POSTGRES_MANUAL_USER")
POSTGRES_MANUAL_PASSWORD = os.getenv("POSTGRES_MANUAL_PASSWORD")
POSTGRES_MANUAL_HOST = "localhost"
POSTGRES_MANUAL_PORT = os.getenv("POSTGRES_MANUAL_PORT")

# SQLAlchemyエンジンの作成
POSTGRES_MANUAL_URL = f"postgresql://{POSTGRES_MANUAL_USER}:{POSTGRES_MANUAL_PASSWORD}@{POSTGRES_MANUAL_HOST}:{POSTGRES_MANUAL_PORT}/{POSTGRES_MANUAL_NAME}"
engine = create_engine(POSTGRES_MANUAL_URL)

query = "SELECT * FROM manual_table"
df = pd.read_sql(query, engine)

# manual_vectorカラムをリストに変換
df['manual_vector'] = df['manual_vector'].apply(ast.literal_eval)
print(df)
print("---------")

for i in range(10):
    print(len(df['manual_vector'][i]))
