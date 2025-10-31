import chromadb
from openai import OpenAI
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.client.get_or_create_collection("agro_docs")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def add_document(self, text: str, metadata: dict):
        emb = self.openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL, input=text
        ).data[0].embedding
        self.collection.add(documents=[text], embeddings=[emb],
                            metadatas=[metadata], ids=[metadata["id"]])

    def query(self, query: str, n=3):
        q_emb = self.openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL, input=query
        ).data[0].embedding
        results = self.collection.query(query_embeddings=[q_emb], n_results=n)
        return results["documents"], results["metadatas"]
