import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from cart.models import CartItem, WishlistItem
from products.models import Product
from users.models import CustomUser
from .serializers import CartItemSerializer, WishlistItemSerializer


class AddToCartView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not all([user_id, product_id, quantity]):
            return Response({'error': 'User ID, product ID, and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            cart_item.quantity += int(quantity)
            cart_item.active = True 
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(user=user, product=product, quantity=int(quantity), active=True) 
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# class DeleteCartItems(APIView):
    
#     def delete(self, request):

#         cart_items = CartItem.objects.all()
        
#         cart_items.delete()
        
#         return Response({'message': 'All cart items deleted successfully'}, status=204)



class UpdateCartItemQuantityView(APIView):
    def patch(self, request, customer_id, item_id):
        try:
            user = CustomUser.objects.get(customer_id=customer_id)
            cart_item = CartItem.objects.get(user=user, pk=item_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if not new_quantity or new_quantity <= 0:
            return Response({'error': 'Invalid quantity provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.clean_fields()  
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)



class CartItemListView(APIView):
    def get(self, request, customer_id):  
        try:
            user = CustomUser.objects.get(customer_id=customer_id)  
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(user=user, active=True)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request, customer_id):  
        add_to_cart_view = AddToCartView.as_view()
        return add_to_cart_view(request)


class RemoveFromCartView(APIView):
    def delete(self, request, pk, format=None):
        try:
            cart_item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        cart_item.active = False
        cart_item.delete()
        return Response({'success': 'removed from cart'}, status=status.HTTP_204_NO_CONTENT)
    

class AddToWishlistView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        if not all([user_id, product_id]):
            return Response({'error': 'User ID and product ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wishlist_item = WishlistItem.objects.create(user_id=user_id, product_id=product_id)
            serializer = WishlistItemSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class AddWishlistToCartView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wishlist_items = WishlistItem.objects.filter(user_id=user_id)
            for wishlist_item in wishlist_items:
                product = wishlist_item.product

                existing_cart_item = CartItem.objects.filter(user_id=user_id, product=product).first()

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
                        user_id=user_id,
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