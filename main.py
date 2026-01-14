from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import speech_recognition as sr
from langdetect import detect
from googletrans import Translator
from gtts import gTTS
import uuid
import os

app = FastAPI()
translator = Translator()

AUDIO_FOLDER = "audio_outputs"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Multilingual Avatar Backend is running"}

# 🎤 Speech → Text + Language Detection
@app.post("/speech-to-text/")
async def speech_to_text(audio: UploadFile = File(...)):
    recognizer = sr.Recognizer()

    temp_audio = f"temp_{uuid.uuid4()}.wav"
    with open(temp_audio, "wb") as f:
        f.write(await audio.read())

    try:
        with sr.AudioFile(temp_audio) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        language = detect(text)

        return {
            "text": text,
            "detected_language": language
        }

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    finally:
        os.remove(temp_audio)

# 🌍 Translation Endpoint
@app.post("/translate/")
def translate_text(text: str, target_language: str):
    translated = translator.translate(text, dest=target_language)
    return {
        "original_text": text,
        "translated_text": translated.text,
        "target_language": target_language
    }

# 🧑‍🎤 Text → Avatar Voice
@app.post("/text-to-speech/")
def text_to_speech(text: str, language: str = "en"):
    filename = f"{AUDIO_FOLDER}/{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang=language)
    tts.save(filename)

    return {
        "message": "Audio generated",
        "audio_file": filename
      }
