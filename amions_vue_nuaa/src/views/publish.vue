<template>
  <div class="publish-container">
    <Profile_header />
    <h2>发布商品</h2>
    <form @submit.prevent="handleSubmit" class="publish-form">
      <!-- 商品图片上传 -->
      <div class="form-group">
        <label for="image-upload" class="upload-label">
          <div v-if="previewImage" class="image-preview">
            <img :src="previewImage" alt="商品预览图" />
          </div>
          <div v-else class="upload-placeholder">
            <span>+</span>
            <p>点击上传商品图片</p>
          </div>
        </label>
        <input 
          id="image-upload" 
          type="file" 
          ref="fileInputRef"
          accept="image/*" 
          @change="handleImageChange"
          class="hidden-input"
        />
        <p class="help-text">支持 JPG、PNG 格式，大小不超过 5MB</p>
      </div>

      <!-- 商品名称 -->
      <div class="form-group">
        <label for="product-name">商品名称</label>
        <input 
          id="product-name" 
          type="text" 
          v-model="formData.title" 
          placeholder="请输入商品名称"
          required
        />
      </div>

      <!-- 商品类别 -->
      <div class="form-group">
        <label>商品类别</label>
        <div class="category-radio-group">
          <label
            v-for="category in childCategories"
            :key="category.id"
            class="category-radio-item"
            :class="{ 'is-selected': formData.category_id === category.id }"
          >
            <input
              type="radio"
              :value="category.id"
              v-model="formData.category_id"
              class="category-radio-input"
            />
            <span class="category-radio-label">{{ category.name }}</span>
          </label>
        </div>
        <p v-if="childCategories.length === 0" class="help-text">暂无可用分类</p>
      </div>

      <!-- 商品价格 -->
      <div class="form-group">
        <label for="product-price">商品价格</label>
        <input 
          id="product-price" 
          type="number" 
          v-model.number="formData.price" 
          placeholder="请输入商品价格"
          min="0.01"
          step="0.01"
          required
        />
      </div>

      <!-- 商品成色 -->
      <div class="form-group">
        <label for="product-quality">成色</label>
        <input 
          id="product-quality" 
          type="number" 
          v-model.number="formData.quality" 
          placeholder="请输入商品成色（50-100之间的整数）"
          required
        />
        <p class="help-text">商品的新旧程度（50~100）</p>
      </div>

      <!-- 商品详情 -->
      <div class="form-group">
        <label for="product-details">商品详情</label>
        <textarea 
          id="product-details" 
          v-model="formData.details" 
          placeholder="请输入商品的详细描述（最多800字）"
          maxlength="800"
          rows="6"
          class="details-textarea"
        ></textarea>
        <p class="help-text">商品的详细描述（最多800字）</p>
      </div>

      <!-- 提交按钮 -->
      <div class="form-group">
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? '发布中...' : '发布商品' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage, ElMessageBox } from 'element-plus';
import { isAuthenticated } from '@/utils/auth';
import Profile_header from "@/components/profile/profile_header.vue"; // 引入认证检查函数

// 定义类型
interface Category {
  id: number;
  parent_id: number;
  name: string;
}

interface FormData {
  title: string;
  category_id: number | null;
  price: number | null;
  quality: number | null;
  details: string | null;
  image: File | null;
}

// 响应式数据
const formData = ref<FormData>({
  title: '',
  category_id: null,
  price: null,
  quality: null,
  details: null,
  image: null
});

const childCategories = ref<Category[]>([]);
const previewImage = ref<string | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const isSubmitting = ref(false);
const router = useRouter();

// 验证成色输入
const validateQuality = (quality: number | null): boolean => {
  if (quality === null || quality === undefined) {
    ElMessage.error('请输入商品成色');
    return false;
  }
  
  if (quality < 50) {
    ElMessage.warning('商品太旧不支持上架');
    return false;
  }
  
  if (quality > 100) {
    ElMessage.warning('商品成色不能超过100');
    return false;
  }
  
  if (!Number.isInteger(quality)) {
    ElMessage.warning('商品成色必须是整数');
    return false;
  }
  
  return true;
};

// 处理图片选择
const handleImageChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件');
      return;
    }
    
    // 验证文件大小（不超过5MB）
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB');
      return;
    }
    
    // 更新表单数据
    formData.value.image = file;
    
    // 生成预览图片
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

// 检查用户是否已认证
const checkAuthentication = (): boolean => {
  if (!isAuthenticated()) {
    ElMessage.error('登录已过期，请重新登录');
    router.push('/login');
    return false;
  }
  return true;
};

