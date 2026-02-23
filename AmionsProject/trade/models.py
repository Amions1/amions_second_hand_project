import json

from django.db import models
from markdown_it.rules_inline import image


# 用户表
class User(models.Model):
    ROLE_NORMAL = 1
    ROLE_ADMIN = 2
    ROLE_SUPER_ADMIN = 3
    ROLE_CHOICES = (
        (ROLE_NORMAL, "普通用户"),
        (ROLE_ADMIN, "管理员"),
        (ROLE_SUPER_ADMIN, "超级管理员"),
    )


    STATUS_NORMAL = 1
    STATUS_DISABLE = 0
    STATUS_CHOICES = (
        (STATUS_NORMAL, "正常"),
        (STATUS_DISABLE, "禁用"),
    )

    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    password = models.CharField(max_length=128, verbose_name="密码")
    nickname = models.CharField(max_length=32, verbose_name="用户昵称")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_NORMAL, verbose_name="状态")
    role = models.SmallIntegerField(choices=ROLE_CHOICES, default=ROLE_NORMAL, verbose_name="用户角色")

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    # 可选：新增快捷判断方法（代码更易读）
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

# 商品分类表
class GoodsCategory(models.Model):
    name = models.CharField(max_length=32, verbose_name="分类名称")
    parent_id = models.IntegerField(default=0, verbose_name="父分类ID")

    #序列化成json格式，在视图中返回给前端
    def __str__(self):
        result = {}
        result["name"]=self.name
        result["parent_id"]=self.parent_id
        return json.dumps(result,ensure_ascii=False)

    class Meta:
        db_table = "goods_category"
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name



# 商品表
class Goods(models.Model):
    STATUS_ON = 1
    STATUS_SOLD = 2
    STATUS_OFF = 3
    STATUS_FORCE_OFF = 4  #强制下架状态
    STATUS_CHOICES = (
        (STATUS_ON, "在售"),
        (STATUS_SOLD, "已卖出"),
        (STATUS_OFF, "已下架"),
        (STATUS_FORCE_OFF, "强制下架"),
    )

    title = models.CharField(max_length=128, verbose_name="商品标题")
    category_id = models.IntegerField(verbose_name="所属二级分类ID")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="商品价格")
    quality = models.SmallIntegerField(verbose_name="成色")
    publisher = models.ForeignKey(User, on_delete=models.PROTECT, db_column="publisher_id", verbose_name="发布者")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ON, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    image=models.ImageField(upload_to='product_images/', db_column="image",verbose_name="商品图片")
    details = models.CharField(max_length=800,default="卖家啥也没写。。。。。。",verbose_name="商品详情")

    #序列化成json格式
    def __str__(self):
        result = {}
        result["title"]=self.title
        result["category_id"]=self.category_id
        result["price"]=self.price
        result["quality"]=self.quality
        result["publisher"]=self.publisher
        result["status"]=self.status
        result["create_time"]=self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        result["image"] = str(self.image) if self.image else ""
        result['details']=self.details
        return json.dumps(result,ensure_ascii=False)

    class Meta:
        db_table = "goods"
        verbose_name = "商品"
        verbose_name_plural = verbose_name



# 订单表
class Order(models.Model):

    STATUS_UNPAY = 0
    STATUS_PAY = 1
    STATUS_CHOICES = (
        (STATUS_UNPAY, "未支付"),
        (STATUS_PAY, "已支付"),
    )

    goods = models.ForeignKey(Goods, on_delete=models.PROTECT, db_column="goods_id", verbose_name="商品")
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="buyer_orders", db_column="buyer_id", verbose_name="买家")
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="seller_orders", db_column="seller_id", verbose_name="卖家")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_UNPAY, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="交易时间")

    class Meta:
        db_table = "order"
        verbose_name = "订单"
        verbose_name_plural = verbose_name


# 用户收藏表
class UserWish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", verbose_name="用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, db_column="goods_id", verbose_name="商品")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        db_table = "user_wish"
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name
        # 确保同一个用户不能重复收藏同一商品
        unique_together = ('user', 'goods')
    
    def __str__(self):
        return f"{self.user.nickname} 收藏了 {self.goods.title}"
