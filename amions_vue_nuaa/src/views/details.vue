<template>
  <div class="details-container">
    <!-- 引入导航栏组件 -->
    <Profile_header />
    <div class="details-main">
      <div class="product-detail">
        <!-- 左侧：商品图片 -->
        <div class="product-image-section">
          <div v-if="getImageUrl(goodsDetail.image)" class="product-image">
            <img :src="getImageUrl(goodsDetail.image)" :alt="goodsDetail.title" @error="imageError"/>
          </div>
        </div>

        <!-- 右侧：商品信息 -->
        <div class="product-info-section">
          <h2 class="product-title">{{ goodsDetail.title }}</h2>
          <div class="product-meta">
            <div class="meta-item">
              <span class="label">价格:</span>
              <span class="value">¥{{ goodsDetail.price }}</span>
            </div>
            <div class="meta-item">
              <span class="label">状态:</span>
              <span class="value">{{ goodsDetail.status == 1 ? '在售中' : '已下架' }}</span>
            </div>
            <div class="meta-item" v-if="goodsDetail.create_time">
              <span class="label">上架时间:</span>
              <span class="value">{{ formatDate(goodsDetail.create_time) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">发布者:</span>
              <span class="value">{{ goodsDetail.publisher_nickname || '未知用户' }}</span>
            </div>
          </div>

          <div class="product-details">
            <h3>商品详情</h3>
            <div class="details-content">
              {{ goodsDetail.details || '暂无商品详情描述' }}
            </div>
          </div>

          <div class="action-buttons">
            <button class="btn-chat" @click="chatWithSeller">我要聊聊</button>
            <button class="btn-buy" @click="buyNow">我要购买</button>
            <el-button
              class="btn-favorite"
              :loading="isFavoriteLoading"
              :disabled="isFavorited"
              circle
              @click="addToFavorites"
            >
              <el-icon v-if="!isFavorited"><Star /></el-icon>
              <el-icon v-else><StarFilled /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 聊天窗口 -->
    <ChatWindow
      v-if="showChatWindow"
      :seller-id="goodsDetail.publisher_id"
      :buyer-id="getCurrentBuyerId()"
      :seller-nickname="goodsDetail.publisher_nickname || '未知用户'"
      :goods-title="goodsDetail.title"
      :goods-id="goodsDetail.id"
      @close="showChatWindow = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Star, StarFilled } from '@element-plus/icons-vue';
import Home_header from '@/components/home/home_header.vue';
import request from '@/utils/request';
import Profile_header from "@/components/profile/profile_header.vue";
import ChatWindow from '@/components/chat/ChatWindow.vue';
import { useRouter } from 'vue-router';
import {getUserInfo} from "@/utils/auth";
import {isAuthenticated} from "@/utils/auth";

const router = useRouter();

// 检查认证状态的函数
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
}

// 定义商品信息类型
interface GoodsDetail {
  id: number;
  title: string;
  price: number;
  image: string;
  status: number;
  create_time?: string;
  details?: string;
  publisher_id: bigint;
  publisher_nickname?: string;
}

// 响应式数据
const route = useRoute();
const goodsId = ref<number>(parseInt(route.params.id as string));
const goodsDetail = ref<GoodsDetail>({
  id: 0,
  title: '',
  price: 0,
  image: '',
  status: 1,
  publisher_id: BigInt(0)
});

// 收藏相关状态
const isFavorited = ref<boolean>(false);
const isFavoriteLoading = ref<boolean>(false);

// 聊天窗口状态
const showChatWindow = ref<boolean>(false);

// 获取当前买家ID
const getCurrentBuyerId = (): bigint => {
  const userInfo = getUserInfo();
  console.log('获取用户信息:', userInfo); // 调试信息
  
  if (!userInfo || !userInfo.user_id) {
    console.log('用户信息缺失，返回默认值');
    // 如果获取不到用户信息，返回默认值
    return BigInt(0);
  }
  
  console.log('用户ID:', userInfo.user_id, '类型:', typeof userInfo.user_id);
  return BigInt(userInfo.user_id);
};

// 页面加载时获取商品详情
onMounted(async () => {
  try {
    const response = await request.get(`api/details/${goodsId.value}/`);
    if (response.data.status === '200') {
      goodsDetail.value = response.data.goods_detail;
      // 检查当前商品是否已被收藏
      await checkFavoriteStatus();
    } else {
      console.error('获取商品详情失败:', response.data.msg);
    }
  } catch (error: any) {
    console.error('请求商品详情失败：', error);
    if (error.response?.status === 401) {
      console.log('商品详情请求未授权，部分功能受限');
    }
  }
});

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
  const defaultImg = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"><rect width="400" height="400" fill="#f0f0f0"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="16" fill="#999">图片无法加载</text></svg>';
  (event.target as HTMLImageElement).src = defaultImg;
};

// 检查商品收藏状态
const checkFavoriteStatus = async () => {
  // 如果用户未登录，直接返回
  if (!isAuthenticated()) {
    return;
  }

  try {
    // 获取当前用户信息
    const userInfo = getUserInfo();
    if (!userInfo || !userInfo.user_id) {
      console.log('无法获取用户信息');
      return;
    }

    const response = await request.get(`api/details/wish/${userInfo.user_id}/${goodsId.value}`);
    if (response.data.status === '200') {
      isFavorited.value = response.data.is_favorited;
    }
  } catch (error: any) {
    console.error('检查收藏状态失败：', error);
    // 非关键功能，静默处理错误
  }
};

