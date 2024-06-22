from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import numpy as np
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API keyの設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# データベース接続情報
POSTGRES_DB = os.getenv("POSTGRES_DB", "tocdb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "pgvector_toc")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# S3_DB URL
S3_DB_URL = os.getenv("S3_DB_URL", "http://localhost:9000")

# OpenAI Embeddingsの初期化
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENAI_API_KEY,
)

class SearchQuery(BaseModel):
    query: str
    top_n: int = 3

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

@app.post("/search")
async def search(query: SearchQuery):
    try:
        # クエリをベクトル化し、正規化
        query_vector = normalize_vector(embeddings.embed_query(query.query))

        # PostgreSQLに接続
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # 類似検索クエリの実行
        similarity_search_query = """
        SELECT file_name, toc, page, toc_vector, (toc_vector <#> %s::vector) AS distance
        FROM toc_table
        ORDER BY distance ASC
        LIMIT %s;
        """
        cursor.execute(similarity_search_query, (query_vector.tolist(), query.top_n))
        results = cursor.fetchall()

        # 結果の整形
        formatted_results = [
            {
                "file_name": result[0],
                "toc": result[1],
                "page": result[2],
                "distance": float(result[4]),
                "link_text": f"{result[0]}, p.{result[2]}",
                "pdf_url": f"{S3_DB_URL}/pdf/{result[0]}?page={result[2]}"
            }
            for result in results
        ]

        cursor.close()
        conn.close()

        return {"results": formatted_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
