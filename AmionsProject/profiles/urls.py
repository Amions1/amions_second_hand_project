from django.contrib import admin
from django.urls import path
from .views import publishedGoods, UpdateNickname, BoughtView, SoldView, ChangePassword, OffShelfView, WishGoodsView, TakeDownOrPutUpView

urlpatterns = [
    path('', publishedGoods.as_view(), name='publishedGoods'),
    path('update_nickname/', UpdateNickname.as_view(), name='UpdateNickname'),
    path('bought/', BoughtView.as_view(), name='BoughtView'),
    path('sold/', SoldView.as_view(), name='SoldView'),
    path('changepassword/', ChangePassword.as_view(), name='ChangePassword'),
    path('off_shelf/<int:user_id>/',OffShelfView.as_view(),name='OffShelfView'),
    path('wishlist/<int:user_id>/',WishGoodsView.as_view(),name='WishGoodsView'),
    path('takedown_or_putup/', TakeDownOrPutUpView.as_view(), name='TakeDownOrPutUpView')
]