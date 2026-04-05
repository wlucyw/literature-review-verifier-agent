from fastapi import APIRouter, HTTPException

from app.core.schemas import VerifyRequest, VerifyResponse
from app.services.verify_service import VerifyService

router = APIRouter()
service = VerifyService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "literature-review-verifier"}


@router.post("/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest) -> VerifyResponse:
    try:
        return service.verify(request)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
