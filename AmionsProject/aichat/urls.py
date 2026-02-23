"""
AI聊天应用URL配置
"""

from django.urls import path

from aichat.views import AIChatView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai_chat'),
]