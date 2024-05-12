from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.apps import apps
from django.db.models import Q


from .enums import RatingTag
from .utils import format_rating_records
from django.db import models
from django.db.models import Avg, Count, Q

class RatingManager(models.Manager):
    def create_rating(self, rating_type, description):
        Rating = apps.get_model('common.Rating')
        
        rating_type = int(rating_type)
        
        try:
            RatingTag(rating_type)  # Attempt to create an enum member from the value
            
            rating_Id = RatingTag[RatingTag(rating_type).name].value
            rating = Rating(rating_type=rating_Id, description=description)
            rating.save(using=self._db)
        
            return rating
          
        except ValueError:
            raise ValidationError(_("Rating type value is invalid"))
        
       

    def get_ratings(self, rating_type):
        Rating = apps.get_model('common.Rating')
        
        # If no rating type was passed to request, proceed to fetch all ratings regardless of type.
        if rating_type is None:
            records = Rating.objects.all()
            if len(records) < 1:
                raise ValidationError("No records were found")
            
            formatted_records = format_rating_records(records)
            return formatted_records
        
        rating_type = int(rating_type)
        if rating_type not in RatingTag:
            raise ValidationError(_("Rating type value is invalid"))
        
        try:
            if rating_type == RatingTag.WORSE.value:
                rating_type = RatingTag.WORSE.value
            
            elif rating_type == RatingTag.BAD.value:
                rating_type = RatingTag.BAD.value
                
            elif rating_type == RatingTag.GOOD.value:
                rating_type = RatingTag.GOOD.value
                
            elif rating_type == RatingTag.GREAT.value:
                rating_type = RatingTag.GREAT.value
                
            elif rating_type == RatingTag.EXCELLENT.value:
                rating_type = RatingTag.EXCELLENT.value
            
            rating_Id = RatingTag[RatingTag(rating_type).name].value
            records = Rating.objects.filter(**{'rating_type': rating_Id})
            if not records:
                raise ValidationError("No records were found")
            
            #formatted_records = format_rating_records(records)
            formatted_records = format_rating_records(records)
            return formatted_records
        
    
        except Exception as e:
            raise ValidationError(e.detail)
        



class CommonManager(models.Manager):
   
    def get_statistics(self):
        # Get the models
        Rating = apps.get_model('common', 'Rating')
        Order = apps.get_model('orders', 'Order')
        Product = apps.get_model('products', 'Product')

        # Get average ratings
        avg_ratings = Rating.objects.all().aggregate(Avg('rating_type'))['rating_type__avg']

        # Get total completed orders
        total_completed_orders = Order.objects.filter(status=Order.COMPLETED).count()

        # Get total pending orders
        total_pending_orders = Order.objects.filter(status=Order.PENDING).count()

        # Get total available products
        total_available_products = Product.objects.filter(is_suspended=False).count()

        return {
            'average_ratings': avg_ratings,
            'total_completed_orders': total_completed_orders,
            'total_pending_orders': total_pending_orders,
            'total_available_products': total_available_products,
        }