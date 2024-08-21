from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from products.filters import ProductCategoryFilter, ProductFilter
from .models import CoverPageCarousel, LatestArival, Product, ProductCategory, Variation
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import (
    CoverPageCarouselSerializer, 
    CreateVariationsSerializer, 
    LatestArivalSerializer, 
    ProductCategorySerializer,
    ProductDeleteSerializer,
    ProductDetailSerializer, 
    ProductSerializer, 
    SupercategoryCreateSerializer, 
    SupercategorySerializer, 
    VariationSerializer 
)
from rest_framework.permissions import IsAuthenticated


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    filterset_class = ProductFilter

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        else:
            products = Product.objects.all()
            filtered_products = self.filter_queryset(products)
            serializer = ProductSerializer(filtered_products, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response({
            'message': 'Product created successfully',
            'product': serializer.data
        }, status=status.HTTP_201_CREATED)

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


class CreateVariationsView(APIView):
    def post(self, request):
        serializer = CreateVariationsSerializer(data=request.data)
        if serializer.is_valid():
            variations = serializer.save()
            return Response({'message': 'Variations created successfully', 'variations': VariationSerializer(variations, many=True).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VariationCreateView(generics.CreateAPIView):
    queryset = Variation.objects.all()
    serializer_class = VariationSerializer


class VariationListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VariationSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Variation.objects.filter(product_variant_id=product_id)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        variations_data = request.data.get('variations', [])

        if not product_id or not variations_data:
            return Response(
                {"detail": "Product ID and variations data are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        variations = []
        for variation_data in variations_data:
            variation_data['product_variant'] = product.id 
            serializer = self.get_serializer(data=variation_data)
            serializer.is_valid(raise_exception=True)
            created_variation = serializer.save()
            variations.append(created_variation)

        return Response(
            VariationSerializer(variations, many=True).data,
            status=status.HTTP_201_CREATED
        )

class VariationListAPIView(generics.ListAPIView):
    serializer_class = VariationSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['product_variant']  

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Variation.objects.filter(product_variant_id=product_id)

class VariationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Variation.objects.all()
    serializer_class = VariationSerializer



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