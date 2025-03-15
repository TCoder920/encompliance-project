import asyncio
import sqlite3
from app.database import get_db
from app.services.document_service import list_documents

async def test_list_documents():
    db = next(get_db())
    user_id = 8  # User ID to test
    
    # Direct DB check
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE uploaded_by = ? AND is_deleted = 0", (user_id,))
    rows = cursor.fetchall()
    print(f"Direct DB query found {len(rows)} documents for user {user_id}")
    for row in rows:
        print(f"Document ID: {row[0]}, Filename: {row[1]}, Filepath: {row[2]}")
    
    # Test service function
    try:
        documents = await list_documents(db, user_id)
        print(f"\nService function found {len(documents)} documents for user {user_id}")
        for doc in documents:
            print(f"Document ID: {doc['id']}, Filename: {doc['filename']}")
    except Exception as e:
        print(f"Error in list_documents: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_list_documents()) 