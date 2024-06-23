rag-streaming/
├── frontend/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       └── index.html
│
├── backend/
│   ├── main.py
│   ├── manual.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── utils/
│       └── vector_to_postgres.py
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
│       ├── pdf/
│       ├── xlsx/
│       └── docx/
│
├── docker-compose.yml
└── .env
