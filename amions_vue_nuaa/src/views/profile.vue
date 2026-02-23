<template>
  <div class="profile-container">
    <!-- 引入导航栏组件 -->
    <Profile_header />
    <div class="profile-main">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <div class="nav-item" @click="toggleNav('myTransactions')" :class="{ active: expandedNavs.has('myTransactions') }">
          <div class="nav-title">
            <span>🎁我的交易</span>
            <span class="arrow" :class="{ expanded: expandedNavs.has('myTransactions') }">▼</span>
          </div>
          <div class="sub-nav" v-if="expandedNavs.has('myTransactions')">
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'published' }"
              @click.stop="switchSubNav('published')"
            >
              我发布的
            </div>
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'bought' }"
              @click.stop="switchSubNav('bought')"
            >
              我买到的
            </div>
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'offShelf' }"
              @click.stop="switchSubNav('offShelf')"
            >
              已下架的
            </div>
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'sold' }"
              @click.stop="switchSubNav('sold')"
            >
              已卖出的
            </div>
          </div>
        </div>

        <div class="nav-item" @click="toggleNav('myWishlist')" :class="{ active: expandedNavs.has('myWishlist') }">
          <div class="nav-title">
            <span>⭐我想要的</span>
            <span class="arrow" :class="{ expanded: expandedNavs.has('myWishlist') }">▼</span>
          </div>
          <div class="sub-nav" v-if="expandedNavs.has('myWishlist')">
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'wishlist' }"
              @click.stop="switchSubNav('wishlist')"
            >
              收藏夹
            </div>
          </div>
        </div>

        <div class="nav-item" @click="toggleNav('personalInfo')" :class="{ active: expandedNavs.has('personalInfo') }">
          <div class="nav-title">
            <span>👔个人资料</span>
            <span class="arrow" :class="{ expanded: expandedNavs.has('personalInfo') }">▼</span>
          </div>
          <div class="sub-nav" v-if="expandedNavs.has('personalInfo')">
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'editProfile' }"
              @click.stop="switchSubNav('editProfile')"
            >
              编辑资料
            </div>
            <div 
              class="sub-item" 
              :class="{ active: activeSubNav === 'changePassword' }"
              @click.stop="switchSubNav('changePassword')"
            >
              修改密码
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="content-area">
        <!-- 根据当前选中的导航显示对应内容 -->
        <div v-if="activeSubNav === 'published'" class="content-section">
          <h3>我发布的商品</h3>
          <div v-if="publishedGoods.length === 0" class="no-data">
            <p>暂无发布的商品</p>
          </div>
          <div v-else>
            <div class="goods-grid">
              <div 
                class="goods-item clickable-item" 
                v-for="goods in paginatedPublishedGoods" 
                :key="goods.id"
                @click="openEditModal(goods)"
              >
                <div v-if="getImageUrl(goods.image)" class="goods-image">
                  <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
                </div>
                <div class="goods-info">
                  <h4 class="goods-title">{{ goods.title }}</h4>
                  <p class="goods-price">¥{{ goods.price }}</p>
                  <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                  <p class="goods-status" v-if="goods.status !== undefined">
                    状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                  </p>
                  <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
                  <!-- 下架按钮 -->
                  <button 
                    class="take-down-btn" 
                    @click.stop="takeDownOrPutDownGoods(goods)"
                    title="下架商品"
                  >
                    下架
                  </button>
                </div>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="publishedTotalPages > 1">
              <button 
                class="page-btn" 
                @click="paginationState.published.currentPage = Math.max(1, paginationState.published.currentPage - 1)"
                :disabled="paginationState.published.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.published.currentPage }} 页，共 {{ publishedTotalPages }} 页
              </span>
              <button 
                class="page-btn" 
                @click="paginationState.published.currentPage = Math.min(publishedTotalPages, paginationState.published.currentPage + 1)"
                :disabled="paginationState.published.currentPage >= publishedTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeSubNav === 'offShelf'" class="content-section">
          <h3>已下架的商品</h3>
          <div v-if="offShelfGoods.length === 0" class="no-data">
            <p>暂无下架商品</p>
          </div>
          <div v-else>
            <div class="goods-grid">
              <div 
                class="goods-item clickable-item"
                v-for="goods in paginatedOffShelfGoods"
                :key="goods.id"
              >
                <div v-if="getImageUrl(goods.image)" class="goods-image">
                  <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
                </div>
                <div class="goods-info">
                  <h4 class="goods-title">{{ goods.title }}</h4>
                  <p class="goods-price">¥{{ goods.price }}</p>
                  <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                  <p class="goods-status" v-if="goods.status !== undefined">
                    状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                  </p>
                  <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
                  <button
                    class="put-up-btn"
                    @click.stop="takeDownOrPutDownGoods(goods)"
                    title="上架商品"
                  >
                    上架
                  </button>
                </div>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="offShelfTotalPages > 1">
              <button 
                class="page-btn" 
                @click="paginationState.offShelf.currentPage = Math.max(1, paginationState.offShelf.currentPage - 1)"
                :disabled="paginationState.offShelf.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.offShelf.currentPage }} 页，共 {{ offShelfTotalPages }} 页
              </span>
              <button 
                class="page-btn" 
                @click="paginationState.offShelf.currentPage = Math.min(offShelfTotalPages, paginationState.offShelf.currentPage + 1)"
                :disabled="paginationState.offShelf.currentPage >= offShelfTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <div v-else-if="activeSubNav === 'bought'" class="content-section">
          <h3>我买到的商品</h3>
          <div v-if="boughtGoods.length === 0" class="no-data">
            <p>暂无购买记录</p>
          </div>
          <div v-else>
            <div class="goods-grid">
              <div
                class="goods-item clickable-item"
                v-for="goods in paginatedBoughtGoods"
                :key="goods.id"
              >
                <div v-if="getImageUrl(goods.image)" class="goods-image">
                  <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
                </div>
                <div class="goods-info">
                  <h4 class="goods-title">{{ goods.title }}</h4>
                  <p class="goods-price">¥{{ goods.price }}</p>
                  <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                  <p class="goods-status" v-if="goods.status !== undefined">
                    状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                  </p>
                  <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
                </div>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="boughtTotalPages > 1">
              <button
                class="page-btn"
                @click="paginationState.bought.currentPage = Math.max(1, paginationState.bought.currentPage - 1)"
                :disabled="paginationState.bought.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.bought.currentPage }} 页，共 {{ boughtTotalPages }} 页
              </span>
              <button
                class="page-btn"
                @click="paginationState.bought.currentPage = Math.min(boughtTotalPages, paginationState.bought.currentPage + 1)"
                :disabled="paginationState.bought.currentPage >= boughtTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeSubNav === 'sold'" class="content-section">
          <h3>已卖出的商品</h3>
          <div v-if="soldGoods.length === 0" class="no-data">
            <p>暂无销售记录</p>
          </div>
          <div v-else class="goods-grid">
            <div 
              class="goods-item" 
              v-for="goods in paginatedSoldGoods"
              :key="goods.id"
            >
              <div v-if="getImageUrl(goods.image)" class="goods-image">
                <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
              </div>
              <div class="goods-info">
                <h4 class="goods-title">{{ goods.title }}</h4>
                <p class="goods-price">¥{{ goods.price }}</p>
                <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                <p class="goods-status" v-if="goods.status !== undefined">
                  状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                </p>
                <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="soldTotalPages > 1">
              <button
                class="page-btn"
                @click="paginationState.sold.currentPage = Math.max(1, paginationState.sold.currentPage - 1)"
                :disabled="paginationState.sold.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.sold.currentPage }} 页，共 {{ soldTotalPages }} 页
              </span>
              <button
                class="page-btn"
                @click="paginationState.sold.currentPage = Math.min(soldTotalPages, paginationState.sold.currentPage + 1)"
                :disabled="paginationState.sold.currentPage >= soldTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeSubNav === 'editProfile'" class="content-section">
          <h3>编辑个人资料</h3>
          <div class="profile-form">
            <div class="form-group">
              <label>用户名:</label>
              <input type="text" v-model="userInfo.nickname" class="editable-input"/>
            </div>
            <div class="form-group">
              <label>手机号:</label>
              <input type="text" v-model="userInfo.phone" readonly class="readonly-input" title="手机号不可更改"/>
            </div>
            <div class="form-actions">
              <button class="save-btn" @click="saveProfile">保存资料</button>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeSubNav === 'changePassword'" class="content-section">
          <h3>修改密码</h3>
          <div class="password-form">
            <div class="form-group">
              <label>当前密码:</label>
              <input type="password" v-model="currentPassword" placeholder="请输入当前密码"/>
            </div>
            <div class="form-group">
              <label>新密码:</label>
              <input type="password" v-model="newPassword" placeholder="请输入新密码"/>
            </div>
            <div class="form-group">
              <label>确认新密码:</label>
              <input type="password" v-model="confirmNewPassword" placeholder="请再次输入新密码"/>
            </div>
            <div class="form-actions">
              <button class="save-btn" @click="changePassword">修改密码</button>
            </div>
          </div>
        </div>

        <div v-else-if="activeSubNav === 'wishlist'" class="content-section">
          <h3>我想要的商品</h3>
          <div v-if="wishlistGoods.length === 0" class="no-data">
            <p>收藏夹空空如也~~~</p>
          </div>
          <div v-else>
            <div class="goods-grid">
              <div
                class="goods-item clickable-item"
                v-for="goods in paginatedWishlistGoods"
                :key="goods.id"
              >
                <router-link :to="`/details/${goods.id}`" class="goods-link">
                  <div v-if="getImageUrl(goods.image)" class="goods-image">
                    <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError" />
                  </div>
                  <div class="goods-info">
                    <h4 class="goods-title">{{ goods.title }}</h4>
                    <p class="goods-price">¥{{ goods.price }}</p>
                    <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                    <p class="goods-status" v-if="goods.status !== undefined">
                      状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                    </p>
                    <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
                  </div>
                </router-link>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="wishlistTotalPages > 1">
              <button
                class="page-btn"
                @click="paginationState.wishlist.currentPage = Math.max(1, paginationState.wishlist.currentPage - 1)"
                :disabled="paginationState.wishlist.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.wishlist.currentPage }} 页，共 {{ wishlistTotalPages }} 页
              </span>
              <button
                class="page-btn"
                @click="paginationState.wishlist.currentPage = Math.min(wishlistTotalPages, paginationState.wishlist.currentPage + 1)"
                :disabled="paginationState.wishlist.currentPage >= wishlistTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
        
        <!-- 默认显示当前用户发布的所有商品 -->
        <div v-else class="content-section">
          <h3>我发布的商品</h3>
          <div v-if="publishedGoods.length === 0" class="no-data">
            <p>暂无发布的商品</p>
          </div>
          <div v-else>
            <div class="goods-grid">
              <div 
                class="goods-item clickable-item" 
                v-for="goods in paginatedPublishedGoods" 
                :key="goods.id"
                @click="openEditModal(goods)"
              >
                <div v-if="getImageUrl(goods.image)" class="goods-image">
                  <img :src="getImageUrl(goods.image)" :alt="goods.title" @error="imageError"/>
                </div>
                <div class="goods-info">
                  <h4 class="goods-title">{{ goods.title }}</h4>
                  <p class="goods-price">¥{{ goods.price }}</p>
                  <p class="goods-quality" v-if="goods.quality">成色: {{ goods.quality }}</p>
                  <p class="goods-status" v-if="goods.status !== undefined">
                    状态: {{ goods.status == 1 ? '在售中' : goods.status == 2 ? '已售完' : '已下架' }}
                  </p>
                  <p class="goods-publisher" v-if="goods.publisher_nickname">发布者: {{ goods.publisher_nickname }}</p>
                </div>
              </div>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="publishedTotalPages > 1">
              <button 
                class="page-btn" 
                @click="paginationState.published.currentPage = Math.max(1, paginationState.published.currentPage - 1)"
                :disabled="paginationState.published.currentPage <= 1"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ paginationState.published.currentPage }} 页，共 {{ publishedTotalPages }} 页
              </span>
              <button 
                class="page-btn" 
                @click="paginationState.published.currentPage = Math.min(publishedTotalPages, paginationState.published.currentPage + 1)"
                :disabled="paginationState.published.currentPage >= publishedTotalPages"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
    
    <!-- 编辑商品价格弹窗 -->
    <el-dialog
      v-model="showEditModal"
      title="编辑商品价格"
      width="400px"
      :before-close="closeEditModal"
    >
      <div v-if="editingProduct" class="edit-modal-content">
        <div class="product-preview">
