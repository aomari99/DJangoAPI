from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer
from pages.models import *
from django.http import HttpResponseForbidden 
from django.shortcuts import get_object_or_404
from .configreceipt import read_config
from .parse import *
import cv2 
import pytesseract
import numpy as np
import os 
import imutils
from skimage.filters import threshold_local

salt1 = "abcgfhködup977s" 
salt2 = "üopasdznm,sdu67"
dir_path = os.path.dirname(os.path.realpath(__file__))
from django.utils import timezone
from firebase_admin import messaging
# See documentation on defining a message payload.
def sendMessage(user,msg_title,msg_body,otherUser):
    print('Successfully sending message:', msg_title , msg_body , otherUser.profile_pic.url , user.firebase_token)
    message = messaging.Message(
        notification=messaging.Notification(
            title=msg_title,
            body=msg_body,
            image= "https://moco.fluffistar.com"+otherUser.profile_pic.url
        ),
        token=user.firebase_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped
#parse receipt
def parse(img ):
    orig = img.copy()
    
    img = get_grayscale(img)
    img = unsharp_mask(img)

     
     
    
    isWritten = cv2.imwrite('api/test.png' , img)
 
# show the contour (outline) of the piece of paper
    

    #isWritten = cv2.imwrite('api/test.png' , img)
    
    config = r'-l deu --oem 3 --psm 6'
    
    # Adding custom options
    config_stat = read_config("api/config.yml")
    string = pytesseract.image_to_string( (img), config=config)
    print(string)
    receipt = ocr_receipts_txt(config_stat , string)
     
    
    #receipt_files = get_files_in_folder(config.receipts_path)
    #stats = ocr_receipts(config, receipt_files)  
    return receipt
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
     if value < 60 :
         return True
     return False

#get user profile data

class UserProfileSerializer(serializers.ModelSerializer):
    usertype_txt = serializers.CharField(source='get_usertype_display')
  
    class Meta:
            model = User
            fields = ('id','name','firstname','phone_number','email','Street', 'plz', 'City' ,'profile_pic', 'location',  'usertype_txt')


 
            

#update user Location
class UserProfileLocationSerializer(serializers.ModelSerializer):

    lat_point = serializers.DecimalField(max_digits=None, decimal_places=None,write_only=True)
    long_point = serializers.DecimalField(max_digits=None, decimal_places=None,write_only=True)
    def update(self, instance, validated_data):
        instance.location = Point( float (validated_data['lat_point']) , float(validated_data['long_point']))
        instance.save()
        return instance
    class Meta:
            model = User           
            fields = ['location','lat_point','long_point']
            extra_kwargs={
                'location': {'read_only': True}
            }
#update Firebasetoken User          
class UserProfileFirebaseSerializer(serializers.ModelSerializer):
    class Meta:
            model = User           
            fields = ['firebase_token']



#payed shop serializer

#done shop serializer 

#update buylist ?? nice to have 

#update user Profile data
class UserProfileUpdateSerializer(serializers.ModelSerializer):

    usertype_txt = serializers.CharField(source='get_usertype_display',read_only=True)
    def update(self, instance, validated_data): # <- to update values + shop
    #update Shop at shop_id set helper 
        instance.name = validated_data.get('name', instance.name)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.Street = validated_data.get('Street', instance.Street)
        instance.plz = validated_data.get('plz', instance.plz)
        instance.City = validated_data.get('City', instance.City)
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.public = validated_data.get('public', instance.public)
        
        if(instance.usertype != validated_data.get('usertype', instance.usertype)):
            if(Shop.objects.filter( helpsearcher = instance  ,   finished_date__isnull = True).exists() or Shop.objects.filter( helper =instance  ,   finished_date__isnull = True).exists() or Angebot.objects.filter(helper = instance  , viewed = False).exists()):
                raise serializers.ValidationError("Usertype kann nicht geändert werden. Du hast noch einen Offenen Einkauf oder Angebot")
            else:
                instance.usertype = validated_data.get('usertype', instance.usertype)
        

        instance.save()
        return instance
    class Meta:
            model = User
            
            fields = ('name','firstname','phone_number','email', 'Street', 'plz', 'City' ,'profile_pic', 'public', 'usertype','usertype_txt')
            extra_kwargs = {
            'name': {'required': False},
            'firstname': {'required': False},
            'phone_number': {'required': False},
            'email': {'read_only':True},
            'Street': {'required': False},
            'plz': {'required': False},
            'City': {'required': False},
            'profile_pic': {'required': False},
            'usertype': {'required': False},
            'public': {'required': False},
        }

#items list
class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
            model = Item 
            fields = ('id','name','cost' )


class ArticleSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    class Meta:
            model = Article 
            fields = ('item','count' )

class GETBuyListSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True,read_only=True)
    class Meta:
            model = BuyList 
            fields = ['id','articles','creation_date']

