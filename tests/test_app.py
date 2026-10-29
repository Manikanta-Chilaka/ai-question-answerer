from fastapi.testclient import TestClient
from app import app
from unittest.mock import patch
from openai import RateLimitError
import httpx

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message" : "AI question answerer api is running"
    }

def test_short():
    response = client.post(
        "/ask",
        json = {"question":""}
    )
    assert response.status_code == 422

def test_long():
    response = client.post(
        "/ask",
        json = {"question":"a"*10000}
    )
    assert response.status_code == 422


def test_ask_success():
    with patch("app.ask_ai", return_value = "Python is a programming language") as mock_ai:
        response = client.post(
            "/ask",
            json = {"question":"What is python?"}
        )
        assert response.json() == {
            "question":"What is python?",
            "answer":"Python is a programming language"
        }

        mock_ai.assert_called_once_with("What is python?")




def test_rate_limit():
    request = httpx.Request(
        "POST",
        "https://integrate.api.nvidia.com/v1/chat/completions"
    )

    response = httpx.Response(
        429,
        request=request,
        json={"error": {"message": "Rate limit reached"}}
    )

    with patch(
        "app.client.chat.completions.create",
        side_effect=RateLimitError(
            message="Rate limit reached",
            response=response,
            body={"error": {"message": "Rate limit reached"}}
        )
    ):
        result = client.post(
            "/ask",
            json={"question": "What is Python?"}
        )

    assert result.status_code == 503
    assert result.json() == {
        "detail": "The AI provider is rate-limiting requests. Try again later."
    }
