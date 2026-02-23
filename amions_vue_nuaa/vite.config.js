import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // 禁用 vue inspector 的转换
          hoistStatic: true
        }
      }
    }),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: './',
  server: {
    host: '0.0.0.0',    // 核心配置：允许外网访问
    port: 5173,
    strictPort: true,  // 端口被占时自动换端口，避免启动失败
    // open: true,
    cors: true,
    allowedHosts: ['69mdjw853446.vicp.fun', '69mdjw853446.vicp.fun:37276'],
    proxy: {
      '/media': {
        target: 'http://69mdjw853446.vicp.fun:37276', // 后端服务器地址
        changeOrigin: true,
        secure: false,
      },
      // 如果有其他API也需要代理，可以继续添加
      '/api': {
        target: 'http://69mdjw853446.vicp.fun:37276',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})


