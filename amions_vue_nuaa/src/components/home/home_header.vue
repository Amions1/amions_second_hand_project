<template>
  <!-- 导航栏容器（固定顶部） -->
  <header class="header-nav">
    <div class="nav-wrapper">
      <!-- 左侧：Logo -->
      <div class="logo-box">
        <!-- Logo图片 + 点击返回首页 -->
        <router-link to="/home">
          <img
            src="@/components/home/icons/1.jpg"
            alt="二手优品 Logo"
            class="logo-img"
          >
        </router-link>
      </div>

      <!-- 中间：搜索框 -->
      <div class="search-box">
        <input
          type="text"
          v-model="searchKey"
          placeholder="搜索闲置商品，如：笔记本、沙发..."
          class="search-input"
          @keyup.enter="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">🏸搜索</button>
      </div>

      <!-- 右侧：用户信息 -->
      <div class="user-box">
        <!-- 显示登录用户名，无则提示登录 -->
        <div class="user-info" v-if="userInfo.nickname">
          <div class="user-actions-row">
            <!-- 消息按钮 -->
            <el-button
              type="primary"
              class="message-btn"
              @click="goToMessage"
            >
              💬消息
            </el-button>
            <!-- AI助手组件 -->
            <AIChat class="ai-chat-component" />
            <!-- 用户欢迎文字 -->
            <span class="username" @mouseover="showDropdown = true">用户 <span style="color: red">{{ userInfo.nickname }}</span>,欢迎您!</span>
            <div class="user-dropdown" v-if="showDropdown" @mouseleave="showDropdown = false">
              <ul class="dropdown-menu">
                <li class="dropdown-item" @click="goToProfile">
                  <span class="dropdown-icon">👤</span> 个人信息
                </li>
                <li class="dropdown-item" @click="goToPublish">
                  <span class="dropdown-icon">📝</span> 我要发布
                </li>
                <li class="dropdown-item" @click="goToManager" v-if="userInfo.role===2 ||userInfo.role===3">
                  <span class="dropdown-icon">⚙️</span> 管理员
                </li>
                <li class="dropdown-item" @click="handleLogout">
                  <span class="dropdown-icon">🚪</span> 退出登录
                </li>
              </ul>
            </div>
          </div>
        </div>
        <router-link to="/login" class="login-btn" v-else>
          登录/注册
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {ElMessage,ElMessageBox} from "element-plus";
import { addUserInfoListener } from '@/utils/auth'
import request from '@/utils/request'
import AIChat from '@/components/aichat/aichat.vue'

// 1. 路由实例（跳转/退出）
const router = useRouter()

// 2. 搜索关键词响应式
const searchKey = ref('')

// 3. 用户信息（从SessionStorage读取）
const userInfo = ref({
  nickname: '',
  user_id:'',
  phone:'',
  role:''
})

// 4. 控制下拉菜单显示
const showDropdown = ref(false)

// 5. 页面加载时读取登录信息
onMounted(() => {
  const storedUser = sessionStorage.getItem('userInfo')
  if (storedUser) {
    // 👇 修复：直接赋值整个解析后的对象，而不是只提取nickname
    userInfo.value = JSON.parse(storedUser);
    console.log("右上角信息:", userInfo.value.nickname)
    console.log("右上角信息:", userInfo.value.user_id)
    console.log("右上角信息:", userInfo.value.phone)
  }
  
  // 订阅用户信息更新事件
  unsubscribe = addUserInfoListener(handleUserInfoUpdate);
})

// 取消订阅函数
let unsubscribe = null

// 处理用户信息更新
const handleUserInfoUpdate = (newUserInfo) => {
  // 更新本地状态
  userInfo.value.nickname = newUserInfo.nickname
}

// 组件卸载时取消订阅
onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe();
  }
})

