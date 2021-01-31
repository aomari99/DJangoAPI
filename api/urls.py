from django.urls import path
from .views import *
 
urlpatterns = [
path('user/hfs', HelpSearchlUser.as_view()),
path('user/hf' ,HelplUser.as_view() ),
path('user/add' ,UserAdd.as_view() ),
path('items',AllItems.as_view()),
path('buylist/add',BuyListAdd.as_view()),
path('shop/add',ShopAdd.as_view()),
path('user/login',UserGet.as_view()),
path('user/<session_id>',UserProfile.as_view()),
path('user/update/<session_id>',UserUpdate.as_view()),
]
