# Actionable Task List: Physical AI & Humanoid Robotics Textbook Portal

This document provides a detailed, low-level list of actionable tasks for the project, broken down by phase as defined in `plan.md`.

## Phase 1: Content and Docusaurus Structure (Book MVP)

1.  **Syllabus Finalization**:
    *   [ ] 1.1. Review and confirm the 12-chapter syllabus outlined in `.specify/specs/01-book-and-rag-portal.md`.

2.  **Chapter Generation (Gemini CLI)**:
    *   [ ] 2.1. Create a new directory `docs/textbook`.
    *   [ ] 2.2. Generate "Chapter 1: Introduction to Physical AI and Robotics" (`docs/textbook/ch01-introduction.md`).
    *   [ ] 2.3. Generate "Chapter 2: Robot Kinematics and Dynamics" (`docs/textbook/ch02-kinematics-dynamics.md`).
    *   [ ] 2.4. Generate "Chapter 3: Sensors and Perception for Physical AI" (`docs/textbook/ch03-sensors-perception.md`).
    *   [ ] 2.5. Generate "Chapter 4: Robot Control Architectures" (`docs/textbook/ch04-control-architectures.md`).
    *   [ ] 2.6. Generate "Chapter 5: Machine Learning for Robotic Control" (`docs/textbook/ch05-ml-for-control.md`).
    *   [ ] 2.7. Generate "Chapter 6: Reinforcement Learning in Robotics" (`docs/textbook/ch06-rl-in-robotics.md`).
    *   [ ] 2.8. Generate "Chapter 7: Humanoid Robot Design and Actuation" (`docs/textbook/ch07-humanoid-design.md`).
    *   [ ] 2.9. Generate "Chapter 8: Human-Robot Interaction and Collaboration" (`docs/textbook/ch08-hri-collaboration.md`).
    *   [ ] 2.10. Generate "Chapter 9: Ethical and Societal Implications of Humanoid AI" (`docs/textbook/ch09-ethics-society.md`).
    *   [ ] 2.11. Generate "Chapter 10: Advanced Locomotion and Manipulation" (`docs/textbook/ch10-advanced-locomotion.md`).
    *   [ ] 2.12. Generate "Chapter 11: Swarm Robotics and Multi-Agent Systems" (`docs/textbook/ch11-swarm-robotics.md`).
    *   [ ] 2.13. Generate "Chapter 12: Future Trends and Research Challenges" (`docs/textbook/ch12-future-trends.md`).

3.  **Docusaurus Configuration**:
    *   [ ] 3.1. Modify `sidebars.js` to create a new sidebar for the textbook.
    *   [ ] 3.2. Structure the sidebar into four parts as specified in the plan, linking all 12 generated chapters.
    *   [ ] 3.3. Update `docusaurus.config.js` to add a link to the textbook in the main navbar.
    *   [ ] 3.4. Run `npm start` to test the new Docusaurus structure locally.

## Phase 2: RAG Backend Infrastructure

4.  **Qdrant Cloud Setup**:
    *   [ ] 4.1. Create an account on the Qdrant Cloud platform.
    *   [ ] 4.2. Provision a new free-tier vector database cluster.
    *   [ ] 4.3. Obtain the cluster URL and API key.
    *   [ ] 4.4. Store credentials securely (e.g., in a `.env` file or environment variables).

5.  **Neon Postgres Setup**:
    *   [ ] 5.1. Create an account on Neon.
    *   [ ] 5.2. Create a new serverless Postgres project.
    *   [ ] 5.3. Obtain the database connection string.
    *   [ ] 5.4. Store the connection string securely.

6.  **FastAPI Backend Development**:
    *   [ ] 6.1. Create a new directory for the backend (e.g., `backend/`).
    *   [ ] 6.2. Set up a Python virtual environment.
    *   [ ] 6.3. Install necessary packages: `fastapi`, `uvicorn`, `qdrant-client`, `psycopg2-binary`, `openai`.
    *   [ ] 6.4. Create a main application file (`main.py`) and define the core FastAPI app.
    *   [ ] 6.5. Implement an API endpoint (e.g., `/chat`) to receive user queries.
    *   [ ] 6.6. Develop a service module to connect to and interact with Qdrant.
    *   [ ] 6.7. Develop a service module to connect to and interact with Neon Postgres.
    *   [ ] 6.8. Implement the logic for embedding text and performing vector searches.

## Phase 3: RAG Frontend and Integration

7.  **Chatbot UI Component Development**:
    *   [ ] 7.1. Create a new React component for the chat interface (e.g., `src/components/Chatbot/index.js` and `styles.css`).
    *   [ ] 7.2. Design the UI with an input field, a send button, and a message display area.
    *   [ ] 7.3. Implement state management for the chat history and user input.

8.  **Docusaurus Integration**:
    *   [ ] 8.1. "Swizzle" the Docusaurus `Layout` component to add a persistent space for the chatbot UI.
    *   [ ] 8.2. Import and render the new `Chatbot` component within the swizzled `Layout`.
    *   [ ] 8.3. Implement the API call from the Chatbot component to the FastAPI backend's `/chat` endpoint.

9.  **Contextual RAG Implementation**:
    *   [ ] 9.1. Add JavaScript logic to the frontend to capture text selected by the user in the textbook content area.
    *   [ ] 9.2. Add a button or context menu item (e.g., "Ask about this") that appears when text is selected.
    *   [ ] 9.3. Modify the `/chat` API call to include the selected text as additional context in the payload.
    *   [ ] 9.4. Update the FastAPI backend to prioritize the provided context when performing the vector search and generating the prompt for the language model.
