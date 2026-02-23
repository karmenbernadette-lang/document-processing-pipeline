# Document Processing Pipeline (M02)

This project implements a document processing pipeline that ingests PDF and TXT documents, extracts structured text and metadata, generates vector embeddings, and stores results in a Qdrant vector database.

Milestone M02 establishes ingestion, processing, embedding, storage, Docker deployment, and CI/CD configuration.

---

# Architecture Overview

data/input  
↓  
Ingestion (ingest.py)  
↓  
Text Extraction (extract_text.py)  
↓  
Cleaning + Tokenization (chunk_text.py)  
↓  
Chunking  
↓  
Embedding (sentence-transformers)  
↓  
Vector Database (Qdrant)  
↓  
data/output  

---

# Components

- **Ingestion Module** – Reads files from `data/input`
- **Text Extraction Module** – Extracts text and metadata from PDFs and TXT
- **Metadata Extraction** – Title, author, creation date, page count
- **Chunking Module** – Cleans text, removes stop words, tokenizes, creates chunks
- **Embedding Module** – Generates vector embeddings
- **Database Module** – Stores embeddings and metadata in Qdrant
- **CI/CD** – GitHub Actions workflow validates the pipeline on push

---

# Prerequisites

- Python 3.9+
- Docker Desktop
- Git

---

# Complete Setup & Run Instructions (Copy Once)

```bash
# 1️⃣ Clone the Repository
git clone https://github.com/karmenbernadette-lang/document-processing-pipeline.git
cd document-processing-pipeline

# 2️⃣ Create Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# 3️⃣ Install Dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    pip install pymupdf qdrant-client sentence-transformers scikit-learn
fi

# 4️⃣ Start Qdrant Database
docker compose up -d

# 5️⃣ Verify Qdrant is Running
curl http://localhost:6333/healthz

# 6️⃣ Run the Pipeline
PYTHONPATH=src python -m pipeline.run_ingest
```

---

# Adding Documents

Place PDF or TXT files inside:

```
data/input/
```

Then re-run:

```bash
PYTHONPATH=src python -m pipeline.run_ingest
```

---

# Verify Database Storage

Check collections:

```bash
curl http://localhost:6333/collections
```

You should see:

```
m02_documents
```

---

# Output Artifacts

Generated files are saved in:

```
data/output/
```

Artifacts include:

- *_raw.txt  
- *_chunks.json  
- ingestion_manifest.json  

---

# CI/CD

This repository includes:

```
.github/workflows/ci.yml
```

On every push to `main`, GitHub Actions:

- Sets up Python  
- Installs dependencies  
- Verifies pipeline imports successfully  

This satisfies the CI/CD requirement for M02.

---

# Acceptance Criteria Coverage

✔ Reads PDF and TXT files  
✔ Extracts metadata  
✔ Cleans and tokenizes text  
✔ Generates chunks  
✔ Produces vector embeddings  
✔ Stores embeddings in Qdrant  
✔ Dockerized database  
✔ CI/CD configured  

---

# Author

Karmen Elvis  
M02 – Data Pipeline & CI/CD

