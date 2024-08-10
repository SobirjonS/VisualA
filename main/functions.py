from . import models
from django.core.files import File

from deep_translator import GoogleTranslator
import google.generativeai as genai
import speech_recognition as sr
from io import BytesIO
import requests
import sys
import re
import os


def translate_uz_to_en(text: str) -> str:
    translator = GoogleTranslator(source='uz', target='en')
    translation = translator.translate(text)
    return translation


def translate_en_to_uz(text: str) -> str:
    translator = GoogleTranslator(source='en', target='uz')
    translation = translator.translate(text)
    return translation


def translate_ru_to_uz(text: str) -> str:
    translator = GoogleTranslator(source='ru', target='uz')
    translation = translator.translate(text)
    return translation


def generate_answer(data):
    stderr_fileno = sys.stderr.fileno()
    old_stderr = os.dup(stderr_fileno)
    sys.stderr.flush()
    os.dup2(os.open(os.devnull, os.O_WRONLY), stderr_fileno)
    try:
        genai.configure(api_key="AIzaSyDwsJ-wwN943ubYPgZm6jhHs0zpCS4ZlWw")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(data)
    finally:
        sys.stderr.flush()
        os.dup2(old_stderr, stderr_fileno)
        os.close(old_stderr)
    clean_response = re.sub(r'\n|\*|\*\*', '', response.text).strip()
    return clean_response   


def audio_to_text(audio):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio)

    with audio_file as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Речь не распознана"
    except sr.RequestError as e:
        return f"Ошибка запроса к сервису распознавания: {str(e)}"



def text_to_speech(text, user):
    url = 'https://api.narakeet.com/text-to-speech/m4a'
    
    headers = {
        'Accept': 'application/octet-stream',
        'Content-Type': 'text/plain',
        'x-api-key': 'hZctKZjQNh8yFrSKG61Ms1buS6MXsnYK1HnKJowK',
    }
    
    params = {
        'voice': 'dilnoza',
        'language': 'uz-UZ'
    }
    
    data = text.encode('utf8')
    
    response = requests.post(url, headers=headers, params=params, data=data)
    
    if response.status_code == 200:
        m4a_audio = BytesIO(response.content)
        m4a_audio.seek(0)
        
        m4a_file = File(m4a_audio, name="audio_answer.m4a")
        audio_instance = models.ResponseAudio(user=user, audio=m4a_file)
        audio_instance.save()