import os
import dotenv
from qdrant_client import QdrantClient

# Modern LangChain libraries (these versions work in your environment)
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

# Legacy LangChain chain helpers (correct versions that link the components)
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain


# -------------------------------
# 1. Load Environment Variables
# -------------------------------
dotenv.load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "physical_ai_textbook"
K = 3

if not all([QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY]):
    print("❌ Missing env variables. Please fix .env file.")
    exit()


# -------------------------------
# 2. Initialize Qdrant + Embeddings
# -------------------------------
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    task_type="retrieval_query",
    google_api_key=GEMINI_API_KEY
)

# Correct VectorStore initialization (CLOUD)
vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings_model
)


# -------------------------------
# 3. Build RAG Chain (No Memory)
# -------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=GEMINI_API_KEY
)


SYSTEM_PROMPT = """
You are a knowledgeable AI Assistant specialized in Physical AI and Humanoid Robotics.
You must ONLY answer using the context provided.

Rules:
1. If answer is NOT in context → say:
    "I am sorry, but I cannot find that information in the Physical AI textbook."
2. Cite context chunk numbers.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT + "\n\nContext: {context}"),
    ("human", "{input}")
])

document_chain = create_stuff_documents_chain(llm, prompt)
retriever = vectorstore.as_retriever(search_kwargs={"k": K})
rag_chain = create_retrieval_chain(retriever, document_chain)


# -------------------------------
# 4. Chatbot Loop
# -------------------------------
def run_chatbot():
    print("🤖 Physical AI RAG Chatbot (CLI)")
    print("Ask something about the textbook.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            response = rag_chain.invoke({"input": user_input})
            print("\nAI:", response["answer"], "\n")

        except Exception as e:
            print("\n❌ RAG Error:", e, "\n")


if __name__ == "__main__":
    run_chatbot()