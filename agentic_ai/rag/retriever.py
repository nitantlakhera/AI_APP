import os

import chromadb
from sentence_transformers import SentenceTransformer

# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_PATH = "rag/vector_db"

COLLECTION_NAME = "knowledge"

# Can be overridden using environment variable:
#
# Windows:
#   set RAG_EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
#
# If not provided, this model is used.
EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "BAAI/bge-base-en-v1.5"
)

# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\n========================================")
print("LOADING RAG EMBEDDING MODEL")
print("========================================")

print("Embedding Model:", EMBEDDING_MODEL)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

# ============================================================
# CONNECT TO CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

def retrieve_documents(
        question,
        top_k=4
):
    query_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    retrieved_documents = []

    for document, metadata in zip(
            documents,
            metadatas
    ):
        retrieved_documents.append({
            "document": document,
            "metadata": metadata
        })

    return retrieved_documents
