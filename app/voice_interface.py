


import threading
import time
import pyttsx3
import speech_recognition as sr
from chat_engine import ask_ollama

# Initialize the engine once to avoid "run loop already started" errors
engine = pyttsx3.init()

def speak(text):
    engine.stop()  # stop any previous speech
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Speech recognition service is unavailable."


def wake_word_listener():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Waiting for wake word...")
        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                if "hey pekko" in text:
                    print("👂 Wake word detected!")
                    run_voice_assistant()
                    break
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("⚠️ Speech recognition service unavailable.")
                break


def run_voice_assistant():
    speak("I'm listening.")
    prompt = listen()
    print(f"🧑 You said: {prompt}")
    start_time = time.time()
    response = ask_ollama(prompt)
    delay = round(time.time() - start_time, 2)
    print(f"🤖 Pekko: {response} (⏱️ Response time: {delay}s)")
    if delay > 5:
        speak("Sorry for the delay.")
    speak(response)

def start_wake_listener():
    threading.Thread(target=wake_word_listener, daemon=True).start()