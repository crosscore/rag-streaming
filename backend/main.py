# backend/main.py

from fastapi import FastAPI, WebSocket, HTTPException
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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

POSTGRES_TOC_DB = os.getenv("POSTGRES_TOC_DB", "tocdb")
POSTGRES_TOC_USER = os.getenv("POSTGRES_TOC_USER", "user")
POSTGRES_TOC_PASSWORD = os.getenv("POSTGRES_TOC_PASSWORD", "password")
POSTGRES_TOC_HOST = os.getenv("POSTGRES_TOC_HOST", "pgvector_toc")
POSTGRES_TOC_PORT = os.getenv("POSTGRES_TOC_PORT", "5432")

S3_DB_URL = os.getenv("S3_DB_URL", "http://localhost:9000")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENAI_API_KEY,
)

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            question = data["question"]
            top_n = data.get("top_n", 3)

            # 文字列をベクトル化し、正規化
            question_vector = normalize_vector(embeddings.embed_query(question))

            conn = psycopg2.connect(
                dbname=POSTGRES_TOC_DB,
                user=POSTGRES_TOC_USER,
                password=POSTGRES_TOC_PASSWORD,
                host=POSTGRES_TOC_HOST,
                port=POSTGRES_TOC_PORT
            )
            cursor = conn.cursor()

            similarity_search_query = """
            SELECT file_name, toc, page, toc_vector, (toc_vector <#> %s::vector) AS distance
            FROM toc_table
            ORDER BY distance ASC
            LIMIT %s;
            """
            cursor.execute(similarity_search_query, (question_vector.tolist(), top_n))
            results = cursor.fetchall()

            # 結果の整形
            formatted_results = [
                {
                    "file_name": result[0],
                    "toc": result[1],
                    "page": result[2],
                    "distance": float(result[4]),
                    "link_text": f"{result[0]}, p.{result[2]}",
                    "pdf_url": f"{S3_DB_URL}/data/pdf/{result[0]}?page={result[2]}"
                }
                for result in results
            ]

            cursor.close()
            conn.close()

            await websocket.send_json({"results": formatted_results})

        except Exception as e:
            await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
