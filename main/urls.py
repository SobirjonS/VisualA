from django.urls import path
from . import views

urlpatterns = [
    path('audio-question/', views.audio_question, name='audio-question'),
    path('text-question/', views.text_question, name='text-question'),
]