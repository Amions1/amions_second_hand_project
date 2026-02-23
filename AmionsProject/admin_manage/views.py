import json

from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views import View
import json
from trade.models import User, Goods, GoodsCategory, Order
from django.core.cache import cache


#获取所有用户
class GetUsersView(View):
    def get(self,request):
        getUsers=User.objects.all()
        try:
            if not getUsers:
                return JsonResponse({
                    'status':'400',
                    'msg':'数据库为空',
                    'data':[]
                })

            results_list = []

            for user in getUsers:
                results_list.append({
                    "id": user.id,
                    "phone": user.phone,
                    "password": user.password,
                    "nickname":user.nickname,
                    "status":user.status,
                    "role":user.role
                })


            results_json = {
                "status": "200",
                'msg':'用户数据返回成功',
                "data": results_list
            }

            return HttpResponse(
                # ensure_ascii=False防止乱码
                json.dumps(results_json, indent=4, ensure_ascii=False),
                # 指定响应类型和编码
                content_type="application/json; charset=utf-8"
            )


        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f"服务器错误:{str(e)}",
                'data': []
            })


    def post(self, request):
        return HttpResponse({"error":'请用get请求访问'},status=405)
        pass

#获取所有商品
class GetGoodsView(View):
    def get(self,request):
        # 使用 select_related 优化查询，获取商品和发布者信息
        getGoods=Goods.objects.select_related('publisher').all()
        
        # 获取所有分类信息，用于后续匹配
        categories = {cat.id: cat.name for cat in GoodsCategory.objects.all()}
        try:
            if not getGoods:
                return JsonResponse({
                    'status':'400',
                    'msg':'数据库为空',
                    'data':[]
                })


            results_list = []

            for goods in getGoods:

                image_url = ""
                if goods.image:
                    # 直接使用 goods.image，因为它已经是相对于 MEDIA_ROOT 的路径
                    image_url = f"{settings.MEDIA_URL}{goods.image}".replace("\\", "/")

                results_list.append({
                    "id": goods.id,
                    "title": goods.title,
                    "category_id": goods.category_id,
                    "category_name": categories.get(goods.category_id, ''),  # 添加分类名称
                    "price": float(goods.price) ,
                    "quality": int(goods.quality) ,
                    "status": int(goods.status) ,
                    "create_time": goods.create_time.isoformat(),
                    "publisher_id": goods.publisher.id,
                    "publisher_nickname": goods.publisher.nickname,  # 添加发布者昵称
                    "image": image_url
                })


            results_json = {
                "status": "200",
                'msg':'商品数据返回成功',
                "data": results_list
            }


            return HttpResponse(
                # ensure_ascii=False防止乱码
                json.dumps(results_json, indent=4, ensure_ascii=False),
                # 指定响应类型和编码
                content_type="application/json; charset=utf-8"
            )


        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f"服务器错误:{str(e)}",
                'data': []
            })


    def post(self, request):
        return HttpResponse({"error":'请用get请求访问'},status=405)
        pass

#获取所有商品一级分类
class GetGoodsCategories(View):
    def get(self,request):
        # 按照 parent_id 从小到大排序
        get_categories=GoodsCategory.objects.all().order_by('parent_id')
        
        # 获取所有分类信息，用于查找父分类名称
        categories_dict = {cat.id: cat.name for cat in get_categories}
        try:
            if not get_categories:
                return JsonResponse({
                    'status':'400',
                    'msg':'数据库为空',
                    'data':[]
                })


            results_list = []
            # 手动序列化id,name,parent_id和parent_name字段
            for categories in get_categories:
                # 获取父分类名称，如果parent_id为0则返回提示信息
                parent_name = categories_dict.get(categories.parent_id, '(已为顶级分类)') if categories.parent_id != 0 else '(已为顶级分类)'
                
                results_list.append({
                    "id": categories.id,
                    "name": categories.name,
                    "parent_id": categories.parent_id,
                    "parent_name": parent_name  # 添加父分类名称
                })


            results_json = {
                "status": "200",
                'msg':'商品数据返回成功',
                "data": results_list
            }


            return HttpResponse(
                # ensure_ascii=False防止乱码
                json.dumps(results_json, indent=4, ensure_ascii=False),
                # 指定响应类型和编码
                content_type="application/json; charset=utf-8"
            )


        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f"服务器错误:{str(e)}",
                'data': []
            })


    def post(self, request):
        return HttpResponse({"error":'请用get请求访问'},status=405)