<!--          <div class="product-image" v-if="getImageUrl(editingProduct.image)">-->
<!--            <img :src="getImageUrl(editingProduct.image)" :alt="editingProduct.title" />-->
<!--          </div>-->
          <div class="product-info">
            <h4>{{ editingProduct.title }}</h4>
            <p>当前价格: ¥{{ editingProduct.price }}</p>
          </div>
        </div>
        
        <div class="price-input">
          <label>新价格:</label>
          <el-input
            v-model.number="newPrice"
            type="number"
            placeholder="请输入新价格"
            :min="0"
            step="0.1"
          >
            <template #append>元</template>
          </el-input>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeEditModal">取消</el-button>
          <el-button type="primary" @click="updateProductPrice">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Profile_header from '@/components/profile/profile_header.vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import { isAuthenticated } from '@/utils/auth'
import request from '@/utils/request'
import { updateUserInfo } from '@/utils/auth'
import { useRouter } from 'vue-router'

const router = useRouter()

// 检查认证状态的函数
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
}

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

// 分页相关类型
interface PaginationState {
  currentPage: number;
  itemsPerPage: number;
}

// 响应式数据
const activeNav = ref<string | null>(null)
const expandedNavs = ref<Set<string>>(new Set()) // 使用Set来跟踪多个展开的菜单
const activeSubNav = ref<string>('published') // 默认显示我发布的商品
const userInfo = ref<UserInfo>({
  user_id:0,
  nickname: '',
  phone: '',

})
const publishedGoods = ref<GoodsItem[]>([])
const boughtGoods = ref<GoodsItem[]>([])
const offShelfGoods = ref<GoodsItem[]>([])
const soldGoods = ref<GoodsItem[]>([])
const wishlistGoods = ref<GoodsItem[]>([])
const currentPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')

