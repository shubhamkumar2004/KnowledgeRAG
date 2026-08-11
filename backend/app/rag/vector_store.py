from pathlib import Path
import shutil

import chromadb
from sentence_transformers import SentenceTransformer

from app.rag.chunker import load_documents, chunk_documents


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

VECTOR_DB_DIR = Path("vector_db")

COLLECTION_NAME = "ekta_trust"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

def load_embedding_model():
    """
    Load the SentenceTransformer model used to generate embeddings.
    """

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded.")

    return model


# ---------------------------------------------------------
# Prepare text for embedding
# ---------------------------------------------------------

def create_embedding_text(chunk: dict) -> str:
    """
    Add page/source information to the chunk before generating
    its embedding.

    Example:

    Page: Vision

    Create a casteless and atrocity free society...
    """

    source_name = (
        chunk["source"]
        .replace(".aspx.txt", "")
        .replace(".txt", "")
        .replace("%20", " ")
    )

    return (
        f"Page: {source_name}\n\n"
        f"{chunk['text']}"
    )


# ---------------------------------------------------------
# Build Vector Database
# ---------------------------------------------------------

def build_vector_store():
    """
    Load documents, create chunks, generate embeddings,
    and store everything inside ChromaDB.
    """

    # 1. Load scraped text files
    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    # 2. Split documents into chunks
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # 3. Load embedding model
    model = load_embedding_model()

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # texts = original clean text stored in ChromaDB
    #
    # embedding_texts = text + page name used ONLY
    # for generating embeddings
    # -----------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embedding_texts = [
        create_embedding_text(chunk)
        for chunk in chunks
    ]

    # 4. Generate embeddings
    print(
        f"\nGenerating embeddings for "
        f"{len(embedding_texts)} chunks..."
    )

    embeddings = model.encode(
        embedding_texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("Embeddings generated")

    # 5. Prepare IDs and metadata
    ids = []

    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(f"chunk_{index}")

        metadatas.append(
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
        )

    # 6. Remove old vector database
    if VECTOR_DB_DIR.exists():

        print("\nRemoving old vector database...")

        shutil.rmtree(VECTOR_DB_DIR)

    VECTOR_DB_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # 7. Create ChromaDB client
    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR)
    )

    # 8. Create collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )

    # 9. Store vectors
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("\nVector database created successfully!")
    print(f"Total vectors stored: {collection.count()}")


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":
    build_vector_store()