// 提交表单
const handleSubmit = async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }

  // 验证必填字段
  if (!formData.value.title || !formData.value.title.trim()) {
    ElMessage.error('请输入商品名称');
    return;
  }
  
  if (!formData.value.category_id) {
    ElMessage.error('请选择商品类别');
    return;
  }
  
  if (!formData.value.price || formData.value.price <= 0 || formData.value.price>9999999) {
    ElMessage.error('请输入有效的商品价格');
    return;
  }
  
  if (!validateQuality(formData.value.quality)) {
    return;
  }
  
  if (!formData.value.image) {
    ElMessage.error('请上传商品图片');
    return;
  }
  
  // 获取当前用户信息
  const storedUser = sessionStorage.getItem('userInfo');
  if (!storedUser) {
    ElMessage.error('登录信息已过期，请重新登录');
    router.push('/login');
    return;
  }
  
  const userInfo = JSON.parse(storedUser);
  isSubmitting.value = true;
  
  try {
    // 创建 FormData 对象上传文件和其他数据
    const submitData = new FormData();
    submitData.append('title', formData.value.title);
    submitData.append('category_id', formData.value.category_id.toString());
    submitData.append('price', formData.value.price.toString());
    submitData.append('quality', formData.value.quality!.toString());
    submitData.append('details', formData.value.details?.trim() || '');
    submitData.append('status', '1'); // 默认状态为1
    submitData.append('user_id', userInfo.user_id); // 当前用户ID
    submitData.append('image', formData.value.image); // 图片文件

    // 不要手动设置Content-Type，让浏览器自动设置带有boundary的multipart类型
    const response = await request.post('api/goods/', submitData);
    
    // 统一处理响应状态码
    switch (response.data.status) {
      case '200':
        // 发布成功
        ElMessage.success('商品发布成功！');
        resetForm();
        router.push('/home');
        break;
        
      case '400':
        // 请求参数错误
        ElMessage.error(`发布失败: ${response.data.msg || '请求参数有误'}`);
        break;
        
      case '401':
        // 认证失败
        ElMessage.error(response.data.msg);
        router.push('/login');
        break;
        
      case '500':
        // 服务器内部错误
        ElMessage.error('服务器错误，请稍后重试');
        break;
        
      default:
        // 其他未知状态
        ElMessage.error(`发布失败: ${response.data.msg || '未知错误'}`);
        console.warn('未知的响应状态:', response.data);
    }
    
  } catch (error: any) {
    console.error('发布商品失败:', error);
  } finally {
    isSubmitting.value = false;
  }
};

// 重置表单函数
const resetForm = () => {
  formData.value = {
    title: '',
    category_id: null,
    price: null,
    quality: null,
    details: null,
    image: null
  };
  previewImage.value = null;
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
};

// 初始化时获取分类数据
onMounted(async () => {
  // 检查认证状态
  if (!checkAuthentication()) {
    return;
  }
  
  try {
    const response = await request.get('api/goods/first');
    if (response.data.status === '200') {
      // 过滤出子类别（parent_id 不为 0 的分类）
      childCategories.value = response.data.goods_category.filter(
        (category: Category) => category.parent_id !== 0
      );
    } else {
      console.error('获取商品分类失败:', response.data.msg);
    }
  } catch (error: any) {
    console.error('请求商品分类失败：', error);
    if (error.response?.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      router.push('/login');
    }
  }
});
</script>

<style scoped>
.publish-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.publish-container h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.publish-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

/* 商品类别单选按钮组样式 */
.category-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.category-radio-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background-color: #f5f7fa;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-radio-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.category-radio-item.is-selected {
  border-color: #409eff;
  background-color: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.category-radio-input {
  display: none;
}

.category-radio-label {
  font-size: 14px;
  font-weight: 500;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.upload-label {
  display: block;
  width: 200px;
  height: 200px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  margin-bottom: 10px;
  transition: border-color 0.3s;
}

.upload-label:hover {
  border-color: #409eff;
}

.image-preview {
  width: 100%;
  height: 100%;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #999;
}

.upload-placeholder span {
  font-size: 40px;
  margin-bottom: 10px;
}

.hidden-input {
  display: none;
}

.help-text {
  color: #999;
  font-size: 14px;
  margin-top: 5px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.submit-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

textarea.details-textarea {
  width: 100%;
  min-height: 150px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}
</style>