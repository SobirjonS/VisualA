from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import functions
from . import serializers

from pydub import AudioSegment
from io import BytesIO

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
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
    
    recognized_text = functions.audio_to_text(audio_instance.audio)
    if not recognized_text:
        return Response({"error": "Could not recognize any text from the audio."}, status=status.HTTP_400_BAD_REQUEST)
    
    answer = functions.generate_answer(recognized_text)
    uz_answer = functions.translate_ru_to_uz(answer)
    functions.text_to_speech(text=uz_answer, user=user)
    try:
        latest_audio = models.ResponseAudio.objects.filter(user=user).latest('created_at')
    except ObjectDoesNotExist:
        return Response({"error": "No audio response found for the user."}, status=status.HTTP_404_NOT_FOUND)
    serializer = serializers.ResponseAudioSerializer(latest_audio)
    
    return Response({"recognized_text": recognized_text, "uz_answer": uz_answer, "audio_answer": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def text_question(request):
    data = request.data.get('text')
    user = request.user
    if not data:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    text_answer = functions.generate_answer(data)
    uz_answer = functions.translate_ru_to_uz(text_answer)
    functions.text_to_speech(text=uz_answer, user=user)
    try:
        latest_audio = models.ResponseAudio.objects.filter(user=user).latest('created_at')
    except ObjectDoesNotExist:
        return Response({"error": "No audio response found for the user."}, status=status.HTTP_404_NOT_FOUND)
    serializer = serializers.ResponseAudioSerializer(latest_audio)
    
    return Response({"uz_answer": uz_answer, "audio_answer": serializer.data}, status=status.HTTP_200_OK)
