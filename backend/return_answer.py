from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import psycopg2
import numpy as np
from langchain_openai import OpenAIEmbeddings
from typing import List

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_NAME = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# OpenAI Embeddingsの初期化
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENAI_API_KEY,
)

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    file_name: str
    toc: str
    page: int
    similarity: float

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

def get_POSTGRES_connection():
    return psycopg2.connect(
        dbname=POSTGRES_NAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )

@app.post("/query", response_model=List[Answer])
async def query(question: Question):
    try:
        # 質問文をベクトル化し、正規化
        question_vector = normalize_vector(embeddings.embed_query(question.text))

        # データベース接続
        conn = get_POSTGRES_connection()
        cursor = conn.cursor()

        # 類似検索クエリの実行
        query = """
        SELECT file_name, toc, page, 1 - (toc_vector <#> %s) AS distance
        FROM toc_table
        ORDER BY distance DESC
        LIMIT 3;
        """
        cursor.execute(query, (question_vector.tolist(),))
        results = cursor.fetchall()

        # 結果の整形
        answers = [
            Answer(
                file_name=row[0],
                toc=row[1],
                page=row[2],
                similarity=float(row[3])
            )
            for row in results
        ]

        cursor.close()
        conn.close()

        return answers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
