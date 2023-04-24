from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from paraphraser.paraphrase import get_paraphrases

class Paraphraser(APIView):
    def get(self, request):
        tree = request.GET.get("tree")
        limit = request.GET.get("limit") or 20
        return Response({'paraphrases': [{'tree': t} for t in get_paraphrases(tree, int(limit))]})