

import json
from memory_manager import recall
import requests


def load_profile():
    with open("data/profile.json") as f:
        profile = json.load(f)
        # Ensure "owner" key exists to avoid KeyError
        if "owner" not in profile:
            profile["owner"] = "your user"
        return profile

profile = load_profile()


# LLaMA/Mistral (Ollama) API integration
def ask_ollama(prompt, model="mistral"):
    context = recall("chat_history")
    context_str = "\n".join([f"{m['user']} → {m['pekko']}" for m in context]) if isinstance(context, list) else ""
    full_prompt = f"{context_str}\nUser: {prompt}"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": full_prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"[Ollama Error: {e}]"


# Weather API helper
def get_weather(city):
    api_key = "2211f45ee8adc0562f5b8abb832d8562"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("main"):
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"The current temperature in {city.title()} is {temp}°C with {desc}."
        elif data.get("message"):
            return f"⚠️ Could not retrieve weather: {data['message']}"
        else:
            return "⚠️ Sorry, I couldn't fetch the weather right now."
    except Exception as e:
        return f"❌ Weather fetch failed: {e}"