import google.generativeai as genai
from django.conf import settings
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import sys
import re
import os


def generate_answer(data):
    # Сохраняем текущий stderr
    stderr_fileno = sys.stderr.fileno()
    old_stderr = os.dup(stderr_fileno)

    # Перенаправляем stderr в os.devnull
    sys.stderr.flush()
    os.dup2(os.open(os.devnull, os.O_WRONLY), stderr_fileno)
    try:
        # Настраиваем API ключ
        genai.configure(api_key="AIzaSyCZWUo7rG6rQdm7R3w88_7NSbbzjpidLe4")

        # Инициализируем модель
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Получаем ответ от модели
        response = model.generate_content(data)
    finally:
        # Восстанавливаем stderr
        sys.stderr.flush()
        os.dup2(old_stderr, stderr_fileno)
        os.close(old_stderr)

    clean_response = re.sub(r'\n|\*|\*\*', '', response.text).strip()
    # Выводим ответ без предупреждений
    return clean_response   


def audio_to_text(audio_path):
    # Загружаем аудиофайл и конвертируем в формат WAV
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1)  # Устанавливаем один канал (моно)
    audio.export("media/temp/temp.wav", format="wav")

    # Используем Recognizer из SpeechRecognition
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile("media/temp/temp.wav")

    with audio_file as source:
        audio_data = recognizer.record(source)
    
    # Попробуем распознать текст из аудиофайла
    try:
        # Используем Google Web Speech API для распознавания
        text = recognizer.recognize_google(audio_data, language="en-EN")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return ""



def text_to_audio(text, output_path='media/audio/output_audio.mp3'):
    tts = gTTS(text, lang='en')
    tts.save(output_path)
    return output_path 

