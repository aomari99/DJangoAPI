from django.urls import path
from .views import *

urlpatterns = [
path('user/hfs/<session_id>', HelpSearchUser.as_view()),
path('user/hf/<session_id>' ,HelplUser.as_view() ),
path('user/add' ,UserAdd.as_view() ),
path('items',AllItems.as_view()),
path('buylist/add',BuyListAdd.as_view()),
path('shop/add',ShopAdd.as_view()),
path('article/add',AddArticle.as_view()),
path('user/login',UserGet.as_view()),
path('user/<session_id>',UserProfile.as_view()),
path('buylist/<session_id>',BuyListGet.as_view()),
path('angebot/hfs/<session_id>',AngebotGetHFS.as_view()),
path('angebot/hf/<session_id>',AngebotGetHF.as_view()),
path('angebot/hfs/<session_id>/<id>',AngebotReview.as_view()),
path('shop/<session_id>/<int:pk>',ShopGetOne.as_view()),
path('buylist/delete/<session_id>/<id>',BuyListDelete.as_view()),
path('shop/delete/<session_id>/<id>',ShopDelete.as_view()),
path('shop/pay/<session_id>/<id>',ShopPayedHF.as_view()),
path('shop/payprove/<session_id>/<id>',ShopPayedHFS.as_view()),
path('shop/donehfs/<session_id>/<id>',ShopDone.as_view()),
path('shop/donehf/<session_id>/<id>',ShopDoneHF.as_view()),
path('angebot/add',AngebotAdd.as_view()),
path('shop/<session_id>',ShopGet.as_view()),
path('user/update/<session_id>',UserUpdate.as_view()),
path('user/location/<session_id>',UserLocation.as_view()),
path('user/firebase/<session_id>',UserFirebaseToken.as_view()),
path('user/search/<session_id>' ,SearchHFS.as_view() ),
 
]
