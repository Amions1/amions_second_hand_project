from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('users', GetUsersView.as_view(), name='GetUsersView'),
    path('goods', GetGoodsView.as_view(), name='GetGoodsView'),
    path('categories', GetGoodsCategories.as_view(), name='GetGoodsCategories'),
    path('orders', GetOrders.as_view(), name='GetOrders'),
    path('ban_user', BanUserView.as_view(), name='BanUserView'),
    path('product/<int:product_id>/', ProductManageView.as_view(), name='ProductManageView'),
    path('category/<int:category_id>/', UpdateCategoryNameView.as_view(), name='UpdateCategoryNameView'),
    path('category/', AddCategoryView.as_view(), name='AddCategoryView'),  # 新增分类接口
]
