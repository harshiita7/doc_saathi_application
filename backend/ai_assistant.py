"""
ai_assistant.py
---------------
Connects to the Google Gemini REST API and generates an answer
to the user's question using relevant passages from the uploaded PDF.

We call the Gemini REST API directly with httpx instead of the
google-genai SDK to avoid the SDK's aggressive retry behaviour,
which can hang the server when a model is unavailable.
"""

import os

import httpx


# Base URL for the Gemini generateContent REST endpoint
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent"
)

# Model to use. This can be changed without touching any other file.
# Confirmed working via live test: gemini-3.1-flash-lite
_MODEL = "gemini-3.1-flash-lite"


def generate_answer(question: str, passages: list) -> str:
    """
    Send the user's question and relevant document passages to Gemini.

    Parameters
    ----------
    question : str
        The plain-language question from the user.
    passages : list of dict
        Each dict has {"page": int, "text": str} from document_search.py.

    Returns
    -------
    str
        The AI-generated answer text.

    Raises
    ------
    RuntimeError
        If the API key is missing or the Gemini API returns an error.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")

    # Build the context from all relevant passages, tagged by page number
    context = "\n\n".join(
        f"[Page {p['page']}]\n{p['text']}" for p in passages
    )

    # Prompt engineering — keep answers grounded in the document
    prompt = (
        "You are a helpful government document assistant.\n"
        "Answer the user's question using ONLY the information provided below "
        "from the uploaded government document.\n"
        "Explain your answer in simple, clear English.\n"
        "Do NOT invent government rules, eligibility criteria, dates, amounts, "
        "or procedures that are not explicitly mentioned in the supplied text.\n"
        "If the answer cannot be found in the provided information, respond with:\n"
        "\"I could not find the answer to this question in the uploaded document.\"\n\n"
        f"Document information:\n{context}\n\n"
        f"Question: {question}"
    )

    url = _GEMINI_URL.format(model=_MODEL)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,   # Keep answers factual and consistent
            "maxOutputTokens": 1024,
        },
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                url,
                params={"key": api_key},
                json=payload,
            )

        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", response.text)
            raise RuntimeError(f"Gemini API error ({response.status_code}): {error_msg}")

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    except httpx.TimeoutException:
        raise RuntimeError("Gemini did not respond in time. Please try again.")
    except (KeyError, IndexError) as exc:
        raise RuntimeError("Unexpected response format from Gemini API.") from exc
