# Implementation Plan: Physical AI & Humanoid Robotics Textbook Portal

This document outlines the phased implementation plan for the "Physical AI & Humanoid Robotics Textbook Portal" project. The plan is divided into three distinct phases, prioritizing the development of the core textbook content and Docusaurus structure, followed by the implementation of the RAG (Retrieval Augmented Generation) chatbot system.

## Phase 1: Content and Docusaurus Structure (Book MVP)

**Objective**: To create a minimum viable product (MVP) of the textbook, focusing on content generation, structuring the Docusaurus site, and ensuring a solid foundation for the subsequent RAG implementation.

### 1.1. Syllabus Finalization (12 Chapters)
*   **Task**: Review and finalize the 12-chapter syllabus as outlined in the project specification (`01-book-and-rag-portal.md`).
*   **Details**: Ensure chapter titles, order, and content scope are well-defined before content generation begins. This step is critical for maintaining a logical flow and comprehensive coverage of the subject matter.

### 1.2. Chapter Generation (using Gemini CLI)
*   **Task**: Generate the content for each of the 12 chapters using the Gemini CLI.
*   **Details**: Each chapter will be generated as a separate Markdown file. The generation process will adhere strictly to the rules defined in the `constitution.md` file, ensuring technical accuracy, appropriate formatting (H2 headings, LaTeX for equations), and suitability for the target audience.

### 1.3. Docusaurus Sidebar Configuration
*   **Task**: Configure the Docusaurus sidebar to reflect the 12-chapter structure of the textbook.
*   **Details**: This involves editing the `sidebars.js` file to create a logical and user-friendly navigation structure. The sidebar will be organized into four parts, corresponding to the four thematic sections of the book.

## Phase 2: RAG Backend Infrastructure

**Objective**: To build the backend infrastructure required to support the RAG chatbot, including setting up the vector database, relational database, API, and selecting an appropriate embedding model.

### 2.1. Qdrant Cloud Setup
*   **Task**: Set up a new Qdrant Cloud instance using the free tier.
*   **Details**: This will involve creating an account, provisioning a new cluster, and obtaining the necessary API keys for connecting to the vector database.

### 2.2. Neon Postgres Setup
*   **Task**: Set up a new serverless Postgres database using Neon.
*   **Details**: Create a new project, configure the database, and obtain the connection string for use in the FastAPI backend. This database will store metadata associated with the textbook content.

### 2.3. FastAPI Backend Development
*   **Task**: Develop a FastAPI application to serve as the backend for the RAG chatbot.
*   **Details**: The API will have endpoints for handling user queries, interacting with the Qdrant and Neon databases, and communicating with the OpenAI Agents/ChatKit SDKs. This will include logic for embedding queries and processing retrieved context.

### 2.4. Embedding Model Selection
*   **Task**: Research and select a suitable text embedding model.
*   **Details**: Evaluate available models (e.g., from OpenAI, Hugging Face) based on performance, cost, and ease of integration. The chosen model will be used to convert both the textbook content and user queries into vector representations.

## Phase 3: RAG Frontend and Integration

**Objective**: To develop the frontend components for the chatbot and integrate them into the Docusaurus portal, including the implementation of the contextual RAG feature.

### 3.1. Chatbot Component Development (Docusaurus Integration)
*   **Task**: Create a new React component for the chatbot interface.
*   **Details**: This component will be integrated into the Docusaurus frontend, providing a user-friendly interface for interacting with the chatbot. It will handle user input, display responses, and manage the chat history.

### 3.2. Contextual RAG Logic (User Selection Feature)
*   **Task**: Implement the logic for contextual RAG.
*   **Details**: This will involve developing a mechanism for users to select specific text passages within the Docusaurus book. The selected text will be passed to the backend along with the user's query, allowing the chatbot to provide highly relevant, context-aware answers. This feature will require close integration between the Docusaurus frontend and the FastAPI backend.
