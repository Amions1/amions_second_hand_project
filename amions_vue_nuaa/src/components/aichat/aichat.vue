<script setup>
import { ref, computed, nextTick } from 'vue'
import { ElMessage, ElButton } from 'element-plus'
import { Close, Promotion } from '@element-plus/icons-vue'

// 控制聊天窗口显示/隐藏
const isChatOpen = ref(false)

// 用户输入的消息
const userInput = ref('')

// 消息列表
const messages = ref([
  { type: 'ai', content: '你好！我是AI智能助手小小烽，有什么可以帮你的吗？' }
])

// 是否正在加载（等待AI回复）
const isLoading = ref(false)

// 获取当前登录用户ID
const userId = computed(() => {
  const storedUser = sessionStorage.getItem('userInfo')
  if (storedUser) {
    const userInfo = JSON.parse(storedUser)
    return userInfo.user_id || ''
  }
  return ''
})

// 切换聊天窗口显示状态
const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  if (isChatOpen.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 关闭聊天窗口
const closeChat = () => {
  isChatOpen.value = false
}

// 发送消息到AI
const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message) {
    ElMessage.warning('请输入消息内容')
    return
  }

  // 添加用户消息到列表
  messages.value.push({ type: 'user', content: message })
  userInput.value = ''
  isLoading.value = true

  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })

  try {
    const response = await sendMessageToAI(message, userId.value)
    // 添加AI回复到列表
    messages.value.push({ type: 'ai', content: response })
  } catch (error) {
    ElMessage.error(error.message || 'AI回复失败，请稍后重试')
    messages.value.push({ type: 'ai', content: '抱歉，我遇到了一些问题，请稍后再试。' })
  } finally {
    isLoading.value = false
    await nextTick(() => {
      scrollToBottom()
    })
  }
}

// 获取后端基础URL（与request.js保持一致）
const getBaseUrl = () => {
  const hostname = window.location.hostname
  const isLocalhost = /localhost|127\.0\.0\.1/.test(hostname)
  const isLocalNetwork = /^192\.168\./.test(hostname)

  if (isLocalhost) {
    return 'http://127.0.0.1:8000'
  } else if (isLocalNetwork) {
    return `http://${hostname}:8000`
  } else {
    return 'http://69mdjw853446.vicp.fun:37276'
  }
}

// 向后端发送请求
async function sendMessageToAI(message, userId) {
  const baseUrl = getBaseUrl()

  const response = await fetch(`${baseUrl}/api/aichat/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      user_id: userId || undefined
    })
  })

  const data = await response.json()
  if (data.status === '200') {
    return data.data.response
  } else {
    throw new Error(data.msg || '请求失败')
  }
}

// 处理回车键发送
const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 滚动消息列表到底部
const scrollToBottom = () => {
  const messageList = document.querySelector('.message-list')
  if (messageList) {
    messageList.scrollTop = messageList.scrollHeight
  }
}
</script>

<template>
  <div class="ai-chat-wrapper">
    <!-- AI助手按钮 -->
    <el-button
      type="primary"
      class="ai-chat-btn"
      @click="toggleChat"
      :class="{ 'is-active': isChatOpen }"
    >
      <span class="ai-icon">🤖</span>
      <span>AI助手</span>
    </el-button>

    <!-- 聊天窗口 -->
    <transition name="chat-fade">
      <div v-if="isChatOpen" class="chat-window">
        <!-- 窗口头部 -->
        <div class="chat-header">
          <div class="header-left">
            <span class="header-icon">🤖</span>
            <span class="header-title">AI智能助手小小烽</span>
          </div>
          <el-icon class="close-btn" @click="closeChat"><Close /></el-icon>
        </div>

        <!-- 消息列表 -->
        <div class="message-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-item"
            :class="msg.type"
          >
            <div class="message-avatar">
              <span v-if="msg.type === 'ai'">🤖</span>
              <span v-else>我</span>
            </div>
            <div class="message-content">
              <div class="message-bubble">{{ msg.content }}</div>
            </div>
          </div>
          <!-- 加载状态 -->
          <div v-if="isLoading" class="message-item ai loading">
            <div class="message-avatar">
              <span>🤖</span>
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <span class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-wrapper">
            <textarea
              v-model="userInput"
              placeholder="请输入您的问题..."
              class="chat-input"
              @keydown="handleKeyDown"
              rows="1"
            ></textarea>
            <el-button
              type="primary"
              class="send-btn"
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!userInput.trim()"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.ai-chat-wrapper {
  position: relative;
  display: inline-block;
}

/* AI助手按钮样式 - 与消息按钮风格统一 */
.ai-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  height: 32px;
  font-size: 14px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.ai-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.ai-chat-btn.is-active {
  background-color: #66b1ff;
}

.ai-icon {
  font-size: 16px;
  line-height: 1;
}

/* 聊天窗口样式 */
.chat-window {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 380px;
  height: 500px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1001;
}

/* 窗口头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 20px;
  line-height: 1;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.message-item.ai .message-avatar {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.message-item.user .message-avatar {
  background-color: #67c23a;
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-item.ai .message-bubble {
  background-color: #ffffff;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

/* 加载动画 */
.loading-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: #909399;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 20px;
  background-color: #ffffff;
  border-top: 1px solid #ebeef5;
}

.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  min-height: 40px;
  max-height: 100px;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #409eff;
}

.chat-input::placeholder {
  color: #c0c4cc;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 动画效果 */
.chat-fade-enter-active,
.chat-fade-leave-active {
  transition: all 0.3s ease;
}

.chat-fade-enter-from,
.chat-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* 滚动条样式 */
.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
}
</style>