// 编辑弹窗相关
const showEditModal = ref(false)
const editingProduct = ref<GoodsItem | null>(null)
const newPrice = ref<number>(0)

// 分页状态管理
const paginationState = ref<Record<string, PaginationState>>({
  published: { currentPage: 1, itemsPerPage: 8 },
  bought: { currentPage: 1, itemsPerPage: 8 },
  offShelf: { currentPage: 1, itemsPerPage: 8 },
  sold: { currentPage: 1, itemsPerPage: 8 },
  wishlist: { currentPage: 1, itemsPerPage: 8 }
})

// 页面加载时读取用户信息
onMounted(async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  const storedUser = sessionStorage.getItem('userInfo')
  if (storedUser) {
    const parsedUser = JSON.parse(storedUser);
    userInfo.value = {
      user_id:parsedUser.user_id,
      nickname: parsedUser.nickname,
      phone: parsedUser.phone
    };
    // 加载当前用户发布的商品
    await loadPublishedGoods(parsedUser.user_id)
  } else {
    // 如果没有用户信息，重定向到登录页
    if (!checkAuthentication()) {
      return;
    }
  }
})

// 加载当前用户发布的商品
const loadPublishedGoods = async (userId: string) => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 这里需要后端提供一个根据用户ID获取其发布商品的接口
    const response = await request.get(`api/user/profiles/?user_id=${userId}`)
    if (response.data.status === '200') {
      publishedGoods.value = response.data.goods_list || []
    } else if(response.data.status === '401'){
      ElMessage.error("登录已过期，请重新登录")
      router.push("/login")
    }
    else {
      console.error('获取发布的商品失败:', response.data.msg)
    }
  } catch (error: any) {
    console.error('请求发布的商品失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
}

// 加载我买到的商品
const loadBoughtGoods = async (userId: string) => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 根据buyer_id查询order表
    const response = await request.get(`api/user/profiles/bought/?buyer_id=${userId}`)
    if (response.data.status === '200') {
      boughtGoods.value = response.data.data
    } else {
      console.error('获取买到的商品失败:', response.data.msg)
    }
  } catch (error: any) {
    console.error('请求买到的商品失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
}

// 加载已下架的商品
const loadOffShelfGoods = async (userId: string) => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 根据用户ID获取已下架的商品
    const response = await request.get(`api/user/profiles/off_shelf/${userId}`)
    if (response.data.status === '200') {
      console.log(response.data.data)
      offShelfGoods.value = response.data.data || []
    } else {
      console.error('获取已下架的商品失败:', response.data.msg)
    }
  } catch (error: any) {
    console.error('请求已下架的商品失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
}

// 加载收藏夹商品
const loadWishlistGoods = async (userId: string) => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 根据用户ID获取收藏夹商品
    const response = await request.get(`api/user/profiles/wishlist/${userId}`)
    if (response.data.status === '200') {
      console.log(response.data.data)
      wishlistGoods.value = response.data.data || []
    } else {
      console.error('获取收藏夹商品失败:', response.data.msg)
    }
  } catch (error: any) {
    console.error('请求收藏夹商品失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
}

// 加载已卖出的商品
const loadSoldGoods = async (userId: string) => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 根据seller_id查询order表
    const response = await request.get(`api/user/profiles/sold/?seller_id=${userId}`)
    if (response.data.status === '200') {
      soldGoods.value = response.data.data
      console.log("已卖出的："+response.data.data)
    } else {
      console.error('获取已卖出的商品失败:', response.data.msg)
    }
  } catch (error: any) {
    console.error('请求已卖出的商品失败：', error)
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
}

