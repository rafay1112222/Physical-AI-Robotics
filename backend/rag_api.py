import os
import sys
import dotenv
from qdrant_client import QdrantClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware # Added CORS

# --- IMPORTS FOR LCEL, GEMINI, & MEMORY ---
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory 
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# --- FastAPI Initialization ---
app = FastAPI(title="Physical AI RAG Chatbot API")

# --- CORS Configuration (Crucial for Frontend Communication) ---
# Allows communication from the frontend (which is likely on a different port/origin)
origins = ["*"] # Using "*" allows all origins for easy testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
# --------------------------

# --- Session Management (CRITICAL) ---
# Stores chat history for each unique session ID sent by the frontend
sessions = {}

# Pydantic model for the incoming JSON request
class ChatRequest(BaseModel):
    user_input: str
    session_id: str
    # The frontend needs to send the previous history for stateful conversation
    history: list[dict] = [] 

# -------------------------------
# 1. Configuration and Environment Load
# -------------------------------
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "physical_ai_textbook"
K = 5

if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
    print("❌ ERROR: Missing environment variables for RAG setup.")
    sys.exit(1)


# -------------------------------
# 2. RAG Chain Initialization (runs ONCE when API starts)
# -------------------------------
def initialize_rag_chain():
    try:
        # 2.1 Initialize Qdrant + Embeddings + Retriever
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", task_type="retrieval_query", google_api_key=GEMINI_API_KEY
        )
        vectorstore = QdrantVectorStore(
            client=qdrant_client, collection_name=COLLECTION_NAME, embedding=embeddings_model
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": K})

        # 2.2 LLM and Prompts Setup
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=GEMINI_API_KEY)
        
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
            ("system", "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question. Keep the original language."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        
        # 2.3 Final RAG Chain
        return create_retrieval_chain(history_aware_retriever, document_chain)

    except Exception as e:
        print(f"❌ FATAL RAG CHAIN INITIALIZATION ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Backend initialization failed: {str(e)}")


# Store the initialized RAG chain globally
try:
    rag_chain = initialize_rag_chain()
except HTTPException:
    sys.exit(1)


# -------------------------------
# 3. API Endpoint Definition
# -------------------------------
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # --- Session Retrieval/Creation ---
    if request.session_id not in sessions:
        sessions[request.session_id] = InMemoryChatMessageHistory()
        for msg in request.history:
            if msg.get('role') == 'user':
                sessions[request.session_id].add_user_message(msg.get('content'))
            elif msg.get('role') == 'assistant':
                sessions[request.session_id].add_ai_message(msg.get('content'))

    chat_history_store = sessions[request.session_id]
    chat_history_messages: list[BaseMessage] = chat_history_store.messages

    try:
        # Invoke the RAG chain
        response = await rag_chain.ainvoke({
            "input": request.user_input,
            "chat_history": chat_history_messages
        })
        
        ai_answer = response["answer"]
        
        # Update history for the next turn
        chat_history_store.add_user_message(request.user_input)
        chat_history_store.add_ai_message(ai_answer)

        # Return the response as JSON
        return {"answer": ai_answer, "session_id": request.session_id}

    except Exception as e:
        print(f"❌ RAG Execution Error: {e}")
        raise HTTPException(status_code=500, detail="Internal RAG chain error.")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG API is running."}