class ShopUpdateDoneSerializer(serializers.ModelSerializer):
    helper = UserProfileSerializer(read_only=True)
    helpsearcher =  UserProfileSerializer(read_only=True)
    buylist = GETBuyListSerializer(read_only=True)
    def update(self, instance, validated_data):
        instance.done = validated_data.get('done', instance.done)
        instance.bill_hf = validated_data.get('bill_hf', instance.bill_hf)
        instance.bill_hfs = validated_data.get('bill_hfs', instance.bill_hfs)
        instance.save()
        if(instance.done):
            sendMessage(instance.helper,"Hat ihren Einkauf Bestätigt",instance.helpsearcher.firstname+ " "+ instance.helpsearcher.name ,instance.helpsearcher)
        if(not instance.done):
            path = 'config/static'+instance.bill_hf.url
            print("PAth : "  + path)
            img = cv2.imread(path)
            data = parse(img)
            if(data.sum is None):
                raise serializers.ValidationError("Bild konnte nicht erkannt werden lade bitte ein neues hoch")
            instance.price = data.sum
            instance.save()
            sendMessage(instance.helpsearcher,"Hat ihren Einkauf erledigt. Der Preis Beträgt " +instance.price+ " Euro",instance.helper.firstname+ " "+ instance.helper.name ,instance.helper)
            
        return instance
    class Meta:
            model = Shop
            fields = ['id','price','buylist','helpsearcher','helper','payed','payed_prove','done','bill_hfs','bill_hf','raiting','creation_date','finished_date']
            extra_kwargs = {
            'done': {'required': False},
            'bill_hf': {'required': False},
            'bill_hfs': {'required': False},
             
                'id': {'read_only':True},'price': {'read_only':True},'buylist': {'read_only':True},'helpsearcher': {'read_only':True},'helper': {'read_only':True},'payed': {'read_only':True}, 'payed_prove':{'read_only':True} ,'raiting' : {'read_only':True},'creation_date' : {'read_only':True},'finished_date': {'read_only':True}
        
            }

class ShopUpdatePayedHFSerializer(serializers.ModelSerializer): 
    helper = UserProfileSerializer(read_only=True)
    helpsearcher =  UserProfileSerializer(read_only=True)
    buylist = GETBuyListSerializer(read_only=True)
    def update(self, instance, validated_data):
        instance.payed = validated_data.get('payed', instance.payed)
        instance.finished_date = validated_data.get('finished_date', instance.finished_date)
        sendMessage(instance.helpsearcher,"Bezahlung erhalten"if( instance.payed == True ) else "Bezahlung nicht erhalten",instance.helper.firstname+ " "+ instance.helper.name ,instance.helper) 
        instance.save()
        return instance
    class Meta:
            model = Shop
            fields = ['id','price','buylist','helpsearcher','helper','payed','payed_prove','done','bill_hfs','bill_hf','raiting','creation_date','finished_date']
            extra_kwargs = {
                'id': {'read_only':True},'price': {'read_only':True},'buylist': {'read_only':True},'helpsearcher': {'read_only':True},'helper': {'read_only':True}, 'payed_prove': {'read_only':True},'done': {'read_only':True},'bill_hfs': {'read_only':True} ,'bill_hf': {'read_only':True},'raiting' : {'read_only':True},'creation_date' : {'read_only':True} 
            }

