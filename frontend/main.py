from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8001")
S3_URL = os.getenv("S3_URL", "http://localhost:9000")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async with httpx.AsyncClient() as client:
        while True:
            question = await websocket.receive_text()
            response = await client.post(f"{BACKEND_URL}/query", json={"question": question})
            results = response.json()
            formatted_results = [
                {
                    "link": f"{S3_URL}/pdf/{result['file_name']}#page={result['page']}",
                    "title": f"{result['file_name']} - Page {result['page']}",
                    "toc": result['toc'],
                    "rank": result['rank'],
                    "distance": result['distance']
                }
                for result in results
            ]
            await websocket.send_json(formatted_results)
