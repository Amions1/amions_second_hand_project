<template>
  <div class="message-container">
    <!-- 引入导航栏组件 -->
    <Profile_header />
    
    <div class="message-main">
      <div class="message-layout">
        <!-- 左侧：聊天用户列表 -->
        <div class="user-list">
          <div class="user-list-header">
            <h3>聊天列表</h3>
          </div>
          <div class="user-list-content">
            <!-- 用户列表项 -->
            <div 
              v-for="user in chatUsers" 
              :key="user.id"
              :class="['user-item', { active: user.id === activeUserId }]"
              @click="selectUser(user)"
            >
              <div class="user-info">
                <div class="user-name">{{ user.name }}</div>
                <div class="user-last-message">{{ user.lastMessage }}</div>
              </div>
              <div class="user-time">{{ formatTime(user.lastTime) }}</div>
            </div>
            
            <!-- 空状态 -->
            <div v-if="chatUsers.length === 0" class="empty-state">
              暂无聊天记录
            </div>
          </div>
        </div>

        <!-- 中间：聊天主区域 -->
        <div class="chat-main">
          <!-- 聊天头部 -->
          <div class="chat-header" v-if="activeUser">
            <div class="chat-user-info">
              <div class="chat-user-details">
                <h4>{{ activeUser.name }}</h4>
              </div>
            </div>
          </div>

          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="messagesContainer" v-if="activeUser">
            <div 
              v-for="(message, index) in currentMessages" 
              :key="index" 
              :class="['message', message.sender === 'me' ? 'sent' : 'received']"
            >
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatMessageTime(message.timestamp) }}</div>
              </div>
            </div>
            
            <!-- 无消息状态 -->
            <div v-if="currentMessages.length === 0" class="no-messages">
              还没有消息，开始聊天吧...
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area" v-if="activeUser">
            <input 
              v-model="newMessage" 
              type="text" 
              placeholder="输入消息..." 
              class="message-input"
              @keyup.enter="sendMessage"
              :disabled="isSending"
            />
            <button 
              class="send-btn" 
              @click="sendMessage" 
              :disabled="!newMessage.trim() || isSending"
            >
              {{ isSending ? '发送中...' : '发送' }}
            </button>
          </div>

          <!-- 未选择用户提示 -->
          <div v-else class="select-user-prompt">
            <p>请选择一个用户开始聊天</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import Profile_header from "@/components/profile/profile_header.vue";
import { isAuthenticated, getUserInfo } from "@/utils/auth";
import request from '@/utils/request';

// 路由实例
const router = useRouter();

// 检查认证状态
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('请先登录');
    router.push('/login');
    return false;
  }
  return true;
};

// 用户信息接口定义
interface ChatUser {
  id: number;
  name: string;
  lastMessage: string;
  lastTime: Date;
}

// 消息接口定义
interface ChatMessage {
  sender: 'me' | 'other';
  content: string;
  timestamp: Date;
}

// 扩展消息接口，包含发送方信息
interface ExtendedChatMessage extends ChatMessage {
  senderId?: number;
  senderName?: string;
}

// 响应式数据
const chatUsers = ref<ChatUser[]>([]);

const activeUserId = ref<number | null>(null);
const activeUser = ref<ChatUser | null>(null);
const currentMessages = ref<ChatMessage[]>([]);
const newMessage = ref<string>('');
const isSending = ref<boolean>(false);
const messagesContainer = ref<HTMLDivElement | null>(null);
let websocket: WebSocket | null = null;

// 选择用户
const selectUser = (user: ChatUser) => {
  console.log('👥 selectUser 被调用，选择的用户:', user);
  activeUserId.value = user.id;
  activeUser.value = user;

  // 关闭之前的WebSocket连接
  if (websocket) {
    websocket.close();
    websocket = null;
  }

  // 初始化WebSocket连接
  initWebSocket(user.id);

  // 这里应该从后端获取该用户的聊天记录
  loadChatHistory(user.id);
};

