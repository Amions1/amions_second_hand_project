import json
import logging
import os
import re
from urllib.parse import urlencode

from Cryptodome.PublicKey import RSA
from django import http
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from trade.models import User, Goods, Order
from alipay import AliPay


def clean_key(raw_key: str, key_type: str = "PRIVATE") -> str:
    """
    将原始密钥字符串格式化为符合SDK源码正则要求的PEM格式
    :param raw_key: 原始密钥字符串（你的应用私钥/支付宝公钥）
    :param key_type: 密钥类型，PRIVATE（私钥）或 PUBLIC（公钥）
    :return: 符合正则要求的合法PEM格式字符串
    """
    # 1. 清理所有无关字符（换行、空格、回车、隐藏字符）
    clean_key = re.sub(r'-----BEGIN.*-----|-----END.*-----|\r|\n|\s+', '', raw_key)

    # 2. 按源码正则要求组装标准PEM格式：
    #    - BEGIN行：开头可选空白 + -----BEGIN xxx----- + 至少一个空白（换行）
    #    - END行：-----END xxx----- + 结尾可选空白，且BEGIN/END的marker必须一致
    begin_line = f"-----BEGIN {key_type} KEY-----\n"  # \n满足\s+要求
    end_line = f"\n-----END {key_type} KEY-----"  # 结尾无多余空格，满足\s*$要求
    # 3. 拼接最终合法格式
    valid_pem = begin_line + clean_key + end_line
    return valid_pem

class SettlementView(View):
    def get(self, request):
        return JsonResponse({"error": "请用post请求访问!"}, status=405)

    def post(self, request):
        try:
            # 获取POST数据
            goods_id = request.POST.get('goods_id')
            buyer_id = request.POST.get('buyer_id')
            seller_id = request.POST.get('seller_id')
            price = request.POST.get('price')
            image = request.POST.get('image')
            title = request.POST.get('title')


            # 设置订单状态为0（订单发起中）
            order_status = 0

            # 数据验证
            if not all([price, goods_id, buyer_id, seller_id]):
                return JsonResponse({
                    "status": "400",
                    "msg": "缺少必要参数"
                }, status=400)

            # 类型验证
            try:
                price = float(price)
                goods_id = int(goods_id)
                buyer_id = int(buyer_id)
                seller_id = int(seller_id)
                image=str(image)
                title=str(title)
            except ValueError:
                return JsonResponse({
                    "status": "400",
                    "msg": "参数类型错误"
                }, status=400)

            # 验证用户是否存在
            try:
                buyer = User.objects.get(id=buyer_id)
                seller = User.objects.get(id=seller_id)
            except User.DoesNotExist:
                return JsonResponse({
                    "status": "400",
                    "msg": "买家或卖家不存在"
                }, status=400)

            # 验证商品是否存在
            try:
                goods = Goods.objects.get(id=goods_id)
            except Goods.DoesNotExist:
                return JsonResponse({
                    "status": "400",
                    "msg": "商品不存在"
                }, status=400)

            # 验证商品状态是否允许购买
            if goods.status != Goods.STATUS_ON:
                return JsonResponse({
                    "status": "400",
                    "msg": "商品当前不可购买"
                }, status=400)

            # 验证价格是否一致
            if float(goods.price) != price:
                return JsonResponse({
                    "status": "400",
                    "msg": "价格不匹配"
                }, status=400)

            # 验证卖家不是买家本人
            if buyer_id == seller_id:
                return JsonResponse({
                    "status": "400",
                    "msg": "不能购买自己的商品"
                }, status=400)

            # 创建订单记录 - 使用前端传递的数据
            # create_time会由Django模型自动设置为当前时间
            order = Order.objects.create(
                goods_id=goods_id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                price=price,
                status=order_status  # 使用正确的变量名
            )

            # 打印生成的订单内容
            print(f"用户提交了订单。。。。:")
            return JsonResponse({
                "status": "200",
                "msg": "购买请求已提交！",
                "order_id": order.id,
                "order_info": {
                "id": order.id,
                "goods_id": order.goods_id,
                "buyer_id": order.buyer_id,
                "seller_id": order.seller_id,
                "price": float(order.price),
                "status": order.status,
                "create_time": order.create_time.isoformat(),
                "image": image,
                "title": title
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "status": "400",
                "msg": "JSON解析错误"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": "500",
                "msg": f"服务器内部错误: {str(e)}"
            }, status=500)




#支付宝付款
class PaySuccess(View):
    def get(self, request):
        order_id = request.GET.get("order_id")
        print(f"用户正在付款中。。。。")

        # 如果没有order_id参数，返回错误
        if not order_id:
            return JsonResponse({'status': '400', 'msg': '订单ID不能为空'})

        # 检查order_id是否为数字
        try:
            order_id = int(order_id)
        except ValueError:
            return JsonResponse({'status': '400', 'msg': '订单ID格式错误'})

        # 订单校验
        try:
            order = Order.objects.get(id=order_id, status=Order.STATUS_UNPAY)
        except Order.DoesNotExist:
            return JsonResponse({'status': '400', 'msg': '订单信息错误'})

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "settlement/keys/app_private_key.pem")
        ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "settlement/keys/alipay_public_key.pem")

        # 读取密钥文件内容
        with open(APP_PRIVATE_KEY_PATH, 'r', encoding='utf-8') as f:
            app_private_key_string = f.read()

        with open(ALIPAY_PUBLIC_KEY_PATH, 'r', encoding='utf-8') as f:
            alipay_public_key_string = f.read()

        # 创建alipay对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL if hasattr(settings, 'ALIPAY_NOTIFY_URL') else None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 调用支付宝接口，获取支付页面
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=str(order_id),
            total_amount=str(order.price),
            subject="阿烽二手优品%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        # 返回支付链接的JSON
        alipay_url =settings.ALIPAY_URL+'?'+order_string
        return JsonResponse({
            'status': '200',
            'msg': '获取支付链接成功',
            'alipay_url': alipay_url,
            'order_id': order_id
        })

    def post(self, request):
        return HttpResponse('post')

