import faiss
import numpy as np
import os
import pickle

DIMENSION = 1536
INDEX_PATH = "faiss.index"
ID_MAP_PATH = "vector_ids.pkl"

# Load or create FAISS index and ID map
if os.path.exists(INDEX_PATH) and os.path.exists(ID_MAP_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(ID_MAP_PATH, "rb") as f:
        id_map = pickle.load(f)
else:
    index = faiss.IndexFlatL2(DIMENSION)
    id_map = []

def normalize(vec):
    return vec / np.linalg.norm(vec)

def add_to_vector_store(url: str, embedding: list[float]):
    vec = normalize(np.array(embedding, dtype='float32')).reshape(1, -1)
    index.add(vec)
    id_map.append(url)

    # Persist index and ID map to disk
    faiss.write_index(index, INDEX_PATH)
    with open(ID_MAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

def search_similar(query_embedding: list[float], k=5):
    if index.ntotal == 0:
        return []

    query_vec = normalize(np.array(query_embedding, dtype='float32')).reshape(1, -1)
    D, I = index.search(query_vec, k)

    results = []
    for idx in I[0]:
        if idx < len(id_map):
            results.append(id_map[idx])
    return results