#获取所有订单信息
class GetOrders(View):
    def get(self,request):
        get_orders=Order.objects.all()
        try:
            if not get_orders:
                return JsonResponse({
                    'status':'400',
                    'msg':'数据库为空',
                    'data':[]
                })


            results_list = []
            # 手动序列化id,name和parent_id字段
            for orders in get_orders:
                results_list.append({
                    "id": orders.id,
                    "price":float(orders.price),
                    "status":orders.status,
                    "create_time":orders.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "goods_id":orders.goods_id,
                    "buyer_id":orders.buyer_id,
                    "seller_id":orders.seller_id
                })


            results_json = {
                "status": "200",
                'msg':'商品数据返回成功',
                "data": results_list
            }


            return HttpResponse(
                # ensure_ascii=False防止乱码
                json.dumps(results_json, indent=4, ensure_ascii=False),
                # 指定响应类型和编码
                content_type="application/json; charset=utf-8"
            )


        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f"服务器错误:{str(e)}",
                'data': []
            })


    def post(self, request):
        return HttpResponse({"error":'请用get请求访问'},status=405)

#封禁/解封用户
class BanUserView(View):
    def get(self, request):
        return HttpResponse({"error":'请用post请求访问'},status=405)

    def post(self, request):
        try:
            # 从JSON body获取数据
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            user_id = body_data.get('user_id')
            current_user_id = body_data.get('current_user_id')  # 获取操作管理员的ID

            if not user_id or not current_user_id:
                return JsonResponse({
                    'status':'400',
                    'msg':'缺少必要参数',
                })

            # 获取目标用户和管理员用户对象
            try:
                target_user = User.objects.get(id=user_id)
                current_user_id = User.objects.get(id=current_user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': '404',
                    'msg': '用户不存在'
                })

            # 权限检查：不能操作自己
            if target_user.id == current_user_id.id:
                return JsonResponse({
                    'status': '403',
                    'msg': '不能对自己进行操作'
                })

            # 权限检查：不能操作权限相同或更高的用户
            if target_user.role >= current_user_id.role:
                return JsonResponse({
                    'status': '403',
                    'msg': '权限不足，不能操作同级或更高级别的用户'
                })

            # 检查用户当前状态并进行相应操作
            if target_user.status == 1:  # 正常状态，执行封禁
                target_user.status = 0  # 0表示禁用状态
                target_user.save()
                #封禁时把用户jwt从redis中删除，实现实时的强制下线
                cache.delete(f"jwt_token_{user_id}")
                return JsonResponse({
                    'status': '200',
                    'msg': '封禁成功',
                })
            elif target_user.status == 0:  # 封禁状态，执行解封
                target_user.status = 1  # 1表示正常状态
                target_user.save()
                return JsonResponse({
                    'status': '200',
                    'msg': '解封成功',
                })
            else:
                return JsonResponse({
                    'status': '400',
                    'msg': '用户状态异常'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': '400',
                'msg': '请求数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'status':'500',
                'msg': f'服务器错误: {str(e)}',
            })

#修改商品名称
class ProductManageView(View):
    def put(self, request, product_id):
        try:
            # 检查请求体是否为空
            if not request.body:
                return JsonResponse({
                    'status': '400',
                    'msg': '请求体为空'
                })

            # 安全地解析JSON数据
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError as e:
                return JsonResponse({
                    'status': '400',
                    'msg': f'JSON格式错误: {str(e)}'
                })

            # 获取并验证价格参数
            new_price = data.get('price')
            if not new_price:
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少价格参数'
                })

            # 验证价格格式和范围
            try:
                price_decimal = float(new_price)
                if price_decimal <= 0:
                    return JsonResponse({
                        'status': '400',
                        'msg': '价格必须大于0'
                    })
                if price_decimal > 9999999:  # 设置合理的价格上限
                    return JsonResponse({
                        'status': '400',
                        'msg': '价格超出合理范围'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': '400',
                    'msg': '价格格式不正确'
                })

            # 查询商品并更新
            try:
                product = Goods.objects.get(id=product_id)

                # 检查商品状态，已卖出的商品不能修改价格
                if product.status == Goods.STATUS_SOLD:
                    return JsonResponse({
                        'status': '400',
                        'msg': '该商品已卖出'
                    })

                if product.status == Goods.STATUS_OFF or product.status==Goods.STATUS_FORCE_OFF:
                    return JsonResponse({
                        'status': '400',
                        'msg': '该商品已下架'
                    })

                # 检查新价格是否与当前价格相同
                if float(product.price) == price_decimal:
                    return JsonResponse({
                        'status': '200',
                        'msg': '价格未发生变化，无需更新'
                    })

                # 更新商品价格
                old_price = float(product.price)
                product.price = price_decimal
                product.save()

                print(f"商品 {product_id} 价格已从 {old_price} 更新为: {price_decimal}")

                return JsonResponse({
                    'status': '200',
                    'msg': f'商品价格更新成功，从 {old_price} 修改为 {price_decimal}'
                })
            except Goods.DoesNotExist:
                return JsonResponse({
                    'status': '404',
                    'msg': '商品不存在'
                })

        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f'更新失败: {str(e)}'
            })

