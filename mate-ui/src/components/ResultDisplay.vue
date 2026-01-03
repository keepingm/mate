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
        <div class="content-body" ref="contentBody">
          <!-- 对话消息列表 -->
          <div class="message-list">
            <!-- AI 回复消息 -->
            <div v-if="content || generating" class="message-item ai-message">
              <el-avatar class="message-avatar" :size="32">
                <el-icon><Avatar /></el-icon>
              </el-avatar>
              <div class="message-content">
                <div
                  v-if="content"
                  class="content-text"
                >
                  <vue-markdown :source="content" :options="markdownOptions" />
                </div>
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
import { ChatDotRound, Avatar } from '@element-plus/icons-vue'
import VueMarkdown from 'vue3-markdown-it'
import 'highlight.js/styles/default.css' // 代码高亮主题

// 配置marked以支持代码高亮
import hljs from 'highlight.js'

// 设置marked选项
marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false
});

export default {
  name: 'ResultDisplay',
  components: {
    ChatDotRound,
    Avatar,
    VueMarkdown
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
      stages: ['测试计划', '测试设计', '测试评审', '测试开发', '测试运行'],
      markdownOptions: {
        html: true,
        linkify: true,
        typographer: true,
        breaks: true,
        langPrefix: 'hljs language-',
        highlight: function (str, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(str, { language: lang }).value;
            } catch (err) {
              console.error('代码高亮错误:', err);
            }
          }
          return hljs.highlightAuto(str).value;
        }
      }
    }
  },
  mounted() {
    // 组件挂载后无需特殊配置
  },
  computed: {
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

<style>
.result-display {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.progress-section {
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
  z-index: 1;
}

.progress-step:not(:last-child) .step-indicator::after {
  content: '';
  position: absolute;
  top: 16px;
  left: 50%;
  right: -50%;
  height: 2px;
  background: #dcdfe6;
  z-index: -1;
}

.progress-step.completed:not(:last-child) .step-indicator::after {
  background: #409eff;
}

.step-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  background: #f4f4f5;
  color: #909399;
  font-size: 14px;
  font-weight: bold;
  position: relative;
  z-index: 2;
}

.progress-step.completed .step-indicator {
  background: #409eff;
  color: #fff;
}

.progress-step.active .step-indicator {
  background: #409eff;
  color: #fff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.3);
}

.step-check {
  font-size: 16px;
  font-weight: bold;
}

.step-number {
  font-size: 14px;
}

.step-label {
  font-size: 12px;
  color: #606266;
  text-align: center;
  max-width: 60px;
  word-break: break-word;
}

.progress-step.completed .step-label,
.progress-step.active .step-label {
  color: #409eff;
}

.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-icon {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 16px;
}

.logo-text {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  letter-spacing: 1px;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.content-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  padding: 0 16px;
}

.message-avatar {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-text {
  width: 100%;
}

/* 代码块样式增强 */
.content-text pre {
  background-color: #2d2d2d !important;
  border-radius: 8px !important;
  padding: 16px !important;
  overflow-x: auto !important;
  margin: 16px 0 !important;
  border: 1px solid #444 !important;
  position: relative;
}

.content-text code {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace !important;
  font-size: 14px !important;
}

.content-text pre code {
  background: none !important;
  padding: 0 !important;
  color: #f8f8f2 !important;
  display: block !important;
  overflow-x: auto !important;
}

/* 代码高亮主题 */
.content-text .hljs-comment,
.content-text .hljs-quote {
  color: #888;
}

.content-text .hljs-keyword,
.content-text .hljs-selector-tag,
.content-text .hljs-subst {
  color: #f92672;
}

.content-text .hljs-number,
.content-text .hljs-literal,
.content-text .hljs-variable,
.content-text .hljs-template-variable,
.content-text .hljs-tag .hljs-attr {
  color: #ae81ff;
}

.content-text .hljs-string,
.content-text .hljs-doctag {
  color: #a6e22e;
}

.content-text .hljs-title,
.content-text .hljs-section,
.content-text .hljs-selector-id {
  color: #a6e22e;
}

.content-text .hljs-type,
.content-text .hljs-class .hljs-title {
  color: #66d9ef;
}

.content-text .hljs-tag,
.content-text .hljs-name,
.content-text .hljs-attribute {
  color: #f92672;
}

.content-text .hljs-symbol,
.content-text .hljs-bullet,
.content-text .hljs-link,
.content-text .hljs-meta,
.content-text .hljs-selector-attr,
.content-text .hljs-selector-pseudo {
  color: #bf79db;
}

.content-text .hljs-built_in,
.content-text .hljs-deletion {
  color: #e6db74;
}

.content-text .hljs-formula {
  background: #0f0f0f;
}

.content-text .hljs-emphasis {
  font-style: italic;
}

.content-text .hljs-strong {
  font-weight: bold;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 20px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #b5b5b5;
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 16px;
  background-color: #409eff;
  margin-left: 4px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>


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

