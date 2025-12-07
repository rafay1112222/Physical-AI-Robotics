import os
import dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant # Corrected Qdrant import

# --- 1. Load Environment Variables ---
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. Configuration ---
COLLECTION_NAME = "physical_ai_textbook"
# DOCS_PATH must point to the parent directory's 'docs' folder
DOCS_PATH = os.path.join(os.path.dirname(os.getcwd()), "docs") 
VECTOR_DIMENSION = 768

# --- 3. Indexing Function ---

def index_textbook_data():
    """Loads markdown documents, splits them, creates embeddings, and uploads to Qdrant."""
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not found in .env. Cannot run indexing.")
        return

    print(f"Starting indexing process from directory: {DOCS_PATH}")

    # Load documents from the Docusaurus 'docs' directory
    loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.md",
        loader_kwargs={'autodetect_encoding': True}
    )
    documents = loader.load()
    print(f"Successfully loaded {len(documents)} source documents.")

    # Split documents into smaller, coherent chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks for indexing.")

    # Initialize the Gemini Embedding Model
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",
        api_key=GEMINI_API_KEY
    )

   # Initialize Qdrant Client
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=300 # Set timeout to 300 seconds (5 minutes)
    )

    # Prepare Qdrant Collection
    print(f"Checking for collection '{COLLECTION_NAME}'...")
    try:
        if qdrant_client.collection_exists(collection_name=COLLECTION_NAME):
            # Delete existing collection to ensure a clean re-index
            qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
            print(f"Existing collection '{COLLECTION_NAME}' deleted.")

        # Create the new collection
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIMENSION, distance=Distance.COSINE),
            on_disk_payload=True 
        )
        print(f"Collection '{COLLECTION_NAME}' created with dimension {VECTOR_DIMENSION}.")

    except Exception as e:
        print(f"Error connecting to Qdrant or managing collection: {e}")
        return

    # Create vectors and upload to Qdrant
    # Create vectors and upload to Qdrant
    print("Generating embeddings and uploading vectors... (This may take a moment)")
    
    # We will use LangChain's Qdrant vector store integration for simplicity
    Qdrant.from_documents( 
        texts,
        embeddings_model,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        timeout=300 # Set timeout to 300 seconds (5 minutes)
    )
    
    print("\n✅ Textbook indexing complete!")
    print(f"Total chunks indexed: {len(texts)}.")

if __name__ == "__main__":
    index_textbook_data()