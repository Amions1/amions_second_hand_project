<template>
  <div class="manager-container">
    <!-- 头部 -->
    <Profile_header />
    
    <div class="manager-main">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="nav-menu">
          <ul>
            <li 
              v-for="item in navItems" 
              :key="item.key"
              :class="{ active: activeTab === item.key }"
              @click="switchTab(item.key)"
            >
              {{ item.label }}
            </li>
          </ul>
        </nav>
      </aside>
      
      <!-- 主内容区域 -->
      <main class="content-area">
        <!-- 用户管理 -->
        <div v-if="activeTab === 'users'" class="tab-content">
          <h2>用户管理</h2>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="field in userFields" :key="field.key">{{ field.label }}</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUserData" :key="user.id">
                  <td v-for="field in userFields" :key="field.key">
                    <span v-if="field.key === 'status'" :class="getStatusClass(user.status)">
                      {{ getStatusText(user.status) }}
                    </span>
                    <span v-else-if="field.key === 'role'" :class="getRoleClass(user.role)">
                      {{ getRoleText(user.role) }}
                    </span>
                    <span v-else>
                      {{ user[field.key] }}
                    </span>
                  </td>
                  <td>
                    <button 
                      class="ban-btn"
                      :class="{ banned: user.status === 0 }"
                      @click="toggleUserStatus(user.id)"
                    >
                      {{ user.status === 1 ? '封禁' : '解封' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- 分页控件 -->
            <div class="pagination" v-if="userTotalPages > 1">
              <button 
                class="page-btn" 
                @click="userCurrentPage = Math.max(1, userCurrentPage - 1)"
                :disabled="userCurrentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ userCurrentPage }} 页，共 {{ userTotalPages }} 页
              </span>
              <button 
                class="page-btn" 
                @click="userCurrentPage = Math.min(userTotalPages, userCurrentPage + 1)"
                :disabled="userCurrentPage >= userTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
        
        <!-- 商品管理 -->
        <div v-if="activeTab === 'products'" class="tab-content">
          <h2>商品管理</h2>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="field in productFields" :key="field.key">{{ field.label }}</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in paginatedProductData" :key="product.id">
                  <td v-for="field in productFields" :key="field.key">
                    <span v-if="field.key === 'status'" :class="getProductStatusClass(product)">
                      {{ getStatusText(product.status) }}
                    </span>
                    <span v-else>
                      {{ product[field.key] }}
                    </span>
                  </td>
                  <td class="actions">
                    <el-button 
                      type="primary"
                      @click="openEditModal(product)"
                      :disabled="disabledProducts.has(product.id)"
                      size="default"
                      style="padding: 6px 12px; font-size: 14px;"
                    >
                      修改
                    </el-button>
                    <el-button
                      type="danger"
                      :disabled="product.status === 2 || product.status === 3 || product.status === 4"
                      @click="forceTakeDownGoods(product)"
                      size="default"
                      style="padding: 6px 12px; font-size: 14px;"
                    >
                      下架
                    </el-button>
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- 分页控件 -->
            <div class="pagination" v-if="productTotalPages > 1">
              <button
                class="page-btn"
                @click="productCurrentPage = Math.max(1, productCurrentPage - 1)"
                :disabled="productCurrentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ productCurrentPage }} 页，共 {{ productTotalPages }} 页
              </span>
              <button
                class="page-btn"
                @click="productCurrentPage = Math.min(productTotalPages, productCurrentPage + 1)"
                :disabled="productCurrentPage >= productTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <!-- 商品分类管理 -->
        <div v-if="activeTab === 'categories'" class="tab-content">
          <h2>商品分类管理</h2>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="field in categoryFields" :key="field.key">{{ field.label }}</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="category in paginatedCategoryData" :key="category.id">
                  <td v-for="field in categoryFields" :key="field.key">
                    {{ category[field.key] }}
                  </td>
                  <td>
                    <el-button 
                      type="primary" 
                      @click="openCategoryEditModal(category)" 
                      size="default"
                      style="padding: 6px 12px; font-size: 14px;"
                    >
                      修改
                    </el-button>
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- 分页控件和新增按钮容器 -->
            <div class="pagination-container">
              <div class="pagination-wrapper" v-if="categoryTotalPages > 1">
                <button
                  class="page-btn"
                  @click="categoryCurrentPage = Math.max(1, categoryCurrentPage - 1)"
                  :disabled="categoryCurrentPage <= 1"
                >
                  上一页
                </button>
                <span class="page-info">
                  第 {{ categoryCurrentPage }} 页，共 {{ categoryTotalPages }} 页
                </span>
                <button
                  class="page-btn"
                  @click="categoryCurrentPage = Math.min(categoryTotalPages, categoryCurrentPage + 1)"
                  :disabled="categoryCurrentPage >= categoryTotalPages"
                >
                  下一页
                </button>
              </div>
              <div class="add-category-wrapper">
                <el-button 
                  type="danger" 
                  @click="openAddCategoryModal" 
                  size="default"
                >
                  新增分类
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 订单管理 -->
        <div v-if="activeTab === 'orders'" class="tab-content">
          <h2>订单管理</h2>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="field in orderFields" :key="field.key">{{ field.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in paginatedOrderData" :key="order.id">
                  <td v-for="field in orderFields" :key="field.key">
                    {{ order[field.key] }}
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- 分页控件 -->
            <div class="pagination" v-if="orderTotalPages > 1">
              <button
                class="page-btn"
                @click="orderCurrentPage = Math.max(1, orderCurrentPage - 1)"
                :disabled="orderCurrentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ orderCurrentPage }} 页，共 {{ orderTotalPages }} 页
              </span>
              <button
                class="page-btn"
                @click="orderCurrentPage = Math.min(orderTotalPages, orderCurrentPage + 1)"
                :disabled="orderCurrentPage >= orderTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <!-- 数据显示 -->
        <div v-if="activeTab === 'statistics'" class="tab-content">
          <h2>商品分类统计</h2>
          <div class="chart-container">
            <div ref="categoryChartRef" class="chart-wrapper"></div>
          </div>
          <div class="statistics-info">
            <h3>分类详情</h3>
            <div class="category-list">
              <div 
                v-for="item in categoryStatistics" 
                :key="item.name" 
                class="category-item"
              >
                <span class="category-name">{{ item.name }}</span>
                <span class="category-count">{{ item.value }}个商品</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 修改价格弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <h3>修改商品价格</h3>
        <div class="form-group">
          <label>商品名称：</label>
          <input type="text" :value="editingProduct.title" disabled>
        </div>
        <div class="form-group">
          <label>当前价格：</label>
          <input type="text" :value="editingProduct.price" disabled>
        </div>
        <div class="form-group">
          <label>新价格：</label>
          <input type="number" v-model="newPrice" placeholder="请输入新价格">
        </div>
        <div class="modal-actions">
          <button class="confirm-btn" @click="updateProductPrice">确认</button>
          <button class="cancel-btn" @click="closeEditModal">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 修改分类名称弹窗 -->
    <div v-if="showCategoryEditModal" class="modal-overlay" @click="closeCategoryEditModal">
      <div class="modal-content" @click.stop>
        <h3>修改分类名称</h3>
        <div class="form-group">
          <label>分类ID：</label>
          <input type="text" :value="editingCategory.id" disabled>
        </div>
        <div class="form-group">
          <label>当前名称：</label>
          <input type="text" :value="editingCategory.name" disabled>
        </div>
        <div class="form-group">
          <label>新名称：</label>
          <input type="text" v-model="newCategoryName" placeholder="请输入新的分类名称">
        </div>
        <div class="modal-actions">
          <button class="confirm-btn" @click="updateCategoryName">确认</button>
          <button class="cancel-btn" @click="closeCategoryEditModal">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 新增分类弹窗 -->
    <div v-if="showAddCategoryModal" class="modal-overlay" @click="closeAddCategoryModal">
      <div class="modal-content" @click.stop>
        <h3>新增商品分类</h3>
        <div class="form-group">
          <label>分类名称：</label>
          <input type="text" v-model="newCategoryData.name" placeholder="请输入分类名称">
        </div>
        <div class="form-group">
          <label>父分类ID（可选）：</label>
          <input type="number" v-model="newCategoryData.parent_id" placeholder="请输入父分类ID（留空表示一级分类）">
        </div>
        <div class="modal-actions">
          <button class="confirm-btn" @click="addNewCategory">确认</button>
          <button class="cancel-btn" @click="closeAddCategoryModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Profile_header from '@/components/profile/profile_header.vue'
import request from '@/utils/request'
import { isAuthenticated } from '@/utils/auth'
import * as echarts from 'echarts'

const router = useRouter()

// 检查认证状态
const checkAuth = () => {
  if (!isAuthenticated()) {
    ElMessage.error('请先登录')
    router.push('/login')
    return false
  }
  return true
}

// 导航项
const navItems = [
  { key: 'users', label: '用户管理' },
  { key: 'products', label: '商品管理' },
  { key: 'categories', label: '商品分类管理' },
  { key: 'orders', label: '订单信息' },
  { key: 'statistics', label: '数据显示' }
]

// 当前激活的标签页
const activeTab = ref('users')

// 数据存储
const userData = ref<any[]>([])
const productData = ref<any[]>([])
const categoryData = ref<any[]>([])
const orderData = ref<any[]>([])

// 图表相关数据
const categoryChartRef = ref<HTMLDivElement | null>(null)
let categoryChart: echarts.ECharts | null = null
const categoryStatistics = ref<Array<{name: string, value: number}>>([])

// 定义用户信息类型
interface UserInfo {
  user_id:number
  nickname: string;
  phone: string;
}

// 定义商品信息类型
interface GoodsItem {
  id: number;
  title: string;
  category_id:number;
  price: number;
  quality?: string;
  status?: number;
  create_time?:string;
  image: string;
  publisher_id:number;
  publisher_nickname?: string;
}
// 分页相关变量
const userCurrentPage = ref(1)
const productCurrentPage = ref(1)
const categoryCurrentPage = ref(1)
const orderCurrentPage = ref(1)
const itemsPerPage = 8

// 计算分页数据
const paginatedUserData = computed(() => {
  const start = (userCurrentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return userData.value.slice(start, end)
})

const paginatedProductData = computed(() => {
  const start = (productCurrentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return productData.value.slice(start, end)
})

const paginatedCategoryData = computed(() => {
  const start = (categoryCurrentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return categoryData.value.slice(start, end)
})

const paginatedOrderData = computed(() => {
  const start = (orderCurrentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return orderData.value.slice(start, end)
})

// 计算总页数
const userTotalPages = computed(() => Math.ceil(userData.value.length / itemsPerPage))
const productTotalPages = computed(() => Math.ceil(productData.value.length / itemsPerPage))
const categoryTotalPages = computed(() => Math.ceil(categoryData.value.length / itemsPerPage))
const orderTotalPages = computed(() => Math.ceil(orderData.value.length / itemsPerPage))

//用户表
const userFields = ref([
  { key: 'id', label: '用户ID' },
  { key: 'phone', label: '手机号' },
  { key: 'nickname', label: '昵称' },
  { key: 'status', label: '状态' },
  { key: 'role', label: '权限' }
])

//商品表
const productFields = ref([
  { key: 'id', label: '商品ID' },
  { key: 'title', label: '商品标题' },
  { key: 'price', label: '价格' },
  { key: 'category_name', label: '所属分类' },
  { key: 'publisher_id', label: '发布者ID' },
  { key: 'publisher_nickname', label: '发布者' },
  { key: 'quality', label: '成色' },
  { key: 'status', label: '状态' }
])

//商品分类表
const categoryFields = ref([
  { key: 'id', label: '分类ID' },
  { key: 'name', label: '分类名称' },
  { key: 'parent_id', label: '父分类ID' },
  { key: 'parent_name', label: '父分类' }
])

//订单表
const orderFields = ref([
  { key: 'id', label: '订单ID' },
  { key: 'price', label: '价格' },
  { key: 'status', label: '状态' },
  { key: 'create_time', label: '创建时间' },
  { key: 'goods_id', label: '商品ID' },
  { key: 'buyer_id', label: '买家ID' },
  { key: 'seller_id', label: '卖家ID' },
])

// 编辑弹窗相关
const showEditModal = ref(false)
const editingProduct = ref<any>({})
const newPrice = ref<number>(0)

// 跟踪商品修改按钮的禁用状态
const disabledProducts = ref<Set<number>>(new Set())

// 计算哪些商品的修改按钮应该被禁用（不是在售中的商品）
const calculateDisabledProducts = () => {
  const disabledSet = new Set<number>()
  productData.value.forEach(product => {
    // 只有在售中(status===1)的商品才允许修改
    if (product.status !== 1) {
      disabledSet.add(product.id)
    }
  })
  disabledProducts.value = disabledSet
}

// 分类编辑弹窗相关
const showCategoryEditModal = ref(false)
const editingCategory = ref<any>({})
const newCategoryName = ref<string>('')

// 新增分类弹窗相关
const showAddCategoryModal = ref(false)
const newCategoryData = ref({
  name: '',
  parent_id: null as number | null
})

// 切换标签页
const switchTab = (tabKey: string) => {
  activeTab.value = tabKey
  // 重置分页
  userCurrentPage.value = 1
  productCurrentPage.value = 1
  categoryCurrentPage.value = 1
  orderCurrentPage.value = 1
  loadData(tabKey)
}

// 加载数据
const loadData = async (tabKey: string) => {
  try {
    switch (tabKey) {
      case 'users':
        await loadUsers()
        break
      case 'products':
        await loadProducts()
        break
      case 'categories':
        await loadCategories()
        break
      case 'orders':
        await loadOrders()
        break
      case 'statistics':
        await loadCategoryStatistics()
        break
    }
  } catch (error: any) {
    console.error('加载数据失败：', error)
    ElMessage.error('数据加载失败')
  }
}

// 加载用户数据
const loadUsers = async () => {
  try {
    const response = await request.get('api/admin_manage/users')
    if (response.data.status === '200') {
      userData.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载用户数据失败：', error)
  }
}

// 加载商品数据
const loadProducts = async () => {
  try {
    const response = await request.get('api/admin_manage/goods')
    if (response.data.status === '200') {
      productData.value = response.data.data || []
      // 清除所有禁用状态
      disabledProducts.value.clear()
      // 根据商品状态计算禁用状态
      calculateDisabledProducts()

    }
  } catch (error) {
    console.error('加载商品数据失败：', error)
  }
}

// 加载分类数据
const loadCategories = async () => {
  try {
    const response = await request.get('api/admin_manage/categories')
    if (response.data.status === '200') {
      categoryData.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载分类数据失败：', error)
  }
}

// 加载订单数据
const loadOrders = async () => {
  try {
    const response = await request.get('api/admin_manage/orders')
    if (response.data.status === '200') {
      console.log(response.data.data)
      orderData.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载订单数据失败：', error)
  }
}

// 加载分类统计数据
const loadCategoryStatistics = async () => {
  try {
    const response = await request.get('api/goods/goodslist/')
    if (response.data.status === '200') {
      const goodsData = response.data.data || []
      // 统计各分类的商品数量
      const categoryCountMap = new Map<string, number>()
      
      goodsData.forEach((goods: any) => {
        const categoryName = goods.category_name || '未分类'
        categoryCountMap.set(categoryName, (categoryCountMap.get(categoryName) || 0) + 1)
      })
      
      // 转换为图表需要的格式
      const statisticsData = Array.from(categoryCountMap.entries()).map(([name, value]) => ({
        name,
        value
      }))
      
      categoryStatistics.value = statisticsData
      await nextTick()
      updateCategoryChart(statisticsData)
    }
  } catch (error) {
    console.error('加载分类统计数据失败：', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 更新分类统计图表
const updateCategoryChart = (data: Array<{name: string, value: number}>) => {
  // 检查容器是否存在且有尺寸
  if (!categoryChartRef.value || 
      categoryChartRef.value.clientWidth === 0 || 
      categoryChartRef.value.clientHeight === 0) {
    // 如果容器还没准备好，等待一段时间后重试
    setTimeout(() => updateCategoryChart(data), 100)
    return
  }
  
  // 如果已有图表实例，先销毁重建
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }
  
  // 重新初始化图表
  categoryChart = echarts.init(categoryChartRef.value)
  
  // 图表配置
  const option = {
    title: {
      text: '商品分类统计',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '商品数量',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}个'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: data
      }
    ]
  }
  
  categoryChart.setOption(option)
  
  // 监听窗口大小变化
  const handleResize = () => {
    categoryChart?.resize()
  }
  
  window.addEventListener('resize', handleResize)
  
  // 返回清理函数
  return () => {
    window.removeEventListener('resize', handleResize)
  }
}

// 封禁/解封用户
const toggleUserStatus = async (userId: number) => {
  // 先获取用户当前状态来决定提示文案
  const user = userData.value.find(u => u.id === userId);
  const isCurrentlyActive = user?.status === 1;
  const actionText = isCurrentlyActive ? '封禁' : '解封';

  // 获取当前登录用户信息
  const currentUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
  const currentUserId = currentUser.user_id;

  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要${actionText}该用户吗？`,
      `${actionText}用户`,
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 用户确认后发送请求，同时传递当前用户ID
    const response = await request.post('api/admin_manage/ban_user', {
      user_id: userId,
      current_user_id: currentUserId
    });
    if (response.data.status === '200') {
      ElMessage.success(response.data.msg);
      await loadUsers();
    } else {
      ElMessage.error(response.data.msg || '操作失败');
    }
  } catch (error: any) {
    // 用户取消操作或请求失败
    if (error === 'cancel' || error === 'close') {
      // 用户取消，不做任何操作
      return;
    }
    console.error('切换用户状态失败：', error);
    ElMessage.error('操作失败');
  }
}

// 获取商品状态样式类
const getProductStatusClass = (product: any): string => {
  return product.status === 1 ? 'status-selling' :
         product.status === 2 ? 'status-sold':
         product.status === 3 ? 'status-off':'status-force-off';

}

// 获取状态文本
const getStatusText = (status: number): string => {
  if (activeTab.value === 'users') {
    // 用户管理状态
    return status === 1 ? '正常' : '封禁中'
  } else if (activeTab.value === 'products') {
    // 商品管理状态
        return status === 1 ? '在售中' :
       status === 2 ? '已售完' :
       status === 3 ? '已下架' :
       status === 4 ? '已强制下架' : '未知状态'; // 最后加默认值，防止未知状态返回 undefined
  }
  return status === 1 ? '正常' : '封禁中'
}

// 获取状态样式类
const getStatusClass = (status: number): string => {
  if (activeTab.value === 'users') {
    // 用户管理状态样式
    return status === 1 ? 'status-normal' : 'status-banned'
  } else if (activeTab.value === 'products') {
    // 商品管理状态样式
    return status === 1 ? 'status-selling' : 'status-sold'
  }
  return status === 1 ? 'status-normal' : 'status-banned'
}

// 获取角色文本
const getRoleText = (role: number): string => {
  switch (role) {
    case 1: return '普通用户'
    case 2: return '管理员'
    case 3: return '超级管理员'
    default: return '未知'
  }
}

// 获取角色样式类
const getRoleClass = (role: number): string => {
  switch (role) {
    case 1: return 'role-user'
    case 2: return 'role-admin'
    case 3: return 'role-super-admin'
    default: return ''
  }
}

// 打开编辑弹窗
const openEditModal = (product: any) => {
  editingProduct.value = { ...product }
  newPrice.value = product.price
  showEditModal.value = true
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false
  editingProduct.value = {}
  newPrice.value = 0
}

// 打开分类编辑弹窗
const openCategoryEditModal = (category: any) => {
  editingCategory.value = { ...category }
  newCategoryName.value = category.name
  showCategoryEditModal.value = true
}

const openAddCategoryModal = () => {
  newCategoryData.value = {
    name: '',
    parent_id: null
  }
  showAddCategoryModal.value = true
}

// 关闭新增分类弹窗
const closeAddCategoryModal = () => {
  showAddCategoryModal.value = false
  newCategoryData.value = {
    name: '',
    parent_id: null
  }
}

// 新增分类
const addNewCategory = async () => {
  if (!newCategoryData.value.name.trim()) {
    ElMessage.error('请输入分类名称')
    return
  }

  try {
    // 使用 FormData 格式
    const formData = new FormData()
    formData.append('name', newCategoryData.value.name.trim())
    if (newCategoryData.value.parent_id) {
      formData.append('parent_id', newCategoryData.value.parent_id.toString())
    }
    
    const response = await request.post('api/admin_manage/category/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.status === '200' || response.data.status === '201') {
      ElMessage.success(response.data.msg || '分类添加成功')
      closeAddCategoryModal()
      await loadCategories()
    } else {
      ElMessage.error(response.data.msg || '添加失败')
    }
  } catch (error: any) {
    console.error('新增分类失败：', error)
    ElMessage.error('添加失败')
  }
}

// 关闭分类编辑弹窗
const closeCategoryEditModal = () => {
  showCategoryEditModal.value = false
  editingCategory.value = {}
  newCategoryName.value = ''
}

// 更新商品价格
const updateProductPrice = async () => {
  if (!newPrice.value || newPrice.value <= 0) {
    ElMessage.error('请输入有效的价格')
    return
  }

  try {
    const response = await request.put(`api/admin_manage/product/${editingProduct.value.id}/`, {
      price: newPrice.value
    })
    if (response.data.status === '200') {
      ElMessage.success(response.data.msg)
      // 移除禁用状态
      disabledProducts.value.delete(editingProduct.value.id)
      closeEditModal()
      await loadProducts()
    } else {
      ElMessage.error(response.data.msg || '更新失败')
      // 状态码不是200时，禁用该商品的修改按钮
      disabledProducts.value.add(editingProduct.value.id)
    }
  } catch (error: any) {
    console.error('更新商品价格失败：', error)
    ElMessage.error('更新失败')
    // 请求失败时也禁用按钮
    if (editingProduct.value.id) {
      disabledProducts.value.add(editingProduct.value.id)
    }
  }
}

// 更新分类名称
const updateCategoryName = async () => {
  if (!newCategoryName.value.trim()) {
    ElMessage.error('请输入分类名称')
    return
  }

  if (newCategoryName.value.trim() === editingCategory.value.name) {
    ElMessage.warning('分类名称未发生变化')
    return
  }

  try {
    // 使用 FormData 格式
    const formData = new FormData()
    formData.append('name', newCategoryName.value.trim())
    
    const response = await request.post(`api/admin_manage/category/${editingCategory.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    console.log(response.data)
    if (response.data.status === '200') {
      ElMessage.success(response.data.msg)
      closeCategoryEditModal()
      await loadCategories()
    } else {
      ElMessage.error(response.data.msg || '更新失败')
    }
  } catch (error: any) {
    console.error('更新分类名称失败：', error)
    ElMessage.error('更新失败')
  }
}

// 检查认证状态的函数
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
}

// 管理员强制下架商品函数
const forceTakeDownGoods = async (goods: GoodsItem) => {
  if (!checkAuthentication()) return;

  try {
    // 管理员只能强制下架，在售中的商品才能被强制下架
    if (goods.status === 2 || goods.status === 3 || goods.status === 4) {
      ElMessage.error('该商品无法下架');
      return;
    }

    const confirmMessage = '确定要下架该商品吗？';
    const title = '确认下架';

    await ElMessageBox.confirm(
      confirmMessage,
      title,
      {
        confirmButtonText: '确认下架',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 获取当前用户ID
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    const userId = storedUser.user_id;

    // 使用FormData发送数据，包含userId、goodsId和商品状态
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('goods_id', goods.id.toString());
    formData.append('current_status', goods.status?.toString() || '1');

    const response = await request.post('api/user/profiles/takedown_or_putup/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.status === '200') {
      ElMessage.success('商品下架成功！');
      // 操作成功后重新加载商品数据
      await loadProducts();
    } else {
      ElMessage.error(response.data.msg || '强制下架失败');
    }
  } catch (error: any) {
    if (error === 'cancel') return; // 用户取消操作

    console.error('强制下架商品失败:', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '强制下架失败');
    }
  }
};


// 页面加载时检查认证并加载初始数据
onMounted(() => {
  if (checkAuth()) {
    loadData(activeTab.value)
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }
})
</script>

<style scoped>
.manager-container {
  min-height: 100vh;
  background-color: #f8fafc;
}

.manager-main {
  display: flex;
  margin-top: 60px;
  min-height: calc(100vh - 60px);
}

/* 左侧导航栏 */
.sidebar {
  width: 200px;
  background-color: white;
  border-right: 1px solid #e2e8f0;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

.nav-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-menu li {
  padding: 15px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.3s ease;
  color: #4a5568;
  font-weight: 500;
}

.nav-menu li:hover {
  background-color: #ebf8ff;
  color: #3182ce;
}

.nav-menu li.active {
  background-color: #3182ce;
  color: white;
  border-left: 4px solid #2b6cb0;
}

/* 主内容区域 */
.content-area {
  flex: 1;
  padding: 30px;
  background-color: #f8fafc;
}

.tab-content h2 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
}

/* 表格样式 */
.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 20px;
  text-align: center;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}


.data-table th {
  background-color: #f7fafc;
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  color: #4a5568;
  border-bottom: 2px solid #e2e8f0;
  white-space: nowrap;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #4a5568;
  vertical-align: middle;
  text-align: left;
}

.data-table tbody tr:hover {
  background-color: #f7fafc;
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
  gap: 15px;
  padding: 0 20px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #2b6cb0;
}

.page-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #4a5568;
  white-space: nowrap;
}

/* 操作按钮 */
.ban-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: #e53e3e;
  color: white;
}

.ban-btn:hover {
  background-color: #c53030;
}

.ban-btn.banned {
  background-color: #38a169;
}

.ban-btn.banned:hover {
  background-color: #2f855a;
}

.actions {
  display: flex;
  gap: 8px;
}

/* 统计占位符 */
.statistics-placeholder {
  background-color: white;
  border-radius: 8px;
  padding: 60px;
  text-align: left;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.statistics-placeholder p {
  font-size: 18px;
  color: #718096;
  margin: 0;
}

/* 图表容器样式 */
.chart-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
}

.statistics-info {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.statistics-info h3 {
  margin: 0 0 15px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.category-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f7fafc;
  border-radius: 6px;
  border-left: 4px solid #3182ce;
}

.category-name {
  font-weight: 500;
  color: #2d3748;
}

.category-count {
  font-weight: 600;
  color: #3182ce;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #4a5568;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:disabled {
  background-color: #f7fafc;
  color: #a0aec0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.confirm-btn, .cancel-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.confirm-btn {
  background-color: #3182ce;
  color: white;
}

.confirm-btn:hover {
  background-color: #2b6cb0;
}

.cancel-btn {
  background-color: #e2e8f0;
  color: #4a5568;
}

.cancel-btn:hover {
  background-color: #cbd5e0;
}

/* 用户状态显示样式 */
.status-banned {
  color: #e53e3e; /* 红色 - 封禁中 */
  font-weight: 500;
}

/* 商品状态显示样式 */
.status-selling {
  color: #38a169;
  font-weight: 500;
}

.status-sold {
  color: #66b1ff;
  font-weight: 500;
}
.status-off {
  color: coral;
  font-weight: 500;
}
.status-force-off {
  color: red;
  font-weight: 500;
}

/* 用户角色显示样式 */
.role-user {
  color: #000000; /* 黑色 */
  font-weight: 500;
}

.role-admin {
  color: #3182ce; /* 蓝色 */
  font-weight: 500;
}

.role-super-admin {
  color: #ffd700; /* 金色 */
  font-weight: 600;
}

/* 分页控件和新增按钮容器 */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  padding: 0 20px;
  gap: 30px; /* 分页和按钮之间的间距 */
}

.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 15px;
}

.add-category-wrapper {
  flex-shrink: 0; /* 防止按钮被压缩 */
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    gap: 15px;
    padding: 0 10px;
  }
  
  .pagination-wrapper {
    order: 2;
  }
  
  .add-category-wrapper {
    order: 1;
  }
  
  .pagination {
    justify-content: center;
  }
}
</style>