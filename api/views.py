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
import logging
from django.db.models import Q
from rest_framework.response import Response
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
 

class UserLocation(generics.UpdateAPIView): 
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserProfileLocationSerializer
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

class UserFirebaseToken(generics.UpdateAPIView): 
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserProfileFirebaseSerializer
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
        
        logger.info('Something went wrong!')
        point = Point(long_point,lat_point)
        queryset = User.objects.filter(usertype ='HF',public=False ,location__distance_lte=(point,Distance(km=radius)))
        return queryset
    
   

class HelpSearchUser(generics.ListAPIView):
  
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        obj = get_object_or_404(User.objects.all(), **filters)  # Lookup the object

        radius =  int(self.request.query_params['radius'])
        
        if radius > 100:
            raise serializers.ValidationError("To high radius")       
        data = User.objects.filter(usertype ='HFS',public=False ,location__distance_lte=(obj.location,Distance(km=radius)))
        if(validsessionid(obj)):
            self.check_object_permissions(self.request, obj)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class AddArticle(generics.ListCreateAPIView):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializerADDList  
        

class SearchHFS(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = Shop.objects.all()
    serializer_class = GETSearchShopListSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        obj = get_object_or_404(User.objects.all(), **filters)  # Lookup the object

        radius =  int(self.request.query_params['radius'])
        
        if radius > 100:
            raise serializers.ValidationError("To high radius")    
        data = Shop.objects.filter( helper__isnull=True , helpsearcher__location__distance_lte=(obj.location,Distance(km=radius)) )
        if(validsessionid(obj)):
            self.check_object_permissions(self.request, obj)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class SearchUser(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        obj = get_object_or_404(User.objects.all(), **filters)  # Lookup the object

        radius =  int(self.request.query_params['radius'])
        
        if radius > 100:
            raise serializers.ValidationError("To high radius")    
        if(obj.usertype=='HF'):
            data = User.objects.filter(usertype ='HFS',public=False ,location__distance_lte=(obj.location,Distance(km=radius)))
        else:
            data = User.objects.filter(usertype ='HF',public=False ,location__distance_lte=(obj.location,Distance(km=radius)))
        if(validsessionid(obj)):
            self.check_object_permissions(self.request, obj)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class ShopDelete(generics.DestroyAPIView):
    lookup_fields = ['session_id','id']
    queryset = Shop.objects.all()
    serializer_class = GETAllShopListSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}
        
        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helpsearcher'] = obj
                filter['helper__isnull']=True
                
        data = get_object_or_404(Shop.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")    

class BuyListDelete(generics.DestroyAPIView):
    lookup_fields = ['session_id','id']
    queryset = BuyList.objects.all()
    serializer_class = BuyListSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helpsearcher'] = obj



                 
        data = get_object_or_404(BuyList.objects.all(), **filter)


        if(Shop.objects.filter(buylist = data , finished_date__isnull = True).exists()):
            raise serializers.ValidationError("Die EinkaufListe wird in einem Offenen Einkauf verwendet") 

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")    

class BuyListGet(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = BuyList.objects.all()
    serializer_class = GETBuyListSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        user = get_object_or_404(User.objects.all(), **filters)  # Lookup the object
        
       
           
        
        obj = BuyList.objects.filter(helpsearcher = user)
        if(validsessionid(user)):
            self.check_object_permissions(self.request, obj)
            return obj.order_by('-creation_date')
        raise serializers.ValidationError("Invalid Sessionid")

class ShopGet(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = Shop.objects.all()
    serializer_class = GETAllShopListSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        user = get_object_or_404(User.objects.all(), **filters)  # Lookup the object
        
       
           
        
        obj = Shop.objects.filter( Q(helpsearcher = user) | Q(helper = user))
        if(validsessionid(user)):
            self.check_object_permissions(self.request, obj)
            return obj.order_by('-creation_date')
        raise serializers.ValidationError("Invalid Sessionid")

class ShopGetOne(generics.RetrieveAPIView):
    lookup_fields = ['session_id','pk']
    queryset = Shop.objects.all()
    serializer_class = GETAllShopListSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        if self.kwargs['session_id']: # Ignore empty fields.
                filters['session_id'] = self.kwargs['session_id']
                user = get_object_or_404(User.objects.all(), **filters) 
        filters = {}
        
        if self.kwargs['pk']: # Ignore empty fields.
                obj = Shop.objects.filter(Q(helpsearcher = user) | Q(helper = user), id = self.kwargs['pk'])
        
        if(validsessionid(user)):
            self.check_object_permissions(self.request, obj)
            return obj 
        raise serializers.ValidationError("Invalid Sessionid")

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

class AngebotGetHFS(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = Angebot.objects.all()
    serializer_class = GetAngebotSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        user = get_object_or_404(User.objects.all(), **filters)  # Lookup the object
        
       
           
        
        obj = Angebot.objects.filter( viewed = False,  shop__helpsearcher = user )
        if(validsessionid(user)):
            self.check_object_permissions(self.request, obj)
            return obj.order_by('-creation_date')
        raise serializers.ValidationError("Invalid Sessionid")
class AngebotGetHF(generics.ListAPIView):
    lookup_fields = ['session_id']
    queryset = Angebot.objects.all()
    serializer_class = GetHFAngebotSerializer
    def filter_queryset(self,queryset):
        # Apply any filter backends
        filters = {}
        for field in self.lookup_fields:
            if self.kwargs[field]: # Ignore empty fields.
                filters[field] = self.kwargs[field]
        user = get_object_or_404(User.objects.all(), **filters)  # Lookup the object
        obj = Angebot.objects.filter(   helper = user )
        if(validsessionid(user)):
            self.check_object_permissions(self.request, obj)
            return obj.order_by('-creation_date')
        raise serializers.ValidationError("Invalid Sessionid")
class AngebotAdd(generics.CreateAPIView):
    
    queryset = Angebot.objects.all()
    serializer_class = CreateAngebotSerializer

class AngebotReview(generics.UpdateAPIView):   
    lookup_fields = ['session_id','id']
    queryset = Angebot.objects.all()
    serializer_class = SetAngebotSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['shop__helpsearcher'] = obj
                filter['viewed']=False
        data = get_object_or_404(Angebot.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")


class ShopDoneHF(generics.UpdateAPIView):   
    lookup_fields = ['session_id','id']
    queryset = Shop.objects.all()
    serializer_class = ShopUpdateDoneSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helper'] = obj
                filter['done']=False
        data = get_object_or_404(Shop.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class ShopDone(generics.UpdateAPIView):   
    lookup_fields = ['session_id','id']
    queryset = Shop.objects.all()
    serializer_class = ShopUpdateDoneSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helpsearcher'] = obj
                filter['done']=False
        data = get_object_or_404(Shop.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class ShopPayedHF(generics.UpdateAPIView):   
    lookup_fields = ['session_id','id']
    queryset = Shop.objects.all()
    serializer_class = ShopUpdatePayedHFSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helper'] = obj
                filter['payed']=False
        data = get_object_or_404(Shop.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")

class ShopPayedHFS(generics.UpdateAPIView):   
    lookup_fields = ['session_id','id']
    queryset = Shop.objects.all()
    serializer_class = ShopUpdatePayedHFSSerializer
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}

        if self.kwargs['session_id']: # Ignore empty fields.
                filter['session_id'] = self.kwargs['session_id']
        obj = get_object_or_404(User.objects.all(), **filter)  # Lookup the object
        filter = {}

        if self.kwargs['id']: # Ignore empty fields.
                filter['id'] = self.kwargs['id']
                filter['helpsearcher'] = obj
                
        data = get_object_or_404(Shop.objects.all(), **filter)

        if(validsessionid(obj)):
            self.check_object_permissions(self.request, data)
            return data
        raise serializers.ValidationError("Invalid Sessionid")
