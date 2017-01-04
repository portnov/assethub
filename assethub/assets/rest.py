from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#from rest_framework import generics

from assets.models import Asset
from assets.serializers import AssetSerializer

class AssetList(APIView):
    queryset = Asset.objects.all()
    #serializer_class = AssetSerializer

    # Retrieve a list of assets
    def get(self, request, format=None):
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    # Create new asset
    def post(self, request, format=None):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author = self.request.user, pub_date=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssetDetail(APIView):
    queryset = Asset.objects.all()
    #serializer_class = AssetSerializer

    def get_object(self, pk):
        return get_object_or_404(Asset, pk=pk)

    # Get details for one asset
    def get(self, request, pk, format=None):
        asset = self.get_object(pk)
        serializer = AssetSerializer(asset)
        return Response(serializer.data)

    # Update one asset
    def put(self, request, pk, format=None):
        asset = self.get_object(pk)
        serializer = AssetSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