// 6. 搜索功能
const handleSearch = async () => {
  if (!searchKey.value.trim()) {
    ElMessage.warning('请输入搜索关键词！')
    return
  }
  
  try {
    // 调用后端搜索接口
    const response = await request.get(`api/goods/search/?keyword=${encodeURIComponent(searchKey.value.trim())}`);
    
    if (response.data.status === '200') {
      // 搜索成功，触发搜索结果展示
      // 使用replace确保即使是相同的搜索词也会触发更新
      // 添加时间戳参数以确保路由变化
      router.replace({ 
        path: '/home', 
        query: { 
          search: searchKey.value.trim(),
          t: Date.now().toString()
        } 
      });
      ElMessage.success(`找到 ${response.data.data?.length || 0} 条相关结果`);
    } else {
      ElMessage.error(response.data.msg || '搜索失败');
    }
  } catch (error) {
    console.error('搜索请求失败：', error);
    if (error.response?.status === 401) {
      ElMessage.error('登录信息已过期，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '搜索失败，请稍后重试');
    }
  }
}

// 7. 个人信息页面跳转
const goToProfile = () => {
  // 这里可以跳转到个人信息页面
  showDropdown.value = false;
   router.push('/profile') // 如果有个人资料页面
}

// 8. 发布页面跳转
const goToPublish = () => {
  showDropdown.value = false;
  router.push('/publish') // 跳转到发布页面
}

const goToManager = () => {
  showDropdown.value = false;
  router.push('/manager') // 跳转到发布页面
}

// 消息页面跳转
const goToMessage = () => {
  router.push('/message') // 跳转到消息页面
}

// 9. 退出登录功能
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    // 确认后的操作
    sessionStorage.removeItem('userInfo')
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    userInfo.value = { nickname: '' }
    showDropdown.value = false
    router.push('/login')
    ElMessage({
      message: '退出登录成功',
      type: 'success',
      plain: true,
    })
  } catch {
    // 取消操作，不做任何事情
  }
}


</script>

<style scoped>
/* 导航栏整体样式 */
.header-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 999; /* 确保导航栏在最上层 */
}

/* 导航栏内容容器（居中限制宽度） */
.nav-wrapper {
  width: 1200px;
  height: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
}

/* 左侧Logo样式 */
.logo-box {
  display: flex;
  align-items: center;
}
.logo-img {
  width: 160px;
  height: 60px;
  border-radius: 4px; /* 长方形Logo */
  object-fit: cover;
  margin-right: 8px;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
/* 去除router-link默认样式 */
.logo-box a {
  text-decoration: none;
  color: inherit;
}

/* 中间搜索框样式 */
.search-box {
  flex: 1;
  max-width: 600px;
  margin: 0 20px;
  display: flex;
  align-items: center;
}
.search-input {
  flex: 1;
  height: 40px;
  padding: 0 15px;
  border: 1px solid #ddd;
  border-radius: 20px 0 0 20px;
  outline: none;
  font-size: 14px;
}
.search-input:focus {
  border-color: #409eff; /* 聚焦时高亮 */
}
.search-btn {
  height: 40px;
  width: 80px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 0 20px 20px 0;
  cursor: pointer;
  font-size: 14px;
}
.search-btn:hover {
  background-color: #66b1ff;
}

/* 右侧用户信息样式 */
.user-box {
  display: flex;
  align-items: center;
  position: relative; /* 用于下拉菜单定位 */
}

.user-info {
  position: relative;
}

.user-dropdown-wrapper {
  position: relative;
}

.username {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  margin-right: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.username:hover {
  background-color: #f5f7fa;
}

/* 下拉菜单样式 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
  z-index: 1000;
  min-width: 160px;
  margin-top: 4px;
}

.dropdown-menu {
  list-style: none;
  margin: 0;
  padding: 8px 0;
}

.dropdown-item {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

/* 用户操作行 - 水平排列 */
.user-actions-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 消息按钮样式 */
.message-btn {
  cursor: pointer;
  margin: 0;
}

/* AI助手组件样式 */
.ai-chat-component {
  margin: 0;
}

/* 用户欢迎文字样式 */
.username {
  margin-left: 10px;
}

.dropdown-icon {
  margin-right: 8px;
  font-size: 14px;
}

/* 未登录时的登录按钮（原有样式不变） */
.login-btn {
  text-decoration: none;
  padding: 6px 15px;
  background-color: #f56c6c;
  color: white;
  border-radius: 20px;
  font-size: 14px;
}
.login-btn:hover {
  background-color: #f78989;
}
</style>