#支付宝回调
class SettlementSuccessView(View):

    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        params=dict(request.GET)
        logger = logging.getLogger(__name__)
        logger.info(f"支付宝回传的所有参数param:{params}")

        # 遍历所有参数，取列表第一个元素转为字符串
        for key, value in params.items():
            if isinstance(value, list) and len(value) > 0:
                params[key] = value[0]
            # 提取签名并从参数中移除（验签需要）
        signature = params.pop('sign', None)
        if not signature:
            return JsonResponse({'status': '400', 'msg': '签名缺失'})

        # 验证支付宝签名以确保安全性
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "settlement/keys/alipay_public_key.pem")
        APP_PRIVATE_KEY = os.path.join(BASE_DIR, "settlement/keys/app_private_key.pem")

        with open(ALIPAY_PUBLIC_KEY_PATH, 'r', encoding='utf-8') as f:
            alipay_public_key_string = f.read()

        with open(APP_PRIVATE_KEY, 'r', encoding='utf-8') as f:
            app_private_key_string = f.read()


        # 创建alipay对象用于验签，验证支付宝回调签名时只需支付宝公钥
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string=clean_key(app_private_key_string, key_type="PRIVATE"),
            alipay_public_key_string=clean_key(alipay_public_key_string, key_type="PUBLIC"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        # 验证签名
        try:
            verify_result = alipay.verify(params, signature)
            if verify_result:
                # 签名验证成功，处理支付结果
                out_trade_no = params.get('out_trade_no') #订单号

                if out_trade_no:
                    try:
                        order_id=int(params.get('out_trade_no'))
                        order = Order.objects.get(id=order_id)

                            # 检查当前订单状态，避免重复更新
                        if order.status == Order.STATUS_UNPAY:
                            order.status = Order.STATUS_PAY
                            order.save()

                            # 同时更新对应商品的状态为已售出
                            if order.goods.status != Goods.STATUS_SOLD:  # 避免重复更新
                                order.goods.status = Goods.STATUS_SOLD
                                order.goods.save()
                        #响应成功跳转回前端支付成功页面
                        # 构建查询参数
                        context = {
                            'order_id': order_id,
                            'price': str(order.price),  # 转换为字符串
                            'time': order.create_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
                        }

                        # 编码查询参数
                        query_string = urlencode(context)
                        print("用户付款成功")
                        #http://69mdjw853446.vicp.fun/paysuccess
                        return HttpResponseRedirect(f"{settings.FRONTEND_BASE_URL}/paysuccess?{query_string}")
                    except (Order.DoesNotExist, ValueError):
                        return JsonResponse({
                            'status': '400',
                            'msg': '订单信息错误'
                        })
                else:
                    return JsonResponse({
                        'status': '400',
                        'msg': '非法请求'
                    })
            else:
                # 签名验证失败
                return JsonResponse({
                    'status': '400',
                    'msg': '签名验证失败'
                })
        except Exception as e:
            # 验签过程出现异常
            print(f"验签过程出错: {str(e)}")  # 添加调试信息
            return JsonResponse({
                'status': '500',
                'msg': f'验签过程出错: {str(e)}'
            })
