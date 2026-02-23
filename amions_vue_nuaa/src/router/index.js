// src/router/index.js
import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
// 导入你的组件（注意路径：你的登录页是 login.vue 小写，需对应）
import Login from '@/views/login.vue'
import Home from '@/views/home.vue' // 需新建首页组件
import Publish from '@/views/publish.vue' // 新增发布页面
import Profile from '@/views/profile.vue' // 新增个人资料页面
import Sign from '@/views/sign.vue' // 新增注册页面
import Details from '@/views/details.vue' // 新增商品详情页面
import Settlement from '@/views/settlement.vue' // 新增结算页面
import PaySuccess from '@/views/paysuccess.vue' // 新增支付成功页面
import Manager from '@/views/manager.vue' // 新增管理员页面
import Message from '@/views/message.vue' // 新增消息页面
import { authGuard } from '@/middleware/auth-guard.js' // 导入认证守卫

// 定义路由规则
const routes = [
  {
    path: '/',
    redirect: '/home' // 默认跳主页
  },
  {
    path: '/login',
    name: 'login',
    component: Login, // 对应 login.vue 组件
    meta: { requiresAuth: false } // 登录页不需要认证
  },
  {
    path: '/home',
    name: 'Home',
    component: Home, // 对应首页组件
    meta: { requiresAuth: false } // 首页不需要认证
  },
  {
    path: '/publish',
    name: 'Publish',
    component: Publish, // 对应发布页面
    meta: { requiresAuth: true } // 发布页面需要认证
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile, // 对应个人资料页面
    meta: { requiresAuth: true } // 个人资料页面需要认证
  },
  {
    path: '/sign',
    name: 'Sign',
    component: Sign, // 对应注册页面
    meta: { requiresAuth: false } // 注册页不需要认证
  },
  {
    path: '/details/:id',
    name: 'Details',
    component: Details,
    props: true, // 将路由参数作为props传递
    meta: { requiresAuth: false } // 商品详情页需要认证
  },
  {
    path: '/settlement',
    name: 'Settlement',
    component: Settlement, // 对应结算页面
    meta: { requiresAuth: true } // 结算页面需要认证
  },
  {
    path: '/paysuccess',
    name: 'PaySuccess',
    component: PaySuccess, // 对应支付成功页面
    meta: { requiresAuth: false } // 支付成功页面不需要认证
  },
  {
    path: '/manager',
    name: 'Manager',
    component: Manager, // 对应管理员页面
    meta: { requiresAuth: true } // 管理员页面需要认证
  },
  {
    path: '/message',
    name: 'Message',
    component: Message, // 对应消息页面
    meta: { requiresAuth: true } // 消息页面需要认证
  },
  // 静态资源路径，直接返回，不走前端路由
  {
    path: '/media/:pathMatch(.*)',
    component: { render: () => null }, // 空组件
    meta: { skipRoute: true }
  }
]

// 创建路由实例（Vue 3 语法）
const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History 模式
  routes,
  // 配置滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
})

// 添加全局前置守卫
router.beforeEach(authGuard);

export default router