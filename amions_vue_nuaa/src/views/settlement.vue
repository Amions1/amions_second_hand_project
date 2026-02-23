<template>
  <div class="settlement-container">
    <!-- 引入导航栏组件 -->
    <Profile_header />
    <div class="settlement-main">
      <h2>确认订单</h2>
      
      <div class="order-summary" v-if="orderInfo">
        <div class="product-info">
          <div v-if="orderInfo.image && getImageUrl(orderInfo.image)" class="product-image">
            <img :src="getImageUrl(orderInfo.image)!" :alt="orderInfo.title" @error="imageError"/>
          </div>
          <div class="product-details">
            <h3>{{ orderInfo.title }}</h3>
            <p class="product-price">价格: ¥{{ orderInfo.price }}</p>
            <p class="product-seller">卖家ID: {{ orderInfo.seller_id }}</p>
            <p class="product-id">商品ID: {{ orderInfo.goods_id }}</p>
          </div>
        </div>
        
        <div class="confirm-actions">
          <button class="submit-order-btn" @click="submitOrder" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '提交订单' }}
          </button>
          <button class="cancel-btn" @click="goBack">取消</button>
        </div>
      </div>
      
      <div v-else class="no-data">
        <p>订单信息加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { isAuthenticated, getUserInfo } from '@/utils/auth';
import request from '@/utils/request';
import Profile_header from "@/components/profile/profile_header.vue";

interface OrderInfo {
  goods_id: number;
  title: string;
  seller_id: bigint;
  price: number;
  image?: string;
  buyer_id?: bigint;
}

const route = useRoute();
const router = useRouter();
const orderInfo = ref<OrderInfo | null>(null);
const isSubmitting = ref(false); // 防止重复提交标志

// 检查认证状态的函数
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
};

