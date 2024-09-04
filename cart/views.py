import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from cart.models import CartItem, WishlistItem
from products.models import Color, Product, Size, Variation
from users.models import CustomUser
from .serializers import CartItemSerializer, WishlistItemSerializer
from .utils import add_to_session_cart
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import  AllowAny





class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data
        
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not isinstance(items, list) or not items:
            return Response({'error': 'A non-empty items array is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        added_items = []

        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            color_id = item.get('color_id')
            size_id = item.get('size_id')

            if not all([product_id, quantity]):
                return Response({'error': 'Each item must have a product ID and quantity'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response({'error': f'Product with ID {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            variation_query = {'product_variant': product}
            if color_id:
                variation_query['colors'] = color_id
            if size_id:
                variation_query['size'] = size_id  # Ensure this field exists in the model

            try:
                variation = Variation.objects.get(**variation_query)
            except Variation.DoesNotExist:
                return Response({'error': 'No matching variation found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Proceed with adding the item to the cart
            cart_item = CartItem.objects.create(user=user, product=product, variation=variation, quantity=quantity)
            added_items.append(cart_item)

        return Response({'added_items': added_items}, status=status.HTTP_201_CREATED)




class RemoveFromCartView(APIView):
    def delete(self, request, pk, format=None):
        try:
            cart_item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        cart_item.active = False
        cart_item.delete()
        return Response({'success': 'removed from cart'}, status=status.HTTP_204_NO_CONTENT)


class CartItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user, active=True)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        add_to_cart_view = AddToCartView.as_view()
        return add_to_cart_view(request)



class UpdateCartItemQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        user = request.user

        try:
            cart_item = CartItem.objects.get(user=user, pk=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if not new_quantity or new_quantity <= 0:
            return Response({'error': 'Invalid quantity provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.clean_fields()  # Validate the field values
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)



class DeleteCartItems(APIView):
    
    def delete(self, request):

        cart_items = CartItem.objects.all()
        
        cart_items.delete()
        
        return Response({'message': 'All cart items deleted successfully'}, status=204)
    

class AddToWishlistView(APIView):
    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wishlist_item = WishlistItem.objects.create(user=user, product_id=product_id)
            serializer = WishlistItemSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AddWishlistToCartView(APIView):
    def post(self, request):
        user = request.user

        try:
            wishlist_items = WishlistItem.objects.filter(user=user)
            for wishlist_item in wishlist_items:
                product = wishlist_item.product

                existing_cart_item = CartItem.objects.filter(user=user, product=product).first()

                if existing_cart_item:
                    existing_cart_item.quantity += 1
                    existing_cart_item.save()
                else:
                    default_variation = product.variation_set.first()
                    if default_variation:
                        size_id = default_variation.size_id
                        color_id = default_variation.color_id
                    else:
                        size_id = None
                        color_id = None

                    CartItem.objects.create(
                        user=user,
                        product=product,
                        quantity=1,  
                        size_id=size_id,  
                        color_id=color_id,  
                        active=True
                    )
                wishlist_item.delete()

            return Response({'message': 'Wishlist items added to cart successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class WishlistView(APIView):
    def get(self, request, customer_id, format=None):
        try:
            wishlist_items = WishlistItem.objects.filter(user__customer_id=customer_id)
            serializer = WishlistItemSerializer(wishlist_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PublicWishlistView(APIView):
    def get(self, request, unique_identifier):
        wishlist = get_object_or_404(WishlistItem, unique_identifier=unique_identifier)
        serializer = WishlistItemSerializer(wishlist)
        return Response(serializer.data)