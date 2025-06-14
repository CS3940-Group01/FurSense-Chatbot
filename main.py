from fastapi import FastAPI, HTTPException, Request
from gradio_client import Client
from pydantic import BaseModel
from pymongo import MongoClient


class InferenceRequest(BaseModel):
    question: str


app = FastAPI()
mongodb_client = MongoClient("mongodb+srv://gaykaush:kangaroo18324@cluster0.mpkvg4p.mongodb.net/")
database = mongodb_client["furbot"]

#global user_id


@app.get("/get_chat_history")
async def get_chat_history(request: Request):
    user_id = request.headers.get("userId")
    
    if user_id in database.list_collection_names():
        collection = database[user_id]
        # Fetch all chat history
        chat_history = list(collection.find({}, {"_id": 0}))
        
        return {"chat_history": chat_history}
    else:
        collection = database[user_id]
        collection.insert_one({
        { "id": "1", "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}
        })
        return {"chat_history": [{"id": "1", "sender": "bot", "text": "Hi, I'm your FurBot. How can I assist you today?"}]}
    




@app.post("/inference")
async def inference(request: InferenceRequest, req1uest: Request):
    """
    Perform inference on the given question.
    """
    try:
        client = Client("GayanKK/FurSense-Chat")  # moved inside function
        result = client.predict(
            input=request.question,
            api_name="/predict"
        )
        
  #      result.replace("*", "")  
    #    print(result)

        # Save the question and answer to MongoDB
        user_id = req1uest.headers.get("userId")
        if user_id in database.list_collection_names():
            collection = database[user_id]
        else:
            collection = database[user_id]
            
        number_of_messages = collection.count_documents({})    
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")
