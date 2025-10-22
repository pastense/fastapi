import openai
import os
from pastense_ui import KeyStore
from pathlib import Path


openai.api_key = str(KeyStore().get("OpenAI"))

def get_embedding(text: str) -> list[float]:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text[:1000]  # truncate if needed
    )
    return response.data[0].embedding
