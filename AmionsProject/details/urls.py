from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('<int:id>/', userDetails.as_view(), name='userDetails'),
    path('wish/<int:user_id>/<int:goods_id>',CheckIsWished.as_view(),name="CheckIsWished"),
    path('adduserwish/', AddUserWish.as_view(), name='AddUserWish')
]
