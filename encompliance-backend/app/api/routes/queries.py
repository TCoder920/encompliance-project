from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.query_log import QueryLog
from app.auth.dependencies import get_current_user
from datetime import datetime
from fastapi.responses import JSONResponse

router = APIRouter(tags=["queries"])

# Add OPTIONS handler for CORS preflight requests
@router.options("/query-logs")
@router.options("/query/{query_id}")
@router.options("/queries/all")
async def options_queries():
    """
    Handle OPTIONS requests for query endpoints.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.get("/query-logs")
async def get_query_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0
):
    """
    Get recent query logs for the current user.
    
    Parameters:
    - limit: Maximum number of logs to return (default: 20)
    - skip: Number of logs to skip (for pagination)
    """
    try:
        # Log current user info for debugging
        print(f"Getting query logs for user: {current_user.id}, username: {current_user.username}")
        print(f"Parameters: limit={limit}, skip={skip}")
        
        # Check if query_logs table exists
        try:
            db.execute("SELECT 1 FROM query_logs LIMIT 1")
            print("query_logs table exists")
        except Exception as table_err:
            print(f"Error checking query_logs table: {str(table_err)}")
            # Create the table if it doesn't exist
            from app.models.query_log import QueryLog
            from app.database import Base, engine
            Base.metadata.create_all(bind=engine, tables=[QueryLog.__table__])
            print("Created query_logs table")
        
        # Get recent queries for the current user
        query = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id
        ).order_by(
            QueryLog.created_at.desc()
        )
        
        # Apply pagination
        total_count = query.count()
        queries = query.offset(skip).limit(limit).all()
        
        print(f"Found {len(queries)} logs for user {current_user.id} (total: {total_count})")
        
        # Format the response
        logs = []
        for query in queries:
            # Debug log to see what's in each query
            print(f"Query log: id={query.id}, query={query.query[:30]}..., created_at={query.created_at}")
            
            logs.append({
                "id": query.id,
                "query_text": query.query,
                "response_text": query.response,
                "created_at": query.created_at.isoformat(),
                "document_reference": query.document_reference,
                "conversation_id": query.conversation_id,
                "document_id": query.document_id
            })
        
        # Debug log the final response
        print(f"Returning {len(logs)} logs to client")
        for log in logs:
            print(f"  - Log: id={log['id']}, query={log['query_text'][:30]}..., created_at={log['created_at']}")
        
        return {
            "logs": logs,
            "total": total_count,
            "limit": limit,
            "skip": skip
        }
    except Exception as e:
        # Enhanced error logging
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error getting query logs: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get query logs: {str(e)}"
        )

@router.get("/query/{query_id}")
async def get_query_details(
    query_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get details for a specific query.
    """
    try:
        print(f"Getting query details for ID: {query_id}, user: {current_user.id}")
        
        # Get the query
        query = db.query(QueryLog).filter(
            QueryLog.id == query_id,
            QueryLog.user_id == current_user.id
        ).first()
        
        if not query:
            print(f"Query with ID {query_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with ID {query_id} not found"
            )
        
        print(f"Found query: id={query.id}, query={query.query[:30]}..., document_id={query.document_id}, conversation_id={query.conversation_id}")
        
        # Format the response
        response_data = {
            "id": query.id,
            "query_text": query.query,
            "response_text": query.response,
            "created_at": query.created_at.isoformat(),
            "document_reference": query.document_reference,
            "conversation_id": query.conversation_id,
            "full_conversation": query.conversation_id is not None,
            "documentIds": [query.document_id] if query.document_id and query.document_id > 0 else []
        }
        
        print(f"Returning query details: {response_data}")
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error getting query details: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get query details: {str(e)}"
        )

@router.delete("/query/{query_id}")
async def delete_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a specific query log.
    """
    try:
        print(f"Deleting query with ID: {query_id}, user: {current_user.id}")
        
        # Find the query
        query = db.query(QueryLog).filter(
            QueryLog.id == query_id,
            QueryLog.user_id == current_user.id
        ).first()
        
        if not query:
            print(f"Query with ID {query_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with ID {query_id} not found"
            )
        
        # Delete the query
        db.delete(query)
        db.commit()
        
        print(f"Successfully deleted query with ID: {query_id}")
        return {"message": f"Query with ID {query_id} has been deleted"}
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error deleting query: {str(e)}")
        print(f"Traceback: {error_traceback}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete query: {str(e)}"
        )

@router.delete("/queries/all")
async def delete_all_queries(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete all query logs for the current user.
    """
    try:
        print(f"Deleting all queries for user: {current_user.id}")
        
        # Find and count all queries for this user
        query_count = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id
        ).count()
        
        # Delete all queries for this user
        result = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id
        ).delete(synchronize_session=False)
        
        # Commit the transaction
        db.commit()
        
        print(f"Successfully deleted {result} queries for user {current_user.id}")
        return {"message": f"Successfully deleted {result} queries", "count": result}
    except Exception as e:
        # Log the error
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error deleting all queries: {str(e)}")
        print(f"Traceback: {error_traceback}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all queries: {str(e)}"
        ) 