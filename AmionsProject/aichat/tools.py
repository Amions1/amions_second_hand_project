
from langchain_core.tools import tool
from trade.models import Goods, GoodsCategory, Order, User
from django.db.models import Q
from .knowledge_base import search_knowledge_base

# 根据关键词搜索商品
@tool
def search_goods(keyword: str) -> str:
    """
    搜索商品：根据关键词在商品库中搜索匹配的商品

    当用户想要查找商品、搜索商品、找某类商品时，必须调用此工具。

    Args:
        keyword: 搜索关键词，可以是商品标题或详情中的文字，例如"手机"、"电脑"、"书籍"等

    Returns:
        匹配的商品列表信息，包含商品ID、标题、价格、成色等
    """
    goods_list = Goods.objects.filter(
        Q(title__icontains=keyword) | Q(details__icontains=keyword),
        status=Goods.STATUS_ON  # 只搜索在售商品
    )

    if not goods_list:
        return f"未找到与'{keyword}'相关的商品"

    # 获取所有分类信息，用于后续匹配
    categories = {cat.id: cat.name for cat in GoodsCategory.objects.all()}

    results = []
    for goods in goods_list:
        results.append({
            "id": goods.id,
            "title": goods.title,
            "category_id": goods.category_id,
            "category_name": categories.get(goods.category_id, "未知分类"),
            "price": float(goods.price),
            "quality": goods.quality,
            "status": goods.status,
            "publisher_id": goods.publisher_id,
            "publisher_nickname": goods.publisher.nickname,
            "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": goods.details[:100] + "..." if len(goods.details) > 100 else goods.details
        })

    return f"找到{len(results)}个相关商品：\n" + str(results)


# 获取所有商品分类列表
@tool
def get_goods_categories() -> str:
    """
    获取所有商品分类列表

    Returns:
        商品分类信息
    """
    categories = GoodsCategory.objects.all()
    results = [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in categories]
    return f"商品分类列表：\n{results}"


# 根据分类ID获取商品列表
@tool
def get_goods_by_category(category_id: int) -> str:
    """
    根据分类ID获取商品列表

    Args:
        category_id: 分类ID

    Returns:
        该分类下的商品列表
    """
    goods_list = Goods.objects.filter(category_id=category_id, status=Goods.STATUS_ON)[:10]

    if not goods_list:
        return f"该分类下暂无商品"

    results = []
    for goods in goods_list:
        results.append({
            "id": goods.id,
            "title": goods.title,
            "price": float(goods.price),
            "quality": goods.quality,
            "publisher": goods.publisher.nickname
        })

    return f"该分类下有{len(results)}个商品：\n{results}"


