from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from assets.models import Asset
from assets.serializers import AssetSerializer
from assets.views.common import get_assets_query, get_simple_search_qry

class AssetList(APIView):
    #queryset = Asset.objects.all()
    #serializer_class = AssetSerializer

    def get_queryset(self):
        appslug = self.kwargs.get('appslug', None)
        cslug = self.kwargs.get('cslug', None)
        tagslug = self.request.query_params.get('tag', None)
        author_name = self.request.query_params.get('author', None)
        version = self.request.query_params.get('appversion', None)

        qry, _t = get_assets_query(appslug=appslug, cslug=cslug, tslug=tagslug, verstring=version)
        if author_name is not None:
            author = get_object_or_404(User, username=author_name)
            qry = qry & Q(author=author)
        query = self.request.query_params.get('query', None)
        if query is not None:
            search = get_simple_search_qry(query)
            qry = qry & search
        return Asset.objects.filter(qry)

    # Retrieve a list of assets
    def get(self, request, appslug=None, cslug=None, format=None):
        assets = self.get_queryset()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    # Create new asset
    def post(self, request, format=None):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author = self.request.user, pub_date=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchList(ListAPIView):
    serializer_class = AssetSerializer

    def get_queryset(self):
        query = self.request.query_params['query']
        qry = get_simple_search_qry(query)
        return Asset.objects.filter(qry)

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




