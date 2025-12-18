import os
import sys
import ssl
import dotenv
from qdrant_client import QdrantClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- 1. SSL PATCH (Crucial for Hugging Face/Docker) ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- IMPORTS FOR LCEL, GEMINI, & MEMORY ---
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory 
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever

# --- FastAPI Initialization ---
app = FastAPI(title="Physical AI RAG Chatbot API")

# Allow all origins so your GitHub Pages can talk to Hugging Face
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

sessions = {}

class ChatRequest(BaseModel):
    user_input: str
    session_id: str
    history: list[dict] = [] 

# --- Configuration ---
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "").strip()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
COLLECTION_NAME = "physical_ai_textbook"
K = 5

if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
    print("❌ ERROR: Missing environment variables.")
    sys.exit(1)

# --- RAG Chain Initialization ---
def initialize_rag_chain():
    try:
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            task_type="retrieval_query", 
            google_api_key=GEMINI_API_KEY
        )
        
        vectorstore = QdrantVectorStore(
            client=qdrant_client, collection_name=COLLECTION_NAME, embedding=embeddings_model
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": K})

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3, 
            google_api_key=GEMINI_API_KEY,
            transport="rest" 
        )
        
        SYSTEM_PROMPT = """You are a knowledgeable AI Assistant specialized in Physical AI and Humanoid Robotics.
You must ONLY answer using the context provided.
Rules:
1. If answer is NOT in context -> say: "I am sorry, but I cannot find that information in the Physical AI textbook."
2. Cite context chunk numbers (where applicable)."""

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\nContext: {context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}") 
        ])
        document_chain = create_stuff_documents_chain(llm, qa_prompt)

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the following conversation and a follow up question, rephrase it to be standalone."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        return create_retrieval_chain(history_aware_retriever, document_chain)

    except Exception as e:
        print(f"❌ FATAL RAG CHAIN INITIALIZATION ERROR: {e}")
        raise e

# Initialize global chain
try:
    rag_chain = initialize_rag_chain()
except Exception:
    sys.exit(1)

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Physical AI RAG API is live and healthy!", "port": 7860}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if request.session_id not in sessions:
        sessions[request.session_id] = InMemoryChatMessageHistory()
    
    chat_history_store = sessions[request.session_id]
    
    try:
        response = await rag_chain.ainvoke({
            "input": request.user_input,
            "chat_history": chat_history_store.messages
        })
        
        ai_answer = response["answer"]
        chat_history_store.add_user_message(request.user_input)
        chat_history_store.add_ai_message(ai_answer)

        return {"answer": ai_answer, "session_id": request.session_id}

    except Exception as e:
        print(f"❌ RAG Execution Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))