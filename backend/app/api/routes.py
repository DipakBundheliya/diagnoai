from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.services.langchain_service import get_ai_response

# create fast api router
router = APIRouter()

# Request model
class ChatRequest(BaseModel):
    user_id: str
    query: str

# chat API
@router.post("/chat")
async def chat_with_ai(request : ChatRequest):
    try:
        response = get_ai_response(request.query , request.user_id)
        return {"user_id": request.user_id , "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# for test api , you can enter curl command , curl -X 'POST' \  'http://127.0.0.1:8000/chat' \  -H 'Content-Type: application/json' \  -d '{    "user_id": "223456",    "query": "I feel unwell"}'