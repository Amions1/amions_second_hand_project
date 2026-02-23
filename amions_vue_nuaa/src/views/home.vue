<template>
  <div class="home-container">
    <!-- 引入导航栏组件 -->
    <Home_header />
    <div class="home-main">
      <!-- 侧边栏,主内容区的弹性布局 -->
      <div class="layout-wrapper">
        <!-- 左侧分类侧边栏 -->
        <aside class="category-sidebar">
          <h3 class="category-title">🚩商品分类</h3>
          <!--按父分类分组的子分类列表-->
          <div class="grouped-child-categories">
            <div
              class="child-category-group"
              v-for="parent in filteredParentCategories"
              :key="parent.id"
              @mouseenter="loadGoodsByCategory(parent.id)"
            >
              <div class="child-category-row">
                <span class="parent-category-name">{{ parent.name }}：</span>
                <span
                  v-for="(child, index) in groupedChildCategories[parent.id]"
                  :key="child.id"
                >
                  <span class="child-category-item">{{ child.name }}</span>
                  <span v-if="index < groupedChildCategories[parent.id].length - 1" class="separator">/</span>
                </span>
              </div>
            </div>
          </div>
        </aside>

        <main class="content-area">
          <div v-if="goodsData.length === 0 && !isSearching" class="carousel-container">
            <el-carousel height="400px" class="main-carousel">
              <el-carousel-item v-for="(image, index) in carouselImages" :key="index">
                <img :src="image" :alt="`轮播图 ${index + 1}`" class="carousel-image" />
              </el-carousel-item>
            </el-carousel>
          </div>
          
          <div v-else-if="goodsData.length === 0 && isSearching && isHoveringCategory" class="placeholder-content">
            <p>当前显示分类商品</p>
            <p>此分类暂无商品</p>
          </div>
          
          <div v-else-if="isSearching && !isHoveringCategory" class="search-result-header">
            <h3>搜索结果："{{ searchQuery }}"</h3>
            <p>共找到 {{ goodsData.length }} 个相关商品</p>
          </div>
          
          <!-- 商品列表 -->
          <div v-if="goodsData.length > 0" class="goods-list">
            <div class="goods-grid">
              <div 
                class="goods-item" 
                v-for="goods in currentGoodsData"
                :key="goods.id"
              >
                <div v-if="getImageUrl(goods.image)" class="goods-image">
                  <router-link :to="`/details/${goods.id}`">
                    <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
                  </router-link>
                </div>
                <div class="goods-info">
                  <h4 class="goods-title">{{ goods.title }}</h4>
                  <p class="goods-price">¥{{ goods.price }}</p>
                  <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                   <p class="goods-status" v-if="goods.status !== undefined">
                       状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                   </p>
                  <p class="goods-status" v-if="goods.status">发布者: {{ goods.publisher_nickname}}</p>
                </div>
              </div>
            </div>
            
            <!-- 分页控件 -->
            <div class="pagination" v-if="totalPages > 1">
              <button 
                class="page-btn" 
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage <= 1"
              >
                上一页
              </button>
              
              <span class="page-info">
                第 {{ currentPage }} 页，共 {{ totalPages }} 页
              </span>
              
              <button 
                class="page-btn" 
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage >= totalPages"
              >
                下一页
              </button>
            </div>
          </div>
          
          <div v-else-if="isSearching && !isHoveringCategory && goodsData.length === 0" class="no-search-results">
            <p>未找到与 "{{ searchQuery }}" 相关的商品</p>
          </div>
        </main>
      </div>
    </div>
    <!-- 特价抢购区域 -->
    <div class="home-second">
      <h3 class="special-title">🔥 特价抢购 - 价格最低商品Top5</h3>
      <div class="special-products">
        <div
          class="special-product-item"
          v-for="product in lowestPriceProducts"
          :key="product.id"
          @click="goToDetails(product.id)"
        >
          <div v-if="getImageUrl(product.image)" class="special-product-image">
            <img :src="getImageUrl(product.image)" :alt="product.title" @error="imageError"/>
          </div>
          <div class="special-product-info">
            <h4 class="goods-title">{{ product.title }}</h4>
            <p class="goods-price">¥{{ product.price }}</p>
            <p class="goods-quality">成色:{{ product.quality }}</p>
            <p class="goods-status">状态:{{ product.status }}</p>
            <p class="special-product-nickname" v-if="product.publisher_nickname">发布者: {{ product.publisher_nickname }}</p>
          </div>
        </div>

        <div class="no-special-products" v-if="lowestPriceProducts.length === 0">
          <p>暂无特价商品</p>
        </div>
      </div>
    </div>
  </div>
  <!-- 底部栏组件 -->
  <Home_footer />
