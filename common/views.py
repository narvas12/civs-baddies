from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from common.managers import CommonManager
from .pagination import CustomPagination
from .serializers import DashboardDataSerializer, RatingCreateSerializer, RatingSerializer, NewsFlashSerializer
from .renderers import ApiCustomRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import Rating, NewsFlash
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny


class RatingCreateView(GenericAPIView):
    serializer_class = RatingCreateSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        rating = request.data
        serializer=self.serializer_class(data=rating)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            room_data=serializer.data
            return Response({
                'payload':None,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RatingsView(GenericAPIView):
    serializer_class = RatingSerializer
    renderer_classes = (ApiCustomRenderer,)
    pagination_class = CustomPagination

    def get(self, request):
        rating_type = self.request.query_params.get('rating_type', None)
        records = Rating.objects.get_ratings(rating_type)
        
        page = self.paginate_queryset(records)  
        serializer = self.serializer_class(page, many=True)
        if serializer.is_valid:
                return self.get_paginated_response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardData(APIView):
    def get(self, request, format=None):
        manager = CommonManager()

        statistics = manager.get_statistics()

        serializer = DashboardDataSerializer(statistics)

        return Response(serializer.data)



class NewsFlashAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, newsflash_id=None):
        if newsflash_id:

            newsflash = get_object_or_404(NewsFlash, pk=newsflash_id)
            serializer = NewsFlashSerializer(newsflash)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            newsflashes = NewsFlash.objects.all()
            serializer = NewsFlashSerializer(newsflashes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = NewsFlashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, newsflash_id):

        newsflash = get_object_or_404(NewsFlash, pk=newsflash_id)
        serializer = NewsFlashSerializer(newsflash, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, newsflash_id):

        newsflash = get_object_or_404(NewsFlash, pk=newsflash_id)
        newsflash.delete()
        return Response({'message': 'NewsFlash deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)