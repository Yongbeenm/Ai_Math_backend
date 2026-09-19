from fastapi import APIRouter

from app.models.schemas import APIResponse, SolveRequest
from app.services.history_service import save_history_entry
from app.services.math_service import MathProcessingError, process_question

router = APIRouter()


@router.post("/math/solve", response_model=APIResponse, tags=["math"])
async def solve_math(payload: SolveRequest) -> APIResponse:
    try:
        data = process_question(payload.question)
    except MathProcessingError as exc:
        return APIResponse(success=False, data=None, error=str(exc))

    await save_history_entry(question=payload.question, data=data)
    return APIResponse(success=True, data=data, error=None)
