import os
import sys
import dotenv

# --- RAG INGESTION IMPORTS ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client import QdrantClient

# -------------------------------
# 1. Configuration (MUST MATCH RAG CHATBOT)
# -------------------------------
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "physical_ai_textbook"

# --- USER-DEFINED INPUT FILE ---
PDF_FILE_PATH = "Physical_AI_Textbook.pdf" 
# Ensure your PDF is in the same directory, or change this path!

# --- CHUNKING PARAMETERS ---
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 150
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
VECTOR_SIZE = 768 # The expected dimension for the text-embedding-004 model

# Error check (same as chatbot)
if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
    print("❌ ERROR: Missing required environment variables. Check .env file.")
    sys.exit(1)


# -------------------------------
# 2. Main Ingestion Function
# -------------------------------
def ingest_documents():
    print("--- Starting Document Ingestion Process ---")
    print(f"1. Loading file: {PDF_FILE_PATH}")
    
    # --- A. Load Document ---
    try:
        loader = PyPDFLoader(PDF_FILE_PATH)
        documents = loader.load()
        print(f"   ✅ Loaded {len(documents)} pages.")
    except Exception as e:
        print(f"❌ ERROR: Could not load PDF file: {e}")
        print("   -> Check if the file path is correct and 'pypdf' is installed.")
        sys.exit(1)

    # --- B. Split Documents into Chunks ---
    print(f"2. Splitting text (Size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   ✅ Created {len(chunks)} text chunks for embedding.")

    # --- C. Initialize Embeddings and Qdrant ---
    print("3. Initializing Gemini Embeddings and Qdrant Client...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            task_type="retrieval_document", # Important: Use retrieval_document for indexing
            google_api_key=GEMINI_API_KEY
        )
        
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
    except Exception as e:
        print(f"❌ ERROR during initialization: {e}")
        sys.exit(1)

    # --- D. Ensure Collection Exists and Upload Data ---
    print(f"4. Uploading chunks to Qdrant collection: {COLLECTION_NAME}")
    
    # --- IMPORTANT: Create/Recreate Collection ---
    # This deletes the existing collection and creates a new one!
    print("   -> WARNING: Recreating collection to ensure fresh data.")
    try:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    except Exception as e:
        print(f"❌ ERROR creating collection: {e}")
        print("   -> Check Qdrant URL/Key permissions.")
        sys.exit(1)

    # --- Upload Documents ---
   # --- Upload Documents ---
    try:
        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            collection_name=COLLECTION_NAME,
            # client=qdrant_client, # REMOVED: This was the source of the error
            force_recreate=False 
        )
        print("\n=======================================================")
        print(f"✅ INGESTION SUCCESSFUL! {len(chunks)} chunks uploaded.")
        print("=======================================================")
    except Exception as e:
        print(f"\n❌ FATAL ERROR during upload (likely API or rate limit): {e}")
        print("   -> Check your Gemini API key usage and Qdrant collection status.")

if __name__ == "__main__":
    ingest_documents()