import logging

from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.views import View
from trade.models import User


class userSign(View):
    def get(self,request):
        return HttpResponse({"请用post请求访问!"}, status=405)


    def post(self,request):
        print("用户正在注册中。。。。")
        nickname = request.POST.get('nickname')
        phone=request.POST.get('phone')
        password=request.POST.get('password')

        if not all([phone, password, nickname]):
            return JsonResponse({
                'status': '400',
                'msg': '缺少必要参数'
            })
        
        # 类型转换
        try:
            phone_str=str(phone)
            password=str(password)
            nickname=str(nickname)
            user_status='1'
            role='1'
        except ValueError:
            return JsonResponse({
                'status': '400',
                'msg': '参数类型错误'
            })


        # 验证手机号是否已经存在
        try:
            User.objects.get(phone=phone_str)
            # 如果找到用户，说明手机号已被注册
            return JsonResponse({
                'status': '400',
                'msg': '手机号已被注册'
            })
        except User.DoesNotExist:
            # 如果没有找到用户，则可以继续注册流程
            pass

        # 创建用户对象并添加到数据库
        user = User(
            phone=phone_str,
            password=make_password(password),
            nickname=nickname,
            status=user_status,
            role=role
        )
        user.save()

        print(f"用户注册成功:  手机号:{phone_str}, 密码:{password},加密后的密码:{make_password(password)},昵称： {nickname}")
        return JsonResponse({
            'status': '200',
            'msg': '注册成功'
        })