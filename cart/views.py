import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from cart.models import CartItem, WishList
from products.models import Color, Product, Size, Variation
from users.models import CustomUser
from .serializers import CartItemSerializer, WishlistItemSerializer
from .utils import add_to_session_cart
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import  AllowAny, IsAuthenticatedOrReadOnly





class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data

        if not isinstance(items, list) or not items:
            return Response({'error': 'A non-empty items array is required'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = []

        for item in items:
            product, variation_or_error = self.get_product_and_variation(item)


            if not product:
                return variation_or_error

            color = item.get('color')
            size = item.get('size')

            if not color:
                return Response({'error': 'Color is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not size:
                return Response({'error': 'Size is required'}, status=status.HTTP_400_BAD_REQUEST)

            quantity = item.get('quantity')
            if not quantity or int(quantity) <= 0:
                return Response({'error': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)


            existing_cart_items = CartItem.objects.filter(
                user=user,
                product=product,
                variation=variation_or_error,  
                color=color,
                size=size
            )

            if existing_cart_items.exists():

                cart_item = existing_cart_items.first()
                cart_item.quantity += int(quantity)
                cart_item.save()
            else:

                cart_item = CartItem(
                    user=user,
                    product=product,
                    variation=variation_or_error,  
                    quantity=quantity,
                    color=color,
                    size=size
                )
                cart_item.save()

            cart_items.append(cart_item)


        serializer = CartItemSerializer(cart_items, many=True)

        return Response({
            'message': 'Items successfully added to cart.',
            'cart_items': serializer.data
        }, status=status.HTTP_201_CREATED)


    def get_product_and_variation(self, item):
        """Helper method to get product and variation from the item."""
        product_id = item.get('product_id')
        variation_id = item.get('variation_id')

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return None, Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        variation = None
        if variation_id:
            try:
                variation = Variation.objects.get(pk=variation_id, product=product)
            except Variation.DoesNotExist:
                return None, Response({'error': 'Variation not found'}, status=status.HTTP_404_NOT_FOUND)

        return product, variation








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
    

class WishlistAPIView(APIView):
    def get(self, request, slug=None):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key


        if slug:
            wishlist_item = get_object_or_404(WishList, slug=slug, session_key=session_key)
            serializer = WishlistItemSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            wishlist_items = WishList.objects.filter(session_key=session_key)
            serializer = WishlistItemSerializer(wishlist_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        data = request.data
        data['session_key'] = session_key
        serializer = WishlistItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, slug):
        wishlist_item = get_object_or_404(WishList, slug=slug)
        serializer = WishlistItemSerializer(wishlist_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):

        wishlist_item = get_object_or_404(WishList, slug=slug)
        wishlist_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class AddWishlistToCartView(APIView):
    def post(self, request):
        user = request.user

        try:
            wishlist_items = WishList.objects.filter(user=user)
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
            wishlist_items = WishList.objects.filter(user__customer_id=customer_id)
            serializer = WishlistItemSerializer(wishlist_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PublicWishlistView(APIView):
    def get(self, request, unique_identifier):
        wishlist = get_object_or_404(WishList, unique_identifier=unique_identifier)
        serializer = WishlistItemSerializer(wishlist)
        return Response(serializer.data)