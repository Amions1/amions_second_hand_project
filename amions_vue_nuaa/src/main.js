// src/main.js
import { createApp } from 'vue' // Vue 3 核心导入
import App from './App.vue'
import router from './router/index.js' // 导入路由

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 创建 app 实例并挂载路由
const app = createApp(App)
app.use(router) // 挂载路由
app.use(ElementPlus)
app.mount('#app')