// 添加到我想要的
const addToFavorites = async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }

  // 如果已经收藏，则不重复操作
  if (isFavorited.value) {
    ElMessage.info('该商品已在您的收藏中');
    return;
  }

  isFavoriteLoading.value = true;

  try {
    // 获取当前用户信息
    const userInfo = getUserInfo();
    if (!userInfo || !userInfo.user_id) {
      ElMessage.error('无法获取当前用户信息，请重新登录');
      router.push('/login');
      return;
    }

    // 发送POST请求添加收藏 - 使用FormData格式
    const formData = new FormData();
    formData.append('user_id', userInfo.user_id.toString());
    formData.append('goods_id', goodsId.value.toString());

    const response = await request.post('api/details/adduserwish/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.status === '201') {
      ElMessage.success('已添加到我想要');
      isFavorited.value = true;
      console.log('收藏成功', response.data);
    } else {
      ElMessage.error(response.data.msg || '收藏失败');
      console.error('收藏失败:', response.data.msg);
    }
  } catch (error: any) {
    console.error('收藏请求失败：', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else if (error.response?.status === 409) {
      // 409 Conflict 表示已存在
      ElMessage.info('该商品已在您的收藏中');
      isFavorited.value = true;
    } else {
      ElMessage.error(error.response?.data?.msg || '收藏失败，请稍后重试');
    }
  } finally {
    isFavoriteLoading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 我要聊聊功能
const chatWithSeller = () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }

  // 获取当前用户信息
  const userInfo = getUserInfo();
  if (!userInfo || !userInfo.user_id) {
    ElMessage.error('无法获取当前用户信息，请重新登录');
    router.push('/login');
    return;
  }

  // 检查是否是商品发布者本人
  const userIdStr = userInfo.user_id.toString();
  const publisherIdStr = goodsDetail.value.publisher_id.toString();

  
  if (userIdStr === publisherIdStr) {
    ElMessage.info('您是该商品发布者本人');
    return;
  }

  console.log('发起与卖家的聊天');
  // 显示聊天窗口
  showChatWindow.value = true;
};

// 我要购买功能
const buyNow = async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }

  console.log('发起购买');

  // 获取当前用户信息
  const userInfo = getUserInfo();
  if (!userInfo || !userInfo.user_id) {
    ElMessage.error('无法获取当前用户信息，请重新登录');
    router.push('/login');
    return;
  }

  try {

    console.log(goodsDetail.value.id)
    console.log(userInfo.user_id)
    console.log(goodsDetail.value.publisher_id)
    console.log(goodsDetail.value.price)
    // 创建FormData对象发送表单数据
    const formData = new FormData();
    formData.append('goods_id', goodsDetail.value.id.toString());
    formData.append('buyer_id', userInfo.user_id.toString());
    formData.append('seller_id', goodsDetail.value.publisher_id.toString());
    formData.append('price', goodsDetail.value.price.toString());
    formData.append('image',goodsDetail.value.image.toString());
    formData.append('title',goodsDetail.value.title.toString());

    // 向后端发起支付请求，发送表单格式的数据
    const response = await request.post('api/settlement/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.status === '200') {
      ElMessage.success('购买请求已提交！');
      console.log('购买成功', response.data);

      // 跳转到结算页面，并传递订单信息
      router.push({
        path: '/settlement',
        query: {
          orderId: response.data.order_id.toString(),
          goodsId: goodsDetail.value.id.toString(),
          title: goodsDetail.value.title,
          sellerId: goodsDetail.value.publisher_id.toString(),
          price: goodsDetail.value.price.toString(),
          image: goodsDetail.value.image,
          buyerId: userInfo.user_id.toString()
        }
      });
    } else {
      ElMessage.error(response.data.msg || '购买失败');
      console.error('购买失败:', response.data.msg);
    }
  } catch (error: any) {
    console.error('购买请求失败：', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '购买请求失败，请检查网络连接');
    }
  }
};
</script>

<style scoped>
.details-container {
  padding-top: 60px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.details-main {
  width: 1200px;
  margin: 0 auto;
  padding: 30px 10px;
}

.product-detail {
  display: flex;
  gap: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 20px;
}

.product-image-section {
  flex: 1;
  min-width: 400px;
}

.product-image {
  width: 100%;
  height: 500px;
  overflow: hidden;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-info-section {
  flex: 1;
  min-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 24px;
  margin: 0 0 15px 0;
  color: #333;
  line-height: 1.3;
}

.product-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.meta-item {
  display: flex;
  gap: 15px;
}

.label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.value {
  color: #333;
  flex: 1;
}

.product-details {
  flex: 1;
}

.product-details h3 {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: #333;
}

.details-content {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  line-height: 1.6;
  min-height: 200px;
  max-height: 300px;
  overflow-y: auto;
}

.action-buttons {
  display: flex;
  gap: 15px;
  padding-top: 20px;
  align-items: center;
}

.btn-chat, .btn-buy {
  flex: 1;
  padding: 15px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-chat {
  background-color: #409eff;
  color: white;
}

.btn-chat:hover {
  background-color: #66b1ff;
}

.btn-buy {
  background-color: #e74c3c;
  color: white;
}

.btn-buy:hover {
  background-color: #c0392b;
}

.btn-favorite {
  width: 50px !important;
  height: 50px !important;
  background-color: #fadb14 !important;
  border: none;
  box-shadow: 0 2px 8px rgba(250, 219, 20, 0.3);
}

.btn-favorite:hover:not(:disabled) {
  background-color: #ffd666 !important;
  transform: scale(1.1);
}

.btn-favorite:disabled {
  background-color: #d9d9d9 !important;
  cursor: not-allowed;
}

.el-icon {
  font-size: 20px;
  color: #333;
}
</style>