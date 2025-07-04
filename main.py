from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import PageVisit
from db import Base, engine, SessionLocal
from pydantic import BaseModel
from datetime import datetime

from embedding import get_embedding
from vector_store import index, id_map, add_to_vector_store
import numpy as np

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class PageVisitInput(BaseModel):
    url: str
    title: str
    content: str
    timestamp: str


@app.post("/page_visit")
def store_page(visit: PageVisitInput):
    db = SessionLocal()
    page = PageVisit(
        url=visit.url,
        title=visit.title,
        content=visit.content,
        timestamp=datetime.fromisoformat(visit.timestamp.replace("Z", ""))
    )
    db.merge(page)
    db.commit()
    db.close()

    try:
        embedding = get_embedding(visit.content)
        add_to_vector_store(visit.url, embedding)
    except Exception as e:
        print("Embedding or FAISS add failed:", e)

    return {"status": "stored + embedded"}

@app.get("/semantic_search")
def semantic_search(q: str, k: int = 5):
    query_vec = np.array(get_embedding(q), dtype='float32').reshape(1, -1)
    D, I = index.search(query_vec, k)

    results = []
    for idx in I[0]:
        if idx < len(id_map):
            results.append({"url": id_map[idx]})

    return {"results": results}

