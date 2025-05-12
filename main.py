from fastapi import FastAPI, HTTPException
from gradio_client import Client
from pydantic import BaseModel


class InferenceRequest(BaseModel):
    question: str


app = FastAPI()

@app.post("/inference")
async def inference(request: InferenceRequest):
    """
    Perform inference on the given question.
    """
    try:
        client = Client("GayanKK/FurSense-Chat")  # moved inside function
        result = client.predict(
            input=request.question,
            api_name="/predict"
        )
    #    print(result)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")
