from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import NewsFlash
from .serializers import NewsFlashSerializer

class NewsFlashAPIView(APIView):
    # Get all NewsFlashes or create a new one
    def get(self, request):
        newsflashes = NewsFlash.objects.all()
        serializer = NewsFlashSerializer(newsflashes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NewsFlashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get, update, or delete a specific NewsFlash by its ID
    def put(self, request, pk=None):
        newsflash = get_object_or_404(NewsFlash, pk=pk)
        serializer = NewsFlashSerializer(newsflash, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        newsflash = get_object_or_404(NewsFlash, pk=pk)
        newsflash.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
