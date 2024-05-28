from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from common.managers import CommonManager
from .pagination import CustomPagination
from .serializers import DashboardDataSerializer, RatingCreateSerializer, RatingSerializer
from .renderers import ApiCustomRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import Rating


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