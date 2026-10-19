
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticRetriever:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def build_index(self, chunks: list[dict]) -> None:
        """Create a FAISS index from text chunks."""
        if not chunks:
            raise ValueError("Cannot build an index from empty chunks.")

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        embeddings = np.asarray(embeddings, dtype="float32")

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.chunks = chunks

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the most relevant chunks for a question."""
        if self.index is None:
            raise RuntimeError("Build the index before searching.")

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        query_embedding = np.asarray(query_embedding, dtype="float32")

        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_embedding, k)

        results = []
        for score, index in zip(scores[0], indices[0]):
            if index >= 0:
                chunk = self.chunks[int(index)]
                results.append({
                    **chunk,
                    "score": float(score),
                })

        return results
