from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.models.schemas import APIResponse
from app.services.history_service import (
    clear_all_history,
    delete_history_entry,
    get_history_stats,
    list_history,
)

router = APIRouter()


@router.get("/math/history", response_model=APIResponse, tags=["math"])
async def get_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip (for pagination)"),
    problem_type: Optional[str] = Query(None, description="Filter by problem type (e.g., 'linear_equation')"),
    date_from: Optional[datetime] = Query(None, description="Filter entries created after this datetime (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter entries created before this datetime (ISO 8601)"),
    search: Optional[str] = Query(None, description="Search in question text (case-insensitive)"),
) -> APIResponse:
    """
    Get history of solved math problems with filtering and pagination.
    
    Supports:
    - Pagination: use limit and offset
    - Filter by problem type: problem_type=linear_equation
    - Filter by date range: date_from=2024-01-01T00:00:00Z&date_to=2024-12-31T23:59:59Z
    - Search in questions: search=polynomial
    
    Returns paginated results with metadata.
    """
    entries, total_count = await list_history(
        limit=limit,
        offset=offset,
        problem_type=problem_type,
        date_from=date_from,
        date_to=date_to,
        search_query=search,
    )
    
    # Format entries
    items = [
        {
            "id": entry.id,
            "question": entry.question,
            "problem_type": entry.problem_type,
            "normalized_expression": entry.normalized_expression,
            "answer": entry.answer,
            "is_verified": entry.is_verified,
            "steps": entry.steps_json,
            "created_at": entry.created_at.isoformat(),
        }
        for entry in entries
    ]
    
    # Calculate pagination metadata
    has_more = (offset + len(items)) < total_count
    
    response_data = {
        "items": items,
        "pagination": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "returned_count": len(items),
            "has_more": has_more,
        },
    }
    
    return APIResponse(success=True, data=response_data, error=None)


@router.get("/math/history/stats", response_model=APIResponse, tags=["math"])
async def get_stats() -> APIResponse:
    """
    Get statistics about history entries.
    
    Returns:
    - Total count of entries
    - Count by problem type
    """
    stats = await get_history_stats()
    return APIResponse(success=True, data=stats, error=None)


@router.delete("/math/history/{entry_id}", response_model=APIResponse, tags=["math"])
async def delete_entry(entry_id: int) -> APIResponse:
    """
    Delete a specific history entry by ID.
    """
    deleted = await delete_history_entry(entry_id)
    
    if not deleted:
        return APIResponse(
            success=False,
            data=None,
            error=f"History entry with ID {entry_id} not found"
        )
    
    return APIResponse(
        success=True,
        data={"deleted_id": entry_id},
        error=None
    )


@router.delete("/math/history", response_model=APIResponse, tags=["math"])
async def clear_history() -> APIResponse:
    """
    Clear all history entries.
    
    WARNING: This permanently deletes all history. Use with caution.
    """
    count = await clear_all_history()
    
    return APIResponse(
        success=True,
        data={"deleted_count": count},
        error=None
    )
