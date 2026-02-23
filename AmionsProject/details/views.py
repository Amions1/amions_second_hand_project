import logging
from django.http import HttpResponse, JsonResponse
from django.views import View
from trade.models import Goods
from trade.models import UserWish, User, Goods
class userDetails(View):
    def get(self,request,id):

        logger=logging.getLogger(__name__)
        logger.info("进入details的get请求")

        try:
            # 使用JOIN查询获取商品信息和关联的发布者信息
            goods = Goods.objects.select_related('publisher').get(id=id)

            # 构造响应数据
            goods_detail_data = {
                'id': goods.id,
                'title': goods.title,
                'price': float(goods.price),
                'image': goods.image.url if goods.image else '',
                'status': goods.status,
                'create_time': goods.create_time.strftime('%Y-%m-%d %H:%M') if hasattr(goods, 'create_time') else '',
                'details': goods.details or '',
                'publisher_id': goods.publisher_id,
                'publisher_nickname': goods.publisher.nickname if goods.publisher else '未知用户'
            }

            print("用户正在查看商品详情")
            return JsonResponse({
                'status': '200',
                'msg': '获取商品详情成功',
                'goods_detail': goods_detail_data
            })

        except Goods.DoesNotExist:
            return JsonResponse({
                'status': '400',
                'msg': '商品不存在'
            })
        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f'服务器错误: {str(e)}'
            })

    def post(self,request):
        return HttpResponse({"请用get请求访问!"}, status=405)

class CheckIsWished(View):
    def get(self,request,user_id, goods_id):
        try:
            # 验证参数
            if not user_id or not goods_id:
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少必要参数',
                    'is_favorited': False
                })
            
            # 尝试查询用户是否收藏了该商品
            try:
                user = User.objects.get(id=int(user_id))
                goods = Goods.objects.get(id=int(goods_id))
            except (User.DoesNotExist, Goods.DoesNotExist):
                return JsonResponse({
                    'status': '404',
                    'msg': '用户或商品不存在',
                    'is_favorited': False
                })
            except ValueError:
                return JsonResponse({
                    'status': '400',
                    'msg': '参数格式错误',
                    'is_favorited': False
                })
            
            # 检查是否存在收藏记录
            try:
                UserWish.objects.get(user=user, goods=goods)
                is_favorited = True
                msg = '商品已收藏'
            except UserWish.DoesNotExist:
                is_favorited = False
                msg = '商品未收藏'
            
            return JsonResponse({
                'status': '200',
                'msg': msg,
                'is_favorited': is_favorited
            })
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"检查收藏状态时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': f'服务器内部错误: {str(e)}',
                'is_favorited': False
            })


class AddUserWish(View):
    def post(self, request):
        try:
            # 从POST数据中获取参数
            user_id = request.POST.get('user_id')
            goods_id = request.POST.get('goods_id')

            print(f"user_id:{user_id},goods_id:{goods_id}")
            
            # 验证必要参数
            if not user_id or not goods_id:
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少必要参数'
                })
            
            # 验证用户和商品是否存在
            try:
                user = User.objects.get(id=int(user_id))
                goods = Goods.objects.get(id=int(goods_id))
            except (User.DoesNotExist, Goods.DoesNotExist):
                return JsonResponse({
                    'status': '404',
                    'msg': '用户或商品不存在'
                })
            except ValueError:
                return JsonResponse({
                    'status': '400',
                    'msg': '参数格式错误'
                })
            
            # 检查用户是否试图收藏自己的商品
            if goods.publisher_id == user.id:
                return JsonResponse({
                    'status': '400',
                    'msg': '不能收藏自己发布的商品'
                })
            
            # 检查是否已经收藏
            if UserWish.objects.filter(user=user, goods=goods).exists():
                return JsonResponse({
                    'status': '409',
                    'msg': '该商品已在您的收藏中'
                })
            
            # 创建收藏记录 Django会自动为create_time字段填充当前的时间戳
            try:
                user_wish = UserWish.objects.create(
                    user=user,
                    goods=goods
                )
                
                logger = logging.getLogger(__name__)
                logger.info(f"用户 {user.nickname} 收藏了商品 {goods.title}")
                
                return JsonResponse({
                    'status': '201',
                    'msg': '收藏成功',
                    'data': {
                        'user_wish_id': user_wish.id,
                        'user_id': user.id,
                        'goods_id': goods.id,
                        'create_time': user_wish.create_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
                
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"创建收藏记录时发生错误: {str(e)}")
                return JsonResponse({
                    'status': '500',
                    'msg': f'服务器内部错误: {str(e)}'
                })
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"添加收藏时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': f'服务器内部错误: {str(e)}'
            })