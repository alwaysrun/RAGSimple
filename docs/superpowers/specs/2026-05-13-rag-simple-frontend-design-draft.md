# RAGSimple Design: Streamlit Frontend

## 1. User Interface Layout

### Sidebar: Control Center
- **Configuration Overview:** Displays active LLM model and Embedding model (read from backend `/config`).
- **Document Management:**
    - **File Uploader:** Drag-and-drop for `.pdf`, `.md`, `.txt`.
    - **Ingestion Button:** Triggers the `/ingest` call to the backend.
    - **Document List:** Shows currently indexed files (fetched via `/documents`).
- **System Actions:**
    - **Clear Chat:** Resets the local Streamlit session state.
    - **Reset Database:** Triggers the `/reset` call to the backend.

### Main Area: Chat Interface
- **Chat History:** Displays messages from the user and responses from the RAG system in a standard chat bubble format.
- **Reference display:** (Optional) Expandable section below each AI response showing which document chunks were used as context.
- **Chat Input:** Fixed at the bottom for user queries.

## 2. Communication Strategy (Frontend -> Backend)
- **API Client:** A dedicated Python module within the Streamlit app to handle all `requests` to the FastAPI backend.
- **Error Handling:** Displays friendly error messages (e.g., "Connection to backend failed", "LLM API Error") via `st.error`.
- **Loading States:** Uses `st.spinner` during ingestion and query execution to provide visual feedback.

## 3. Tech Stack
- **UI Framework:** Streamlit
- **HTTP Client:** `requests`

---
**Does this Streamlit UI design meet your requirements?** If so, I will proceed to consolidate everything into the final design document.
