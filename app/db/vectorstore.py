import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings

chroma_client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
embedding_function = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.google_api_key
)

collection = chroma_client.get_or_create_collection(name="documents")


def add_document_to_vectorstore(doc_id: str, text: str, metadata: dict):
    embedding = embedding_function.embed_query(text)
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )


def query_vectorstore(query_text: str, n_results: int = 5):
    query_embedding = embedding_function.embed_query(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results