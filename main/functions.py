from deep_translator import GoogleTranslator
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
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


def audio_to_text(audio_path):
    audio = AudioSegment.from_file(audio_path, format="aac")
    audio = audio.set_channels(1)
    audio.export("media/temp/temp.wav", format="wav")

    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile("media/temp/temp.wav")

    with audio_file as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Речь не распознана"
    except sr.RequestError as e:
        return f"Ошибка запроса к сервису распознавания: {str(e)}"


import requests

def text_to_speech(text):
    url = 'https://api.narakeet.com/text-to-speech/m4a'
    
    headers = {
        'Accept': 'application/octet-stream',
        'Content-Type': 'text/plain',
        'x-api-key': 'hZctKZjQNh8yFrSKG61Ms1buS6MXsnYK1HnKJowK',
    }
    
    params = {
        'voice': 'dilnoza',  # Используем имя голоса
        'language': 'uz-UZ'  # Используем код языка
    }
    
    data = text.encode('utf8')
    
    response = requests.post(url, headers=headers, params=params, data=data)
    
    if response.status_code == 200:
        with open('media/audio/output_audio.m4a', 'wb') as f:
            f.write(response.content)
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")


# def text_to_speech(text, output_path='media/audio/output_audio.mp3'):
#     tts = gTTS(text, lang='ru')
#     tts.save(output_path)
#     return output_path