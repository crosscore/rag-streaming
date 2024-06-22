from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from sqlalchemy import create_engine, text
from openai import OpenAI

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

engine = create_engine(DATABASE_URL)
client = OpenAI(api_key=OPENAI_API_KEY)

class Query(BaseModel):
    question: str

@app.post("/query")
async def query(query: Query):
    # Embed the question
    response = client.embeddings.create(input=query.question, model="text-embedding-ada-002")
    question_embedding = response.data[0].embedding

    # Query the database
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT toc, file_name, page, 1 - (embedding <=> :embedding) AS cosine_similarity
            FROM documents
            ORDER BY cosine_similarity DESC
            LIMIT 3
        """), {"embedding": question_embedding})

        results = [
            {
                "rank": i + 1,
                "toc": row.toc,
                "file_name": row.file_name,
                "page": row.page,
                "distance": float(row.cosine_similarity)
            }
            for i, row in enumerate(result)
        ]

    return results
