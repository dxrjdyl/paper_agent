from typing import List, Dict, Any
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from config import CHROMA_DIR, EMBEDDING_MODEL

class VectorStore:
    def __init__(self, collection_name: str = "graduate_literature"):
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def add_paper_chunks(self, paper_id: str, title: str, chunks: List[str]):
        if not chunks:
            return
        ids = [f"{paper_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"paper_id": paper_id, "title": title, "chunk_index": i} for i in range(len(chunks))]
        try:
            self.collection.delete(ids=ids)
        except Exception:
            pass
        self.collection.add(ids=ids, documents=chunks, metadatas=metadatas)

    def search(self, query: str, n_results: int = 6) -> List[Dict[str, Any]]:
        res = self.collection.query(query_texts=[query], n_results=n_results)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        ids = res.get("ids", [[]])[0]
        out = []
        for i, doc in enumerate(docs):
            out.append({
                "id": ids[i] if i < len(ids) else "",
                "content": doc,
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else None,
            })
        return out
