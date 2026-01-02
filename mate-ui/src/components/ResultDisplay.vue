<template>
  <div class="result-display">
    <div v-if="currentStageIndex >= 0" class="progress-section">
      <div class="progress-title">生成进度</div>
      <div class="progress-steps">
        <div
          v-for="(stage, index) in stages"
          :key="index"
          class="progress-step"
          :class="{
            active: index === currentStageIndex,
            completed: index < currentStageIndex
          }"
        >
          <div class="step-indicator">
            <span v-if="index < currentStageIndex" class="step-check">✓</span>
            <span v-else class="step-number">{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ stage }}</div>
        </div>
      </div>
    </div>
    
    <div class="content-section">
      <div v-if="!content && !generating" class="empty-state">
        <!-- Logo 展示 -->
        <div class="logo-display">
          <div class="logo-container">
            <el-icon class="logo-icon"><ChatDotRound /></el-icon>
            <span class="logo-text">Mate AI</span>
          </div>
        </div>
      </div>
      <div v-else class="content-area">
        <div class="content-header">
          <h3 v-if="currentTitle">{{ currentTitle }}</h3>
        </div>
        <div class="content-body" ref="contentBody">
          <!-- 对话消息列表 -->
          <div class="message-list">
            <!-- AI 回复消息 -->
            <div v-if="content || generating" class="message-item ai-message">
              <el-avatar class="message-avatar" :size="32">
                <el-icon><Robot /></el-icon>
              </el-avatar>
              <div class="message-content">
                <div 
                  v-if="content" 
                  class="content-text markdown-body"
                  v-html="renderedContent"
                ></div>
                <div v-if="generating && !content" class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div v-if="generating && content" class="typing-cursor">|</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ChatDotRound, Robot } from '@element-plus/icons-vue'

export default {
  name: 'ResultDisplay',
  components: {
    ChatDotRound,
    Robot
  },
  props: {
    content: {
      type: String,
      default: ''
    },
    currentStage: {
      type: String,
      default: ''
    },
    currentStageIndex: {
      type: Number,
      default: -1
    },
    generating: {
      type: Boolean,
      default: false
    },
    currentTitle: {
      type: String,
      default: ''
    },
    // 是否启用 Markdown 渲染，默认启用
    enableMarkdown: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      stages: ['测试计划', '测试设计', '测试评审', '测试开发', '测试运行']
    }
  },
  mounted() {
    // 配置 marked 选项
    marked.setOptions({
      breaks: true, // 支持 GitHub 风格的换行
      gfm: true, // 启用 GitHub Flavored Markdown
      headerIds: false, // 禁用自动生成 header ID
      mangle: false // 不混淆邮箱地址
    })
  },
  computed: {
    renderedContent() {
      if (!this.content) return ''
      
      if (this.enableMarkdown) {
        try {
          // 使用 marked 将 Markdown 转换为 HTML
          const html = marked.parse(this.content)
          // 使用 DOMPurify 清理 HTML，防止 XSS 攻击
          return DOMPurify.sanitize(html)
        } catch (error) {
          console.error('Markdown 渲染错误:', error)
          // 如果渲染失败，返回原始内容（转义 HTML）
          return this.escapeHtml(this.content)
        }
      } else {
        // 如果不启用 Markdown，返回转义的 HTML
        return this.escapeHtml(this.content)
      }
    }
  },
  watch: {
    content() {
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    }
  },
  methods: {
    scrollToBottom() {
      const contentBody = this.$refs.contentBody
      if (contentBody) {
        contentBody.scrollTop = contentBody.scrollHeight
      }
    },
    escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }
  }
}
</script>

<style scoped>
.result-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: transparent;
  overflow: hidden;
}

.progress-section {
  padding: 24px 0;
  background: transparent;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 24px;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e4e7ed;
  z-index: 0;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
  flex: 1;
}

.step-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f5f7fa;
  border: 2px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.progress-step.completed .step-indicator {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.progress-step.active .step-indicator {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  animation: pulse 1.5s infinite;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(33, 150, 243, 0);
  }
}

.step-number {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
}

.progress-step.active .step-number {
  color: white;
}

.progress-step.completed .step-number {
  color: white;
}

.step-check {
  font-size: 20px;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.progress-step.completed .step-label,
.progress-step.active .step-label {
  color: #303133;
  font-weight: 500;
}

.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  min-height: 400px;
}

.logo-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 60px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  font-size: 64px;
  color: #409eff;
  animation: float 3s ease-in-out infinite;
}

.logo-text {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 2px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-text {
  font-size: 16px;
  color: #909399;
  margin-top: 20px;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: 24px 0;
  border-bottom: none;
  background: transparent;
  text-align: center;
}

.content-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.content-body {
  flex: 1;
  padding: 40px 0;
  overflow-y: auto;
  background-color: transparent;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.message-avatar {
  flex-shrink: 0;
  background: #f0f2f5;
}

.message-avatar :deep(.el-icon) {
  color: #409eff;
  font-size: 18px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.ai-message .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.ai-message .message-avatar :deep(.el-icon) {
  color: white;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.content-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.9;
  color: #303133;
  word-wrap: break-word;
  max-width: 100%;
  padding: 16px 0;
}

/* Markdown 样式 */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  color: #24292e;
}

.markdown-body h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h3 {
  font-size: 1.25em;
}

.markdown-body p {
  margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
  margin-bottom: 16px;
  padding-left: 2em;
}

.markdown-body li {
  margin-bottom: 8px;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body pre code {
  display: inline;
  max-width: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}

.markdown-body blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin-bottom: 16px;
}

.markdown-body table {
  border-spacing: 0;
  border-collapse: collapse;
  margin-bottom: 16px;
  width: 100%;
}

.markdown-body table th,
.markdown-body table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body table th {
  font-weight: 600;
  background-color: #f6f8fa;
}

.markdown-body table tr {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-body table tr:nth-child(2n) {
  background-color: #f6f8fa;
}

.markdown-body a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  margin-bottom: 16px;
  border-radius: 4px;
}

.markdown-body hr {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #e1e4e8;
  border: 0;
}

.typing-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  font-weight: bold;
  color: #2196f3;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

.content-body::-webkit-scrollbar {
  width: 8px;
}

.content-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.content-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

