from fastapi import FastAPI, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import PageVisit, User
from db import Base, engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth import *
from datetime import datetime
from processing import clean_content
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from embedding import get_embedding
from vector_dao import index, id_map, add_to_vector_store
import numpy as np

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RegisterUser(BaseModel):
    email: str
    password: str

class PageVisitCreate(BaseModel):
    url: str
    title: str
    visit_time: datetime

@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/page_visits")
def add_page_visit(pv: PageVisitCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token).get("sub")
    user = db.query(User).get(int(user_id))
    new_pv = PageVisit(**pv.dict(), owner=user)
    db.add(new_pv)
    db.commit()
    db.refresh(new_pv)
    return new_pv


class SearchQuery(BaseModel):
    q: str
    k: int = 5

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
        cleaned_content = clean_content(visit.content)
        embedding = get_embedding(cleaned_content)
        add_to_vector_store(visit.url, embedding)
    except Exception as e:
        print("Embedding or FAISS add failed:", e)

    return {"status": "stored + embedded"}

@app.post("/semantic_search")
def semantic_search(searchQuery: SearchQuery):
    q = searchQuery.q
    k = searchQuery.k
    query_vec = np.array(get_embedding(q), dtype='float32').reshape(1, -1)
    D, I = index.search(query_vec, k)

    results = []
    for idx in I[0]:
        if idx < len(id_map):
            results.append({"url": id_map[idx]})
    # print(results)
    return {"results": results}

@app.post("/show_results")
def show_results(urls: list[str] = Body(...)):
    db = SessionLocal()
    results = []

    for url in urls:
        record = db.query(PageVisit).filter_by(url=url).first()
        if record:
            results.append({
                "url": record.url,
                "title": record.title,
                "favicon": f"https://www.google.com/s2/favicons?sz=64&domain={record.url}"
            })
    
    db.close()
    return {"results": results}