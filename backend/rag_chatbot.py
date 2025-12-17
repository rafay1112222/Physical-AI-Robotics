import os
import sys
import dotenv
from qdrant_client import QdrantClient

# --- IMPORTS FOR LCEL, GEMINI, & MEMORY ---
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # <-- ADDED MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory 
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# Note: These legacy imports are necessary for the 'classic' chains you are using
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage # <-- ADDED Message Types

# -------------------------------
# 1. Configuration and Environment Load
# -------------------------------
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "physical_ai_textbook"
K = 5  # Retrieval size increased for better accuracy

if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
    print("❌ ERROR: Missing required environment variables. Check .env file.")
    sys.exit(1)


# -------------------------------
# 2. Initialize Qdrant + Embeddings + Retriever
# -------------------------------
try:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    
    # Initialize GoogleGenerativeAIEmbeddings
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        task_type="retrieval_query",
        google_api_key=GEMINI_API_KEY
    )

    # Correct VectorStore initialization
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings_model
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": K})

except Exception as e:
    print(f"❌ ERROR initializing Qdrant/Embeddings: {e}")
    sys.exit(1)


# -------------------------------
# 3. Build RAG Chain (WITH MEMORY)
# -------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=GEMINI_API_KEY
)

# Initialize the in-memory store for chat history
chat_history_store = InMemoryChatMessageHistory()

SYSTEM_PROMPT = """
You are a knowledgeable AI Assistant specialized in Physical AI and Humanoid Robotics.
You must ONLY answer using the context provided.

Rules:
1. If answer is NOT in context -> say:
    "I am sorry, but I cannot find that information in the Physical AI textbook."
2. Cite context chunk numbers (where applicable).
"""

# --- 3.1: The main prompt for answering the question ---
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT + "\n\nContext: {context}"),
    MessagesPlaceholder("chat_history"), # <-- FIX 1: Passes history to the answer chain
    ("human", "{input}") 
])

document_chain = create_stuff_documents_chain(llm, qa_prompt)

# --- 3.2: The prompt for generating a standalone question (History-Aware) ---
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question. Keep the original language."),
    MessagesPlaceholder("chat_history"), # <-- FIX 2: Passes history to the rephrasing chain
    ("human", "{input}")
])

history_aware_retriever = create_history_aware_retriever(
    llm,
    retriever,
    contextualize_q_prompt
)

# --- 3.3: Combine the parts into the final RAG chain ---
rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)


# -------------------------------
# 4. Chatbot Loop and Execution
# -------------------------------
def run_chatbot():
    print("---------------------------------------------------------")
    print("🤖 Physical AI RAG Chatbot (Gemini + Qdrant) - LIVE")
    print("Ask something about the textbook. Follow-up questions are supported.")
    print("Type 'exit' or 'quit' to end the session.")
    print("---------------------------------------------------------")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            print("AI: Thinking...")
            
            # --- FIX 3: Pass BOTH input and the chat_history list to the invoke call ---
            response = rag_chain.invoke({
                "input": user_input,
                "chat_history": chat_history_store.messages # Pass the list of previous messages
            })
            
            # Get the final answer
            ai_answer = response["answer"]
            
            # --- Update History (CRITICAL for follow-up questions) ---
            chat_history_store.add_user_message(user_input)
            chat_history_store.add_ai_message(ai_answer)
            
            print("\nAI:", ai_answer)

        except Exception as e:
            # Print the detailed exception for better debugging if the crash happens again
            print("\n❌ FATAL RAG Error (Check Log Above):", e) 
            print("Check your API keys, internet connection, or if your PDF content is causing the model to crash.")
            sys.exit(1)


if __name__ == "__main__":
    run_chatbot()