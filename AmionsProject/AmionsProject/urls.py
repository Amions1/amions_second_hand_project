"""
URL configuration for AmionsProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from operator import index

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from login.views import LoginView

urlpatterns = [
    path('', include('trade.urls')),
    path('admin/', admin.site.urls),
    path('api/goods/', include('trade.urls')),
    path('api/auth/login/', include('login.urls')),
    path('api/user/profiles/', include('profiles.urls')),
    path('api/auth/sign/', include('sign.urls')),
    path('api/details/', include('details.urls')),
    path('api/settlement/', include('settlement.urls')),
    path('api/admin_manage/', include('admin_manage.urls')),
    path('api/chat/', include('chat.urls')),

    path('api/aichat/', include('aichat.urls')),  # 添加AI聊天路由
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)