# 查询当前用户的订单信息
@tool
def get_user_orders(user_id: int) -> str:
    """
    查询用户的订单信息，包括买入的订单和卖出的订单

    当用户询问"我的订单"、"我买了什么"、"我卖了什么"、"查看订单"时，必须调用此工具。

    Args:
        user_id: 用户ID

    Returns:
        用户的订单列表，包含买入订单和卖出订单
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"用户ID {user_id} 不存在"

    # 查询买入的订单（作为买家）
    bought_orders = Order.objects.filter(buyer=user).select_related('goods', 'seller')

    # 查询卖出的订单（作为卖家）
    sold_orders = Order.objects.filter(seller=user).select_related('goods', 'buyer')

    result_text = f"用户 {user.nickname} 的订单信息：\n\n"

    # 买入的订单
    if bought_orders:
        result_text += "【买入的订单】\n"
        for order in bought_orders:
            status = "已支付" if order.status == Order.STATUS_PAY else "未支付"
            result_text += (
                f"- 订单ID: {order.id}\n"
                f"  商品: {order.goods.title}\n"
                f"  价格: ¥{order.price}\n"
                f"  卖家: {order.seller.nickname}\n"
                f"  状态: {status}\n"
                f"  时间: {order.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【买入的订单】暂无\n\n"

    # 卖出的订单
    if sold_orders:
        result_text += "【卖出的订单】\n"
        for order in sold_orders:
            status = "已支付" if order.status == Order.STATUS_PAY else "未支付"
            result_text += (
                f"- 订单ID: {order.id}\n"
                f"  商品: {order.goods.title}\n"
                f"  价格: ¥{order.price}\n"
                f"  买家: {order.buyer.nickname}\n"
                f"  状态: {status}\n"
                f"  时间: {order.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【卖出的订单】暂无\n"

    return result_text


# 查询平台知识库
@tool
def query_knowledge_base(query: str) -> str:
    """
    查询平台知识库，获取平台规则、帮助文档、使用说明等信息

    当用户询问平台使用规则、帮助文档、常见问题、平台功能说明、
    用户行为规范、隐私政策、AI助手使用方法等问题时，必须调用此工具。

    Args:
        query: 用户的查询问题，例如"如何使用AI助手"、"平台规则是什么"等

    Returns:
        知识库中相关的平台规则和帮助文档内容
    """
    return search_knowledge_base(query, top_k=3)


# 查询与用户相关的所有商品
@tool
def get_user_related_goods(user_id: int) -> str:
    """
    查询与用户相关的所有商品，根据商品状态判断是发布的、买到的、卖出的还是下架的

    当用户询问"我的商品"、"我发布的商品"、"我买到/卖出的东西"、"我的所有物品"时，必须调用此工具。

    Args:
        user_id: 用户ID

    Returns:
        用户的所有相关商品，按状态分类
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"用户ID {user_id} 不存在"

    # 获取所有分类信息
    categories = {cat.id: cat.name for cat in GoodsCategory.objects.all()}

    # 1. 用户发布的商品（所有状态）
    published_goods = Goods.objects.filter(publisher=user)

    # 2. 用户买到的商品（通过订单，已支付）
    bought_goods_ids = Order.objects.filter(
        buyer=user,
        status=Order.STATUS_PAY
    ).values_list('goods_id', flat=True)
    bought_goods = Goods.objects.filter(id__in=bought_goods_ids)

    # 3. 用户卖出的商品（通过订单，已支付）
    sold_goods_ids = Order.objects.filter(
        seller=user,
        status=Order.STATUS_PAY
    ).values_list('goods_id', flat=True)
    sold_goods = Goods.objects.filter(id__in=sold_goods_ids)

    result_text = f"用户 {user.nickname} 的相关商品：\n\n"

    # 发布的商品按状态分类
    published_on = published_goods.filter(status=Goods.STATUS_ON)
    published_sold = published_goods.filter(status=Goods.STATUS_SOLD)
    published_off = published_goods.filter(status=Goods.STATUS_OFF)
    published_force_off = published_goods.filter(status=Goods.STATUS_FORCE_OFF)

    # 【在售的商品】
    if published_on:
        result_text += "【我发布的 - 在售】\n"
        for goods in published_on:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  成色: {goods.quality}成新\n"
                f"  发布时间: {goods.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【我发布的 - 在售】暂无\n\n"

    # 【已卖出的商品】
    if published_sold:
        result_text += "【我发布的 - 已卖出】\n"
        for goods in published_sold:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  发布时间: {goods.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【我发布的 - 已卖出】暂无\n\n"

    # 【已下架的商品】
    if published_off:
        result_text += "【我发布的 - 已下架】\n"
        for goods in published_off:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  发布时间: {goods.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【我发布的 - 已下架】暂无\n\n"

    # 【强制下架的商品】
    if published_force_off:
        result_text += "【我发布的 - 强制下架】\n"
        for goods in published_force_off:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  发布时间: {goods.create_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
    else:
        result_text += "【我发布的 - 强制下架】暂无\n\n"

    # 【买到的商品】
    if bought_goods:
        result_text += "【我买到的】\n"
        for goods in bought_goods:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  卖家: {goods.publisher.nickname}\n\n"
            )
    else:
        result_text += "【我买到的】暂无\n\n"

    # 【卖出的商品】
    if sold_goods:
        result_text += "【我卖出的】\n"
        for goods in sold_goods:
            result_text += (
                f"- 商品ID: {goods.id}\n"
                f"  标题: {goods.title}\n"
                f"  分类: {categories.get(goods.category_id, '未知分类')}\n"
                f"  价格: ¥{goods.price}\n"
                f"  买家: {goods.publisher.nickname}\n\n"
            )
    else:
        result_text += "【我卖出的】暂无\n"

    return result_text