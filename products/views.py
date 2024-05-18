from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from products.filters import ProductCategoryFilter, ProductFilter
from .models import Product, ProductCategory, Variation
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.views import APIView
from .serializers import ProductCategorySerializer, ProductSerializer, ProductDeleteSerializer, VariationSerializer 
from users.permissions import IsStaffUser




class ProductCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsStaffUser]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Product created successfully'}, status=status.HTTP_201_CREATED)
    

# class ProductCreateAPIView(generics.CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def create(self, request, *args, **kwargs):
#         # Check if data is a single product or multiple products
#         is_multiple = isinstance(request.data, list)
#         if is_multiple:
#             serializer = self.get_serializer(data=request.data, many=True)
#         else:
#             serializer = self.get_serializer(data=request.data)

#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         if is_multiple:
#             return Response({'message': 'Products created successfully'}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({'message': 'Product created successfully'}, status=status.HTTP_201_CREATED)

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)




class ProductUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsStaffUser]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()


        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # Check if the request contains a list of products
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductListAPIView(generics.ListAPIView):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    filterset_class = ProductFilter


class ProductDeleteAPIView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = ProductDeleteSerializer(data=request.data)
        if serializer.is_valid():
            product_ids = serializer.validated_data.get('product_ids', [])
            try:
                products_deleted = Product.objects.filter(id__in=product_ids).delete()
                deleted_count = products_deleted[0] if isinstance(products_deleted, tuple) else 0
                return Response(
                    {"message": f"{deleted_count} products deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT
                )
            except Exception as e:
                return Response(
                    {"error": "Failed to delete products.", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsStaffUser]

    serializer_class = ProductCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductCategoryListAPIView(generics.ListAPIView):
    
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  # Update here
    filterset_class = ProductCategoryFilter
    search_fields = ['name']
    ordering_fields = ['created_at']

    pagination_class = None


class VariationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]


    queryset = Variation.objects.all()
    serializer_class = VariationSerializer

    def create(self, request, *args, **kwargs):
        # Get the product ID from the request data
        product_id = request.data.get('product_id')
        # Get the list of variations from the request data
        variations_data = request.data.get('variations', [])

        if not product_id or not variations_data:
            return Response(
                {"detail": "Product ID and variations data are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the product instance
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create the variations
        created_variations = []
        for variation_data in variations_data:
            variation_data['product_variant'] = product.id  # Add product_variant to each variation data
            serializer = self.get_serializer(data=variation_data)
            serializer.is_valid(raise_exception=True)
            created_variation = serializer.save()
            created_variations.append(created_variation)

        return Response(
            VariationSerializer(created_variations, many=True).data,
            status=status.HTTP_201_CREATED
        )


class VariationListAPIView(generics.ListAPIView):
    queryset = Variation.objects.all()
    serializer_class = VariationSerializer
    filter_backends = [SearchFilter]
    filterset_class = ProductFilter

# class VariationListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Variation.objects.all()
#     serializer_class = VariationSerializer

class VariationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]

    
    queryset = Variation.objects.all()
    serializer_class = VariationSerializer