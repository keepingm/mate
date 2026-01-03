<template>
  <div class="document-upload" :class="{ generating }">
    <div class="upload-panel">

      <!-- 核心输入卡片容器 -->
      <div class="chat-box">

        <!-- 上半部分：文本输入区 (去边框) -->
        <div class="input-section">
          <el-input
            v-model="userPrompt"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 8 }"
            placeholder="输入测试计划..."
            :disabled="generating"
            class="invisible-textarea"
            resize="none"
          />
        </div>

        <!-- 下半部分：工具栏 -->
        <div class="toolbar-section">

          <!-- 左侧：项目选择 (优化后的胶囊样式) -->
          <div class="toolbar-left">
            <el-select
              v-model="selectedProject"
              placeholder="选择项目"
              size="default"
              :disabled="generating"
              class="capsule-select"
              :teleported="false"
            >
              <template #prefix>
                <!-- 加个小图标增加精致感 -->
                <el-icon><FolderOpened /></el-icon>
              </template>
              <el-option
                v-for="project in projects"
                :key="project.value"
                :label="project.label"
                :value="project.value"
              />
            </el-select>
          </div>

          <!-- 右侧：发送按钮 (保持原有逻辑，只调整位置) -->
          <div class="toolbar-right">
            <el-button
              type="primary"
              :loading="generating"
              class="send-btn"
              @click="handleStart"
              circle
            >
              <el-icon v-if="!generating"><VideoPlay /></el-icon>
            </el-button>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { VideoPlay, FolderOpened } from "@element-plus/icons-vue";

export default {
  name: 'DocumentUpload',
  components: { VideoPlay, FolderOpened },
  props: {
    generating: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start'],
  data() {
    return {
      selectedProject: '',
      userPrompt: '',
      projects: [
        { label: 'Stock Project', value: 'project-a' },
        { label: 'ReadTime', value: 'project-b' },
        { label: 'Hone Platform', value: 'project-c' }
      ]
    }
  },
  methods: {
    handleStart() {
      if (this.generating) return
      this.$emit('start', {
        project: this.selectedProject,
        prompt: this.userPrompt
      })
    }
  }
}
</script>

<style scoped>
.document-upload {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  width: 100%;
}

/* 外部容器 */
.upload-panel {
  width: 100%;
  max-width: 890px;
  /* 只有在大容器需要背景时才开启，这里为了仿图，主要样式在 chat-box */
}

/* 仿截图的核心大卡片 */
.chat-box {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 16px; /* 大圆角 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* 柔和的高级阴影 */
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 聚焦时的微交互 */
.chat-box:focus-within {
  border-color: #c0c4cc;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* --- 输入框区域 --- */
.input-section {
  width: 100%;
}

/* 深度修改 Element 输入框，去除原本的边框和阴影 */
.invisible-textarea :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: none !important;
  padding: 4px 8px;
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
  background-color: transparent;
}

.invisible-textarea :deep(.el-textarea__inner::placeholder) {
  color: #a8abb2;
}

/* --- 底部工具栏 --- */
.toolbar-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px; /*稍微内缩一点*/
}

/* --- 胶囊样式下拉框 (高级感核心) --- */
.capsule-select {
  width: 160px;
}

/* 修改 Select 内部 Input 的样式 */
.capsule-select :deep(.el-input__wrapper) {
  background-color: #f2f3f5; /* 淡灰色背景，类似 Notion/Claude 风格 */
  border-radius: 20px;       /* 胶囊圆角 */
  box-shadow: none !important; /* 去除默认边框 */
  padding: 4px 12px;
  transition: all 0.2s;
}

/* 下拉框悬停效果 */
.capsule-select :deep(.el-input__wrapper:hover) {
  background-color: #e6e8eb;
}

/* 下拉框聚焦效果 */
.capsule-select :deep(.el-input__wrapper.is-focus) {
  background-color: #ffffff;
  box-shadow: 0 0 0 1px #409eff inset !important; /* 聚焦时显示细微蓝边 */
}

/* 字体调整 */
.capsule-select :deep(.el-input__inner) {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

/* 调整图标颜色 */
.capsule-select :deep(.el-icon) {
  color: #909399;
}

/* --- 发送按钮 --- */
.send-btn {
  width: 36px;
  height: 36px;
  font-size: 16px;
  transition: transform 0.2s ease;
  /* 如果想要截图那种纯色圆球，Element Plus 的 circle 属性已经很好，
     这里增加一点阴影 */
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3);
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(64, 158, 255, 0.4);
}
</style>