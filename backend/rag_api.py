import os
import dotenv
from qdrant_client import QdrantClient
from pydantic import BaseModel # NEW: For data validation
from fastapi import FastAPI, HTTPException # NEW: For the web service
from fastapi.middleware.cors import CORSMiddleware # NEW: To allow web access

# Modern LangChain libraries (your working versions)
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

# Legacy LangChain chain helpers (your working versions)
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain

# --- 1. FastAPI Setup ---
app = FastAPI(
    title="Physical AI RAG Chatbot API",
    version="1.0.0"
)

# Crucial for browser-based access (allowing your book's web page to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins. Be more specific in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 2. Request Schema (How the frontend sends data) ---
class QueryInput(BaseModel):
    """Defines the structure of the incoming chat request."""
    query: str # The user's question

class QueryResponse(BaseModel):
    """Defines the structure of the outgoing response."""
    answer: str
    source_documents: list


# --- 3. Global RAG Chain Initialization ---
# This dictionary will hold the RAG chain after setup
rag_chain = None 
COLLECTION_NAME = "physical_ai_textbook"
K = 3

@app.on_event("startup")
async def startup_event():
    """Initializes the RAG components only once when the server starts."""
    global rag_chain, COLLECTION_NAME, K

    # Load Environment Variables
    dotenv.load_dotenv()
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
        raise RuntimeError("Missing required environment variables for RAG initialization.")
    
    try:
        # Initialize Qdrant + Embeddings
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type="retrieval_query",
            google_api_key=GEMINI_API_KEY
        )

        vectorstore = QdrantVectorStore(
            client=qdrant_client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings_model
        )

        # Build RAG Chain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=GEMINI_API_KEY
        )

        SYSTEM_PROMPT = """
        You are a knowledgeable AI Assistant specialized in Physical AI and Humanoid Robotics.
        You must ONLY answer using the context provided.
        Rules: 1. If answer is NOT in context → say: "I am sorry, but I cannot find that information in the Physical AI textbook."
        2. Cite context chunk numbers clearly (e.g., [Source 1], [Source 2]).
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\nContext: {context}"),
            ("human", "{input}")
        ])

        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectorstore.as_retriever(search_kwargs={"k": K})
        # IMPORTANT: We need to enable returning source documents to send them to the API user
        rag_chain = create_retrieval_chain(retriever, document_chain) 
        
        print("✅ RAG Chain Initialized Successfully!")

    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG service failed to initialize: {e}")


# --- 4. API Endpoints ---

@app.get("/")
def health_check():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Physical AI RAG API is running."}


@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(input_data: QueryInput):
    """The main endpoint to receive a question and return the RAG answer."""
    if not rag_chain:
         raise HTTPException(status_code=503, detail="RAG service is still starting up or failed initialization.")

    try:
        # Invoke the working RAG chain
        response = rag_chain.invoke({"input": input_data.query})
        
        # Extract source documents for citation on the frontend
        source_docs = []
        if 'context' in response and response['context']:
             for doc in response['context']:
                  source_docs.append(doc.page_content[:150] + "...") # Send first 150 chars as source

        return QueryResponse(
            answer=response["answer"],
            source_documents=source_docs
        )

    except Exception as e:
        print(f"RAG Chain Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal RAG processing error: {e}")