// 切换导航
const toggleNav = (navName: string) => {
  if (expandedNavs.value.has(navName)) {
    // 如果当前展开的就是这个导航，则收缩
    expandedNavs.value.delete(navName)
  } else {
    // 否则展开这个导航
    expandedNavs.value.add(navName)
    activeNav.value = navName
  }
}

// 切换子导航
const switchSubNav = (subNavName: string) => {
  activeSubNav.value = subNavName
  if (subNavName === 'published') {
    // 加载我发布的商品
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    if (storedUser.user_id) {
      loadPublishedGoods(storedUser.user_id);
    }
  } else if (subNavName === 'bought') {
    // 加载我买到的商品
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    if (storedUser.user_id) {
      loadBoughtGoods(storedUser.user_id);
    }
  } else if (subNavName === 'offShelf') {
    // 加载已下架的商品
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    if (storedUser.user_id) {
      loadOffShelfGoods(storedUser.user_id);
    }
  } else if (subNavName === 'sold') {
    // 加载已卖出的商品
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    if (storedUser.user_id) {
      loadSoldGoods(storedUser.user_id);
    }
  } else if (subNavName === 'wishlist') {
    // 加载收藏夹商品
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    if (storedUser.user_id) {
      loadWishlistGoods(storedUser.user_id);
    }
  } else if (subNavName === 'editProfile') {
    // 显示编辑资料页面
  } else if (subNavName === 'changePassword') {
    // 显示修改密码页面
  }
}

