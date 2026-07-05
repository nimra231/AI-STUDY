

"""
vector_store.py
----------------
Owns everything related to turning document text into a searchable
FAISS vector database:
  1. Splitting text into overlapping chunks (LangChain text splitter).
  2. Embedding those chunks locally with sentence-transformers
     (no API key required for this part).
  3. Building / updating an in-memory FAISS index per Streamlit session.

The index lives only in st.session_state (not written to disk) so each
user's uploaded material stays isolated to their own session.
"""

from __future__ import annotations
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME


class VectorStoreError(Exception):
    """Raised when chunking or embedding fails."""
    pass


_embeddings_cache = {}


def get_embeddings_model() -> HuggingFaceEmbeddings:
    """
    Lazily create (and cache) the local embedding model so it is only
    loaded into memory once per process, not once per document.
    """
    if "model" not in _embeddings_cache:
        try:
            _embeddings_cache["model"] = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to load embedding model: {exc}") from exc
    return _embeddings_cache["model"]


def split_text_into_chunks(text: str, source_name: str) -> List[Document]:
    """Split raw text into overlapping chunks, tagged with source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [
        Document(page_content=chunk, metadata={"source": source_name, "chunk_id": i})
        for i, chunk in enumerate(chunks)
    ]


def build_or_update_vector_store(
    existing_store: Optional[FAISS],
    text: str,
    source_name: str,
) -> FAISS:
    """
    Create a new FAISS store from a document's text, or merge it into
    an existing store if one is already present for this session.
    """
    try:
        documents = split_text_into_chunks(text, source_name)
        if not documents:
            raise VectorStoreError(f"No content could be chunked from '{source_name}'.")

        embeddings = get_embeddings_model()

        if existing_store is None:
            return FAISS.from_documents(documents, embeddings)

        existing_store.add_documents(documents)
        return existing_store
    except VectorStoreError:
        raise
    except Exception as exc:
        raise VectorStoreError(f"Failed to embed '{source_name}': {exc}") from exc


def remove_source_from_store(store: Optional[FAISS], source_name: str) -> Optional[FAISS]:
    """
    Rebuild the FAISS index excluding a given source file. FAISS doesn't
    support deleting by metadata directly, so we filter and re-embed the
    remaining chunks instead.
    """
    if store is None:
        return None

    remaining_docs = [
        doc for doc in store.docstore._dict.values()
        if doc.metadata.get("source") != source_name
    ]

    if not remaining_docs:
        return None

    embeddings = get_embeddings_model()
    return FAISS.from_documents(remaining_docs, embeddings)


def similarity_search(store: FAISS, query: str, k: int = 4) -> List[Document]:
    """Retrieve the top-k most relevant chunks for a query."""
    try:
        return store.similarity_search(query, k=k)
    except Exception as exc:
        raise VectorStoreError(f"Search failed: {exc}") from exc
