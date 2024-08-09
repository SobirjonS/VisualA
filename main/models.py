from django.db import models
from django.contrib.auth.models import User


class RequestAudio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='request_audio/')
    created_at = models.DateField(auto_now_add=True)


class ResponseAudio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='response_audio/')
    created_at = models.DateField(auto_now_add=True)