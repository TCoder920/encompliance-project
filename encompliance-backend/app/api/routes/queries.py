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
async def options_queries():
    """
    Handle OPTIONS requests for query endpoints.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.get("/query-logs")
async def get_query_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = 10
):
    """
    Get recent query logs for the current user.
    """
    try:
        # Log current user info for debugging
        print(f"Getting query logs for user: {current_user.id}, username: {current_user.username}")
        
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
        queries = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id
        ).order_by(
            QueryLog.created_at.desc()
        ).limit(limit).all()
        
        print(f"Found {len(queries)} logs for user {current_user.id}")
        
        # Format the response
        logs = []
        for query in queries:
            logs.append({
                "id": query.id,
                "query": query.query_text,
                "timestamp": query.created_at.strftime("%b %d, %I:%M %p"),
                "document": query.document_name
            })
        
        return {"logs": logs}
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
        # Get the query
        query = db.query(QueryLog).filter(
            QueryLog.id == query_id,
            QueryLog.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with ID {query_id} not found"
            )
        
        # Format the response
        return {
            "id": query.id,
            "query": query.query_text,
            "response": query.response_text,
            "timestamp": query.created_at.isoformat(),
            "document": query.document_name,
            "full_conversation": query.conversation_id is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        print(f"Error getting query details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get query details: {str(e)}"
        ) 