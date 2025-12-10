"""
RAG API for Physical AI & Humanoid Robotics Textbook Portal
Implements a Retrieval-Augmented Generation API using Context7 and Google Generative AI.
Connects to Qdrant for retrieval from the 'embodied_intelligence_rag' collection.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Physical AI & Robotics RAG API",
              description="Retrieval-Augmented Generation API for the Physical AI & Humanoid Robotics textbook",
              version="1.0.0")

# Models and data storage
class QueryRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    query: str
    response: str

# Global Context7 client
ctx7 = None

@app.on_event("startup")
def startup_event():
    """
    Initialize the Context7 client when the application starts.
    """
    global ctx7
    try:
        from context7 import Context7Client
        ctx7 = Context7Client()
        logger.info("Context7 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Context7 client: {str(e)}")
        raise

@app.get("/")
def read_root():
    return {"message": "Physical AI & Robotics RAG API",
            "description": "A Retrieval-Augmented Generation API for the Physical AI & Humanoid Robotics textbook"}

@app.post("/api/rag_chat", response_model=RAGResponse)
def rag_chat(request: QueryRequest):
    """
    RAG chat endpoint that processes the user's query using Qdrant and Gemini.
    """
    try:
        # Import required libraries inside the function to avoid import-time issues
        from qdrant_client import QdrantClient
        import google.generativeai as genai

        # Get API key from environment variable
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure the Gemini API
        genai.configure(api_key=gemini_api_key)

        # Initialize Qdrant client
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

        qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Generate embedding for the query using Gemini
        embedding_result = genai.embed_content(
            model="embedding-001",
            content=[request.query],
            task_type="retrieval_query"
        )

        query_embedding = embedding_result['embedding']

        # Search using the embedding in Qdrant
        search_results = qdrant_client.search(
            collection_name="embodied_intelligence_rag",
            query_vector=query_embedding,
            limit=4
        )

        # Extract context from search results
        retrieved_docs = []
        for result in search_results:
            # Updated to use proper Qdrant result structure
            if hasattr(result, 'payload') and result.payload and 'content' in result.payload:
                retrieved_docs.append({
                    'content': result.payload['content'],
                    'source': result.payload.get('source', 'Unknown'),
                    'title': result.payload.get('title', 'Untitled')
                })
            elif 'payload' in result and result['payload'] and 'content' in result['payload']:
                retrieved_docs.append({
                    'content': result['payload']['content'],
                    'source': result['payload'].get('source', 'Unknown'),
                    'title': result['payload'].get('title', 'Untitled')
                })

        # Format the context using Context7's format_context method
        context_str = ctx7.format_context(retrieved_docs) if retrieved_docs else "No relevant context found."

        # Create a prompt for Gemini with the retrieved context
        prompt = f"""You are an AI assistant specializing in Physical AI & Humanoid Robotics.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer concise but informative and cite sources when possible.

        Context from the Physical AI & Robotics textbook:
        {context_str}

        Question: {request.query}
        Helpful Answer:"""

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        # Extract text from response
        if hasattr(response, 'text'):
            answer = response.text
        else:
            answer = "I was unable to generate a response. Please try again."

        return RAGResponse(query=request.query, response=answer)

    except Exception as e:
        logger.error(f"Error processing RAG chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error during RAG processing: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)