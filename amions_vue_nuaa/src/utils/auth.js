/**
 * 认证相关的工具函数
 */

/**
 * 获取后端基础URL（与request.js保持一致）
 */
const getBaseUrl = () => {
  const hostname = window.location.hostname;

  const isLocalhost = /localhost|127\.0\.0\.1/.test(hostname);
  const isLocalNetwork = /^192\.168\./.test(hostname);

  if (isLocalhost) {
    return 'http://127.0.0.1:8000';
  } else if (isLocalNetwork) {
    return `http://${hostname}:8000`;
  } else {
    return 'http://69mdjw853446.vicp.fun:37276';
  }
};

/**
 * 获取访问令牌
 */
export const getAccessToken = () => {
  return sessionStorage.getItem('access_token');
};

/**
 * 获取刷新令牌
 */
export const getRefreshToken = () => {
  return sessionStorage.getItem('refresh_token');
};

/**
 * 设置访问令牌
 */
export const setAccessToken = (token) => {
  sessionStorage.setItem('access_token', token);
};

/**
 * 设置刷新令牌
 */
export const setRefreshToken = (token) => {
  sessionStorage.setItem('refresh_token', token);
};

/**
 * 检查用户是否已登录
 */
export const isAuthenticated = () => {
  const token = getAccessToken();
  if (!token) {
    return false;
  }

  // 解码JWT令牌并检查过期时间
  try {
    const payload = parseJwt(token);
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    console.error('解析JWT令牌失败:', error);
    return false;
  }
};

/**
 * 解析JWT令牌
 */
const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    throw new Error('无效的JWT令牌');
  }
};

/**
 * 刷新访问令牌
 */
export const refreshToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error('无刷新令牌');
  }

  try {
    const response = await fetch(`${getBaseUrl()}/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      setAccessToken(data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
      }
      return data.access_token;
    } else {
      // 刷新失败，清除认证信息
      clearAuthInfo();
      throw new Error('刷新令牌失败');
    }
  } catch (error) {
    console.error('刷新令牌时出错:', error);
    clearAuthInfo();
    throw error;
  }
};

/**
 * 检查令牌是否即将过期（在30秒内过期）
 */
export const isTokenExpiringSoon = () => {
  const token = getAccessToken();
  if (!token) {
    return true; // 如果没有令牌，认为即将过期
  }

  try {
    const payload = parseJwt(token);
    const currentTime = Math.floor(Date.now() / 1000);
    const expTime = payload.exp;
    const timeUntilExpire = expTime - currentTime;
    
    // 如果在30秒内过期，则认为需要刷新
    return timeUntilExpire < 30;
  } catch (error) {
    console.error('检查令牌过期时间失败:', error);
    return true;
  }
};

/**
 * 清除认证信息
 */
export const clearAuthInfo = () => {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  sessionStorage.removeItem('userInfo');
};

/**
 * 获取用户信息
 * 优先从SessionStorage获取，如果没有则从JWT令牌中解析
 */
export const getUserInfo = () => {
  // 优先从SessionStorage获取用户信息
  let userInfo = sessionStorage.getItem('userInfo');
  if (userInfo) {
    return JSON.parse(userInfo);
  }

  // 如果SessionStorage中没有用户信息，尝试从JWT令牌中解析
  const token = getAccessToken();
  if (token) {
    try {
      const payload = parseJwt(token);
      // 假设JWT令牌中包含用户信息字段
      if (payload.user_id && payload.nickname && payload.phone) {
        return {
          user_id: payload.user_id,
          nickname: payload.nickname,
          phone: payload.phone
        };
      }
    } catch (error) {
      console.error('从JWT令牌解析用户信息失败:', error);
    }
  }

  return null;
};

/**
 * 更新用户信息到SessionStorage
 */
export const updateUserInfo = (userInfo) => {
  sessionStorage.setItem('userInfo', JSON.stringify(userInfo));
  
  // 通知所有监听器用户信息已更新
  notifyUserInfoUpdate(userInfo);
};

// 用户信息更新监听器数组
const userInfoListeners = [];

/**
 * 添加用户信息更新监听器
 */
export const addUserInfoListener = (callback) => {
  userInfoListeners.push(callback);
  return () => {
    const index = userInfoListeners.indexOf(callback);
    if (index > -1) {
      userInfoListeners.splice(index, 1);
    }
  };
};

/**
 * 通知所有用户信息监听器
 */
const notifyUserInfoUpdate = (newUserInfo) => {
  userInfoListeners.forEach(callback => {
    try {
      callback(newUserInfo);
    } catch (error) {
      console.error('执行用户信息更新回调时出错:', error);
    }
  });
};