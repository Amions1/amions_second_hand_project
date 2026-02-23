from django.contrib import admin
from django.urls import path, include

from .consumer import ChatConsumer
from .views import ChatUsersView, ChatHistoryView

urlpatterns = [
    path('users/', ChatUsersView.as_view(), name='ChatUsersView'),
    path('history/<str:room_name>/', ChatHistoryView.as_view(), name='ChatHistoryView'),
]
