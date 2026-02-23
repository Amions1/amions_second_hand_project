<template>
  <div class="chat-overlay" @click="closeChat">
    <div class="chat-window" @click.stop>
      <!-- 聊天窗口头部 -->
      <div class="chat-header">
        <div class="header-info">
          <h3>与 {{ sellerNickname }} 聊天</h3>
          <p class="goods-title">{{ goodsTitle }}</p>
        </div>
        <button class="close-btn" @click="closeChat">×</button>
      </div>

      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.sender === 'me' ? 'sent' : 'received']"
        >
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        <div v-if="messages.length === 0" class="no-messages">
          开始聊天吧...
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { getUserInfo } from '@/utils/auth';

// 定义props
const props = defineProps<{
  sellerId: bigint;
  buyerId: bigint;
  sellerNickname: string;
  goodsTitle: string;
  goodsId: number;
}>();

// 定义emit事件
const emit = defineEmits<{
  close: [];
}>();

// 消息类型定义
interface ChatMessage {
  sender: 'me' | 'other';
  content: string;
  timestamp: Date;
}



// 响应式数据
const messages = ref<ChatMessage[]>([]);
const newMessage = ref<string>('');
const isSending = ref<boolean>(false);
const messagesContainer = ref<HTMLDivElement | null>(null);
let websocket: WebSocket | null = null;

// 关闭聊天窗口
const closeChat = () => {
  // 关闭WebSocket连接
  if (websocket) {
    websocket.close();
    websocket = null;
  }
  emit('close');
};

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) {
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
    messages.value.push(localMessage);
    scrollToBottom();

    // 通过WebSocket发送消息
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        type: 'message',
        content: messageContent,
        timestamp: new Date().toISOString(),
        senderId: Number(props.buyerId),   // 买家ID
        senderName: getUserInfo()?.nickname || '未知用户'  // 添加发送方昵称
      }));
    } else {
      ElMessage.error('连接已断开，无法发送消息');
    }

    // 清空输入框
    newMessage.value = '';
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

// 格式化时间
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
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
const initWebSocket = () => {
  try {
    console.log('WebSocket初始化参数:', {
      buyerId: props.buyerId,
      sellerId: props.sellerId,
      buyerIdType: typeof props.buyerId,
      sellerIdType: typeof props.sellerId
    });
    
    // 生成房间号：先排序买家ID和卖家ID，确保同一对用户始终在同一房间
    const sortedIds = [Number(props.buyerId), Number(props.sellerId)].sort((a, b) => a - b);
    const roomId = `room_${sortedIds[0]}_${sortedIds[1]}`;
    // WebSocket连接地址，添加当前用户ID作为查询参数
    const currentUserInfo = getUserInfo();
    const backendWsUrl = getBackendWsUrl();
    const wsUrl = `${backendWsUrl}/room/${roomId}/?user_id=${currentUserInfo?.user_id || ''}`;
    console.log('正在连接WebSocket:', wsUrl);
    
    websocket = new WebSocket(wsUrl);

    //客户端和服务端刚创建好连接时自动触发
    websocket.onopen = () => {
      console.log('WebSocket连接已建立');
      ElMessage.success('聊天连接已建立');
    };

    //接收到服务端发送来的数据时自动触发onmessage函数
    websocket.onmessage = (event) => {
      console.log('=== WebSocket onmessage 触发 ===');
      console.log('接收到原始数据:', event.data);
      try {
        // 解析服务端发送的JSON数据
        const data = JSON.parse(event.data);
        console.log("data.type:"+data.type);
        console.log("666");
       // console.log('收到消息:', data);
        
        if (data.type === 'message') {
          // 接收到对方的消息
          const receivedMessage: ChatMessage = {
            sender: 'other',
            content: data.content,
            timestamp: new Date(data.timestamp)
          };
          messages.value.push(receivedMessage);
          scrollToBottom();
          
          // 注意：ChatWindow组件主要用于商品详情页的买家-卖家一对一聊天
          // 不需要在此处维护聊天列表，聊天列表的维护应该在message.vue中处理
          console.log(`💬 ChatWindow收到消息: ${data.content}`);
          console.log(`   - 发送方ID: ${data.senderId}`);
          console.log(`   - 当前买家ID: ${Number(props.buyerId)}`);
          console.log(`   - 当前卖家ID: ${Number(props.sellerId)}`);
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

// 组件挂载时初始化
onMounted(() => {
  initWebSocket();
  scrollToBottom();
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
.chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.chat-window {
  width: 500px;
  height: 600px;
  background-color: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background-color: #409eff;
  color: white;
  border-radius: 8px 8px 0 0;
}

.header-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.goods-title {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.no-messages {
  text-align: center;
  color: #999;
  margin: auto;
  font-size: 14px;
}

.message {
  display: flex;
  max-width: 80%;
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
  padding: 15px;
  border-top: 1px solid #eee;
  gap: 10px;
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
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>