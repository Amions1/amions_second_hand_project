# api/views.py
import logging
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import HttpResponse

from trade.models import User


# 登录接口
class LoginView(APIView):
    # 关闭权限校验（登录接口本身无需认证）
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # 1. 获取前端传的参数
        phone = request.data.get('phone')
        password = request.data.get('password')
        print(f"phone:{phone}, password:{password}")

        # 2. 简单参数校验
        if not phone or not password:
            return Response({
                'status': '400',
                'msg': '手机号和密码不能为空',
                'data': []
            })

        # 3. 查询User表并验证密码
        try:
            # 根据手机号查询自定义表中的用户
            user = User.objects.get(phone=phone)

            # 检查用户状态，状态为0表示禁用
            if user.status == 0:
                return Response({
                    'status': '401',
                    'msg': '账号已被禁用，请联系管理员',
                    'data': []
                })
            # 验证密码
            if not check_password(password, user.password):
                return Response({
                    'status': '401',
                    'msg': '手机号或密码错误',
                    'data': []
                })

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            logger = logging.getLogger(__name__)
            logger.info(f"jwt访问令牌：{refresh.access_token}")
            logger.info(f"jwt刷新令牌：{refresh}")

            # 使用用户ID作为键的一部分，存储访问令牌，将JWT存储到Redis中
            cache.set(f'jwt_token_{user.id}', str(refresh.access_token), timeout=1800)  # 30分钟
            print(f"用户{user.nickname}登录成功")

            return Response({
                'status': '200',
                'msg': '登录成功',
                'data': {
                    'user_id': user.id,
                    'phone': user.phone,
                    'nickname': user.nickname,
                    'role': user.role,
                    'access_token': str(refresh.access_token),  # 访问令牌
                    'refresh_token': str(refresh),  # 刷新令牌
                }
            })

        except User.DoesNotExist:
            # 手机号不存在
            return Response({
                'status': '401',
                'msg': '手机号或密码错误',
                'data': []
            })


# 忘记密码接口
class ForgetView(APIView):

    def get(self, request):
        # 为支持GET请求添加简单响应
        return HttpResponse({"请用post请求访问!"}, status=405)
    
    def post(self, request):
        # 1. 获取前端传的参数
        phone = request.data.get('phone')
        new_password = request.data.get('password')
        
        # 2. 参数校验
        if not phone:
            return Response({
                'status': '400',
                'msg': '手机号不能为空',
                'data': []
            })
        
        if not new_password:
            return Response({
                'status': '400',
                'msg': '新密码不能为空',
                'data': []
            })
        
        # 3. 验证密码强度（可选）
        if len(new_password) < 6:
            return Response({
                'status': '400',
                'msg': '密码长度不能少于6位',
                'data': []
            })
        
        # 4. 查询用户
        try:
            user = User.objects.get(phone=phone)
            
            # 5. 检查用户状态
            if user.status == 0:
                return Response({
                    'status': '401',
                    'msg': '账号已被禁用，请联系管理员',
                    'data': []
                })
            
            # 6. 更新密码
            user.password = make_password(new_password)
            user.save()
            
            logger = logging.getLogger(__name__)
            logger.info(f"用户 {phone} 密码重置成功")
            
            return Response({
                'status': '200',
                'msg': '密码重置成功',
                'data': {
                    'user_id': user.id,
                    'phone': user.phone,
                    'nickname': user.nickname
                }
            })
            
        except User.DoesNotExist:
            # 手机号不存在也返回成功（防止暴力破解）
            return Response({
                'status': '200',
                'msg': '密码重置成功',
                'data': []
            })

