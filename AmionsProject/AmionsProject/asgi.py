"""
ASGI config for AmionsProject project.
"""
import os
import django

# 1. 先设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AmionsProject.settings')

# 2. 手动初始化 Django（必须先做）
django.setup()

# 3. 获取 HTTP 应用
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 4. 延迟导入 Channels 相关模块（避免提前加载消费者）
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 5. 最后导入 routing（此时 Django 已完全初始化）
def get_websocket_urls():
    from . import routing
    return routing.websocket_urlpatterns

# 6. 构建应用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(get_websocket_urls())  # 用函数延迟加载路由
    )
})