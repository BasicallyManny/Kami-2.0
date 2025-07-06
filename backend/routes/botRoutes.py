from fastapi import APIRouter, HTTPException
from minecraft_assistant.chatbot import generate_response
from models.chatbotModels import ChatRequest

chatbotRouter = APIRouter()

@chatbotRouter.post("/chatbot/{guild_id}/{channel_id}")
async def chatbot_response(request: ChatRequest):
    try:
        response = await generate_response(query=request.query, session_id=request.session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))