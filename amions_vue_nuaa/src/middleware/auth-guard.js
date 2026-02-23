/**
 * 全局认证守卫
 */

import { isAuthenticated, clearAuthInfo } from '@/utils/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

/**
 * 检查认证状态的守卫函数
 * 注意：此守卫只基于路由路径进行认证检查
 * 与访问地址（localhost、IP、域名）无关
 */
export const authGuard = async (to, from, next) => {
  // 临时调试版本 - 禁用所有认证跳转
  // 定义需要认证的页面路径（仅这些页面需要登录）
  const protectedPaths = ['/profile', '/publish', '/settlement'];
  
  // 如果目标路径在保护列表中，则需要认证
  if (protectedPaths.includes(to.path)) {
    if (!isAuthenticated()) {
      // 用户未认证，清除可能的无效数据
      clearAuthInfo();
      
      // 提示用户登录
      ElMessage.error('登录信息已过期，请重新登录');
      
      // 跳转到登录页，并记住原目标路径
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    } else {
      // 用户已认证，允许访问
      next();
    }
  } else {
    // 所有其他页面（包括 /home, /login, /sign, /paysuccess 等）
    // 都不需要认证，直接放行
    // 临时移除可能的认证检查，仅用于调试
    next();
  }
};

/**
 * 辅助认证检查函数（用于组件内部调用）
 */
export const requireAuth = () => {
  const router = useRouter();
  
  if (!isAuthenticated()) {
    clearAuthInfo();
    ElMessage.error('登录信息已过期，请重新登录');
    router.push('/login');
    return false;
  }
  
  return true;
};