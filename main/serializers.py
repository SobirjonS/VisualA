from rest_framework import serializers
from . import models

class ResponseAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResponseAudio
        fields = ['audio', 'created_at'] 