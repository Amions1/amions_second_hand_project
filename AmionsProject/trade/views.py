import json
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging
import os
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from trade.models import Goods, User ,GoodsCategory

#获取一级菜单
class GoodsMenuView(View):
    # 函数名固定，会通过函数名来确认请求方式
    def get(self, request):
        # 获取商品分类表所有数据
        goods_category = GoodsCategory.objects.all()

        results_list = []
        # 手动序列化id,name和parent_id字段
        for gc in goods_category:
            results_list.append({
                "id": gc.id,
                "name": gc.name,
                "parent_id": gc.parent_id
            })

        results_json = {
            "status": "200",
            "goods_category": results_list
        }

        print(print("用户正在浏览主页面"))
        return HttpResponse(
            # ensure_ascii=False防止乱码
            json.dumps(results_json, indent=4, ensure_ascii=False),
            # 指定响应类型和编码
            content_type="application/json; charset=utf-8"
        )

    # 获取前端传递过来的发布页面的数据
    def post(self, request):
        user_id = request.POST.get("user_id")

        if not user_id:
            return JsonResponse({
                'status': '400',
                'msg': '缺少用户ID参数'
            })

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

        # 获取用户对象
        try:
            validated_user = User.objects.get(id=user_id)
            print(f"🎯 认证用户: {validated_user.nickname} (ID: {validated_user.id})")
        except User.DoesNotExist:
            print(f"❌ 数据库中未找到用户，ID: {user_id}")
            return JsonResponse({
                'status': '401',
                'msg': f'认证失败: 用户不存在 (ID: {user_id})'
            })

        logger = logging.getLogger(__name__)
        logger.info("前端发布页面进入publish的post请求中")
        print("🚀 用户认证成功，开始处理商品发布...", flush=True)

        # 使用 request.POST.get() 来获取表单数据，使用 request.FILES.get() 来获取上传的文件
        title = request.POST.get('title')
        category_id = request.POST.get('category_id')
        price = request.POST.get('price')
        quality = request.POST.get('quality')
        status = request.POST.get('status', '1')
        publisher_id = user_id
        image = request.FILES.get('image')
        details = request.POST.get('details')
        if not details:
            details = "卖家啥也没写哦。。。。。。"

        if not all([title, category_id, price, quality, details]):  # details允许为空
            return JsonResponse({
                'status': '400',
                'msg': '缺少必要参数'
            })

        # 转换数据类型
        try:
            category_id = int(category_id)
            price = float(price)
            quality = int(quality)
            status = int(status)
            details = str(details)
        except ValueError:
            return JsonResponse({
                'status': '400',
                'msg': '参数类型错误'
            })

        # 使用已验证的用户作为发布者
        publisher = validated_user

        # 处理图片上传（在所有验证通过后）
        image_path = None  # 初始化为None
        if image:
            # 创建上传目录
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
            os.makedirs(upload_dir, exist_ok=True)

            # 生成唯一文件名
            file_extension = os.path.splitext(image.name)[1]
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
            filepath = os.path.join(upload_dir, filename)

            # 保存文件
            with open(filepath, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # 生成数据库中存储的相对路径
            image_path = os.path.join('product_images', filename).replace('\\', '/')

        # 创建商品对象并保存到数据库
        goods = Goods(
            title=title,
            category_id=category_id,
            price=price,
            quality=quality,
            publisher=publisher,
            status=status,
            details=details
        )

        # 如果有上传图片，添加到商品
        if image_path:
            goods.image = image_path

        # 保存到数据库 - id 会自动递增，create_time 会自动设置为当前时间
        goods.save()

        # 清除可能的缓存，确保新发布的商品能够被立即获取
        # 清除与该分类相关的任何可能的缓存
        cache.delete(f'goods_category_{category_id}')
        print("用户发布了商品！")
        print(
            f"商品信息: {title}, {category_id}, {price}, {quality}, {status}, 发布者id: {publisher_id}, 图片路径: {image_path},商品详情:{details}")

        return JsonResponse({
            'status': '200',
            'msg': '商品发布成功',
            'goods_id': goods.id,  # 返回新创建的商品ID
            'image_path': image_path
        })


#获取要所有商品列表(前端Echarts需要)
class GoodsListView(View):
    def get(self, request):
        try:
            # 直接从MySQL查询商品数据，关联商品分类表
            goods_list = Goods.objects.select_related('publisher').all()
            
            # 获取所有分类信息用于名称映射
            categories = {cat.id: cat.name for cat in GoodsCategory.objects.all()}
            
            # 序列化商品数据
            results = []
            for goods in goods_list:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")
                
                results.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "category_name": categories.get(goods.category_id, "未知分类"),
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "image": image_url,
                    "publisher_id": goods.publisher_id,
                    "publisher_nickname": goods.publisher.nickname,
                    "details": goods.details,
                    "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # 构造返回结果
            results_json = {
                "status": "200",
                "msg": "success",
                "data": results,
                "count": len(results)
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            
        except Exception as e:
            logging.error(f"获取商品列表失败: {str(e)}")
            results_json = {
                "status": "500",
                "msg": f"服务器错误: {str(e)}",
                "data": [],
                "count": 0
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )



def cache_all_goods_data():
    """
    将所有商品数据缓存到Redis中
    缓存键：all_goods_data
    过期时间：24小时
    """
    try:
        # 查询所有商品数据
        all_goods = Goods.objects.select_related('publisher').all()
        
        # 序列化商品数据
        goods_data = []
        for goods in all_goods:
            image_url = ""
            if goods.image:
                image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")
            
            goods_data.append({
                "id": goods.id,
                "title": goods.title,
                "price": float(goods.price),
                "quality": goods.quality,
                "status": goods.status,
                "image": image_url,
                "publisher_id": goods.publisher_id,
                "publisher_nickname": goods.publisher.nickname,
                "details": goods.details,
                "category_id": goods.category_id,
                "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 转换为JSON格式的字符串数组
        goods_json = json.dumps(goods_data, ensure_ascii=False)
        
        # 存入Redis，过期时间2小时(7200秒)
        cache.set('all_goods_data', goods_json, timeout=7200)
        logging.info(f"成功缓存 {len(goods_data)} 条商品数据到Redis (JSON格式)")
        
    except Exception as e:
        logging.error(f"缓存商品数据失败: {str(e)}")

def get_goods_from_cache_or_db():
    """
    从Redis获取商品数据，如果没有则从数据库查询并缓存
    """
    # 先尝试从Redis获取
    cached_goods_json = cache.get('all_goods_data')
    
    if cached_goods_json is not None:
        logging.info("从Redis缓存获取商品数据")
        # 将JSON字符串转换回Python对象
        return json.loads(cached_goods_json)
    else:
        logging.info("Redis缓存未命中，从数据库查询并缓存")
        cache_all_goods_data()
        cached_goods_json = cache.get('all_goods_data')
        return json.loads(cached_goods_json) if cached_goods_json else []

# 监听Goods模型的增删改操作，自动清除Redis缓存
@receiver(post_save, sender=Goods)
def clear_goods_cache_on_save(sender, instance, **kwargs):
    """
    当Goods表发生新增或修改时，清除Redis缓存
    """
    cache.delete('all_goods_data')
    logging.info(f"Goods表发生变化，已清除Redis缓存 - 商品ID: {instance.id}")

@receiver(post_delete, sender=Goods)
def clear_goods_cache_on_delete(sender, instance, **kwargs):
    """
    当Goods表发生删除时，清除Redis缓存
    """
    cache.delete('all_goods_data')
    logging.info(f"Goods表发生删除，已清除Redis缓存 - 商品ID: {instance.id}")

#显示二级菜单，也就是具体的goods
class GoodsSubMenu(View):
    def get(self, request):

        # 1. 获取前端传入的一级分类ID（容错处理）
        param_id = request.GET.get('id')
        if not param_id:
            results_json = {
                "status": "400",
                "msg": "缺少分类ID参数",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        # 2. 从缓存获取所有商品数据
        try:
            all_goods_data = get_goods_from_cache_or_db()
            
            # 3. 根据分类ID过滤商品
            filtered_goods = [
                goods for goods in all_goods_data 
                if goods['category_id'] == int(param_id)
            ]
            
            # 4. 构造返回结果
            results_json = {
                "status": "200",
                "msg": "success",
                "goods_list": filtered_goods
            }

            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            
        except ValueError:
            results_json = {
                "status": "400",
                "msg": "分类ID必须是数字",
                "goods_list": []
            }
            return HttpResponse(
                json.dumps(results_json, indent=4, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

#搜索
class Search(View):
    def get(self,request):
        keyword=request.GET.get("keyword")
        print(f"用户的搜索关键词：{keyword}")

        try:
            # 非空判断
            if not keyword:
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少参数',
                    'data': []
                })

            # 对goods表进行模糊查询
            goods_list = Goods.objects.filter(
                Q(title__icontains=keyword) |
                Q(details__icontains=keyword)
            )

            # 序列化查询结果
            results = []
            for goods in goods_list:
                # 构造完整的图片URL
                image_url = ""
                if goods.image:
                    from django.conf import settings
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")

                results.append({
                    "id": goods.id,
                    "title": goods.title,
                    "price": float(goods.price),
                    "quality": goods.quality,
                    "status": goods.status,
                    "image": image_url,
                    "publisher_id": goods.publisher_id,
                    "publisher_nickname": goods.publisher.nickname,
                    "details": goods.details
                })


            return JsonResponse({
                'status': '200',
                'msg': '查询成功',
                'data': results
            })

        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f'{str(e)}',
                'data':[]
            })


