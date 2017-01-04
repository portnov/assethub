from django.contrib.auth.models import User

from rest_framework import serializers, viewsets

from assets.models import Asset

class TagsField(serializers.Field):
    def to_representation(self, obj):
        return ", ".join([tag.slug for tag in obj.all()])
    
    def to_internal_value(self, data):
        raise NotImplemented

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        #exclude = ("num_votes", "pub_date")
        
    tags = TagsField(read_only=True)
    num_votes = serializers.IntegerField(read_only=True)
    pub_date = serializers.DateTimeField(read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

