<template>
  <div class="register-container">
    <div class="register-form">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <label for="nickname" class="form-label">昵称</label>
          <input
            id="nickname"
            v-model="registerForm.nickname"
            type="text"
            placeholder="请输入昵称"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-row">
          <label for="phone" class="form-label">手机号</label>
          <input
            id="phone"
            v-model="registerForm.phone"
            type="tel"
            placeholder="请输入手机号"
            required
            class="form-input"
          />
        </div>
        

        
        <div class="form-row">
          <label for="password" class="form-label">密码</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-row">
          <label for="confirmPassword" class="form-label">确认密码</label>
          <input
            id="confirmPassword"
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
            class="form-input"
          />
        </div>
        
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="login-link">
        <p>已有账号？<router-link to="/login">点此去登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage } from 'element-plus';

// 定义表单数据类型
interface RegisterForm {
  nickname: string;
  phone: string;
  password: string;
  confirmPassword: string;
}

// 响应式数据
const registerForm = ref<RegisterForm>({
  nickname: '',
  phone: '',
  password: '',
  confirmPassword: ''
});


const isSubmitting = ref(false);
const router = useRouter();

// 验证手机号格式
const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/; //手机号格式验证
  return phoneRegex.test(phone);
};


// 处理注册
const handleRegister = async () => {
  // 验证必填字段
  if (!registerForm.value.nickname.trim()) {
    ElMessage.error('请输入昵称');
    return;
  }

  if (registerForm.value.nickname.trim().length>18) {
    ElMessage.error('超出最大长度');
    return;
  }

  if (!registerForm.value.phone.trim()) {
    ElMessage.error('请输入手机号');
    return;
  }

  // 验证手机号格式
  if (!validatePhone(registerForm.value.phone)) {
    ElMessage.error('请输入正确的手机号格式');
    return;
  }

  if (!registerForm.value.password) {
    ElMessage.error('请输入密码');
    return;
  }

  if (!registerForm.value.confirmPassword) {
    ElMessage.error('请确认密码');
    return;
  }

  // 验证两次密码是否一致
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }

  // 验证密码长度
  if (registerForm.value.password.length < 6) {
    ElMessage.error('密码长度至少为6位');
    return;
  }

  isSubmitting.value = true;

  try {
    // 调试：打印即将发送的数据
    console.log('发送的注册数据:', {
      nickname: registerForm.value.nickname,
      phone: registerForm.value.phone,
      password: registerForm.value.password
    });
    
    // 创建 FormData 对象来发送表单数据，以便后端能正确接收
    const formData = new FormData();
    formData.append('nickname', registerForm.value.nickname);
    formData.append('phone', registerForm.value.phone);
    formData.append('password', registerForm.value.password);
    
    // 发送注册请求
    const response = await request.post('api/auth/sign/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('后端响应:', response.data);

    if (response.data.status === '200') {
      ElMessage.success('注册成功！');
      // 注册成功后跳转到登录页面
      router.push('/login');
    } else {
      ElMessage.error(response.data.msg || '注册失败1');
    }
  } catch (error: any) {
    console.error('注册失败2:', error);
    if (error.response) {
      ElMessage.error(error.response.data.msg || '注册失败3');
    } else {
      ElMessage.error('网络错误，请检查后端服务是否启动');
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.register-form {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.register-form h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.form-label {
  width: 80px;
  margin-right: 15px;
  color: #666;
  font-weight: 500;
  text-align: right;
}

.form-input {
  flex: 1;
  max-width: 200px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.phone-input-group {
  display: flex;
  flex: 1;
  gap: 10px;
  max-width: 200px;
}

.phone-input {
  flex: 2;
}

.code-button {
  width: 120px;
  height: 42px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.submit-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>