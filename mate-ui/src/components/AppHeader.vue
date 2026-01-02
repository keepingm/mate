<template>
  <div class="app-header">
    <div class="header-left">
      <span class="selector-label">模型：</span>
      <el-select
        v-model="selectedModel"
        @change="handleModelChange"
        placeholder="选择模型"
        class="model-select"
        size="default"
      >
        <el-option
          v-for="model in models"
          :key="model.value"
          :label="model.label"
          :value="model.value"
        />
      </el-select>
    </div>
    
    <div class="header-right">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="36" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <div class="user-name">{{ userName }}</div>
            <div class="user-role">{{ userRole }}</div>
          </div>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { User, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'

export default {
  name: 'AppHeader',
  components: {
    User,
    ArrowDown,
    Setting,
    SwitchButton
  },
  props: {
    currentModel: {
      type: String,
      default: 'gpt-4'
    },
    userName: {
      type: String,
      default: '用户'
    },
    userRole: {
      type: String,
      default: '普通用户'
    }
  },
  emits: ['model-change', 'user-action'],
  data() {
    return {
      selectedModel: this.currentModel,
      models: [
        { label: 'GPT-4', value: 'gpt-4' },
        { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
        { label: 'Claude 3 Opus', value: 'claude-3-opus' },
        { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet' },
        { label: 'Gemini Pro', value: 'gemini-pro' }
      ]
    }
  },
  watch: {
    currentModel(newVal) {
      this.selectedModel = newVal
    }
  },
  methods: {
    handleModelChange() {
      this.$emit('model-change', this.selectedModel)
    },
    handleCommand(command) {
      this.$emit('user-action', command)
      // 可以在这里处理具体的用户操作
      switch (command) {
        case 'profile':
          console.log('打开个人资料')
          break
        case 'settings':
          console.log('打开设置')
          break
        case 'logout':
          console.log('退出登录')
          break
      }
    }
  }
}
</script>

<style scoped>
.app-header {
  height: 100%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.model-select {
  min-width: 180px;
}

:deep(.el-select .el-input__wrapper) {
  background-color: white;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

:deep(.el-select:hover .el-input__wrapper) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.user-info:hover {
  background: #e4e7ed;
}

.user-avatar {
  flex-shrink: 0;
  background: #e4e7ed;
}

.user-avatar :deep(.el-icon) {
  color: #606266;
  font-size: 18px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
}

.dropdown-icon {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 15px;
  }
  
  .model-select {
    min-width: 140px;
  }
  
  .selector-label {
    font-size: 13px;
  }
  
  .user-details {
    display: none;
  }
}
</style>

