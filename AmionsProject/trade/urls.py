from django.contrib import admin
from django.urls import path, include
from .views import *
from .protected_views import user_profile, add_goods, UserProfileView

urlpatterns = [
    path('', GoodsMenuView.as_view(), name='goods_main_menu'),
    path('first', GoodsMenuView.as_view(), name='goods_main_menu'),
    path('second', GoodsSubMenu.as_view(), name='goods_sub_menu'),
    path('search/', Search.as_view(), name='Search'),
    path('goodslist/', GoodsListView.as_view(), name='GoodsListView'),
]
