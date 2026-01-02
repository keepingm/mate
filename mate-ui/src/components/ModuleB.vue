<template>
  <div class="module-b">
    <div class="module-header">
      <h2>模块 B</h2>
      <p class="module-description">这是模块 B 的功能页面</p>
    </div>
    
    <div class="module-content">
      <el-card class="content-card">
        <template #header>
          <div class="card-header">
            <span>功能区域</span>
          </div>
        </template>
        
        <div class="card-body">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <el-icon class="feature-icon"><Setting /></el-icon>
                <h3>功能 1</h3>
                <p>这是模块 B 的功能 1 描述</p>
                <el-button type="success" size="small">开始使用</el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <el-icon class="feature-icon"><Tools /></el-icon>
                <h3>功能 2</h3>
                <p>这是模块 B 的功能 2 描述</p>
                <el-button type="success" size="small">开始使用</el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="feature-card">
                <el-icon class="feature-icon"><DataAnalysis /></el-icon>
                <h3>功能 3</h3>
                <p>这是模块 B 的功能 3 描述</p>
                <el-button type="success" size="small">开始使用</el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { Setting, Tools, DataAnalysis } from '@element-plus/icons-vue'

export default {
  name: 'ModuleB',
  components: {
    Setting,
    Tools,
    DataAnalysis
  }
}
</script>

<style scoped>
.module-b {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
  background: #f5f7fa;
}

.module-header {
  margin-bottom: 24px;
}

.module-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.module-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.module-content {
  flex: 1;
  overflow: auto;
}

.content-card {
  height: 100%;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.card-body {
  padding: 20px 0;
}

.feature-card {
  text-align: center;
  padding: 24px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 16px;
}

.feature-card h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.feature-card p {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>

