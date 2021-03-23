from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import PermissionDenied
import uuid
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
# Create your models here.
from rest_framework import permissions
from django import forms
from hashlib import sha256
import datetime
from django.http import HttpResponseForbidden    
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

def make_session_id(user):
   while(True): 
    salt1 = uuid.uuid4().hex
    data = (salt1+ str(user.id)+ user.email + datetime.datetime.utcnow().isoformat()  ).encode("utf8")
    hash1 = sha256( data).hexdigest
    print(hash1)
    if( (User.objects.filter(session_id = hash1)).exists() == False ):
        return hash1


class RejectSpambotRequestsMiddleware(object):  
    def __init__(self, get_response):
        self.get_response = get_response
         
    def __call__(self, request):
            response = self.get_response(request)
            api_key = request.GET.get('apikey', False)#.encode("utf-8")
            date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H").encode("utf-8") 
            validapikey = sha256(date).hexdigest().encode("utf-8")
            print(api_key)
            print(validapikey)
            if( api_key == "adam"):
                return  response
            else:
              return HttpResponseForbidden()
class OnlyAPIPermission(permissions.BasePermission):
    def has_permission(self, request, view):
            api_key = request.query_params.get('apikey', False).encode("utf-8")
            date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H").encode("utf-8") 
            validapikey = sha256(date).hexdigest().encode("utf-8")
            #print(api_key)
            #print(validapikey)
            if( api_key == validapikey):
                return True
            else:
            
              return False
import os
import glob
def user_directory_path(instance, filename):  
    filenameout = 'images/user_{0}_{1}'.format(instance.id, filename)
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
    print(filenameout)
    #os.chdir("")
    userimgs = glob.glob(settings.MEDIA_ROOT+"/images/user_"+str(instance.id)+"*")
    for files in userimgs:
            print(files)
            if (files !=filenameout ):
                os.remove(files)
    return filenameout

def rechnung_hf_directory_path(instance, filename):  
    filenameout = 'images/hf_rechnung_{0}_{1}'.format(instance.id, filename)
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
    print(filenameout)
    #os.chdir("")
    userimgs = glob.glob(settings.MEDIA_ROOT+"/images/hf_rechnung_"+str(instance.id)+"*")
    for files in userimgs:
            print(files)
            if (files !=filenameout ):
                os.remove(files)
    return filenameout

def rechnung_hfs_directory_path(instance, filename):  
    filenameout = 'images/hfs_rechnung_{0}_{1}'.format(instance.id, filename)
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
    print(filenameout)
    #os.chdir("")
    userimgs = glob.glob(settings.MEDIA_ROOT+"/images/hfs_rechnung_"+str(instance.id)+"*")
    for files in userimgs:
            print(files)
            if (files !=filenameout ):
                os.remove(files)
    return filenameout

def pay_directory_path(instance, filename):  
    filenameout = 'images/pay_{0}_{1}'.format(instance.id, filename)
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
    print(filenameout)
    #os.chdir("")
    userimgs = glob.glob(settings.MEDIA_ROOT+"/images/pay_"+str(instance.id)+"*")
    for files in userimgs:
            print(files)
            if (files !=filenameout ):
                os.remove(files)
    return filenameout
 
# creating a validator function 
#  #profile_pic = models.ImageField(default='images/user_default.png') #,upload_to = user_directory_path ) 
class User(models.Model):
    name = models.CharField(max_length=250)
    firstname = models.CharField(max_length=250)
    firebase_token = models.CharField(max_length=250,default="")
    plz = models.CharField(max_length=250)
    City = models.CharField(max_length=250)
    Street = models.CharField(max_length=250)
    location = models.PointField(srid=4326,geography=True, default=Point(51.133481, 10.018343)) 
    session_id = models.CharField( max_length=250 ,unique = True)
    phone_number = PhoneNumberField(help_text='Contact phone number',unique=True)
    is_active = models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    last_login=models.DateTimeField( auto_now_add=True)
    last_active= models.DateTimeField( auto_now_add=True)
    created_date= models.DateTimeField( auto_now_add=True)
    public = models.BooleanField(default=False)
    profile_pic = models.ImageField(default='images/user_default.png' ,upload_to = user_directory_path ) 
    #lat_val = models.CharField(max_length=250)
    #long_val =models.CharField(max_length = 250)
    usertypes = [('HF','Helfer'),('HFS','HilfeSuchender')]
    usertype =models.CharField(
        max_length=50,
        choices=usertypes,
         
        default='Helfer',
    )
    password = models.CharField( max_length=200)
    email = models.EmailField(unique=True)
    @property
    def _sessionid(self):
        return self.session_id
    def __str__(self):
        return self.firstname + " " + self.name
class Item(models.Model):
    name = models.CharField(max_length=250)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return self.name 
class Article(models.Model):
    item = models.ForeignKey(Item , on_delete = models.CASCADE)
    count =   models.IntegerField(
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
     )
    def __str__(self):
        return str(self.item) +" "+ str(self.count)
class BuyList(models.Model):
    articles = models.ManyToManyField(Article) 
    helpsearcher = models.ForeignKey(User,limit_choices_to={'usertype': 'HFS'}, on_delete = models.CASCADE)
    creation_date =  models.DateTimeField(
    auto_now_add=True)
    def __str__(self):
        return "ID: " + str(self.id) + " "+ self.helpsearcher.name #+ " " + self.creation_date.strftime("%Y-%m-%d %H:%M") 
class Shop(models.Model):
    helper =models.ForeignKey(User,limit_choices_to={'usertype': 'HF'}, on_delete = models.CASCADE  ,null=True) 
    helpsearcher = models.ForeignKey(User,limit_choices_to={'usertype': 'HFS'}, on_delete = models.CASCADE ,related_name='helpseacher_requests_created') 
    buylist = models.ForeignKey(BuyList,   
          on_delete = models.CASCADE)
    bill_hfs = models.ImageField(null=True ,upload_to = rechnung_hfs_directory_path ) 
    bill_hf = models.ImageField(null=True ,upload_to = rechnung_hf_directory_path ) 
    payed_prove = models.ImageField(null=True ,upload_to = pay_directory_path ) 
    payed = models.BooleanField(default=False)
    done =models.BooleanField(default=False)
    creation_date =  models.DateTimeField(
    auto_now_add=True  )
    raiting  =  models.IntegerField(
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
     )
    finished_date =  models.DateTimeField(null=True)
    def __str__(self):
        return  "ID: " + str(self.id)  

class Angebot(models.Model):
    shop = models.ForeignKey(Shop,limit_choices_to={'helper__isnull': 'True'}, on_delete = models.CASCADE)
    helper = models.ForeignKey(User,limit_choices_to={'usertype': 'HF'}, on_delete = models.CASCADE) 
    approve = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    creation_date =  models.DateTimeField(
    auto_now_add=True  )
    