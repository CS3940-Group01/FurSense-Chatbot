"""FastAPI application for FurSense Chatbot with MongoDB integration"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, APIRouter
from gradio_client import Client
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()

URL = os.getenv("URL")

class InferenceRequest(BaseModel):
    """Model for inference request"""
    question: str


app = FastAPI()
router = APIRouter(prefix="/chatbot")

mongodb_client = MongoClient(URL)
database = mongodb_client["furbot"]


@router.get("/get_chat_history")
async def get_chat_history(request: Request):
    """Endpoint to retrieve chat history for a user"""
    user_id = request.headers.get("userId")

    if user_id in database.list_collection_names():
        collection = database[user_id]
        # Fetch all chat history
        chat_history = list(collection.find({}, {"_id": 0}))
        return {"chat_history": chat_history}
    else:
        collection = database[user_id]
        collection.insert_one(
        { "id": "1", "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}
        )
        return {"chat_history": [{"id": 1, "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}]}


# Endpoint to delete chat history
@router.delete("/delete_chat_history")
async def delete_chat_history(request: Request):
    """Endpoint to delete chat history for a user"""
    user_id = request.headers.get("userId")

    if user_id in database.list_collection_names():
        collection = database[user_id]
        collection.delete_many({})
        collection.insert_one(
            {"id": 1, "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}
        )
    else:
        collection = database[user_id]
        collection.insert_one(
            {"id": 1, "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}
        )
    return {"chat_history": [{"id": 1, "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}]}


@router.post("/inference")
async def inference(request: InferenceRequest, req1uest: Request):
    """
    Perform inference on the given question.
    """
    user_id = req1uest.headers.get("userId")
    if user_id in database.list_collection_names():
        collection = database[user_id]
    else:
        collection = database[user_id]

    number_of_messages = collection.count_documents({})

    # Get the last 3 messages from the collection if available
    last_messages = list(collection.find({}, {"_id": 0}).sort("id", -1).limit(6))

    last_messages.reverse()

    history = []

    for message in last_messages:
        if message["sender"] == "user":
            history.append({"role": "user", "content": message["text"]})
        else:
            history.append({"role": "ai", "content": message["text"]})

    print("Last messages:", history)

    client = Client("GayanKK/FurSense-Chat")
    result = client.predict(
        question=request.question,
        context=history,
        api_name="/predict"
    )

    # Save the question and answer to MongoDB
    collection.insert_one({
        "id": number_of_messages + 1,
        "sender": "user",
        "text": request.question
    })
    collection.insert_one({
        "id": number_of_messages + 2,
        "sender": "bot",
        "text": result
    })

    return {"response": result}


app.include_router(router)
