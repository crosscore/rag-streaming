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
│   └── src/
│       ├── main.py
│       ├── return_answer.py
│       └── ...
│
├── pgvector_toc/
│   ├── Dockerfile
│   └── init-pgvector.sql
│
├── s3_db/
│   ├── Dockerfile
│   ├── app.py
│   └── data/
│       └── pdf/
│           └── ... (PDF files)
│
└── data/
    ├── csv/
    │   ├── original/
    │   │   └── ... (original CSV files)
    │   └── vector/
    │       └── ... (vectorized CSV files)
    └── pdf/
        └── ... (original PDF files)
