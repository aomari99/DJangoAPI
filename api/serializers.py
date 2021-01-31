from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer
from pages.models import *
from django.http import HttpResponseForbidden 
from django.shortcuts import get_object_or_404
salt1 = "abcgfhködup977s" 
salt2 = "üopasdznm,sdu67"
from django.utils import timezone

#show other users
class UserSerializer(GeoModelSerializer):
    usertype_txt = serializers.CharField(source='get_usertype_display')
    
    class Meta:
            geo_field = "location"
            model = User
            fields = ('id', 'plz', 'City' ,'profile_pic' ,'location', 'usertype','usertype_txt' )

#Register Account
class UserPostSerializer(serializers.ModelSerializer):  
    password = serializers.CharField(write_only=True, style={'input_type': 'password'},max_length=20) 
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'},max_length=20) 
      
    class Meta:
            model  = User
            fields = ( 'name','firstname','password','password2','email','phone_number','Street','profile_pic','plz', 'City' , 'usertype' )
            extra_kwargs = {
            'email': {'write_only': True},
            'password': {'write_only': True},
            'password2': {'write_only': True},
             
        }
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
        #dummy session
        data['session_id'] = uuid.uuid4().hex
        if (data['password2']  != data['password']  ):
            raise serializers.ValidationError("Passwords are not the same")
        return data
    def create(self ,validated_data):
        validated_data.pop('password2')
        validated_data['session_id'] = uuid.uuid4().hex
        use = User.objects.create(**validated_data) 
        use.password = hashpw(use.password)
        salt1 = uuid.uuid4().hex
        data = (salt1+ str(use.id)+ use.email + datetime.datetime.utcnow().isoformat()  ).encode("utf8")
        #print(data)
        hash1 = sha256(data).hexdigest()
        use.session_id = hash1
        use.save()
        return use
#send activation link
def sendverifactionemail():
    pass
#is user aktive
def aktive_user(user):
    if(user.is_active):
        return True
    raise serializers.ValidationError("User not aktivated")
# user session valid
def validsessionid(user):
     delta = timezone.now() - user.last_login
     value = (delta.total_seconds()/60)
     print(value)
     if value < 30 :
         return True
     return False

#get user profile data

class UserProfileSerializer(serializers.ModelSerializer):
    usertype_txt = serializers.CharField(source='get_usertype_display')
  
    class Meta:
            model = User
            fields = ('id','name','firstname','phone_number','email','Street', 'plz', 'City' ,'profile_pic',  'usertype_txt')


#create shop with session id and helper id

#create buylist with session id

#payed shop serializer

#done shop serializer

#update buylist

#update user Profile data
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
            model = User
            
            fields = ('name','firstname','phone_number', 'Street', 'plz', 'City' ,'profile_pic', 'public',   'usertype')
            extra_kwargs = {
            'name': {'required': False},
            'firstname': {'required': False},
            'phone_number': {'required': False},
            'Street': {'required': False},
            'plz': {'required': False},
            'City': {'required': False},
            'profile_pic': {'required': False},
            'usertype': {'required': False},
            'public': {'required': False},
        }


#login session_id
class UserGetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'},max_length=20)   
    session_id  = serializers.CharField(read_only=True)
 
 
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
         
        print(self)
        x = self.initial_data
        print(x)
        if (User.objects.filter(email = data['email'] ,password = hashpw(data['password'])).exists() == False ):
            raise serializers.ValidationError("Wrong Email or Password")
        return data
    def create(self,  validated_data):        
        x = User.objects.filter( email = validated_data['email'] ,password = hashpw(validated_data['password']) )[0]
        salt1 = uuid.uuid4().hex
        data = (salt1+ str(x.id)+ x.email + datetime.datetime.utcnow().isoformat()  ).encode("utf8")
        #print(data)
        hash1 = sha256(data).hexdigest()
        #print(hash1)
        x.session_id = hash1
        x.last_active = timezone.now()
        x.last_login = timezone.now()
        x.save() 
        #print (x)
        #validsessionid(x)
        return (x)
  
 


#hash password
def hashpw(passw):    
    data = (salt1 + passw + salt2).encode("utf-8")
    x = sha256(data).hexdigest()
    return x
#items list
class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
            model = Item 
            fields = ('name','cost' )

# old create buylist
class BuyListSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(  write_only=True)
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
         
        print(self)
        x = self.initial_data
        print(x)
        if (User.objects.filter(email = data['email'] ,password = hashpw(data['password']), id = data['helpsearcher'].id).exists() == False ):
            raise serializers.ValidationError("Fuck you")
        return data
    class Meta:
        model = BuyList
        fields = ('id','items','helpsearcher','creation_date','email','password')
        extra_kwargs = {
            'email': {'write_only': True},
            'password': {'write_only': True},
        }
        

    def create(self, validated_data):
        out = BuyList.objects.create(helpsearcher = validated_data['helpsearcher'] )
        for i in validated_data['items']:
            out.items.add(i)
        out.save()
        return out
# old create shoplist
class ShopListSerializer(serializers.ModelSerializer):
    #serializers.query_params.get('password', False).encode("utf-8")
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(write_only=True)
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
        
        if (User.objects.filter(email = data['email'] ,password = hashpw(data['password']), id = data['helpsearcher'].id).exists() == False ):
            raise serializers.ValidationError("Fuck you")
        if (BuyList.objects.filter(id = data['buylist'].id, helpsearcher = data['helpsearcher']).exists() == False ):
            raise serializers.ValidationError("Helpseacher didnt create List")
        return data
    def create(self,validated_data):
        out = Shop.objects.create(helpsearcher = validated_data['helpsearcher'] , helper = validated_data['helper'] , buylist = validated_data['buylist'])
        out.save()
        return out
    class Meta:
        model = Shop
        fields = ('id','helper','helpsearcher','buylist','email','password' )
