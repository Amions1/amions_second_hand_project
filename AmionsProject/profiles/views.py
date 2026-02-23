import json
import logging

from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.db import connection
from django.db.models import Subquery, OuterRef, Exists
from django.http import HttpResponse, JsonResponse
from django.views import View
from trade.models import Goods, User, Order, UserWish  # 导入Goods和User模型
from django.conf import settings

#获取我发布的商品
class publishedGoods(View):
    def get(self,request):
        logger = logging.getLogger(__name__)
        logger.info("个人信息页显示已发布的信息，进入后端get请求中")
        user_id = request.GET.get('user_id')
        logger.info(f"user_id为{user_id}")

        # 从请求头获取token并验证格式
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f"请求头中获取的token:{auth_header}")

        # 1. 检查认证头格式
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': '401',
                'msg': '认证失败: 无效的认证头格式'
            })
        # 提取token
        token = auth_header[7:]  # 移除'Bearer '
        print(f"提取的JWT令牌: {token[:20]}...")

        # 如果Redis中没有找到对应的令牌键，返回401
        if not cache.get(f"jwt_token_{user_id}"):
            print(f"❌ Redis中未找到对应的jwt_token_{{用户ID}}键，认证失败")
            return JsonResponse({
                'status': '401',
                'msg': '认证失败: 令牌无效或已过期'
            })

        print(f"✅ 认证通过：JWT格式正确且Redis中存在对应令牌键")
        
        # 检查是否提供了user_id
        if not user_id:
            results_json = {
                "status": "400",
                "msg": "缺少用户ID参数1",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        
        try:
            # 验证用户是否存在
            user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            results_json = {
                "status": "404",
                "msg": "用户不存在",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        except ValueError:
            results_json = {
                "status": "400",
                "msg": "用户ID必须是数字",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        
        try:
            # 查询该用户发布的所有商品
            user_goods = Goods.objects.filter(publisher=user,status=Goods.STATUS_ON)
            
            # 序列化商品数据
            goods_list = []
            for goods in user_goods:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")
                
                goods_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "image": image_url,  # 返回完整的图片URL
                    "publisher_id": goods.publisher.id,
                    "publisher_nickname": goods.publisher.nickname  # 添加发布者昵称
                })

            print("用户正在查看个人信息页")
            results_json = {
                "status": "200",
                "msg": "获取用户发布商品成功",
                "goods_count": len(goods_list),  # 添加商品数量
                "goods_list": goods_list
            }
            
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            
        except Exception as e:
            logger.error(f"查询用户商品时发生错误: {str(e)}")
            results_json = {
                "status": "500",
                "msg": "服务器内部错误",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )


    def post(self,request):
        return HttpResponse("post")
class UpdateNickname(View):
    def get(self, request):
        logger = logging.getLogger(__name__)
        logger.info("获取用户昵称信息或检查昵称变更，进入后端get请求中")
        user_id = request.GET.get('user_id')
        new_nickname = request.GET.get('new_nickname')
        
        if not user_id:
            return JsonResponse({
                'status': '400',
                'msg': '缺少用户ID参数2',
                'nickname': '',
                'is_same': False
            })
        
        try:
            user = User.objects.get(id=int(user_id))
            
            # 如果提供了新昵称，检查是否与当前昵称相同
            if new_nickname is not None:
                is_same = user.nickname.strip() == new_nickname.strip()
                return JsonResponse({
                    'status': '200',
                    'msg': '检查昵称完成',
                    'nickname': user.nickname,
                    'is_same': is_same
                })
            else:
                # 获取当前昵称
                return JsonResponse({
                    'status': '200',
                    'msg': '获取用户昵称成功',
                    'nickname': user.nickname,
                    'is_same': False
                })
        except User.DoesNotExist:
            return JsonResponse({
                'status': '404',
                'msg': '用户不存在',
                'nickname': '',
                'is_same': False
            })
        except ValueError:
            return JsonResponse({
                'status': '400',
                'msg': '用户ID必须是数字',
                'nickname': '',
                'is_same': False
            })

    def post(self, request):
        logger = logging.getLogger(__name__)
        logger.info("修改用户昵称，进入后端post请求中")
        
        user_id = request.POST.get('user_id')
        new_nickname = request.POST.get('nickname')
        
        # 验证参数
        if not user_id or not new_nickname:
            return JsonResponse({
                'status': '400',
                'msg': '缺少必要参数（用户ID或新昵称）'
            })
        
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({
                'status': '400',
                'msg': '用户ID必须是数字'
            })
        
        # 检查新昵称长度
        if len(new_nickname.strip()) == 0:
            return JsonResponse({
                'status': '400',
                'msg': '昵称不能为空'
            })
        
        if len(new_nickname) > 32:  # 根据User模型中nickname字段的最大长度
            return JsonResponse({
                'status': '400',
                'msg': '昵称长度不能超过32个字符'
            })
        
        try:
            # 查找用户
            user = User.objects.get(id=user_id)
            
            # 检查新昵称是否与当前昵称相同
            if user.nickname.strip() == new_nickname.strip():
                return JsonResponse({
                    'status': '400',
                    'msg': '新昵称与当前昵称相同，请输入不同的昵称'
                })
            
            # 更新昵称
            old_nickname = user.nickname
            user.nickname = new_nickname.strip()
            user.save()
            
            print(f"用户昵称已从 '{old_nickname}' 更新为 '{new_nickname}'")
            
            return JsonResponse({
                'status': '200',
                'msg': '昵称更新成功',
                'old_nickname': old_nickname,
                'new_nickname': new_nickname
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'status': '404',
                'msg': '用户不存在'
            })
        except Exception as e:
            logger.error(f"更新用户昵称时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': '服务器内部错误'
            })

