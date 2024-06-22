rag-streaming/
├── frontend/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── static/
│   └── templates/
│       └── index.html
│
├── backend/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── utils/
│       └── vector_operations.py
│
├── pgvector_toc/
│   ├── Dockerfile
│   └── init_pgvector.sql
│
├── s3_db/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── data/
│       └── pdf/
│
├── docker-compose.yml
└── .env