// 获取后端基础URL（与request.js保持一致）
const getBackendBaseUrl = (): string => {
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

// 处理图片URL的方法
const getImageUrl = (imagePath: string): string | undefined => {
  if (!imagePath) return undefined;

  // 如果已经是完整的URL（以http或https开头），直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  const baseUrl = getBackendBaseUrl();

  // 如果是相对路径，添加后端基础URL
  if (imagePath.startsWith('/')) {
    return `${baseUrl}${imagePath}`;
  }

  // 其他情况，也尝试拼接后端URL
  return `${baseUrl}/${imagePath}`;
};

// 图片加载错误处理
const imageError = (event: Event) => {
  console.error('图片加载失败:', (event.target as HTMLImageElement).src);
  // 设置默认图片
  const defaultImg = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"><rect width="200" height="150" fill="#f0f0f0"/><text x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="14" fill="#999">图片无法加载</text></svg>';
  (event.target as HTMLImageElement).src = defaultImg;
};

// 上架/下架商品请求函数
const takeDownOrPutDownGoods = async (goods: GoodsItem) => {
  if (!checkAuthentication()) return;
  
  try {
    // 根据商品当前状态确定操作类型和提示文字
    const isCurrentlyOnSale = goods.status === 1; // 1表示在售中
    const actionText = isCurrentlyOnSale ? '下架' : '上架';
    const confirmMessage = `确定要${actionText}这个商品吗？`;
    const title = `确认${actionText}`;
    
    await ElMessageBox.confirm(
      confirmMessage,
      title,
      {
        confirmButtonText: '确定',
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
    console.log(response.data.status)
    console.log(response.data.data)
    if (response.data.status === '200') {
      ElMessage.success(`商品${actionText}成功！`);
      // 重新加载相关数据
      switch(activeSubNav.value) {
        case 'published':
          await loadPublishedGoods(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id);
          break;
        case 'bought':
          await loadBoughtGoods(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id);
          break;
        case 'offShelf':
          await loadOffShelfGoods(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id);
          break;
        case 'sold':
          await loadSoldGoods(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id);
          break;
        case 'wishlist':
          await loadWishlistGoods(JSON.parse(sessionStorage.getItem('userInfo') || '{}').user_id);
          break;
      }
    } else {
      ElMessage.error(response.data.msg || '下架失败');
    }
  } catch (error: any) {
    if (error === 'cancel') return; // 用户取消操作
    
    console.error('下架商品失败:', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '下架失败');
    }
  }
};


// 保存个人资料
const saveProfile = async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    // 获取本地存储的用户信息
    const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
    
    // 检查新昵称是否与原昵称相同
    if (userInfo.value.nickname === storedUser.nickname) {
      ElMessage.warning('新昵称与当前昵称相同，无需修改');
      return;
    }
    
    // 显示确认对话框
    await ElMessageBox.confirm(
      '您确定要修改昵称吗？',
      '确认修改',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 只有在用户点击确认后才执行以下代码
    // 使用FormData发送数据，以便后端能正确接收
    const formData = new FormData();
    formData.append('user_id', storedUser.user_id);
    formData.append('nickname', userInfo.value.nickname);
    console.log("表单数据:"+formData.get('user_id'))
    console.log("表单数据:"+formData.get('nickname'))

    const response = await request.post('api/user/profiles/update_nickname/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    if (response.data.status === '200') {
      // 更新本地存储和全局状态
      storedUser.nickname = userInfo.value.nickname;
      updateUserInfo(storedUser);
      
      ElMessage.success('个人资料已保存');
    } else {
      ElMessage.error(response.data.msg || '保存失败');
    }
  } catch (error: any) {
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      console.log("用户点击取消或出现其他错误")
    }
  }
}

