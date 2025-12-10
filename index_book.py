"""
Script to index the Physical AI & Humanoid Robotics textbook documents
into a Qdrant vector database for RAG functionality.

This script:
1. Finds all "Regenerate 'index.md" files in the '../docs' or 'docs/' directory
2. Uses Context7 to load and chunk the Markdown documents
3. Generates embeddings using Google Generative AI (Gemini) SDK
4. Initializes a local Qdrant client connection
5. Creates a new Qdrant collection named 'embodied_intelligence_rag'
6. Uploads all chunked, embedded documents to the Qdrant collection
"""

import os
import sys
import glob
from typing import List, Dict
import hashlib
from pathlib import Path

# Add the backend directory to the Python path to import context7
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import required libraries
from context7 import Context7Client

try:
    import qdrant_client
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
except ImportError:
    raise ImportError("Please install qdrant-client: pip install qdrant-client")

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("Please install google-generativeai: pip install google-generativeai")

def load_markdown_files(docs_dir: str) -> List[Dict]:
    """
    Find and load all "Regenerate 'index.md" files in the specified directory.

    Args:
        docs_dir: Path to the directory containing Markdown files

    Returns:
        List of dictionaries with file content and metadata
    """
    print(f"Searching for 'Regenerate 'index.md' files in '{docs_dir}'...")

    # Find all files that match the pattern containing "index.md" (since special chars may cause issues)
    pattern = os.path.join(docs_dir, "**/*index.md")

    all_files = glob.glob(pattern, recursive=True)

    # Further filter for files that have "index" in the name and possibly "Regenerate"
    all_files = [f for f in all_files if "index" in os.path.basename(f)]

    print(f"Found {len(all_files)} 'Regenerate 'index.md' files")

    documents = []
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create document metadata
            rel_path = os.path.relpath(file_path, docs_dir)
            doc_id = hashlib.md5(content.encode()).hexdigest()

            documents.append({
                'id': doc_id,
                'content': content,
                'file_path': rel_path,
                'title': os.path.basename(file_path),
                'source': file_path
            })
            print(f"Loaded: {rel_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")

    return documents

