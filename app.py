import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise ValueError("Nvidia api key is missing, check your .env file")
client = OpenAI(
base_url = "https://integrate.api.nvidia.com/v1",
api_key = api_key
)



app = FastAPI()

class QuestionRequest(BaseModel):
    question:str = Field(min_length = 1, max_length = 2000)

def ask_ai(question):
    try:
        response = client.chat.completions.create(
        model = "openai/gpt-oss-20b",
        messages = [{"role":"user", "content":question}],
        )
        return response.choices[0].message.content

    except AuthenticationError as error:
        raise HTTPException(
            status_code=502,
            detail="The AI provider rejected the configured credentials."
        ) from error

    except RateLimitError as error:
        raise HTTPException(
            status_code=503,
            detail="The AI provider is rate-limiting requests. Try again later."
        ) from error

    except APIError as error:
        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed."
        ) from error



@app.get("/")
def home():
    return {"message": "AI question answerer api is running"}

@app.post("/ask")
def ask_question(request:QuestionRequest):
    answer = ask_ai(request.question)
    return {"question": request.question, "answer":answer}
