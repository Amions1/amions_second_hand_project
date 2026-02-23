<template>
  <footer class="footer-container">
    <div class="footer-content">
      <div class="footer-section">
        <h4 class="footer-title">阿烽二手优品</h4>
        <p class="footer-description">专业的二手交易平台，为您提供优质的二手商品买卖服务</p>
      </div>
      
      <div class="footer-section">
        <h4 class="footer-title">开发信息</h4>
        <ul class="footer-links">
          <li class="footer-item">开发者:阿烽 </li>
          <li class="footer-item">开发周期: 2026.1-2026.3</li>
          <li class="footer-item">所使用的技术栈: </li>
          <li class="footer-item">Django+Vue3+Redis+Mysql+ECharts+WebSocket+LangChain </li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4 class="footer-title">联系方式</h4>
        <ul class="footer-links">
          <li class="footer-item">邮箱: 1502399401@qq.com</li>
          <li class="footer-item">电话: 15152235183</li>
          <li class="footer-item">微信: W-112-CAP_vemis</li>
        </ul>
      </div>
    </div>
    
    <div class="footer-bottom">
      <p class="copyright">&copy;版权声明：南京航空航天大学 计算机科学与技术专业吴焕烽 毕业设计</p>
      <div class="footer-meta">
        <span class="version">v1.0.0</span>
        <span class="license">许可证: MIT</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// 组件不需要额外的逻辑
</script>

<style scoped>
.footer-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-top: 1px solid #e0e0e0;
  padding: 30px 0 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.footer-section {
  padding: 0 10px;
}

.footer-title {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #3498db;
}

.footer-description {
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-item {
  color: #34495e;
  font-size: 14px;
  margin-bottom: 8px;
  transition: color 0.3s ease;
  position: relative;
  padding-left: 10px;
}

.footer-item::before {
  content: "•";
  color: #3498db;
  font-weight: bold;
  position: absolute;
  left: 0;
  top: 0;
}

.footer-item:hover {
  color: #3498db;
  cursor: pointer;
}

.footer-bottom {
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.copyright {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0 0 10px 0;
}

.footer-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.version, .license {
  color: #95a5a6;
  font-size: 12px;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>