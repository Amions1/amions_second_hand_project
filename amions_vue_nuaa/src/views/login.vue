<template>
  <div class="login-background">
    <div class="login-container">
      <h1>阿烽二手优品 - 登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-item">
          <label>手机号：</label>
          <input
            type="text"
            v-model="loginForm.phone"
            placeholder="请输入手机号"
            required
          >
        </div>
        <div class="form-item">
          <label>密码：</label>
          <input
            type="password"
            v-model="loginForm.password"
            placeholder="请输入密码"
            required
          >
        </div>
        <button type="submit" class="login-btn">登录</button>
      </form>
      <div class="links-container">
        <p>还没有账号？<router-link to="/sign">点我去注册</router-link></p>
        <p class="forgot-password-link" @click="showForgetDialog = true">忘记密码？</p>
      </div>
    </div>
  </div>

  <!-- 忘记密码对话框 -->
  <el-dialog
    v-model="showForgetDialog"
    title="忘记密码"
    width="400px"
    :before-close="handleClose"
  >
    <el-form 
      :model="forgetForm" 
      :rules="forgetRules" 
      ref="forgetFormRef"
      label-width="80px"
    >
      <el-form-item label="手机号" prop="phone">
        <el-input 
          v-model="forgetForm.phone" 
          placeholder="请输入手机号"
          maxlength="11"
        />
      </el-form-item>
      <el-form-item label="新密码" prop="password">
        <el-input 
          v-model="forgetForm.password" 
          type="password"
          placeholder="请输入新密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input 
          v-model="forgetForm.confirmPassword" 
          type="password"
          placeholder="请再次输入新密码"
          show-password
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          提交
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import request from '@/utils/request'
import { ref, reactive } from 'vue'
import { updateUserInfo } from '@/utils/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'


const router = useRouter()

// Vue 3 中用ref替代data
const loginForm = ref({
  phone: '',
  password: ''
})

// 忘记密码相关
const showForgetDialog = ref(false)
const submitLoading = ref(false)
const forgetFormRef = ref()

// 忘记密码表单数据
const forgetForm = reactive({
  phone: '',
  password: '',
  confirmPassword: ''
})

// 手机号验证规则
const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号格式'))
  } else {
    callback()
  }
}

// 密码一致性验证
const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== forgetForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const forgetRules = {
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 关闭对话框
const handleClose = () => {
  showForgetDialog.value = false
  // 重置表单
  forgetForm.phone = ''
  forgetForm.password = ''
  forgetForm.confirmPassword = ''
  if (forgetFormRef.value) {
    forgetFormRef.value.resetFields()
  }
}

// 提交忘记密码
const handleSubmit = async () => {
  if (!forgetFormRef.value) return
  
  await forgetFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const response = await request.post('api/auth/login/forget/', {
          phone: forgetForm.phone,
          password: forgetForm.password
        })
        
        if (response.data.status === '200') {
          ElMessage.success('密码重置成功！')
          handleClose()
        } else {
          ElMessage.error(response.data.msg || '密码重置失败')
        }
      } catch (error) {
        console.error('忘记密码请求失败:', error)
        ElMessage.error('网络错误，请稍后重试')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 登录方法
const handleLogin = async () => {
    const response = await request.post(
      'api/auth/login/',
      loginForm.value
    )

    if(response.data.status==='200'){
      //从后端传回来的phone，user_id，nickname和JWT令牌
      console.log('登录成功返回数据：', response.data)
      ElMessage.success("登录成功!")
      updateUserInfo({
        nickname: response.data.data.nickname,
        user_id: response.data.data.user_id,
        phone: response.data.data.phone,
        role:response.data.data.role
      });
      // 👇 存储JWT令牌
      sessionStorage.setItem('access_token', response.data.data.access_token)
      sessionStorage.setItem('refresh_token', response.data.data.refresh_token)

      console.log("登录昵称："+response.data.data.nickname)
      console.log("登录ID："+response.data.data.user_id)
      console.log("手机号码："+response.data.data.phone)
      console.log("访问令牌："+response.data.data.access_token)
      router.push('/home')
    }
    else{
      ElMessage.error("登录失败:"+response.data.msg)
    }
}
</script>

<style scoped>
/* 添加背景图片样式 */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.login-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/components/home/icons/bg.jpg');
  background-size: cover;
  background-position: center;
  z-index: -1;
}

.login-container {
  width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
}
.form-item {
  margin: 15px 0;
  text-align: left;
}
.form-item label {
  display: inline-block;
  width: 80px;
}
.form-item input {
  width: 280px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.login-btn {
  width: 100%;
  padding: 10px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.login-btn:hover {
  background: #66b1ff;
}

.links-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  font-size: 14px;
}

.forgot-password-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.forgot-password-link:hover {
  color: #66b1ff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>