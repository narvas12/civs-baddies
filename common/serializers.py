from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .models import NewsFlash, Rating

class RatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Rating
        fields = ['id', 'rating_type', 'description']
        #exclude = ['rating_type']
        #depth = 1
        
    def validate(self, attrs):
        if not attrs.get("rating_type"):
            raise serializers.ValidationError("Rating type is required!!")
        if not attrs.get("description"):
            raise serializers.ValidationError("Room name is required!!")

        return attrs

    def create(self, validated_data):
        rating= Rating.objects.create_rating(
                rating_type = validated_data.get('rating_type'),
                description = validated_data.get('description'),
            )
        
        return rating
    
    
class RatingSerializer(serializers.ModelSerializer):
    rating_type = serializers.IntegerField()
    rating_description = serializers.CharField(max_length=12, min_length=4)
    
    class Meta:
        model=Rating
        fields = ['id', 'rating_type', 'rating_description', 'description', "date_created"]
        depth = 2
   
 

class DashboardDataSerializer(serializers.Serializer):
    average_ratings = serializers.FloatField()
    total_completed_orders = serializers.IntegerField()
    total_pending_orders = serializers.IntegerField()
    total_available_products = serializers.IntegerField()


class NewsFlashSerializer(serializers.ModelSerializer):

    class Meta:
        model=NewsFlash
        fields = "__all__"