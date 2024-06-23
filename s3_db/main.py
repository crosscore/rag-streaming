# s3_db/main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data/xlsx")
async def list_xlsx_files():
    xlsx_dir = '/app/data/xlsx'
    if not os.path.exists(xlsx_dir):
        raise HTTPException(status_code=404, detail="XLSX directory not found")
    xlsx_files = [f for f in os.listdir(xlsx_dir) if f.endswith('.xlsx')]
    return JSONResponse(content=xlsx_files)

@app.get("/data/xlsx/{filename:path}")
async def serve_xlsx(filename: str):
    file_path = os.path.join('/app/data/xlsx', filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/data/pdf/{filename:path}")
async def serve_pdf(filename: str, page: int = Query(None)):
    file_path = os.path.join('/app/data/pdf', filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    if page is None:
        return FileResponse(file_path, media_type='application/pdf')

    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        if 0 <= page - 1 < len(reader.pages):
            writer.add_page(reader.pages[page - 1])
        else:
            raise HTTPException(status_code=404, detail="Page not found")

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return StreamingResponse(output, media_type='application/pdf')
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
