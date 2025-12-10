"""
Test script to verify the RAG API can be imported and run
"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all necessary modules can be imported"""
    print("Testing imports...")

    try:
        from langchain_core.vectorstores import VectorStore
        print("[OK] langchain_core.vectorstores imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import langchain_core.vectorstores: {e}")
        return False

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("[OK] langchain_google_genai imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import langchain_google_genai: {e}")
        return False

    try:
        from langchain_community.vectorstores import FAISS
        print("[OK] langchain_community.vectorstores with FAISS imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import langchain_community.vectorstores.FAISS: {e}")
        return False

    try:
        import faiss
        print("[OK] faiss imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import faiss: {e}")
        return False

    # We don't import google.generativeai directly anymore due to compatibility issues
    # It's only imported inside functions when needed

    try:
        from rag_api import app
        print("[OK] rag_api app imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import rag_api: {e}")
        return False

    return True

def test_environment():
    """Test that required environment variables are set"""
    print("\nTesting environment...")

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        print("[OK] GEMINI_API_KEY environment variable is set")
    else:
        print("[WARN] GEMINI_API_KEY environment variable is not set")
        print("  You will need to set this before running the API")

    # FAISS doesn't require a server, so no connection test needed
    print("[OK] FAISS does not require a separate server")

    return True

if __name__ == "__main__":
    print("RAG API Environment Test")
    print("="*40)

    if test_imports():
        print("\n[OK] All imports successful!")
    else:
        print("\n[ERROR] Some imports failed!")
        sys.exit(1)

    test_environment()

    print("\n" + "="*40)
    print("Test completed!")