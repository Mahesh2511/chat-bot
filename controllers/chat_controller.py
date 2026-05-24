import logging

from fastapi import APIRouter, Header, HTTPException

from schemas.chat import ChatRequest
from services.chat_service import conversation

logger = logging.getLogger(__name__)
router = APIRouter()

# This reads the `x-user-id` HTTP header and assigns its value to `x_user_id`, or uses `"anonymous"` as the default if the header is missing.
@router.post("/chat")
def chat_controller(
    request: ChatRequest,
    x_user_id: str = Header(default="anonymous"),
):
    try:
        answer = conversation(user_id=x_user_id, q=request.q)
        logger.info("Chat response generated for user %s", x_user_id)
        return {"status": "success", "data": answer}
    except Exception:
        logger.exception("Chat failed for user %s", x_user_id)
        raise HTTPException(status_code=500, detail="Failed to generate a response")
