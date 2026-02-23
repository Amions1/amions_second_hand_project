import axios from 'axios';
import { getAccessToken, clearAuthInfo, isTokenExpiringSoon, refreshToken } from './auth';


// 核心：根据当前页面域名，动态设置后端接口的baseURL
const getBaseUrl = () => {
  const hostname = window.location.hostname;

  // 判断访问环境
  const isLocalhost = /localhost|127\.0\.0\.1/.test(hostname);
  const isLocalNetwork = /^192\.168\./.test(hostname);  // 局域网IP段

  if (isLocalhost) {
    // 本机访问开发服务器
    return 'http://127.0.0.1:8000';
  } else if (isLocalNetwork) {
    // 局域网其他设备访问，后端地址应该是开发服务器的IP:8000
    return `http://${hostname}:8000`;
  } else {
    // 外网穿透环境
    return 'http://69mdjw853446.vicp.fun:37276';
  }
};

// 创建axios实例
const service = axios.create({
  baseURL: getBaseUrl(), // API的基础URL
  timeout: 5000 // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 检查是否需要刷新令牌
    if (isTokenExpiringSoon()) {
      // 注意：这里我们不会在这里直接刷新，而是在响应拦截器中处理401错误
      console.log('令牌即将过期，将在收到401响应时尝试刷新');
    }
    
    // 从SessionStorage获取token
    const token = getAccessToken();
    if (token) {
      // 在请求头中添加Bearer token
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    // 请求错误处理
    console.error(error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 成功响应处理
    return response;
  },
  async error => {
    // 响应错误处理
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // 如果是401未授权错误，尝试刷新令牌
      originalRequest._retry = true; // 防止无限重试
      
      try {
        // 尝试刷新令牌
        await refreshToken();
        
        // 使用新令牌重新发送原始请求
        const newToken = getAccessToken();
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        
        return service(originalRequest);
      } catch (refreshError) {
        // 如果刷新令牌失败
        console.error('刷新令牌失败:', refreshError);
        clearAuthInfo();
        
        // 仅在受保护的页面上才跳转到登录页
        const protectedPaths = ['/profile', '/publish', '/settlement'];
        const currentPath = window.location.pathname;
        
        if (protectedPaths.includes(currentPath)) {
          window.location.href = '/login';
        }
        // 对于其他页面（如 /home），不执行跳转
        
        return Promise.reject(refreshError);
      }
    }
    
    // 如果不是401错误或者已经重试过了
    console.error(error);
    return Promise.reject(error);
  }
);

export default service;