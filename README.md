# Pastense Backend (FastAPI)
The local backend service for Pastense — a privacy-first semantic search layer for your browser history.

## Overview
This FastAPI service powers the backend for the Pastense browser extension.  
It:
- Receives page metadata from the extension (URL, title, text content)
- Generates semantic embeddings using the OpenAI API
- Stores them in a local SQLite (or FAISS) database
- Exposes `/semantic_search`, `/page_visit`, `/show_results` endpoints for querying and indexing
- Serves a simple frontend on the base URL (https://127.0.0.1:8000) using NiceGUI

## Architecture
Extension → FastAPI → Local Vector Store (SQLite/FAISS)

## Setup

### Prerequisites
- Python 3.10+
- OpenAI API key
- (Optional) platformdirs for cross-OS path handling (eg. DB_PATH=/Users/yourname/Library/Application Support/Pastense/visits.db on MacOS)


### Installation
```
git clone https://github.com/pastense/fastapi.git
cd fastapi
python3 -m venv env # create virtual environment
source env/bin/activate # activate virtual environment
pip install -r requirements.txt # install requirements required to run this FastAPI
```

## Run Locally

`uvicorn main:app --reload`



Feel free to add an issue in the issues tab for feature requests or architectural discussions.