// 获取后端WebSocket基础URL
const getBackendWsUrl = (): string => {
  // 检查当前页面URL以确定使用哪个后端地址
  const currentUrl = window.location.href;
  if (currentUrl.includes('vicp.fun')) {
    // 内网穿透环境
    return 'ws://69mdjw853446.vicp.fun:37276';
  } else {
    // 本地开发环境
    return 'ws://192.168.31.238:8000';
  }
};

// 初始化WebSocket连接
const initWebSocket = (sellerId: number) => {
  try {
    // 获取当前用户信息（买家）
    const userInfo = getUserInfo();
    if (!userInfo) {
      ElMessage.error('用户信息获取失败');
      return;
    }

    // 生成房间号：先排序买家ID和卖家ID，确保同一对用户始终在同一房间
    const sortedIds = [Number(userInfo.user_id), sellerId].sort((a, b) => a - b);
    const roomId = `room_${sortedIds[0]}_${sortedIds[1]}`;
    // WebSocket连接地址，添加当前用户ID作为查询参数
    const backendWsUrl = getBackendWsUrl();
    const wsUrl = `${backendWsUrl}/room/${roomId}/?user_id=${userInfo.user_id || ''}`;
    console.log('正在连接WebSocket:', wsUrl);

    websocket = new WebSocket(wsUrl);

    //客户端和服务端刚创建好连接时自动触发
    websocket.onopen = () => {
      console.log('WebSocket连接已建立');
      ElMessage.success('聊天连接已建立');
    };

    //接收到服务端发送来的数据时自动触发onmessage函数
    websocket.onmessage = (event) => {
      try {
        // 解析服务端发送的JSON数据
        const data = JSON.parse(event.data);
        console.log('message.vue收到消息:', data);
        if (data.type === 'message') {
          // 接收到对方的消息
          const receivedMessage: ExtendedChatMessage = {
            sender: 'other',
            content: data.content,
            timestamp: new Date(data.timestamp),
            senderId: data.senderId, // 假设后端会发送发送方ID
            senderName: data.senderName || '未知用户' // 假设后端会发送发送方昵称
          };

          // 将消息添加到当前聊天记录
          currentMessages.value.push(receivedMessage);
          scrollToBottom();


          // 自动将消息发送方添加到聊天列表中（如果不存在）
          // 注意：只有当发送方不是当前用户自己时才添加
          const currentUserInfo = getUserInfo();
          console.log('=== 消息处理调试信息 ===');
          console.log(`当前用户信息:`, currentUserInfo);
          console.log(`消息发送方ID: ${data.senderId}`);
          console.log(`当前用户ID: ${currentUserInfo?.user_id}`);
          console.log(`类型比较 - senderId类型: ${typeof data.senderId}, user_id类型: ${typeof currentUserInfo?.user_id}`);

          // 注意：需要确保类型一致性进行比较
          const currentUserId = Number(currentUserInfo?.user_id);
          const messageSenderId = Number(data.senderId);

          if (data.senderId && messageSenderId !== currentUserId) {
            console.log(`📥 收到来自其他用户的消息，准备添加到聊天列表`);
            console.log(`   - 消息发送方ID: ${messageSenderId}`);
            console.log(`   - 当前用户ID: ${currentUserId}`);
            addOrUpdateChatUser(messageSenderId, data.senderName || '未知用户', data.content);
          } else if (messageSenderId === currentUserId) {
            console.log(`📝 这是用户自己发送的消息，不需要添加到聊天列表`);
          }
          console.log('=====================');
        } else if (data.type === 'system') {
          // 系统消息
          ElMessage.info(data.content);
        }
      } catch (error) {
        console.error('解析消息失败:', error);
        console.error('原始数据:', event.data);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket连接错误:', error);
      ElMessage.error('聊天连接出现错误');
    };

    //服务端主动断开连接时触发
    websocket.onclose = () => {
      console.log('WebSocket连接已关闭');
    };
  } catch (error) {
    console.error('初始化WebSocket失败:', error);
    ElMessage.error('无法建立聊天连接');
  }
};

// 加载聊天历史
const loadChatHistory = async (userId: number) => {
  try {
    // 获取当前用户信息
    const userInfo = getUserInfo();
    if (!userInfo) {
      scrollToBottom();
      return;
    }

    console.log('开始加载聊天历史...');
    console.log('当前用户ID:', userInfo.user_id);
    console.log('目标用户ID:', userId);
    
    // 生成房间号，与WebSocket保持一致
    const sortedIds = [Number(userInfo.user_id), userId].sort((a, b) => a - b);
    const roomName = `room_${sortedIds[0]}_${sortedIds[1]}`;
    console.log('生成的房间号:', roomName);
    const response = await request.get(`api/chat/history/${roomName}/`);
    console.log('API响应数据:', response.data);

    if (response.data && response.data.status === '200') {
      const historyData = response.data.data || [];
      console.log('✅ 成功获取聊天历史数据:', historyData);
      
      // 转换数据格式以适配现有currentMessages结构
      const formattedMessages = historyData.map((msg: any) => ({
        sender: msg.sender_id == userInfo.user_id ? 'me' : 'other',
        content: msg.content,
        timestamp: new Date(msg.created_at || msg.timestamp)
      }));

      // 更新聊天记录
      currentMessages.value = formattedMessages;
      console.log(`✅ 成功加载 ${formattedMessages.length} 条聊天记录`);
      
      // 打印详细信息
      formattedMessages.forEach((msg: ChatMessage, index: number) => {
        console.log(`消息${index + 1}: 发送方=${msg.sender}, 内容="${msg.content}"`);
      });
    } else {
      console.error('❌ 获取聊天历史失败，响应状态:', response.data?.status);
      console.error('❌ 错误信息:', response.data?.msg);
      // API失败时使用模拟数据
      currentMessages.value = [
        {
          sender: 'other',
          content: '你好，这个商品还在吗？',
          timestamp: new Date(Date.now() - 3600000)
        }
      ];
    }
  } catch (error: any) {
    console.error('❌ 加载聊天历史时发生错误:', error);
    console.error('❌ 错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    
    // 网络错误时使用模拟数据
    console.log('⚠️ 使用模拟数据作为后备方案');
    currentMessages.value = [
      {
        sender: 'other',
        content: '你好，这个商品还在吗？',
        timestamp: new Date(Date.now() - 3600000)
      }
    ];
  } finally {
    scrollToBottom();
  }
};

// 添加或更新聊天用户
const addOrUpdateChatUser = (userId: number, userName: string, lastMessage: string) => {
  const existingUserIndex = chatUsers.value.findIndex(user => user.id === userId);

  if (existingUserIndex !== -1) {
    // 用户已存在，更新最后消息和时间
    console.log(`用户已存在(ID=${userId})，更新最后消息`);
    chatUsers.value[existingUserIndex].lastMessage = lastMessage;
    chatUsers.value[existingUserIndex].lastTime = new Date();
  } else {
    // 用户不存在，添加新用户到聊天列表
    const newUser: ChatUser = {
      id: userId,
      name: userName,
      lastMessage: lastMessage,
      lastTime: new Date(),
    };
    chatUsers.value.unshift(newUser); // 添加到列表顶部
    console.log(`✅ 成功将用户添加到聊天列表:`);
    console.log(`   - 用户ID: ${userId}`);
    console.log(`   - 用户昵称: ${userName}`);
    console.log(`   - 消息内容: ${lastMessage}`);
    console.log(`   - 当前聊天列表总人数: ${chatUsers.value.length}`);
  }

  // 打印当前完整的聊天用户列表
  console.log('当前chatUsers列表:', chatUsers.value.map(user => ({
    id: user.id,
    name: user.name,
    lastMessage: user.lastMessage
  })));
  console.log(`===============\n`);
};

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value || !activeUser.value) {
    return;
  }

  isSending.value = true;
  const messageContent = newMessage.value.trim();

  try {
    // 添加到本地消息列表（立即显示）
    const localMessage: ChatMessage = {
      sender: 'me',
      content: messageContent,
      timestamp: new Date()
    };
    currentMessages.value.push(localMessage);
    scrollToBottom();

    // 通过WebSocket发送消息
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      // 获取当前买家信息
      const buyerInfo = getUserInfo();
      if (!buyerInfo) {
        ElMessage.error('用户信息获取失败');
        return;
      }

      websocket.send(JSON.stringify({
        type: 'message',
        content: messageContent,
        timestamp: new Date().toISOString(),
        senderId: Number(buyerInfo.user_id),   // 买家ID，确保是数字类型
        senderName: buyerInfo.nickname || '未知用户'  // 添加发送方昵称
      }));
    } else {
      ElMessage.error('连接已断开，无法发送消息');
    }

    // 清空输入框
    newMessage.value = '';

    // 更新用户列表中的最后消息
    const userIndex = chatUsers.value.findIndex(u => u.id === activeUser.value?.id);
    if (userIndex !== -1) {
      chatUsers.value[userIndex].lastMessage = messageContent;
      chatUsers.value[userIndex].lastTime = new Date();
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    ElMessage.error('发送消息失败');
  } finally {
    isSending.value = false;
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 格式化时间（用于用户列表）
const formatTime = (date: Date): string => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return `${days}天前`;
};

// 格式化消息时间
const formatMessageTime = (date: Date): string => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 添加加载聊天用户列表的函数
const loadChatUsersFromDatabase = async () => {
  try {
    const userInfo = getUserInfo();
    if (!userInfo) {
      console.log('无法获取用户信息，跳过加载聊天列表');
      return;
    }


    // 使用项目配置的request工具调用后端API，传递用户ID参数
    const response = await request.get(`api/chat/users/?user_id=${userInfo.user_id}`);


    if (response.data && response.data.status === '200') {
      const userData = response.data.data || [];
      console.log('✅ 成功获取聊天用户数据:', userData);
      
      // 转换数据格式以适配现有chatUsers结构
      const formattedUsers = userData.map((user: any) => ({
        id: user.id,
        name: user.nickname || user.name || '未知用户',
        lastMessage: user.last_message || '暂无消息',
        lastTime: new Date(user.last_time || Date.now()),
        online: user.online || false
      }));

      // 更新chatUsers列表
      chatUsers.value = formattedUsers;
      console.log(`✅ 成功加载 ${formattedUsers.length} 个聊天用户`);
      
      // 打印详细信息
      formattedUsers.forEach((user: ChatUser, index: number) => {
        console.log(`用户${index + 1}: ID=${user.id}, 姓名=${user.name}, 最后消息="${user.lastMessage}"`);
      });
    } else {
      console.error('❌ 获取聊天用户列表失败，响应状态:', response.data?.status);
      console.error('❌ 错误信息:', response.data?.msg);
      // 如果API失败，保持现有空列表状态
    }
  } catch (error: any) {
    console.error('❌ 加载聊天用户列表时发生错误:', error);
    console.error('❌ 错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    });
    
    // 如果是400错误，显示具体的错误信息
    if (error.response?.status === 400) {
      const errorMsg = error.response?.data?.msg || error.response?.data?.detail || '请求参数错误';
      console.error('❌ 400错误详细信息:', error.response?.data);
      ElMessage.error(`加载聊天列表失败: ${errorMsg}`);
    } else {
      // 其他网络错误
      ElMessage.error('加载聊天列表失败，请检查网络连接');
    }
  }
};

// 在Message.vue中添加全局消息监听器
const createGlobalMessageListener = () => {
  try {
    const userInfo = getUserInfo();
    if (!userInfo) return null;

    // 创建个人消息监听连接
    const personalRoom = `user_${userInfo.user_id}`;
    const backendWsUrl = getBackendWsUrl();
    const wsUrl = `${backendWsUrl}/room/${personalRoom}/?user_id=${userInfo.user_id}`;
    console.log('正在创建全局消息监听器:', wsUrl);

    const globalWs = new WebSocket(wsUrl);

    globalWs.onopen = () => {
      console.log('✅ 全局消息监听器连接已建立');
    };

    globalWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📡 全局消息监听器收到数据:', data);
        console.log('📡 原始数据类型:', typeof event.data);
        console.log('📡 数据内容:', event.data);

        if (data.type === 'message') {
          console.log('=== 消息处理开始 ===');
          console.log('消息类型检查通过');

          // 处理个人消息通知
          const senderId = Number(data.senderId);
          const currentUserId = Number(userInfo.user_id);

          console.log('用户ID信息:');
          console.log('  - senderId:', data.senderId, '类型:', typeof data.senderId);
          console.log('  - currentUserId:', userInfo.user_id, '类型:', typeof userInfo.user_id);
          console.log('  - 转换后 senderId:', senderId, '类型:', typeof senderId);
          console.log('  - 转换后 currentUserId:', currentUserId, '类型:', typeof currentUserId);
          console.log('  - 是否为不同用户:', senderId !== currentUserId);

          // 只处理发送给当前用户的消息
          if (senderId !== currentUserId) {
            console.log(`📥 收到来自用户${senderId}的消息，准备添加到聊天列表`);
            console.log('调用参数:');
            console.log('  - userId:', senderId);
            console.log('  - userName:', data.senderName || '未知用户');
            console.log('  - lastMessage:', data.content);

            addOrUpdateChatUser(senderId, data.senderName || '未知用户', data.content);
          } else {
            console.log('📝 这是自己发送的消息，不添加到列表');
          }
          console.log('=== 消息处理结束 ===');
        } else {
          console.log('消息类型不是message，当前类型:', data.type);
        }
      } catch (error) {
        console.error('解析全局消息失败:', error);
        console.error('原始数据:', event.data);
      }
    };

    globalWs.onerror = (error) => {
      console.error('全局消息监听器连接错误:', error);
    };

    globalWs.onclose = () => {
      console.log('全局消息监听器连接已关闭');
    };

    return globalWs;
  } catch (error) {
    console.error('创建全局消息监听器失败:', error);
    return null;
  }
};


