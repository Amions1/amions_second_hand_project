import { ElMessageBox, ElMessage } from 'element-plus'
import request from '@/utils/request'
import { isAuthenticated } from '@/utils/auth'
import router from '@/router'

// 检查认证状态的函数
const checkAuthentication = () => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
}

