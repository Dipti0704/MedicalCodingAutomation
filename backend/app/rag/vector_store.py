from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorStore:
    def __init__(self, dataframe):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = dataframe["description"].tolist()
        self.codes = dataframe["code"].tolist()

        self.embeddings = self.model.encode(self.texts, convert_to_numpy=True)

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

    def search(self, query, top_k=1):
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Convert distance to confidence (lower distance = higher confidence)
            confidence = max(0, int(100 - dist * 10))

            results.append({
                "code": self.codes[idx],
                "description": self.texts[idx],
                "confidence": confidence
            })

        return results
