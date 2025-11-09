# review_engine.py
import os
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = "gpt-4o-mini"


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
)
def _call_openai(messages, model=DEFAULT_MODEL, max_tokens=800):
    """
    Wrapper around OpenAI's new Chat API syntax for openai>=1.0.0
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return response.choices[0].message.content


def review_code(code, filename="main.py", language="python", model=DEFAULT_MODEL):
    """
    Analyze the given code and return a structured review.
    Handles Markdown-wrapped or plain JSON responses gracefully.
    """
    prompt = f"""
You are an expert software engineer. Review this {language} code from {filename}.
Give a detailed JSON response with the following fields:
- summary: short purpose of the code
- issues: list of bugs or potential issues
- improvements: list of coding or design improvements
- performance: list of performance optimizations
- security: list of any security concerns
- refactor: improved version or snippet if possible

Respond ONLY with a valid JSON object. Do not include Markdown formatting, explanations, or comments.

Code:
{code}
"""

    messages = [
        {"role": "system", "content": "You are a precise and professional AI code reviewer."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = _call_openai(messages, model=model)

        # 🧹 Clean up potential Markdown fences like ```json ... ```
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.replace("```", "").strip()

        # ✅ Attempt to parse cleaned JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "raw_response": response,
                "error": "Invalid JSON format after cleaning. Model returned non-JSON text."
            }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Example test code
    sample_code = """
def add(a, b):
    return a + b

print(add(5, '3'))
"""
    result = review_code(sample_code, filename="sample.py")
    print(json.dumps(result, indent=2))