// 页面加载时检查认证并初始化
onMounted(async () => {
  console.log('=== Message页面初始化开始 ===');
  
  if (!checkAuthentication()) {
    console.log('❌ 认证失败，终止初始化');
    return;
  }

  console.log('✅ 用户认证通过，开始加载数据');

  // 👇 添加：从数据库加载聊天用户列表
  await loadChatUsersFromDatabase();

  // 创建全局消息监听器
  createGlobalMessageListener();

  // 页面加载时不需要建立WebSocket连接
  // WebSocket连接会在用户点击聊天列表项时建立
  console.log('Message页面初始化完成');
  console.log('=== Message页面初始化结束 ===');
});

// 组件卸载时清理
onUnmounted(() => {
  if (websocket) {
    websocket.close();
    websocket = null;
  }
});
</script>

<style scoped>
.message-container {
  padding-top: 60px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.message-main {
  width: 1200px;
  margin: 0 auto;
  padding: 20px 10px;
}

.message-layout {
  display: flex;
  height: calc(100vh - 120px);
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
}

/* 左侧用户列表样式 */
.user-list {
  width: 300px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.user-list-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
}

.user-list-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.user-list-content {
  flex: 1;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-item:hover {
  background-color: #f5f7fa;
}

.user-item.active {
  background-color: #e3f2fd;
  border-left: 3px solid #409eff;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-last-message {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-time {
  font-size: 11px;
  color: #999;
  margin-left: 8px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 14px;
}

/* 中间聊天区域样式 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
}

.chat-user-info {
  display: flex;
  align-items: center;
}

.chat-user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.chat-user-details h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 16px;
}
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.select-user-prompt {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
}

.no-messages {
  text-align: center;
  color: #999;
  margin: auto;
  font-size: 14px;
}

.message {
  display: flex;
  max-width: 70%;
}

.message.sent {
  align-self: flex-end;
  justify-content: flex-end;
}

.message.received {
  align-self: flex-start;
  justify-content: flex-start;
}

.message-content {
  padding: 10px 15px;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.sent .message-content {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.received .message-content {
  background-color: #f1f1f1;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-text {
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 5px;
  text-align: right;
}

.message.received .message-time {
  text-align: left;
}

.chat-input-area {
  display: flex;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  gap: 10px;
  background-color: white;
}

.message-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.3s;
}

.message-input:focus {
  border-color: #409eff;
}

.message-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.send-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 滚动条样式 */
.user-list-content::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.user-list-content::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.user-list-content::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.user-list-content::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>