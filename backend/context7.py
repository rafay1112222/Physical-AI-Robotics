"""
Context7 - A context management library for RAG applications.

This module provides the Context7Client class which implements methods for
chunking text and formatting context for RAG applications.
"""

import re
from typing import List, Dict, Any


class Context7Client:
    """
    A client for handling context operations in RAG applications.
    """

    def __init__(self):
        """
        Initialize the Context7Client.
        """
        pass

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into semantic chunks with overlapping windows.

        Args:
            text (str): The input text to chunk
            chunk_size (int): The target size of each chunk in characters
            overlap (int): The overlap between chunks in characters

        Returns:
            List[str]: A list of text chunks
        """
        if not text:
            return []

        # Split text into sentences to preserve semantic boundaries
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Add extra punctuation back for better context
            sentence_with_punct = sentence.strip() + "."
            
            # If adding the sentence would exceed chunk size
            if len(current_chunk) + len(sentence_with_punct) > chunk_size:
                # If current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # If the sentence itself is larger than chunk_size, split it by words
                if len(sentence_with_punct) > chunk_size:
                    words = sentence_with_punct.split()
                    temp_chunk = ""
                    
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= chunk_size:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk.strip():
                                chunks.append(temp_chunk.strip())
                            # Start a new temp chunk with overlap from the previous chunk if possible
                            temp_chunk = word + " "
                    
                    if temp_chunk.strip():
                        current_chunk = temp_chunk
                else:
                    # Start a new chunk with the sentence
                    current_chunk = sentence_with_punct
            else:
                # Add sentence to current chunk
                current_chunk += " " + sentence_with_punct

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Apply overlap between chunks if specified
        if overlap > 0 and len(chunks) > 1:
            chunks_with_overlap = []
            for i in range(len(chunks)):
                if i == 0:
                    chunks_with_overlap.append(chunks[i])
                else:
                    # Calculate overlap by taking the last 'overlap' characters from the previous chunk
                    prev_chunk_end = chunks[i-1][-overlap:]
                    new_chunk = prev_chunk_end + " " + chunks[i]
                    chunks_with_overlap.append(new_chunk)
            
            chunks = chunks_with_overlap

        return chunks

    def format_context(self, docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a structured prompt context.

        Args:
            docs (List[Dict[str, Any]]): A list of document dictionaries with content and metadata

        Returns:
            str: Formatted context string
        """
        if not docs:
            return "No relevant context found."

        formatted_contexts = []
        
        for i, doc in enumerate(docs):
            content = doc.get('content', '') if isinstance(doc, dict) else str(doc)
            
            # Extract document metadata if available
            source = doc.get('source', 'Unknown source') if isinstance(doc, dict) else 'Unknown source'
            title = doc.get('title', 'Untitled') if isinstance(doc, dict) else 'Untitled'
            
            # Format the document with its metadata
            formatted_doc = f"Document {i+1} (Source: {source}, Title: {title}):\n"
            formatted_doc += f"{content}\n"
            formatted_doc += "---\n"
            
            formatted_contexts.append(formatted_doc)
        
        return "\n".join(formatted_contexts)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Convenience function to chunk text without instantiating the class.
    
    Args:
        text (str): The input text to chunk
        chunk_size (int): The target size of each chunk in characters
        overlap (int): The overlap between chunks in characters

    Returns:
        List[str]: A list of text chunks
    """
    client = Context7Client()
    return client.chunk_text(text, chunk_size, overlap)