</template>

<script setup lang="ts">

import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElCarousel, ElCarouselItem } from 'element-plus'
import { isAuthenticated } from '@/utils/auth'
import Home_header from "@/components/home/home_header.vue";
import Home_footer from "@/components/home/home_footer.vue";
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

// 检查认证状态的函数（home页面不强制要求认证）
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    console.log('当前未登录，部分功能受限');
    return false;
  }
  return true;
}

// 定义用户信息类型
interface UserInfo {
  nickname: string;
  user_id: string;
  phone: string;
}

// 定义商品分类类型
interface Category {
  id: number;
  parent_id: number;
  name: string;
}

// 定义商品信息类型
interface GoodsItem {
  id: number;
  title: string;
  price: number;
  image: string;
  quality?: string;
  status: number;
  publisher_id:bigint
  publisher_nickname?: string
}

// 定义响应式数据接收登录信息
const userInfo = ref<UserInfo>({
  nickname: '',
  user_id: '',
  phone: ''
})


// 轮播图图片路径
const carouselImages = [
  new URL('@/components/home/icons/main1.png', import.meta.url).href,
  new URL('@/components/home/icons/main2.png', import.meta.url).href,
  new URL('@/components/home/icons/main3.png', import.meta.url).href,
  new URL('@/components/home/icons/main4.png', import.meta.url).href,
]

// 页面加载时读取SessionStorage中的令牌信息
onMounted(() => {
  // 读取并转成对象（JSON.parse）
  const storedUser = sessionStorage.getItem('userInfo')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
  } else {
    // 如果没有用户信息，重定向到登录页
    if (!checkAuthentication()) {
      return;
    }
  }
  
  // 调用获取特价商品的函数
  fetchLowestPriceProducts();
});

// 存储商品分类数据
const categoryList = ref<Category[]>([])
// 标记当前激活的父分类（控制子分类显示）
const activeParent = ref('')

// 存储对应父分类的商品数据
const goodsData = ref<GoodsItem[]>([])

// 特价抢购相关数据
const lowestPriceProducts = ref<GoodsItem[]>([])

// 搜索相关变量
const isSearching = ref(false)
const searchQuery = ref('')

// 保存搜索结果，以便在悬停后可以恢复
const searchResults = ref<GoodsItem[]>([])

// 是否在悬停分类期间临时显示分类数据
const isHoveringCategory = ref(false)

// 分页相关变量
const currentPage = ref(1)
const itemsPerPage = 8  // 每页8个商品
const totalPages = computed(() => {
  let availableGoodsCount;
  if (isSearching.value && !isHoveringCategory.value) {
    // 搜索状态下统计所有搜索结果数量
    availableGoodsCount = goodsData.value.length;
  } else if (isSearching.value && isHoveringCategory.value) {
    // 悬停分类时，也统计所有商品数量
    availableGoodsCount = goodsData.value.length;
  } else {
    // 非搜索状态下只统计在售中的商品数量
    availableGoodsCount = goodsData.value.filter(good => good.status == 1).length;
  }
  return Math.ceil(availableGoodsCount / itemsPerPage)
})

// 获取当前页的商品数据
const currentGoodsData = computed(() => {
  let availableGoods;
  if (isSearching.value && !isHoveringCategory.value) {
    // 搜索状态下且不在悬停分类时，显示搜索结果，不论状态
    availableGoods = goodsData.value;
  } else if (isSearching.value && isHoveringCategory.value) {
    // 搜索状态下但正在悬停分类时，只显示在售商品
    availableGoods = goodsData.value.filter(good => good.status == 1);
  } else {
    // 非搜索状态下只显示在售中的商品（status == 1）
    availableGoods = goodsData.value.filter(good => good.status == 1);
  }
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return availableGoods.slice(start, end)
})

