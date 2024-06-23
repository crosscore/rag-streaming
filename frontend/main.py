# frontend/main.py

from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8001")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async with httpx.AsyncClient() as client:
        while True:
            question = await websocket.receive_text()
            response = await client.post(f"{BACKEND_URL}/search", json={"question": question})
            results = response.json()["results"]
            formatted_results = [
                {
                    "link": result['pdf_url'],
                    "title": result['link_text'],
                    "toc": result['toc'],
                    "distance": result['distance']
                }
                for result in results
            ]
            await websocket.send_json(formatted_results)
