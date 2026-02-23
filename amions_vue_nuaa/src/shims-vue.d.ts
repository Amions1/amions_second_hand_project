declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 为 auth.js 模块添加类型声明
declare module '@/utils/auth' {
  export const getAccessToken: () => string | null;
  export const getRefreshToken: () => string | null;
  export const setAccessToken: (token: string) => void;
  export const setRefreshToken: (token: string) => void;
  export const isAuthenticated: () => boolean;
  export const refreshToken: () => Promise<string>;
  export const isTokenExpiringSoon: () => boolean;
  export const clearAuthInfo: () => void;
  export const getUserInfo: () => any;
  export const updateUserInfo: (userInfo: any) => void;
  export const addUserInfoListener: (callback: (userInfo: any) => void) => () => void;
}