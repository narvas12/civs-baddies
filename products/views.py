from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from products.filters import ProductCategoryFilter, ProductFilter
from .models import CoverPageCarousel, LatestArival, Product, ProductCategory, ProductImage, Variation
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import (
    CoverPageCarouselSerializer, 
    LatestArivalSerializer, 
    ProductCategorySerializer,
    ProductDeleteSerializer,
    ProductDetailSerializer,
    ProductImageSerializer, 
    ProductSerializer, 
    SupercategoryCreateSerializer, 
    SupercategorySerializer, 
    VariationSerializer 
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema



class ProductAPIView(APIView):
    filter_backends = [SearchFilter]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    @swagger_auto_schema(
        responses={200: ProductDetailSerializer(many=True)},
        operation_description="Retrieve all products or a specific product by ID"
    )
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        else:
            products = Product.objects.all()
            filtered_products = self.filter_queryset(products)
            serializer = ProductDetailSerializer(filtered_products, many=True)
            return Response(serializer.data)


    @swagger_auto_schema(
        request_body=ProductSerializer,
        responses={201: ProductSerializer},
        operation_description="Create a new product",
        examples={
            'application/json': {
                "name": "Sample Product",
                "category_id": 1,
                "price": "99.99",
                "quantity": 10,
                "desc": "A detailed description of the sample product.",
                "product_tag": "SP-001",
                "image_files": ["image1.png", "image2.png"],
                "variations": [
                    {"size": "M", "color": "Red", "price": "105.99"},
                    {"size": "L", "color": "Blue", "price": "110.99"}
                ]
            }
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        print(serializer.data)
        return Response({
            'message': 'Product created successfully',
            'product': serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=ProductSerializer,
        responses={200: ProductSerializer},
        operation_description="Update an existing product by ID"
    )
    def put(self, request, pk=None, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Product updated successfully',
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, *args, **kwargs):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            product.delete()
            return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = ProductDeleteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_ids = serializer.validated_data.get('product_ids', [])
            try:
                deleted_count, _ = Product.objects.filter(id__in=product_ids).delete()
                return Response(
                    {"message": f"{deleted_count} products deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT
                )
            except Exception as e:
                return Response(
                    {"error": "Failed to delete products.", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    def filter_queryset(self, queryset):
        # Apply filtering logic here based on request parameters
        return queryset


# class ProductCreateAPIView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         product = serializer.save()  

       
#         product_data = self.get_serializer(product).data

#         return Response({
#             'message': 'Product created successfully',
#             'product': product_data
#         }, status=status.HTTP_201_CREATED)


    

# class ProductUpdateAPIView(generics.UpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_200_OK)
    

    

# class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated]

#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


# class ProductDetailView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get(self, request, *args, **kwargs):
#         try:
#             product = self.get_object()
#             serializer = self.get_serializer(product)
#             return Response(serializer.data)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


# class ProductListAPIView(generics.ListAPIView):
    
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = [SearchFilter]
#     filterset_class = ProductFilter



# class ProductDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = ProductDeleteSerializer(data=request.data)
#         if serializer.is_valid():
#             product_ids = serializer.validated_data.get('product_ids', [])
#             try:
#                 products_deleted = Product.objects.filter(id__in=product_ids).delete()
#                 deleted_count = products_deleted[0] if isinstance(products_deleted, tuple) else 0
#                 return Response(
#                     {"message": f"{deleted_count} products deleted successfully."},
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             except Exception as e:
#                 return Response(
#                     {"error": "Failed to delete products.", "details": str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuperCategoryCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = SupercategoryCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CategoryCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

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



class ProductImageListView(generics.ListAPIView):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            return ProductImage.objects.filter(product=product)
        else:
            return ProductImage.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class VariationAPIView(APIView):
    
    @swagger_auto_schema(
        responses={200: VariationSerializer(many=True)},
        operation_description="Retrieve all variations or a specific variation by ID"
    )
    def get(self, request, pk=None):
        if pk:
            variation = get_object_or_404(Variation, pk=pk)
            serializer = VariationSerializer(variation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            variations = Variation.objects.all()
            serializer = VariationSerializer(variations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=VariationSerializer(many=True),
        responses={201: VariationSerializer(many=True)},
        operation_description="Create one or multiple variations"
    )
    def post(self, request):
        if isinstance(request.data, list):
            serializer = VariationSerializer(data=request.data, many=True)
        else:
            serializer = VariationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Handling when data is a list of variations
            if isinstance(serializer.validated_data, list):
                for variation_data in serializer.validated_data:
                    product = variation_data.get('product_variant')
                    image = variation_data.get('image')
                    
                    if image.product != product:
                        return Response({"error": "Selected image does not belong to the chosen product."}, 
                                        status=status.HTTP_400_BAD_REQUEST)
            else:  # Handling when data is a single variation
                product = serializer.validated_data.get('product_variant')
                image = serializer.validated_data.get('image')
                
                if image.product != product:
                    return Response({"error": "Selected image does not belong to the chosen product."}, 
                                    status=status.HTTP_400_BAD_REQUEST)
            
            # Save the variations
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        request_body=VariationSerializer,
        responses={200: VariationSerializer},
        operation_description="Update an existing variation by ID"
    )
    def put(self, request, pk):
        variation = get_object_or_404(Variation, pk=pk)
        serializer = VariationSerializer(variation, data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_variant']
            image = serializer.validated_data['image']
            
            if image.product != product:
                return Response({"error": "Selected image does not belong to the chosen product."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={204: 'No Content'},
        operation_description="Delete an existing variation by ID"
    )
    def delete(self, request, pk):
        variation = get_object_or_404(Variation, pk=pk)
        variation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class CoverPageCarouselAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        coverpages = CoverPageCarousel.objects.all()
        serializer = CoverPageCarouselSerializer(coverpages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        images = request.FILES.getlist('images')
        image_urls = []
        for image in images:
            coverpage = CoverPageCarousel(images=image)
            coverpage.save()
            image_urls.append(coverpage.images.url)
        return Response({'image_urls': image_urls}, status=status.HTTP_201_CREATED)

class CoverPageCarouselListView(generics.ListAPIView):
    queryset = CoverPageCarousel.objects.all()
    serializer_class = CoverPageCarouselSerializer


class LatestArrivalListView(generics.ListAPIView):
    queryset = LatestArival.objects.all()
    serializer_class = LatestArivalSerializer

class LatestArivalAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        latest_arivals = LatestArival.objects.all()
        serializer = LatestArivalSerializer(latest_arivals, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = LatestArivalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        latest_arival = get_object_or_404(LatestArival, pk=pk)
        serializer = LatestArivalSerializer(latest_arival, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)