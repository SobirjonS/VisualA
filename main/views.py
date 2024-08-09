from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pydub import AudioSegment
from io import BytesIO
from django.core.files import File
from . import models
from . import functions

@api_view(['POST'])
def audio_question(request):
    audio = request.FILES.get('audio')
    user = request.user
    if not audio:
        return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        audio_segment = AudioSegment.from_file(audio, format="aac")
        wav_io = BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        wav_file = File(wav_io, name=f"{audio.name.split('.')[0]}.wav")
        audio_instance = models.RequestAudio(user=user, audio=wav_file)
        audio_instance.save()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

    recognized_text = functions.audio_to_text(audio_instance)
    if not recognized_text:
        return Response({"error": "Could not recognize any text from the audio."}, status=status.HTTP_400_BAD_REQUEST)
    
    answer = functions.generate_answer(recognized_text)
    uz_answer = functions.translate_ru_to_uz(answer)
    functions.text_to_speech(text=uz_answer, user=user)
    audio_answer = models.ResponseAudio.objects.latest('created_at')
    
    return Response({"recognized_text": recognized_text, "uz_answer": uz_answer, "audio_answer": audio_answer}, status=status.HTTP_200_OK)

@api_view(['POST'])
def text_question(request):
    data = request.data.get('text')
    if not data:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    text_answer = functions.generate_answer(data)
    uz_answer = functions.translate_ru_to_uz(text_answer)
    audio_answer = functions.text_to_speech(uz_answer)
    
    return Response({"uz_answer": uz_answer, "audio_answer": "media/audio/output_audio.m4a"}, status=status.HTTP_200_OK)
