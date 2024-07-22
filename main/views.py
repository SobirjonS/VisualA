from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from . import functions


@api_view(['POST'])
def audio_question(request):
    request_audio = request.FILES.get('audio')
    if not request_audio:
        return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    audio_path = f'temp/audio.{request_audio.name.split(".")[-1]}'
    with open(audio_path, 'wb') as f:
        for chunk in request_audio.chunks():
            f.write(chunk)

    recognized_text = functions.audio_to_text(audio_path)
    if not recognized_text:
        return Response({"error": "Could not recognize any text from the audio."}, status=status.HTTP_400_BAD_REQUEST)
    
    text_answer = functions.generate_answer(recognized_text)
    audio_answer = functions.text_to_audio(text_answer)
    
    return Response({"recognized_text": recognized_text, "text_answer": text_answer, "audio_answer": audio_answer}, status=status.HTTP_200_OK)


@api_view(['POST'])
def text_question(request):
    data = request.data.get('text')
    if not data:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    text_answer = functions.generate_answer(data)
    audio_answer = functions.text_to_audio(text_answer)
    
    return Response({"text_answer": text_answer, "audio_answer": audio_answer}, status=status.HTTP_200_OK)