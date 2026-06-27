import requests
from content import ai_context_string
from secret.secret import GEMINI_API_KEY

def get_ai_answer(question):
    api_key = GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = ai_context_string + "\n\nОтветь на вопрос пользователя об этом человеке на основе контекста выше:\n" + question

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            return f"Ошибка API ({response.status_code}): {response.text}"
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Извини, ИИ сейчас недоступен. Ошибка: {e}"