def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Use Context7 to chunk the loaded documents.

    Args:
        documents: List of documents loaded from Markdown files

    Returns:
        List of chunked document pieces
    """
    print("Chunking documents using Context7...")

    # Initialize Context7Client
    ctx7 = Context7Client()

    chunked_docs = []
    for doc in documents:
        try:
            # Use Context7 to split content into chunks
            chunks = ctx7.chunk_text(doc['content'])

            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc['id']}_chunk_{i}"

                chunked_docs.append({
                    'id': chunk_id,
                    'content': chunk,
                    'original_id': doc['id'],
                    'file_path': doc['file_path'],
                    'title': doc['title'],
                    'source': doc['source']
                })

        except Exception as e:
            print(f"Error chunking document {doc['id']}: {str(e)}")

    print(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    return chunked_docs

def generate_embeddings(texts: List[str], gemini_api_key: str) -> List[List[float]]:
    """
    Generate embeddings for the given texts using Gemini.

    Args:
        texts: List of text chunks to embed
        gemini_api_key: API key for Google Generative AI

    Returns:
        List of embeddings (vectors)
    """
    print(f"Generating embeddings for {len(texts)} text chunks using Gemini...")

    # Configure the Gemini API
    genai.configure(api_key=gemini_api_key)

    # Select the embedding model
    embedding_model = "embedding-001"  # Gemini embedding model

    embeddings = []
    for i, text in enumerate(texts):
        try:
            # Generate embedding for the text
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_document",  # Appropriate task type for RAG
                title=None  # We can add title if needed
            )

            embedding = result['embedding']
            embeddings.append(embedding)

            # Progress indicator
            if (i + 1) % 10 == 0 or (i + 1) == len(texts):
                print(f"Generated embeddings for {i + 1}/{len(texts)} chunks")

        except Exception as e:
            print(f"Error generating embedding for chunk {i}: {str(e)}")
            # Add a zero vector in case of error to maintain alignment
            embeddings.append([0.0] * 768)  # Assuming 768-dim vector

    return embeddings

def setup_qdrant_collection(client: QdrantClient, collection_name: str):
    """
    Create or reset a Qdrant collection for storing embeddings.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection to create
    """
    print(f"Setting up Qdrant collection: {collection_name}")

    # Check if collection exists and delete if it does
    try:
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists, deleting it...")
        client.delete_collection(collection_name)
        print("Old collection deleted")
    except:
        print("Collection does not exist yet")

    # Create new collection with appropriate vector size (assuming Gemini embedding-001)
    # Note: Gemini embedding-001 typically produces 768-dimensional vectors
    vector_size = 768

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE
        )
    )

    print(f"Collection '{collection_name}' created successfully")

def upload_to_qdrant(client: QdrantClient, collection_name: str,
                    chunked_docs: List[Dict], embeddings: List[List[float]]):
    """
    Upload chunked documents and their embeddings to Qdrant.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection to upload to
        chunked_docs: List of chunked document dictionaries
        embeddings: List of embeddings corresponding to the documents
    """
    print(f"Uploading {len(chunked_docs)} documents to Qdrant collection: {collection_name}")

    # Prepare points for Qdrant
    points = []
    for i, (doc, embedding) in enumerate(zip(chunked_docs, embeddings)):
        point = models.PointStruct(
            id=i,
            vector=embedding,
            payload={
                'content': doc['content'],
                'original_id': doc['original_id'],
                'file_path': doc['file_path'],
                'title': doc['title'],
                'source': doc['source']
            }
        )
        points.append(point)

    # Upload points to Qdrant
    client.upload_points(
        collection_name=collection_name,
        points=points,
        batch_size=64
    )

    print(f"Successfully uploaded {len(points)} documents to Qdrant")

def main():
    """
    Main function to orchestrate the indexing process.
    """
    print("Starting Physical AI & Humanoid Robotics textbook indexing process...")

    # Define the docs directory - try both possible locations
    docs_dirs = ["../docs", "docs"]
    docs_dir = None

    for possible_dir in docs_dirs:
        if os.path.exists(possible_dir):
            docs_dir = possible_dir
            break

    if docs_dir is None:
        print("Error: Neither '../docs' nor 'docs' directory exists.")
        return

    # Check if the docs directory exists
    if not os.path.exists(docs_dir):
        print(f"Error: Directory '{docs_dir}' does not exist.")
        return

    # Get Gemini API key from environment variable or user input
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        gemini_api_key = input("Please enter your Gemini API key: ").strip()
        if not gemini_api_key:
            print("Error: Gemini API key is required.")
            return

    # Step 1: Load all "Regenerate 'index.md" files
    documents = load_markdown_files(docs_dir)
    if not documents:
        print("No 'Regenerate 'index.md' documents found to index.")
        return

    # Step 2: Chunk the documents
    chunked_docs = chunk_documents(documents)
    if not chunked_docs:
        print("No chunks created from documents.")
        return

    # Extract text content for embedding
    texts_to_embed = [doc['content'] for doc in chunked_docs]

    # Step 3: Generate embeddings using Gemini
    embeddings = generate_embeddings(texts_to_embed, gemini_api_key)
    if not embeddings:
        print("No embeddings generated.")
        return

    # Step 4: Initialize Qdrant client
    print("Initializing Qdrant client...")
    client = QdrantClient(host="localhost", port=6333)  # Default Qdrant settings

    # Test the connection
    try:
        client.get_collections()
        print("Connected to Qdrant successfully")
    except Exception as e:
        print(f"Could not connect to Qdrant: {str(e)}")
        print("Make sure Qdrant is running locally on port 6333")
        return

    # Step 5: Create Qdrant collection
    collection_name = "embodied_intelligence_rag"
    setup_qdrant_collection(client, collection_name)

    # Step 6: Upload documents and embeddings to Qdrant
    upload_to_qdrant(client, collection_name, chunked_docs, embeddings)

    print("\nIndex complete!")

if __name__ == "__main__":
    main()