#获取我买到的商品
class BoughtView(View):
    def get(self, request):
        buyer_id = request.GET.get('buyer_id')
        logger = logging.getLogger(__name__)
        logger.info(f"buyer_id={buyer_id}")

        # 检查是否提供了buyer_id
        if not buyer_id:
            results_json = {
                "status": "400",
                "msg": "缺少买家ID参数",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        try:
            # 验证用户是否存在
            buyer = User.objects.get(id=int(buyer_id))
        except User.DoesNotExist:
            results_json = {
                "status": "404",
                "msg": "买家不存在",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        except ValueError:
            results_json = {
                "status": "400",
                "msg": "买家ID必须是数字",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        try:

            # 查询买家购买的商品列表
            goods_ids = Order.objects.filter(
                buyer_id=int(buyer_id),
                status=Order.STATUS_PAY
            ).values_list('goods_id', flat=True)
            goods_list = Goods.objects.filter(id__in=goods_ids)

            # 使用更安全的方式打印结果
            if goods_list.exists():
                print(f"用户查询到购买了 {goods_list.count()} 个商品")
                for idx, goods in enumerate(goods_list):
                    print(f"商品 {idx + 1}: ID={goods.id}, 标题={goods.title},卖家ID:{goods.publisher_id}",)
            else:
                print("用户未查询到商品")


            # 序列化商品数据
            bought_goods_list = []
            for goods in goods_list:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")


                    # 安全地获取发布者信息
                publisher_id = goods.publisher.id if goods.publisher else None
                publisher_nickname = goods.publisher.nickname if goods.publisher else "未知发布者"


                bought_goods_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "image": image_url,  # 返回完整的图片URL
                    "publisher_id": publisher_id,
                    "publisher_nickname": publisher_nickname  # 添加发布者昵称
                })

            print("用户正在查看购买到的商品")
            results_json = {
                "status": "200",
                "msg": "获取用户购买的商品列表成功",
                "goods_count": len(goods_list),  # 添加商品数量
                "data": bought_goods_list
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        except Exception as e:
            results_json = {
                "status": "500",
                "msg": e,
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
#获取已卖出的的商品
class SoldView(View):
    def get(self, request):
        seller_id = request.GET.get('seller_id')
        logger = logging.getLogger(__name__)
        logger.info(f"seller_id={seller_id}")

        # 检查是否提供了seller_id
        if not seller_id:
            results_json = {
                "status": "400",
                "msg": "缺少卖家ID参数",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        try:
            # 验证用户是否存在
            seller = User.objects.get(id=int(seller_id))
        except User.DoesNotExist:
            results_json = {
                "status": "404",
                "msg": "卖家不存在",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        except ValueError:
            results_json = {
                "status": "400",
                "msg": "卖家ID必须是数字",
                "data": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        try:

            # 查询卖家售卖了的商品列表
            goods_ids = Order.objects.filter(
                seller_id=int(seller_id),
                status=Order.STATUS_PAY
            ).values_list('goods_id', flat=True)
            goods_list = Goods.objects.filter(id__in=goods_ids)

            # 使用更安全的方式打印结果
            if goods_list.exists():
                print(f"用户查询到购买了 {goods_list.count()} 个商品")
                for idx, goods in enumerate(goods_list):
                    print(f"商品 {idx + 1}: ID={goods.id}, 标题={goods.title}")
            else:
                print("用户未查询到商品")


            # 序列化商品数据
            sold_goods_list = []
            for goods in goods_list:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")

                # 安全地获取发布者信息
                sold_goods_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "image": image_url,  # 返回完整的图片URL

                })

            print("用户正在查询售卖的商品")
            results_json = {
                "status": "200",
                "msg": "获取卖家售卖的商品列表成功",
                "goods_count": len(goods_list),  # 添加商品数量
                "data": sold_goods_list
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        except Exception as e:
            results_json = {
                "status": "500",
                "msg": e,
                "bought_goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

class ChangePassword(View):

    def post(self,request):
        phone = request.POST.get("phone")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        # 验证参数
        if not phone or not current_password or not new_password:
            return JsonResponse({
                'status': '400',
                'msg': '缺少必要参数'
            })

        # 验证手机号格式
        if len(phone) != 11 or not phone.isdigit():
            return JsonResponse({
                'status': '400',
                'msg': '手机号格式不正确'
            })

        # 检查新密码长度
        if len(new_password) < 6 or len(new_password) > 20:
            return JsonResponse({
                'status': '400',
                'msg': '新密码长度应在6-20位之间'
            })

        try:
            # 查找用户
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return JsonResponse({
                'status': '404',
                'msg': '用户不存在'
            })

        # 验证当前密码是否正确
        if not check_password(current_password,user.password):
            return JsonResponse({
                'status': '400',
                'msg': '当前密码错误'
            })

        # 检查新密码是否与当前密码相同
        if new_password==user.password:
            return JsonResponse({
                'status': '400',
                'msg': '新密码不能与当前密码相同'
            })

        # 更新密码
        user.password = make_password(new_password)
        user.save()

        print(f"用户 {user.nickname} 密码修改成功")
        
        return JsonResponse({
            'status': '200',
            'msg': '密码修改成功'
        })

#获取已下架的商品
class OffShelfView(View):
    def get(self,request,user_id):
        logger = logging.getLogger(__name__)
        logger.info("获取用户已下架的商品，进入后端get请求中")
        logger.info(f"user_id为{user_id}")
        
        # 检查是否提供了user_id
        if not user_id:
            return HttpResponse({
                "status": "400",
                "msg": "缺少用户ID参数",
                "data": []
            })
        
        try:
            # 验证用户是否存在
            user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return HttpResponse({
                "status": "400",
                "msg": "该用户不存在",
                "data": []
            })
        
        try:
            # 查询该用户已下架的所有商品（status=3和4）
            off_shelf_goods = Goods.objects.filter(
                publisher=user,
                status__in=[Goods.STATUS_OFF, Goods.STATUS_FORCE_OFF]
            )

            # 序列化商品数据
            goods_list = []
            for goods in off_shelf_goods:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")

                goods_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "image": image_url,  # 返回完整的图片URL
                    "publisher_id": goods.publisher.id,
                    "publisher_nickname": goods.publisher.nickname,  # 添加发布者昵称
                    "details": goods.details
                })

            print(f"用户 {user.nickname} 查询到 {len(goods_list)} 个已下架商品")
            results_json = {
                "status": "200",
                "msg": "获取用户已下架商品成功",
                "goods_count": len(goods_list),  # 添加商品数量
                "data": goods_list
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        except Exception as e:
            return HttpResponse({
                "status": "500",
                "msg": f"服务器内部错误 {str(e)}",
                "data": []
            })


    def post(self, request):
        return HttpResponse({'error':'请用get请求访问'},status=405)

#获取我想要的商品
class WishGoodsView(View):
    def get(self, request, user_id):
        logger = logging.getLogger(__name__)
        logger.info("获取用户收藏夹中的商品，进入后端get请求中")
        logger.info(f"user_id为{user_id}")

        # 检查是否提供了user_id
        if not user_id:
            return JsonResponse({
                "status": "400",
                "msg": "缺少用户ID参数",
                "data": []
            })

        try:
            # 验证用户是否存在
            user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return JsonResponse({
                "status": "404",
                "msg": "用户不存在",
                "data": []
            })
        except ValueError:
            return JsonResponse({
                "status": "400",
                "msg": "用户ID必须是数字",
                "data": []
            })

        try:
            # 查询该用户收藏夹的所有商品，使用select_related优化查询
            wish_items = UserWish.objects.select_related('goods', 'goods__publisher').filter(
                user=user,
            )

            # 序列化商品数据
            goods_list = []
            for wish_item in wish_items:
                goods = wish_item.goods
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")

                goods_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "image": image_url,  # 返回完整的图片URL
                    "publisher_id": goods.publisher.id,
                    "publisher_nickname": goods.publisher.nickname,  # 添加发布者昵称
                    "details": goods.details,
                    "wish_time": wish_item.create_time.strftime("%Y-%m-%d %H:%M:%S")  # 收藏时间
                })

            print(f"用户 {user.nickname} 查询到收藏夹中 {len(goods_list)} 个商品")
            results_json = {
                "status": "200",
                "msg": "获取用户收藏夹商品成功",
                "goods_count": len(goods_list),  # 添加商品数量
                "data": goods_list
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        except Exception as e:
            logger.error(f"查询用户收藏夹商品时发生错误: {str(e)}")
            return JsonResponse({
                "status": "500",
                "msg": "服务器内部错误",
                "data": []
            })

    def post(self, request):
        return HttpResponse({'error': '请用get请求访问'}, status=405)

#上架/下架商品
class TakeDownOrPutUpView(View):
    def post(self,request):
        user_id=request.POST.get("user_id")
        goods_id=request.POST.get("goods_id")
        current_status=request.POST.get("current_status")

        try:
            if not user_id or not goods_id or not current_status:
                return JsonResponse({
                    'status':'400',
                    'msg':'缺少必要参数',
                    'data':[]
                })

            try:
                # 验证用户和商品是否存在
                user = User.objects.get(id=int(user_id))
                goods = Goods.objects.get(id=int(goods_id))
                current_status = int(current_status)
            except (User.DoesNotExist, Goods.DoesNotExist):
                return JsonResponse({
                    "status": "404",
                    "msg": "用户或商品不存在",
                    "data": []
                })
            except ValueError:
                return JsonResponse({
                    'status': '400',
                    'msg': '参数格式错误',
                    'data': []
                })

            # 根据current_status决定操作类型
            if current_status == Goods.STATUS_ON:  # 在售状态(1) - 执行下架
                return self._take_down_goods(user, goods)
            elif current_status == Goods.STATUS_OFF:  # 已下架状态(3) - 执行上架
                return self._put_up_goods(user, goods)
            elif current_status == Goods.STATUS_FORCE_OFF:  # 强制下架状态(4) - 无法上架
                return JsonResponse({
                    'status': '400',
                    'msg': '该商品已被强制下架，请联系管理员',
                    'data': []
                })
            elif current_status == Goods.STATUS_SOLD:  # 已卖出状态(2) - 无法操作
                return JsonResponse({
                    'status': '400',
                    'msg': '商品已卖出',
                    'data': []
                })
            else:
                return JsonResponse({
                    'status': '400',
                    'msg': '未知的商品状态',
                    'data': []
                })

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"商品上下架操作时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': f'服务器内部错误: {str(e)}',
                'data': []
            })

    def _take_down_goods(self, user, goods):
        """执行下架操作"""
        # 检查商品是否已经是下架状态
        if goods.status in [Goods.STATUS_OFF, Goods.STATUS_FORCE_OFF]:
            return JsonResponse({
                'status': '400',
                'msg': '商品已经处于下架状态',
                'data': []
            })

        # 检查用户是否有权限操作该商品
        is_self_operation = goods.publisher.id == user.id

        if not is_self_operation:
            # 检查操作者角色是否高于发布者
            if user.role <= goods.publisher.role:
                return JsonResponse({
                    'status': '403',
                    'msg': '权限不足',
                    'data': []
                })

            # 高权限用户下架 - 设置为强制下架
            goods.status = Goods.STATUS_FORCE_OFF
            print(f"管理员 {user.nickname}(角色:{user.get_role_display()}) 强制下架了用户 {goods.publisher.nickname} 的商品: {goods.title}")
        else:
            # 用户自己下架 - 设置为普通下架
            goods.status = Goods.STATUS_OFF
            print(f"用户 {user.nickname} 自行下架了自己的商品: {goods.title}")

        goods.save()

        return JsonResponse({
            'status': '200',
            'msg': '商品下架成功',
            'data': {
                'goods_id': goods.id,
                'title': goods.title,
                'publisher_id': goods.publisher.id,
                'operator_id': user.id,
                'is_self_operation': is_self_operation,
                'new_status': goods.status
            }
        })

    def _put_up_goods(self, user, goods):
        """执行上架操作"""
        # 检查商品是否已经是上架状态
        if goods.status == Goods.STATUS_ON:
            return JsonResponse({
                'status': '400',
                'msg': '商品已经处于在售状态',
                'data': []
            })

        # 检查是否为强制下架状态
        if goods.status == Goods.STATUS_FORCE_OFF:
            return JsonResponse({
                'status': '403',
                'msg': '该商品已被强制下架，请联系管理员',
                'data': []
            })

        # 只有商品发布者可以将自己下架的商品重新上架
        if goods.publisher.id != user.id:
            return JsonResponse({
                'status': '403',
                'msg': '只有商品发布者才能上架自己下架的商品',
                'data': []
            })

        # 执行上架操作
        goods.status = Goods.STATUS_ON
        goods.save()

        print(f"用户 {user.nickname} 上架了自己之前下架的商品: {goods.title}")

        return JsonResponse({
            'status': '200',
            'msg': '商品上架成功',
            'data': {
                'goods_id': goods.id,
                'title': goods.title,
                'publisher_id': goods.publisher.id,
                'operator_id': user.id,
                'new_status': goods.status
            }
        })
    
    def get(self, request):
        return JsonResponse({'error': '请用post请求访问'}, status=405)
