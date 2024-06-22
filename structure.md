rag_streaming/
│
├── .env
├── docker-compose.yml
│
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   └── ...
│   └── templates/
│       ├── index.html
│       └── ...
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── return_answer.py
│   │   └── ...
│   └── data/
│       └── csv/
│           └── vector/
│               └── ... (vectorized CSV files)
│
├── pgvector_toc/
│   ├── Dockerfile
│   └── init-pgvector.sql
│
└── s3_db/
    ├── Dockerfile
    ├── app.py
    └── data/
        ├── pdf/
        │   └── ... (PDF files)
        ├── docx/
        │   └── ... (DOCX files)
        └── xlsx/
            └── ... (XLSX files)
