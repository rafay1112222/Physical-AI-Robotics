"""
Script to index the Physical AI & Humanoid Robotics textbook documents
into a FAISS vector database for RAG functionality.

This script:
1. Finds all Markdown files in the 'docs/' directory
2. Uses LangChain to load and chunk the Markdown documents
3. Generates embeddings using Google Generative AI (Gemini) SDK
4. Creates a FAISS vector store and saves it locally
5. Uploads all chunked, embedded documents to the FAISS store
"""

import os
import glob
from typing import List, Dict
import hashlib
from pathlib import Path
import pickle

# Import required libraries
try:
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
except ImportError:
    raise ImportError("Please install langchain libraries: pip install langchain langchain-community langchain-google-genai langchain-text-splitters")

def load_markdown_files(docs_dir: str) -> List[Document]:
    """
    Find and load all Markdown files in the specified directory.
    
    Args:
        docs_dir: Path to the directory containing Markdown files
        
    Returns:
        List of LangChain Document objects
    """
    print(f"Searching for Markdown files in '{docs_dir}'...")
    
    # Find all .md and .mdx files in docs directory and subdirectories
    markdown_patterns = [
        os.path.join(docs_dir, "**/*.md"),
        os.path.join(docs_dir, "**/*.mdx"),
        os.path.join(docs_dir, "*.md"),
        os.path.join(docs_dir, "*.mdx")
    ]
    
    all_files = []
    for pattern in markdown_patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove duplicates
    all_files = list(set(all_files))
    
    print(f"Found {len(all_files)} Markdown files")
    
    documents = []
    for file_path in all_files:
        try:
            # Use UnstructuredMarkdownLoader if available, otherwise TextLoader
            if file_path.endswith('.mdx'):
                # For .mdx files, use TextLoader which handles them well
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            docs = loader.load()
            
            # Add source metadata to each document
            for doc in docs:
                doc.metadata['source'] = file_path
                rel_path = os.path.relpath(file_path, docs_dir)
                doc.metadata['file_path'] = rel_path
                doc.metadata['title'] = os.path.basename(file_path)
            
            documents.extend(docs)
            print(f"Loaded: {rel_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
    
    return documents

def chunk_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
    """
    Use LangChain to chunk the loaded documents.
    
    Args:
        documents: List of documents loaded from Markdown files
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked document pieces
    """
    print(f"Chunking documents using LangChain (chunk_size={chunk_size}, chunk_overlap={chunk_overlap})...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    
    print(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    return chunked_docs

def create_faiss_index(chunked_docs: List[Document], embeddings_model: str = "embedding-001"):
    """
    Create FAISS index from chunked documents using Google Generative AI embeddings.
    
    Args:
        chunked_docs: List of chunked document pieces
        embeddings_model: Name of the Google embeddings model to use
        
    Returns:
        FAISS vector store
    """
    print(f"Creating FAISS index with {len(chunked_docs)} chunks using {embeddings_model} embeddings...")
    
    # Get API key from environment variable
    import os
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    # Initialize Google Generative AI embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=embeddings_model,
        google_api_key=gemini_api_key
    )
    
    # Create FAISS vector store from documents and embeddings
    vector_store = FAISS.from_documents(
        chunked_docs,
        embeddings
    )
    
    print(f"FAISS index created successfully with {len(chunked_docs)} documents")
    return vector_store

def save_faiss_index(vector_store, output_path: str = "faiss_index"):
    """
    Save the FAISS index to disk.
    
    Args:
        vector_store: FAISS vector store to save
        output_path: Directory path to save the index
    """
    print(f"Saving FAISS index to '{output_path}'...")
    vector_store.save_local(output_path)
    print(f"FAISS index saved successfully to '{output_path}'")

def main():
    """
    Main function to orchestrate the indexing process.
    """
    print("Starting Physical AI & Humanoid Robotics textbook indexing process...")

    # Define the docs directory
    docs_dir = "docs"

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
        # Set the environment variable for this session
        os.environ["GEMINI_API_KEY"] = gemini_api_key
    
    # Step 1: Load all Markdown files
    documents = load_markdown_files(docs_dir)
    if not documents:
        print("No documents found to index.")
        return
    
    # Step 2: Chunk the documents
    chunked_docs = chunk_documents(documents)
    if not chunked_docs:
        print("No chunks created from documents.")
        return
    
    # Step 3: Create FAISS index with embeddings
    try:
        vector_store = create_faiss_index(chunked_docs)
    except Exception as e:
        print(f"Error creating FAISS index: {str(e)}")
        return
    
    # Step 4: Save the index to disk
    try:
        save_faiss_index(vector_store, "faiss_index_embodied_intelligence")
    except Exception as e:
        print(f"Error saving FAISS index: {str(e)}")
        return
    
    print("\nIndexing completed successfully!")
    print(f"Documents indexed: {len(chunked_docs)}")
    print("FAISS index saved as 'faiss_index_embodied_intelligence'")
    print("The Physical AI & Humanoid Robotics textbook is now available for RAG queries.")

if __name__ == "__main__":
    main()