#新增分类
class AddCategoryView(View):
    def post(self, request):
        try:
            name = request.POST.get('name')
            parent_id_str = request.POST.get('parent_id', '0')  # 默认为0表示一级分类
            
            # 验证必填参数
            if not name:
                return JsonResponse({
                    'status': '400',
                    'msg': '分类名称不能为空'
                })
            
            # 验证分类名称
            name = name.strip()
            if not name:
                return JsonResponse({
                    'status': '400',
                    'msg': '分类名称不能为空'
                })
            
            # 验证名称长度
            if len(name) > 18:
                return JsonResponse({
                    'status': '400',
                    'msg': '分类名称长度不能超过18个字符'
                })
            
            # 验证 parent_id
            try:
                parent_id = int(parent_id_str)
                if parent_id < 0:
                    return JsonResponse({
                        'status': '400',
                        'msg': '父分类ID不能为负数'
                    })
            except ValueError:
                return JsonResponse({
                    'status': '400',
                    'msg': '父分类ID格式不正确'
                })
            
            # 检查分类名称是否已存在
            if GoodsCategory.objects.filter(name=name).exists():
                return JsonResponse({
                    'status': '400',
                    'msg': '该分类名称已存在'
                })
            
            # 创建新的分类
            new_category = GoodsCategory.objects.create(
                name=name,
                parent_id=parent_id
            )
            
            print(f"成功创建分类: ID={new_category.id}, 名称={new_category.name}, 父ID={new_category.parent_id}")
            
            # 返回成功响应，状态码201
            return JsonResponse({
                'status': '201',
                'msg': f'分类"{name}"创建成功',
                'data': {
                    'id': new_category.id,
                    'name': new_category.name,
                    'parent_id': new_category.parent_id
                }
            })
            
        except Exception as e:
            print(f"创建分类时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': f'创建失败: {str(e)}'
            })
#更新分类名称
class UpdateCategoryNameView(View):
    def post(self,request,category_id):
        try:
            new_name = request.POST.get('name')
            if not new_name:
                print("未找到 name 参数")
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少分类名称参数'
                })

            print(f"获取到的分类名称: {new_name}")

            # 验证分类名称
            if not new_name.strip():
                return JsonResponse({
                    'status': '400',
                    'msg': '分类名称不能为空'
                })

            # 去除首尾空格
            new_name = new_name.strip()

            # 验证名称长度 (修正为32，与模型保持一致)
            if len(new_name) > 32:
                return JsonResponse({
                    'status': '400',
                    'msg': '分类名称长度不能超过32个字符'
                })

            # 查询分类是否存在
            try:
                category = GoodsCategory.objects.get(id=category_id)
                # 检查新名称是否与当前名称相同
                if category.name == new_name:
                    return JsonResponse({
                        'status': '200',
                        'msg': '分类名称未发生变化'
                    })

                # 检查是否与其他分类名称重复
                if GoodsCategory.objects.filter(name=new_name).exclude(id=category_id).exists():
                    return JsonResponse({
                        'status': '400',
                        'msg': '该分类名称已存在'
                    })

                # 保存原始名称用于日志
                old_name = category.name

                # 更新分类名称
                category.name = new_name
                category.save()

                print(f"分类 {category_id} 名称已从 '{old_name}' 更新为: '{new_name}'")

                return JsonResponse({
                    'status': '200',
                    'msg': f'分类名称更新成功，从 "{old_name}" 修改为 "{new_name}"'
                })

            except GoodsCategory.DoesNotExist:
                return JsonResponse({
                    'status': '404',
                    'msg': '分类不存在'
                })

        except Exception as e:
            print(f"更新分类名称时发生错误: {str(e)}")
            return JsonResponse({
                'status': '500',
                'msg': f'更新失败: {str(e)}'
            })

