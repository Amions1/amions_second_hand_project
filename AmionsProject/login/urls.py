from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 登录接口
    path('', LoginView.as_view(),name='LoginView'),
    path('forget/', ForgetView.as_view(),name='ForgetView'),
    #jwt
    path('token/',TokenObtainPairView.as_view(),name='TokenObtainPairView'),
    path('token/refresh/',TokenRefreshView.as_view(),name='TokenRefreshView'),
    path('token/verify/',TokenVerifyView.as_view(),name='TokenVerifyView')

]