// 修改密码
const changePassword = async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  if (!currentPassword.value || !newPassword.value ||! confirmNewPassword.value) {
    ElMessage.error('请输入密码');
    return;
  }

  if (newPassword.value !== confirmNewPassword.value) {
    ElMessage.error('两次输入的新密码不一致');
    return;
  }

  try {
    // 发送修改密码请求
    const formData = new FormData();
    formData.append('phone', userInfo.value.phone);
    formData.append('current_password', currentPassword.value);
    formData.append('new_password', newPassword.value);

    const response = await request.post('api/user/profiles/changepassword/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.data.status === '200') {
      ElMessage.success('密码修改成功');
      // 清空表单
      currentPassword.value = '';
      newPassword.value = '';
      confirmNewPassword.value = '';
    } else {
      ElMessage.error(response.data.msg || '密码修改失败');
    }
  } catch (error: any) {
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.msg || '网络错误，请稍后重试');
    }
  }
}

// 打开编辑弹窗
const openEditModal = (product: any) => {
  editingProduct.value = { ...product };
  newPrice.value = product.price;
  showEditModal.value = true;
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false;
  editingProduct.value = null;
  newPrice.value = 0;
}



// 计算属性 - 分页数据
const paginatedPublishedGoods = computed(() => {
  const state = paginationState.value.published;
  const start = (state.currentPage - 1) * state.itemsPerPage;
  const end = start + state.itemsPerPage;
  return publishedGoods.value.slice(start, end);
});

const paginatedBoughtGoods = computed(() => {
  const state = paginationState.value.bought;
  const start = (state.currentPage - 1) * state.itemsPerPage;
  const end = start + state.itemsPerPage;
  return boughtGoods.value.slice(start, end);
});

const paginatedOffShelfGoods = computed(() => {
  const state = paginationState.value.offShelf;
  const start = (state.currentPage - 1) * state.itemsPerPage;
  const end = start + state.itemsPerPage;
  return offShelfGoods.value.slice(start, end);
});

const paginatedSoldGoods = computed(() => {
  const state = paginationState.value.sold;
  const start = (state.currentPage - 1) * state.itemsPerPage;
  const end = start + state.itemsPerPage;
  return soldGoods.value.slice(start, end);
});

const paginatedWishlistGoods = computed(() => {
  const state = paginationState.value.wishlist;
  const start = (state.currentPage - 1) * state.itemsPerPage;
  const end = start + state.itemsPerPage;
  return wishlistGoods.value.slice(start, end);
});

// 计算属性 - 总页数
const publishedTotalPages = computed(() => {
  return Math.ceil(publishedGoods.value.length / paginationState.value.published.itemsPerPage);
});

const boughtTotalPages = computed(() => {
  return Math.ceil(boughtGoods.value.length / paginationState.value.bought.itemsPerPage);
});

