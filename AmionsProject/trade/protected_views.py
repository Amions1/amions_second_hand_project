from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Goods, User
import json


# 函数视图示例 - 需要JWT认证
@csrf_exempt
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    获取用户个人信息 - 需要JWT认证
    """
    user = request.user
    return JsonResponse({
        'id': user.id,
        'phone': user.phone,
        'nickname': user.nickname,
        'role': user.role
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_goods(request):
    """
    发布商品 - 需要JWT认证
    """
    user = request.user  # 已认证的用户
    
    # 从前端获取商品信息
    title = request.data.get('title')
    price = request.data.get('price')
    # ... 其他商品信息
    
    # 创建商品，关联到当前用户
    goods = Goods.objects.create(
        title=title,
        price=price,
        publisher=user,
        # ... 其他字段
    )
    
    return JsonResponse({
        'message': '商品发布成功',
        'goods_id': goods.id
    })


# 类视图示例 - 需要JWT认证
from django.views import View
from rest_framework.views import APIView

class UserProfileView(APIView):
    """
    用户个人资料视图 - 需要JWT认证
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return JsonResponse({
            'id': user.id,
            'phone': user.phone,
            'nickname': user.nickname,
            'role': user.role
        })
    
    def post(self, request):
        # 更新用户信息的逻辑
        user = request.user
        nickname = request.data.get('nickname')
        if nickname:
            user.nickname = nickname
            user.save()
        
        return JsonResponse({
            'message': '用户信息更新成功',
            'user': {
                'id': user.id,
                'phone': user.phone,
                'nickname': user.nickname
            }
        })