from datetime import datetime

from sqlalchemy import select
from sqlalchemy.sql import and_

from app.db.session import async_session_maker
from app.models.db_models import SolveHistory
from app.models.schemas import SolveData


async def save_history_entry(question: str, data: SolveData) -> None:
    async with async_session_maker() as session:
        entry = SolveHistory(
            question=question,
            problem_type=data.problem_type,
            normalized_expression=data.normalized_expression,
            answer=data.answer,
            is_verified=data.is_verified,
            steps_json=[step.model_dump() for step in data.steps],
        )
        session.add(entry)
        await session.commit()


async def list_history(
    limit: int = 50,
    offset: int = 0,
    problem_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search_query: str | None = None,
) -> tuple[list[SolveHistory], int]:
    """
    List history entries with filtering and pagination.
    
    Args:
        limit: Maximum number of entries to return (pagination)
        offset: Number of entries to skip (pagination)
        problem_type: Filter by problem type (e.g., "linear_equation")
        date_from: Filter entries created after this datetime
        date_to: Filter entries created before this datetime
        search_query: Search in question text (case-insensitive partial match)
    
    Returns:
        Tuple of (entries list, total count matching filters)
    """
    async with async_session_maker() as session:
        # Build filter conditions
        conditions = []
        
        if problem_type:
            conditions.append(SolveHistory.problem_type == problem_type)
        
        if date_from:
            conditions.append(SolveHistory.created_at >= date_from)
        
        if date_to:
            conditions.append(SolveHistory.created_at <= date_to)
        
        if search_query:
            # Case-insensitive partial match on question
            conditions.append(SolveHistory.question.ilike(f"%{search_query}%"))
        
        # Build query with filters
        query = select(SolveHistory).order_by(SolveHistory.id.desc())
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count (for pagination metadata)
        count_query = select(SolveHistory.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await session.execute(count_query)
        total_count = len(count_result.all())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute
        result = await session.execute(query)
        entries = list(result.scalars().all())
        
        return entries, total_count


async def get_history_stats() -> dict:
    """
    Get statistics about history entries.
    
    Returns:
        Dict with counts by problem type and total count
    """
    async with async_session_maker() as session:
        # Total count
        total_result = await session.execute(select(SolveHistory.id))
        total_count = len(total_result.all())
        
        # Count by problem type
        type_result = await session.execute(
            select(SolveHistory.problem_type, SolveHistory.id)
        )
        
        type_counts = {}
        for problem_type, _ in type_result.all():
            type_counts[problem_type] = type_counts.get(problem_type, 0) + 1
        
        return {
            "total_count": total_count,
            "by_problem_type": type_counts,
        }


async def delete_history_entry(entry_id: int) -> bool:
    """
    Delete a history entry by ID.
    
    Returns:
        True if deleted, False if not found
    """
    async with async_session_maker() as session:
        result = await session.execute(
            select(SolveHistory).where(SolveHistory.id == entry_id)
        )
        entry = result.scalar_one_or_none()
        
        if entry is None:
            return False
        
        await session.delete(entry)
        await session.commit()
        return True


async def clear_all_history() -> int:
    """
    Clear all history entries.
    
    Returns:
        Number of entries deleted
    """
    async with async_session_maker() as session:
        result = await session.execute(select(SolveHistory))
        entries = result.scalars().all()
        count = len(entries)
        
        for entry in entries:
            await session.delete(entry)
        
        await session.commit()
        return count
