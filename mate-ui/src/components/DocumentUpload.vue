<template>
  <div class="document-upload" :class="{ 'generating': generating }">
    <div class="upload-controls">
      <!-- 项目下拉框 -->
      <el-select
        v-model="selectedProject"
        placeholder="选择项目"
        class="project-select"
        size="large"
        :disabled="generating"
      >
        <el-option
          v-for="project in projects"
          :key="project.value"
          :label="project.label"
          :value="project.value"
        />
      </el-select>
      
      <!-- 开始生成按钮 -->
      <el-button
        type="primary"
        size="large"
        :loading="generating"
        :disabled="generating"
        @click="handleStart"
        class="start-btn"
      >
        <el-icon v-if="!generating"><VideoPlay /></el-icon>
        <span>{{ generating ? '生成中...' : '开始生成' }}</span>
      </el-button>
    </div>
  </div>
</template>

<script>
import { VideoPlay } from '@element-plus/icons-vue'

export default {
  name: 'DocumentUpload',
  components: {
    VideoPlay
  },
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
      projects: [
        { label: '项目 A', value: 'project-a' },
        { label: '项目 B', value: 'project-b' },
        { label: '项目 C', value: 'project-c' },
        { label: '项目 D', value: 'project-d' }
      ]
    }
  },
  methods: {
    handleStart() {
      if (!this.generating) {
        this.$emit('start')
      }
    }
  }
}
</script>

<style scoped>
.document-upload {
  padding: 40px 0;
  background-color: transparent;
  transition: all 0.3s ease;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.document-upload.generating {
  position: sticky;
  bottom: 0;
  background: #ffffff;
  border-top: 1px solid #e4e7ed;
  padding: 20px 0;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  min-height: auto;
  z-index: 10;
}

.upload-controls {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: center;
  padding: 0 40px;
}

.document-upload.generating .upload-controls {
  justify-content: flex-end;
  max-width: 100%;
}

.project-select {
  min-width: 180px;
}

.start-btn {
  min-width: 160px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.start-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transform: translateY(-1px);
}

.start-btn :deep(.el-icon) {
  margin-right: 6px;
}

/* 未生成状态时，按钮居中且更大 */
.document-upload:not(.generating) .start-btn {
  min-width: 200px;
  height: 48px;
  font-size: 17px;
}

.document-upload:not(.generating) .project-select {
  min-width: 200px;
}
</style>

