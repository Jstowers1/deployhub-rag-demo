import os
import re
from dataclasses import dataclass, field

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHUNK_SIZE = 500  # chars; split on paragraph boundaries
CHUNK_OVERLAP = 50


@dataclass
class Chunk:
    text: str
    source: str  # filename
    heading: str  # nearest markdown heading


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


def load_documents(data_dir=DATA_DIR):
    docs = []
    for fname in sorted(os.listdir(data_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(data_dir, fname)
        with open(path, encoding="utf-8") as f:
            docs.append((fname, f.read()))
    return docs


def chunk_document(text, source):
    # split into sections by markdown headings
    sections = re.split(r"^(#{1,3}\s+.+)$", text, flags=re.MULTILINE)
    chunks = []
    current_heading = source

    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        if re.match(r"^#{1,3}\s+", section):
            current_heading = section.lstrip("#").strip()
            continue
        # split long sections by double newline (paragraphs)
        paragraphs = section.split("\n\n")
        buf = ""
        for para in paragraphs:
            if len(buf) + len(para) < CHUNK_SIZE:
                buf += para + "\n\n"
            else:
                if buf:
                    chunks.append(Chunk(buf.strip(), source, current_heading))
                buf = para + "\n\n"
        if buf:
            chunks.append(Chunk(buf.strip(), source, current_heading))
    return chunks


def build_chunks(data_dir=DATA_DIR):
    chunks = []
    for fname, text in load_documents(data_dir):
        chunks.extend(chunk_document(text, fname))
    return chunks


class Retriever:
    def __init__(self, data_dir=DATA_DIR):
        self.model = SentenceTransformer(MODEL_NAME)
        self.chunks = build_chunks(data_dir)
        self.index = None
        self._build_index()

    def _build_index(self):
        texts = [c.text for c in self.chunks]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype(np.float32))

    def search(self, query, top_k=3):
        query_vec = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(query_vec.astype(np.float32), top_k)
        return [
            SearchResult(self.chunks[idx], float(score))
            for score, idx in zip(scores[0], indices[0])
            if idx >= 0
        ]


if __name__ == "__main__":
    # self-check: index loads, search returns results
    r = Retriever()
    results = r.search("how much does the pro plan cost?")
    assert len(results) > 0, "no results returned"
    assert "pro" in results[0].chunk.text.lower(), "top result should mention pro plan"
    print(f"indexed {len(r.chunks)} chunks, top result score={results[0].score:.3f}")
    print(f"top: [{results[0].chunk.source}] {results[0].chunk.heading}")
    print("self-check passed")
