import logging

from fastapi import APIRouter, HTTPException

from schemas.ingest import IngestRequest
from services.ingest_service import ingest_file

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest")
def ingest_controller(request: IngestRequest):
    try:
        result = ingest_file(request.file_name, str(request.s3_url))
        return {"status": "success", "data": result}
    except Exception:
        logger.exception("Ingest failed for %s", request.file_name)
        raise HTTPException(status_code=500, detail="Failed to ingest file")
