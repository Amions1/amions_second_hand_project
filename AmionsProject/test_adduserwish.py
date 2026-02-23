"""
测试AddUserWish功能的脚本
"""

import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AmionsProject.settings')
django.setup()

from trade.models import User, Goods, GoodsCategory, UserWish
from django.test import TestCase, Client
from django.urls import reverse
import json

class TestAddUserWish(TestCase):
    def setUp(self):
        """测试前准备数据"""
        # 创建测试用户
        self.test_user = User.objects.create(
            phone='13800138001',
            password='test123',
            nickname='测试用户',
            role=User.ROLE_NORMAL
        )
        
        # 创建测试分类
        self.category = GoodsCategory.objects.create(
            name='测试分类',
            parent_id=0
        )
        
        # 创建测试商品
        self.test_goods = Goods.objects.create(
            title='测试商品',
            category_id=self.category.id,
            price=100.00,
            quality=8,
            publisher=self.test_user,
            status=1,
            details='测试商品描述'
        )

    def test_add_user_wish_success(self):
        """测试成功添加收藏"""
        client = Client()
        
        # 发送POST请求添加收藏
        response = client.post('/details/adduserwish/', {
            'user_id': self.test_user.id,
            'goods_id': self.test_goods.id
        })
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证响应
        self.assertEqual(result['status'], '201')
        self.assertEqual(result['msg'], '收藏成功')
        
        # 验证数据库中确实创建了记录
        user_wish_exists = UserWish.objects.filter(
            user=self.test_user,
            goods=self.test_goods
        ).exists()
        self.assertTrue(user_wish_exists)

    def test_add_duplicate_wish(self):
        """测试重复收藏同一商品"""
        client = Client()
        
        # 先添加一次收藏
        client.post('/details/adduserwish/', {
            'user_id': self.test_user.id,
            'goods_id': self.test_goods.id
        })
        
        # 再次尝试添加同样的收藏
        response = client.post('/details/adduserwish/', {
            'user_id': self.test_user.id,
            'goods_id': self.test_goods.id
        })
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证返回409冲突状态
        self.assertEqual(result['status'], '409')
        self.assertIn('已在您的收藏中', result['msg'])

    def test_add_wish_missing_parameters(self):
        """测试缺少参数的情况"""
        client = Client()
        
        # 不提供user_id
        response = client.post('/details/adduserwish/', {
            'goods_id': self.test_goods.id
        })
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], '400')
        self.assertIn('缺少必要参数', result['msg'])

    def test_add_wish_nonexistent_user(self):
        """测试用户不存在的情况"""
        client = Client()
        
        response = client.post('/details/adduserwish/', {
            'user_id': 99999,  # 不存在的用户ID
            'goods_id': self.test_goods.id
        })
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], '404')
        self.assertIn('用户或商品不存在', result['msg'])

    def test_add_own_goods_to_wishlist(self):
        """测试用户试图收藏自己发布的商品"""
        client = Client()
        
        # 商品的发布者就是测试用户
        response = client.post('/details/adduserwish/', {
            'user_id': self.test_user.id,
            'goods_id': self.test_goods.id
        })
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证返回400错误
        self.assertEqual(result['status'], '400')
        self.assertIn('不能收藏自己发布的商品', result['msg'])

if __name__ == '__main__':
    import unittest
    unittest.main()