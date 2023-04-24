from django.urls import path

from paraphraser import views

urlpatterns = [
    path("paraphrase/", views.Paraphraser.as_view()),
]