// 页面加载时获取订单信息
onMounted(() => {
  // 检查是否为支付回调页面，避免重复执行支付逻辑
  if (isPaymentCallback()) {
    console.log('检测到支付回调参数，不执行初始加载逻辑');
    // 如果是支付回调，可在这里添加相应处理逻辑，如显示支付结果等
    // 也可以在此处处理支付结果
    return;
  }
  
  // 检查是否已在支付流程中，防止页面刷新后重复执行
  // 注意：只有在非支付回调的情况下才检查标记
  // 因为如果是支付回调，我们希望用户能看到支付结果
  if (sessionStorage.getItem('paymentStarted') === 'true') {
    console.log('检测到支付流程已启动，不执行初始加载逻辑');
    // 提供一个用户可操作的选项来清除标记，以便在必要时重新发起支付
    // 显示提示信息并询问用户是否要清除标记
    const continueAnyway = confirm('检测到支付流程已在进行中，是否要重新发起支付？\n注意：这可能意味着您之前已发起过支付。');
    if (continueAnyway) {
      // 用户选择继续，清除标记并继续执行
      sessionStorage.removeItem('paymentStarted');
      console.log('用户选择继续，已清除paymentStarted标记');
    } else {
      // 用户选择不继续，显示提示并跳转
      ElMessage.info('支付流程正在进行中，请在新开的支付页面完成操作');
      // 可以选择延迟跳转到首页，避免用户看到空白的结算页面
      setTimeout(() => {
        router.push('/home');
      }, 3000);
      return;
    }
  }
  
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  // 从路由参数获取订单信息
  const orderId = route.query.orderId as string;
  const goodsId = route.query.goodsId as string;
  const title = route.query.title as string;
  const sellerId = route.query.sellerId as string;
  const price = route.query.price as string;
  const image = route.query.image as string;
  const buyerId = route.query.buyerId as string;
  
  if (goodsId && title && sellerId && price) {
    orderInfo.value = {
      goods_id: parseInt(goodsId),
      title: title,
      seller_id: BigInt(sellerId),
      price: parseFloat(price),
      image: image,
      buyer_id: buyerId ? BigInt(buyerId) : undefined
    };
    console.log('订单信息加载成功:', orderInfo.value);
  } else {
    ElMessage.error('订单信息不完整');
    console.error('缺少订单信息:', { goodsId, title, sellerId, price, image, buyerId });
    //router.go(-1); // 返回上一页
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

// 检查是否为支付回调页面
const isPaymentCallback = (): boolean => {
  const urlParams = new URLSearchParams(window.location.search);
  // 检查URL中是否包含支付宝特有参数
  return urlParams.has('app_id') || urlParams.has('trade_no') || urlParams.has('out_trade_no') || 
         urlParams.has('sign') || urlParams.has('timestamp') || urlParams.has('total_amount');
};

// 提交订单
const submitOrder = async () => {
  // 防止重复提交
  if (isSubmitting.value) {
    ElMessage.info('订单提交中，请勿重复点击');
    return;
  }
  
  // 检查是否为支付回调页面，避免重复执行支付逻辑
  if (isPaymentCallback()) {
    console.log('检测到支付回调参数，不执行初始支付逻辑');
    return;
  }
  
  // 检查是否已在支付流程中
  if (sessionStorage.getItem('paymentStarted') === 'true') {
    ElMessage.info('支付流程已在进行中');
    return;
  }
  
  isSubmitting.value = true; // 设置提交标志
  
  try {
    if (!orderInfo.value) {
      ElMessage.error('订单信息为空');
      return;
    }
  
    // 从路由参数获取买家ID
    const buyerId = route.query.buyerId as string;
    if (!buyerId) {
      ElMessage.error('买家信息缺失');
      return;
    }
  
    const orderId = route.query.orderId as string;
    if (!orderId) {
      ElMessage.error('订单ID缺失');
      return;
    }
    
    // 向后端发起支付请求，用order_id发起get请求
    console.log("order_id=" + orderId);
    const response = await request.get(`api/settlement/paysuccess?order_id=${orderId}`);
    if (response.data.status === '200' || response.data.status === 200) {
      ElMessage.success('订单提交成功！');
      // 获取后端返回的支付宝URL并跳转
      const alipayUrl = response.data.alipay_url;
      console.log("支付宝地址："+alipayUrl);
      if (alipayUrl) {
        // 标记已开始支付流程，防止页面刷新后重复执行
        sessionStorage.setItem('paymentStarted', 'true');
        window.open(alipayUrl, '_blank'); // 在新窗口打开支付宝页面
        
        // 立即返回，不执行后续可能引起问题的代码
        return;
      } else {
        // 如果没有返回支付宝URL，则跳转到首页
        router.push('/home'); // 可以根据需要修改跳转路径
      }
    } else {
      ElMessage.error(response.data.msg || '订单提交失败1');
      console.error('订单提交失败2:', response.data.msg);
    }
  } catch (error: any) {
    console.error('提交订单失败3：', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '订单提交失败，请检查网络连接');
    }
  } finally {
    // 重置提交状态
    isSubmitting.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
.settlement-container {
  padding-top: 60px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.settlement-main {
  width: 800px;
  margin: 0 auto;
  padding: 30px 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.settlement-main h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  color: #333;
}

.order-summary {
  padding: 20px;
}

.product-info {
  display: flex;
  gap: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.product-image {
  width: 150px;
  height: 150px;
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

.product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-details h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.product-price {
  font-size: 16px;
  font-weight: bold;
  color: #e74c3c;
  margin: 5px 0;
}

.product-seller, .product-id {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

.confirm-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.submit-order-btn, .cancel-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-order-btn {
  background-color: #e74c3c;
  color: white;
}

.submit-order-btn:hover {
  background-color: #c0392b;
}

.cancel-btn {
  background-color: #95a5a6;
  color: white;
}

.cancel-btn:hover {
  background-color: #7f8c8d;
}

.no-data {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>