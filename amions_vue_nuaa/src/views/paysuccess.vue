<template>
  <div class="pay-success-container">
    <div class="pay-success-card">
      <div class="success-icon">
        <svg t="1617839546139" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2653" width="80" height="80">
          <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64z m193.5 301.7l-210.6 292a31.9 31.9 0 0 1-51.7 0l-125.5-174.1a32 32 0 1 1 52-37.4L480 634.8l189.5-263.1a32 32 0 1 1 52 37.4z" fill="#52c41a" p-id="2654"></path>
        </svg>
      </div>
      <h2 class="success-title">支付成功</h2>
      <p class="success-desc">您的订单已支付成功，感谢您的购买！</p>
      <div class="order-info">
        <p>订单编号：<span class="order-id">{{ order_id }}</span></p>
        <p>支付金额：<span class="amount">¥{{ price }}</span></p>
        <p>支付时间：<span class="time">{{ time }}</span></p>
      </div>
      <div class="actions">
        <el-button type="primary" @click="viewOrder" size="large">查看订单</el-button>
        <el-button @click="goHome" size="large">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();

// 初始化默认值
const order_id = ref<string>('未知');
const price = ref<string>('0.00');
const time = ref<string>(new Date().toLocaleString());

onMounted(() => {

  // 从Vue Router的查询参数中获取支付信息
  const orderId = route.query.order_id;
  const amount = route.query.price;
  const payTime = route.query.time;
  
  console.log("order_id:" + orderId);
  console.log("price:" + amount);
  console.log("time:" + payTime);
  
  // 更新响应式变量
  if (orderId) order_id.value = String(orderId);
  if (amount) price.value = String(amount);
  if (payTime) time.value = String(payTime);
  
  // 支付已完成，清除支付标记
  sessionStorage.removeItem('paymentStarted');
});

const viewOrder = () => {
  // 跳转到订单详情页面，这里可以根据实际需求调整
  ElMessage.success('跳转到订单详情页面');
  router.push('/profile'); // 或者跳转到具体的订单详情页
};

const goHome = () => {
  router.push('/home');
};
</script>

<style scoped>
.pay-success-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.pay-success-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  padding: 40px;
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success-icon {
  margin-bottom: 24px;
}

.success-title {
  font-size: 28px;
  color: #52c41a;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.success-desc {
  font-size: 16px;
  color: #666;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.order-info {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin: 0 0 32px 0;
  text-align: left;
}

.order-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #333;
}

.order-info span {
  font-weight: 600;
  color: #333;
}

.order-id {
  color: #1890ff;
}

.amount {
  color: #f5222d;
  font-size: 16px;
}

.time {
  color: #888;
}

.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.actions .el-button {
  min-width: 120px;
}

@media (max-width: 768px) {
  .pay-success-card {
    margin: 10px;
    padding: 30px 20px;
  }
  
  .success-title {
    font-size: 24px;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>