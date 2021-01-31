from django.shortcuts import render
from rest_framework import generics
from pages.models import *
from .serializers import *
from url_filter.integrations.drf import DjangoFilterBackend
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from django.http import HttpResponseNotFound
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


class UserAdd(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer
class UserGet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
class UserUpdate(generics.UpdateAPIView): 
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, obj)
            return obj
        raise serializers.ValidationError("Invalid Sessionid")
 
class UserProfile(generics.RetrieveAPIView):   
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, obj)
            return obj
        raise serializers.ValidationError("Invalid Sessionid")


class HelplUser(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def filter_queryset(self, queryset):
        lat_point = float(self.request.query_params['lat'])
        long_point = float(self.request.query_params['long'])
        radius =  int(self.request.query_params['radius'])
        if radius > 100:
            raise serializers.ValidationError("To high radius")

        point = Point(long_point,lat_point)
        queryset = User.objects.filter(usertype ='HF',public=False ,location__distance_lte=(point,Distance(km=radius)))
        return queryset
    
         

class HelpSearchlUser(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def filter_queryset(self, queryset):
        lat_point = float(self.request.query_params['lat'])
        long_point = float(self.request.query_params['long'])
        radius =  int(self.request.query_params['radius'])
        if radius > 100:
            raise serializers.ValidationError("To high radius")

        point = Point(long_point,lat_point)
        queryset = User.objects.filter(usertype ='HFS',public=False ,location__distance_lte=(point,Distance(km=radius)))
        return queryset
class BuyListAdd(generics.CreateAPIView):
    queryset = BuyList.objects.all()
    serializer_class = BuyListSerializer
 
class ShopAdd(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopListSerializer    
    
class AllItems(generics.ListAPIView):
    #permission_classes = (OnlyAPIPermission,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
