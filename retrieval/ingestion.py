"""
Document ingestion pipeline — loads and embeds PMO documents into ChromaDB.
"""
from __future__ import annotations

from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


def ingest_document(file_path: str, collection_name: str, metadata: dict | None = None) -> None:
    """Ingest a single document file into the specified ChromaDB collection."""
    import chromadb
    from langchain_community.document_loaders import (
        Docx2txtLoader,
        PyPDFLoader,
        TextLoader,
    )
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from app.core.config import settings

    path = Path(file_path)
    suffix = path.suffix.lower()

    # Load
    if suffix == ".pdf":
        loader = PyPDFLoader(file_path)
    elif suffix in {".docx", ".doc"}:
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path)

    docs = loader.load()

    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    # Embed
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

    # Store in Chroma
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection = client.get_or_create_collection(collection_name)
    for i, chunk in enumerate(chunks):
        embedding = embeddings.embed_query(chunk.page_content)
        collection.add(
            ids=[f"{path.stem}_{i}"],
            documents=[chunk.page_content],
            embeddings=[embedding],
            metadatas=[metadata or {}],
        )
    logger.info("Document ingested", file=file_path, chunks=len(chunks))