class ShopUpdatePayedHFSSerializer(serializers.ModelSerializer):  
    helper = UserProfileSerializer(read_only=True)
    helpsearcher =  UserProfileSerializer(read_only=True)
    buylist = GETBuyListSerializer(read_only=True)
    def update(self, instance, validated_data):
        instance.payed_prove = validated_data.get('payed_prove', instance.payed_prove)
        sendMessage(instance.helper,"Hat sie Bezahlt",instance.helpsearcher.firstname+ " "+ instance.helpsearcher.name ,instance.helpsearcher)
        instance.save()
        return instance
    class Meta:
            model = Shop
            fields = ['id','price','buylist','helpsearcher','helper','payed','payed_prove','done','bill_hfs','bill_hf','raiting','creation_date','finished_date']
            extra_kwargs = {
                'id': {'read_only':True},'price': {'read_only':True},'buylist': {'read_only':True},'helpsearcher': {'read_only':True},'helper': {'read_only':True},'payed': {'read_only':True}, 'done': {'read_only':True},'bill_hfs': {'read_only':True} ,'bill_hf': {'read_only':True},'raiting' : {'read_only':True},'creation_date' : {'read_only':True},'finished_date': {'read_only':True}
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
         
        #print(self)
        x = self.initial_data
        #print(x)
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



class ArticleSerializerADD(serializers.ModelSerializer):   

    class Meta:
            model = Article
            fields = ['id','item','count']



class ArticleSerializerADDList(serializers.ModelSerializer):
    articles = serializers.ListField(child=ArticleSerializerADD(),write_only=True)
    def create(self, validated_data):
        articless = validated_data['articles']
        
        info = []

        for item in articless:
            info.append(Article(**item))
            
        data = Article.objects.bulk_create(info)
        print(data)
        return data
    def to_representation(self, instance):
        ids=[]
        for item in instance:
            ids.append(item.id)
        output = {"articles":ids}
        print(self)
        return output
    class Meta:
            model = Article 
            fields = ['articles']      



# new create buylist
class BuyListSerializer(serializers.ModelSerializer):
     
    session_id = serializers.CharField(write_only=True)
    articlesdata = serializers.ListField(child=ArticleSerializerADD(),write_only=True)
    articles = ArticleSerializer(many=True,read_only=True)
    def validate(self, data):
        print(self)
        print(data)
        if (User.objects.filter(session_id = data['session_id'] , usertype='HFS'  ).exists()):
         data['helpsearcher'] = User.objects.filter(session_id = data['session_id']  )[0]
        else:
         raise serializers.ValidationError("Invalid Input")

        if(len(data['articlesdata']) ==  0):
            raise serializers.ValidationError("No EmptyList")
        if(validsessionid(data['helpsearcher'])):
              return data
        raise serializers.ValidationError("Invalid Sessionid")
      
    class Meta:
        model = BuyList
        fields = ('articles' ,'helpsearcher','articlesdata' ,'creation_date','session_id')
        extra_kwargs = {
            'helpsearcher': {'read_only': True},
            'articles': {'read_only': True},
            'session_id': {'write_only': True},
             'articlesdata': {'write_only': True},
        }
        

        

    def create(self, validated_data):
        out = BuyList.objects.create(helpsearcher = validated_data['helpsearcher'] )

        articless = validated_data['articlesdata']
        
        info = []

        for item in articless:
            info.append(Article(**item))
            
        data = Article.objects.bulk_create(info)

        for i in data:
            out.articles.add(i)
        out.save()
        return out




# old create shoplist


class GETAllShopListSerializer(serializers.ModelSerializer):
    helper = UserProfileSerializer(read_only=True)
    helpsearcher =  UserProfileSerializer(read_only=True)
    buylist = GETBuyListSerializer(read_only=True)
    class Meta:
        model = Shop
        fields = ['id','price','buylist','helpsearcher','helper','payed','payed_prove','done','bill_hfs','bill_hf','raiting','creation_date','finished_date']
class GETSearchShopListSerializer(serializers.ModelSerializer):
    helpsearcher =  UserProfileSerializer(read_only=True)
    buylist = GETBuyListSerializer(read_only=True)
     
    class Meta:
        model = Shop
        fields = ['id','buylist','helpsearcher','creation_date']
class ShopListSerializer(serializers.ModelSerializer):
    #serializers.query_params.get('password', False).encode("utf-8")
    helpsearcher = UserProfileSerializer(read_only=True)
    session_id = serializers.CharField(write_only=True)
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
        
        if (User.objects.filter(session_id = data['session_id'] , usertype='HFS'  ).exists()):
         data['helpsearcher'] = User.objects.filter(session_id = data['session_id']  )[0]
        else:
         raise serializers.ValidationError("Invalid Input")
             
        if (Shop.objects.filter(helpsearcher = data['helpsearcher'] , finished_date__isnull = True).exists()):
            raise serializers.ValidationError("Ein nicht erledigter Shop ist noch offen")
        if(not validsessionid(data['helpsearcher'])):    
            raise serializers.ValidationError("Invalid Sessionid")

        return data
    def create(self,validated_data):
        out = Shop.objects.create(helpsearcher = validated_data['helpsearcher']   , buylist = validated_data['buylist'])
        out.save()
        return out
    class Meta:
        model = Shop
        fields = ('id','helpsearcher','buylist','session_id' )
        extra_kwargs = {
            'helpsearcher': {'read_only': True},
            'session_id': {'write_only': True},
        }

#get Angebot HF
class GetHFAngebotSerializer(serializers.ModelSerializer):
    helper = UserProfileSerializer(read_only=True)
    shop = GETAllShopListSerializer(read_only=True)
    class Meta:
        model = Angebot
        fields = ['id','shop','creation_date','helper','viewed','approve']

#get Angebot HFS
class GetAngebotSerializer(serializers.ModelSerializer):
    helper = UserProfileSerializer(read_only=True)
    shop = GETAllShopListSerializer(read_only=True)
    class Meta:
        model = Angebot
        fields = ['id','shop','creation_date','helper']
#create Angebot
class CreateAngebotSerializer(serializers.ModelSerializer):
    session_id = serializers.CharField(write_only=True)
    def validate(self, data):
        """
        Check that the blog post is about USer.
        """
        
        if (User.objects.filter(session_id = data['session_id'] , usertype='HF'  ).exists()):
            data['helper'] = User.objects.filter(session_id = data['session_id']  )[0]
        else:
            raise serializers.ValidationError("Invalid Input")
        if(Angebot.objects.filter(helper = data['helper']   , shop = data['shop'], viewed = False).exists()):#if user already did an angebot but didnt got reviewed so he cant annoy hfs
            	raise serializers.ValidationError("Already created an Angebot which didnt got reviewed by User")
        
        sendMessage(data['shop'].helpsearcher,"Hallo ich will helfen",data['helper'].firstname+ " "+ data['helper'].name ,data['helper'])
        if(validsessionid(data['helper'])):
              return data
        raise serializers.ValidationError("Invalid Sessionid")

    def create(self,validated_data):
        out = Angebot.objects.create(helper = validated_data['helper']   , shop = validated_data['shop'])
        out.save()
        return out
    class Meta:
        model = Angebot
        fields = ('id','helper','shop','session_id' )
        extra_kwargs = {
            'helper': {'read_only': True},
            'session_id': {'write_only': True},
        }


#view Angebot and give a decision
class SetAngebotSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data): # <- to update values + shop
        #update Shop at shop_id set helper 
        instance.viewed = validated_data.get('viewed', instance.viewed)
        instance.approve = validated_data.get('approve', instance.approve)
        instance.save()
        shop_id =instance.shop.id
        helper = instance.helper
        shop = Shop.objects.filter(id=shop_id) 
        if(instance.approve):
         
            update = {}
            update['helper'] = helper
            shop.update(**update)
        sendMessage(helper , "Dein Angebot wurde angenommen" if(instance.approve) else "Dein Angebot wurde abgelehnt" , shop[0].helpsearcher.firstname+ " "+ shop[0].helpsearcher.name , shop[0].helpsearcher )
        return instance
    class Meta:
        model = Angebot
        fields = ['viewed','approve']

class oldShopListSerializer(serializers.ModelSerializer):
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
