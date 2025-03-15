import uvicorn
import app.services.document_service as document_service

if __name__ == "__main__":
    # Ensure documents are indexed at startup
    document_service.index_existing_documents()  # Force indexation
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 