const offShelfTotalPages = computed(() => {
  return Math.ceil(offShelfGoods.value.length / paginationState.value.offShelf.itemsPerPage);
});

const soldTotalPages = computed(() => {
  return Math.ceil(soldGoods.value.length / paginationState.value.sold.itemsPerPage);
});

const wishlistTotalPages = computed(() => {
  return Math.ceil(wishlistGoods.value.length / paginationState.value.wishlist.itemsPerPage);
});


// 更新商品价格
const updateProductPrice = async () => {
  if (!editingProduct.value || newPrice.value <= 0) {
    ElMessage.error('请输入有效的价格');
    return;
  }
  
  if (!editingProduct.value) return;
  
  try {
    const response = await request.put(`api/admin_manage/product/${editingProduct.value.id}/`, {
      price: newPrice.value
    });
    
    if (response.data.status === '200') {
      ElMessage.success(response.data.msg);
      closeEditModal();
      // 重新加载发布的商品数据
      const storedUser = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
      if (storedUser.user_id) {
        await loadPublishedGoods(storedUser.user_id);
      }
    } else {
      ElMessage.error(response.data.msg || '更新失败');
    }
  } catch (error: any) {
    console.error('更新商品价格失败：', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    } else {
      ElMessage.error('更新失败');
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding-top: 60px;
  min-height: 100vh;
  background-color: #f9fafb;
}

.profile-main {
  width: 1200px;
  margin: 0 auto;
  padding: 30px 10px;
  display: flex;
  gap: 20px;
}

/* 左侧导航栏样式 */
.sidebar {
  width: 220px;
  background-color: #f8f9fa; /* 浅灰色背景 */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  height: fit-content;
}

.nav-item {
  margin-bottom: 10px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
}

.nav-title {
  padding: 12px 15px;
  background-color: #f1f3f5; /* 浅色背景 */
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.nav-title:hover {
  background-color: #e9ecef; /* 悬停时的背景色 */
}

.arrow {
  transition: transform 0.3s;
  font-size: 12px;
}

.arrow.expanded {
  transform: rotate(180deg);
}

.sub-nav {
  background-color: #e7f5ff; /* 淡蓝色子菜单背景色 */
}

.sub-item {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 1px solid #d0ebff;
}

.sub-item:last-child {
  border-bottom: none;
}

.sub-item:hover {
  background-color: #d0ebff; /* 淡蓝色悬停时的背景色 */
}

.sub-item.active {
  background-color: #74c0fc; /* 激活时的背景色 */
  color: white;
}

.nav-item.active > .nav-title {
  background-color: #a5d8ff; /* 激活时的背景色 */
  color: white;
}

/* 主内容区样式 */
.content-area {
  flex: 1;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.content-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.content-header h2 {
  margin: 0;
  color: #333;
}

.content-section {
  padding: 10px 0;
}

.content-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 商品网格样式 */
.goods-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  /* 每行4个商品 */
  gap: 20px;
}

.goods-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  transition: box-shadow 0.3s ease;
}

.goods-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 商品链接样式 */
.goods-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.goods-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.goods-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.goods-info {
  text-align: left;
}

.goods-title {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goods-price {
  color: #e74c3c;
  font-weight: bold;
  margin: 5px 0;
  font-size: 16px;
}

.goods-quality,
.goods-status,
.goods-publisher {
  font-size: 12px;
  color: #999;
  margin: 3px 0;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.readonly-input {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.editable-input {
  background-color: #ffffff;
  cursor: text;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.save-btn {
  padding: 10px 30px;
  background-color: #4a6fa5; /* 蓝灰色按钮 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.save-btn:hover {
  background-color: #3a5a80;
}

.password-form,
.profile-form {
  max-width: 500px;
  margin: 0 auto;
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.page-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.clickable-item {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.clickable-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

/* 下架按钮样式 */
.take-down-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: #ff4757;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.take-down-btn:hover {
  background-color: #ff2e42;
  transform: scale(1.05);
}

.take-down-btn:active {
  transform: scale(0.95);
}


/* 上架按钮样式 */
.put-up-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: #38a169;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.put-up-btn:hover {
  background-color: #38a169;
  transform: scale(1.05);
}

.put-up-btn:active {
  transform: scale(0.95);
}

/* 确保商品信息区域有足够的空间 */
.goods-info {
  position: relative;
  min-height: 120px;
}
</style>