// 加载对应子分类的商品数据（传入父分类ID，获取该父分类下所有子分类的商品）
const loadGoodsByCategory = async (parentId: number) => {
  try {
    // 获取该父分类下的所有子分类ID
    const childCategories = groupedChildCategories.value[parentId] || [];
    const childIds = childCategories.map(child => child.id);
    
    if (childIds.length === 0) {
      goodsData.value = [];
      return;
    }
    
    // 并发请求所有子分类的商品数据
    const requests = childIds.map(id => 
      request({
        url: `api/goods/second?id=${id}`,
        method: 'GET',
      })
    );
    
    const responses = await Promise.all(requests);
    
    // 合并所有子分类的商品数据
    let allGoods: GoodsItem[] = [];
    responses.forEach(res => {
      if (res.data.status === '200' && res.data.goods_list) {
        allGoods = [...allGoods, ...res.data.goods_list];
      }
    });
    
    console.log('合并后的子分类商品数据：', allGoods);
    
    // 如果当前处于搜索状态，标记为悬停状态并保存当前搜索结果
    if (isSearching.value) {
      searchResults.value = [...goodsData.value];
      isHoveringCategory.value = true;
    }
    goodsData.value = allGoods;
    // 切换分类时，重置到第一页
    currentPage.value = 1
  } catch (error: any) {
    console.error('请求商品数据失败：', error)
    if (error.response?.status === 401) {
      console.log('商品数据请求未授权，部分功能受限');
    }
    goodsData.value = []
  }
}
// 搜索功能
const performSearch = async (query: string) => {
  if (!query.trim()) {
    return;
  }
  
  try {
    const response = await request.get(`api/goods/search/?keyword=${encodeURIComponent(query)}`);
    
    if (response.data.status === '200') {
      goodsData.value = response.data.data
      isSearching.value = true
      searchQuery.value = query
      currentPage.value = 1
      console.log('搜索结果：', goodsData.value)
    } else {
      console.error('搜索失败:', response.data.msg)
      goodsData.value = []
      isSearching.value = false
    }
  } catch (error: any) {
    console.error('搜索请求失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
    goodsData.value = []
    isSearching.value = false
  }
}
// 监听路由变化，当路由参数改变时执行相应操作
watch(
  () => route.query,
  async (newQuery, oldQuery) => {
    const newSearch = newQuery.search as string;
    const oldSearch = oldQuery?.search as string;
    
    // 如果新的路由参数中有搜索词，则执行搜索（即使是相同的搜索词）
    if (newSearch) {
      await performSearch(newSearch);
    } else if (!newSearch && oldSearch) {
      // 如果新参数中没有搜索词但旧参数中有，则清空搜索状态并加载默认内容
      isSearching.value = false;
      isHoveringCategory.value = false;
      searchQuery.value = '';
      goodsData.value = [];
      currentPage.value = 1;
    }
  },
  { immediate: true }
);

onMounted(async () => {
  // 无论是否搜索，都需要加载左侧分类数据
  // 不需要认证也可以加载分类
  try {
    const res = await request({
      url: 'api/goods/first',
      method: 'GET',
    })
    // 赋值商品分类数据
    categoryList.value = res.data.goods_category
    
    // 加载特价抢购商品
    await fetchLowestPriceProducts();
  } catch (error: any) {
    console.error('请求商品分类失败：', error)
    // 打印详细错误，方便排查
    if (error.response?.status === 401) {
      console.log('分类数据请求未授权，部分功能受限');
      // 即使未授权也要尝试获取公共分类数据
      try {
        // 使用不带认证的请求实例获取公共分类
        const publicRes = await fetch(`${getBackendBaseUrl()}api/goods/first`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (publicRes.ok) {
          const publicData = await publicRes.json();
          categoryList.value = publicData.goods_category || [];
          // 加载特价抢购商品
          await fetchLowestPriceProducts();
        }
      } catch (publicError) {
        console.error('获取公共分类数据也失败：', publicError);
        // 加载特价抢购商品
        await fetchLowestPriceProducts();
      }
    } else if (error.response) {
      console.log('后端返回错误状态码：', error.response.status)
      console.log('后端返回错误信息：', error.response.data)
    } else if (error.request) {
      console.log('请求已发送但无响应：', error.request)
    } else {
      console.log('请求配置错误：', error.message)
    }
    // 加载特价抢购商品
    await fetchLowestPriceProducts();
  }
})


// 获取所有父分类
const allParentCategories = computed<Category[]>(() => {
  // 返回所有父分类的项目（即parent_id === 0的项目）
  return categoryList.value.filter((item: Category) => item.parent_id === 0)
});

// 过滤出有子分类的父分类
const filteredParentCategories = computed<Category[]>(() => {
  return allParentCategories.value.filter(parent => 
    groupedChildCategories.value[parent.id] && groupedChildCategories.value[parent.id].length > 0
  );
});

// 按父分类分组的子分类
const groupedChildCategories = computed(() => {
  const result: { [key: number]: Category[] } = {};
  
  categoryList.value.forEach((item: Category) => {
    if (item.parent_id !== 0) {  // 不是父分类，是子分类
      if (!result[item.parent_id]) {
        result[item.parent_id] = [];
      }
      result[item.parent_id].push(item);
    }
  });
  
  return result;
});

// 获取价格最低的5个商品
const fetchLowestPriceProducts = async () => {
  try {
    let allProducts: GoodsItem[] = [];

    // 获取所有分类的所有商品
    if (allProducts.length === 0) {
      try {
        // 尝试获取所有一级分类
        const firstLevelResponse = await request.get('api/goods/first');
        if (firstLevelResponse.data.status === '200') {
          const firstCategories = firstLevelResponse.data.goods_category || [];
          
          // 遍历每个一级分类，获取其下的二级分类商品
          for (const firstCat of firstCategories) {
            try {
              const secondLevelResponse = await request.get(`api/goods/second?id=${firstCat.id}`);
              if (secondLevelResponse.data.status === '200') {
                const categoryProducts: GoodsItem[] = secondLevelResponse.data.goods_list || [];
                allProducts = allProducts.concat(categoryProducts);
              }
            } catch (subCatError) {
              console.error(`获取分类 ${firstCat.id} 的子分类商品失败`, subCatError);
            }
          }
        }
      } catch (firstLevelError) {
        console.error('获取一级分类失败', firstLevelError);
      }
    }

    
    console.log('总共获取到的商品数量：', allProducts.length);
    console.log('原始商品数据示例：', allProducts.slice(0, 3)); // 打印前3个商品作为示例
    
    // 过滤掉已售完的商品(status != 1)，然后按价格升序排序，取前5个
    const availableProducts = allProducts
      .filter(product => {
        const isInStock = product.status == 1; // 只获取在售商品
        const hasValidPrice = typeof product.price === 'number' && product.price > 0;
        return isInStock && hasValidPrice;
      })
      .sort((a, b) => a.price - b.price) // 按价格升序排序
      .slice(0, 5); // 取前5个
    
    lowestPriceProducts.value = availableProducts;
    console.log('最终选中的价格最低的5个商品：', availableProducts);
    
  } catch (error: any) {
    console.error('请求价格最低商品失败：', error);
    if (error.response?.status === 401) {
      console.log('价格最低商品请求未授权，部分功能受限');
    } else if (error.response?.status === 404) {
      console.log('请求的API接口不存在');
    }
    lowestPriceProducts.value = [];
  }
};

// 跳转到商品详情页
const goToDetails = (productId: number) => {
  router.push(`/details/${productId}`);
};

// 获取后端基础URL（与request.js保持一致）
const getBackendBaseUrl = (): string => {
  const hostname = window.location.hostname;
  const isLocalhost = /localhost|127\.0\.0\.1/.test(hostname);
  const isLocalNetwork = /^192\.168\./.test(hostname);

  if (isLocalhost) {
    return 'http://127.0.0.1:8000';
  } else if (isLocalNetwork) {
    return `http://${hostname}:8000`;
  } else {
    return 'http://69mdjw853446.vicp.fun:37276';
  }
};

// 处理图片URL的方法
const getImageUrl = (imagePath: string): string | undefined => {
  if (!imagePath) return undefined;
  
  // 如果已经是完整的URL（以http或https开头），直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  const baseUrl = getBackendBaseUrl();
  
  // 如果是相对路径，添加后端基础URL
  if (imagePath.startsWith('/')) {
    return `${baseUrl}${imagePath}`;
  }
  
  // 其他情况，也尝试拼接后端URL
  return `${baseUrl}/${imagePath}`;
};

// 图片加载错误处理
const imageError = (event: Event) => {
  console.error('图片加载失败:', (event.target as HTMLImageElement).src);
  // 设置默认图片
  const defaultImg = 'data:image/svg+xml;utf8,' +
      '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150">' +
      '<rect width="200" height="150" fill="#f0f0f0"/>' +
      '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="14" fill="#999">图片无法加载</text>' +
      '</svg>';
  (event.target as HTMLImageElement).src = defaultImg;
};


</script>

<style scoped>
.home-container {
  padding-top: 60px;
  min-height: 100vh;
  background-color: #f9fafb;
}


.home-main {
  width: 1200px;
  margin: 0 auto;
  padding: 30px 10px;
}

/* 新增：布局容器 - 侧边栏+主内容 */
.layout-wrapper {
  display: flex;
  gap: 20px;
}

/* 新增：左侧分类侧边栏样式 */
.category-sidebar {
  width: 280px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  height: fit-content;
  margin-left: -20px;
}

.category-title {
  font-size: 18px;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 分组的子分类容器 */
.grouped-child-categories {
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
}

/* 子分类组 */
.child-category-group {
  margin-bottom: 10px;
}

/* 子分类行 */
.child-category-row {
  margin-top: 5px;
  color: #666;
  font-size: 14px;
}

.separator {
  margin: 0 1px;
  color: #999;
}

.child-category-item {
  padding: 8px 5px;
  font-size: 13px;
  color: #666;
}

.child-category-item:hover {
  color: #409eff;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.content-area {
  flex: 1;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  min-height: 500px;
}

.placeholder-content {
  color: #666;
  padding: 20px 0;
}

.goods-list {
  padding: 20px 0;
}

.goods-list h3 {
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.goods-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  /* 每行4个商品 */
  gap: 20px;
}

.goods-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  transition: box-shadow 0.3s ease;
}

.goods-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.goods-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.goods-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.goods-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.goods-info {
  text-align: left;
}

.goods-title {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goods-price {
  color: #e74c3c;
  font-weight: bold;
  margin: 5px 0;
  font-size: 16px;
}

.goods-quality,
.goods-status {
  font-size: 12px;
  color: #999;
  margin: 3px 0;
}

.search-result-header {
  padding: 20px 0;
  border-bottom: 1px solid #eee;
}

.search-result-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.no-search-results {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 16px;
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.page-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.carousel-container {
  width: 100%;
  height: 400px;
  overflow: hidden;
  border-radius: 8px;
}

.main-carousel {
  width: 100%;
  height: 400px;
}

.carousel-image {
  width: 100%;
  height: 400px;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.main-carousel :deep(.el-carousel__container) {
  height: 400px !important;
}

.main-carousel :deep(.el-carousel__item) {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 添加动态模糊效果 */
.carousel-image:hover {
  filter: blur(2px);
  transition: filter 0.5s ease;
}

/* 为走马灯添加一些动态效果 */
.main-carousel :deep(.el-carousel__indicators) {
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  padding: 10px;
  border-radius: 0 0 8px 8px;
}

/* 特价抢购区域样式 */
.home-second {
  width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.special-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #e74c3c;
  text-align: center;
  border-bottom: 2px solid #f8f9fa;
  padding-bottom: 10px;
}

.special-products {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 10px 0;
}

.special-product-item {
  min-width: 200px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  transition: box-shadow 0.3s ease;
  cursor: pointer;
}

.special-product-item {
  min-width: 200px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.special-product-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.special-product-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.special-product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.special-product-info {
  text-align: left;
}

.special-product-nickname {
  font-size: 12px;
  color: #999;
  margin: 3px 0;
}

.no-special-products {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
  flex: 1;
}
</style>