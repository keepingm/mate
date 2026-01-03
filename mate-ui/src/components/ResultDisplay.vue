<template>
  <div class="result-display">
    <!-- 1. 顶部进度条区域 -->
    <div v-if="currentStageIndex >= 0" class="progress-section">
      <div class="progress-title">生成进度</div>
      <div class="progress-steps">
        <div
          v-for="(stage, index) in stages"
          :key="index"
          class="progress-step"
          :class="{
            active: index === currentStageIndex,
            completed: index < currentStageIndex,
            'is-clickable': !generating && index <= maxStageIndex // 只有非生成状态或历史步骤可点
          }"
          @click="handleStepClick(index)"
        >
          <div class="step-indicator">
            <span v-if="index < currentStageIndex" class="step-check">✓</span>
            <span v-else class="step-number">{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ stage }}</div>
        </div>
      </div>
    </div>

    <!-- 2. 内容展示区域 -->
    <div class="content-section">
      <!-- 空状态：显示 Logo -->
      <div v-if="!content && !generating" class="empty-state">
        <div class="logo-display">
          <div class="logo-container">
            <el-icon class="logo-icon"><ChatDotRound /></el-icon>
            <span class="logo-text">Mate AI</span>
          </div>
        </div>
      </div>

      <!-- 有内容状态：显示 Markdown -->
      <div v-else class="content-area">
        <div class="content-body" ref="contentBody">
          <div class="message-list">
            <div class="message-item ai-message">
              <!-- AI 头像 -->
              <el-avatar class="message-avatar" :size="32">
                <el-icon><Avatar /></el-icon>
              </el-avatar>

              <!-- 消息内容 -->
              <div class="message-content">
                <!-- Markdown 渲染区 -->
                <div v-if="content" class="content-text">
                  <vue-markdown :source="content" :options="markdownOptions" />
                </div>

                <!-- 加载/打字动画 -->
                <div v-if="generating && !content" class="typing-indicator">
                  <span></span><span></span><span></span>
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

// 引入浅色高亮主题
import 'highlight.js/styles/github.css'
import hljs from 'highlight.js'

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
  breaks: true,
  gfm: true
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
    }
  },
  data() {
    return {
      stages: ['测试计划', '测试设计', '测试评审', '测试开发', '测试运行'],
      maxStageIndex: 0, // 记录达到过的最大阶段，防止点击未生成的阶段
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
              console.error('Highlight Error:', err);
            }
          }
          return hljs.highlightAuto(str).value;
        }
      }
    }
  },
  watch: {
    content() {
      this.$nextTick(() => { this.scrollToBottom() })
    },
    // 监听进度，更新最大可访问进度
    currentStageIndex(val) {
      if (val > this.maxStageIndex) {
        this.maxStageIndex = val
      }
    }
  },
  methods: {
    scrollToBottom() {
      const contentBody = this.$refs.contentBody
      if (contentBody) {
        contentBody.scrollTop = contentBody.scrollHeight
      }
    },
    // 处理点击事件
    handleStepClick(index) {
      // 正在生成时，或者点击了还没生成的步骤，不允许跳转
      if (this.generating) return
      if (index > this.maxStageIndex) return

      this.$emit('stage-click', index)
    }
  }
}
</script>

<style>
/* 增加点击手势样式 */
.progress-step.is-clickable {
  cursor: pointer;
}
.progress-step.is-clickable:hover .step-indicator {
  border-color: #409eff;
  background-color: #ecf5ff;
}
/*
 * 全局样式部分
 * 用于控制 markdown 渲染出来的 HTML (pre, code 等)
 */

/* --- 1. Mac 风格浅色代码块 --- */
.content-text pre {
  /* 容器背景：白色 */
  background-color: #ffffff !important;
  /* 边框：浅灰 */
  border: 1px solid #d0d7de !important;
  border-radius: 8px !important;
  margin: 24px 0 !important;
  /* 阴影：非常淡的阴影增加层次感 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  position: relative;
  overflow: hidden !important;
  padding: 0 !important; /* 内边距交给 code 处理 */
}

/* --- 2. 模拟 Mac 窗口顶部栏 --- */
.content-text pre::before {
  content: '';
  display: block;
  height: 32px;
  /* 顶部栏背景：极浅的灰色 */
  background-color: #f6f8fa;
  border-bottom: 1px solid #d0d7de;
  /* 模拟红黄绿三个圆点 */
  background-image:
    radial-gradient(circle, #ff5f56 5px, transparent 6px),
    radial-gradient(circle, #ffbd2e 5px, transparent 6px),
    radial-gradient(circle, #27c93f 5px, transparent 6px);
  background-size: 100% 100%;
  background-position: 14px center, 34px center, 54px center;
  background-repeat: no-repeat;
}

/* --- 3. 代码文字区域 --- */
.content-text pre code {
  display: block;
  padding: 16px 20px !important;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  color: #24292f !important; /* 深灰色文字，对比度好 */
  background: transparent !important; /* 背景由 pre 决定 */
  overflow-x: auto;
}

/* --- 4. 滚动条美化 (针对代码块) --- */
.content-text pre code::-webkit-scrollbar {
  height: 6px;
  background-color: transparent;
}
.content-text pre code::-webkit-scrollbar-thumb {
  background-color: #d1d5da;
  border-radius: 3px;
}

/*
 * 关键清理：
 * 已经移除了旧代码中所有 .hljs-* 的手动颜色定义
 * 现在颜色完全由 'highlight.js/styles/github.css' 控制
 */

</style>

<style scoped>
/*
 * 局部样式部分
 * 控制布局、进度条、头像等组件样式
 */

.result-display {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* --- 进度条样式 --- */
.progress-section {
  padding: 24px 0;
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
/* 步骤圆圈 */
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
/* 完成状态 */
.progress-step.completed .step-indicator {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}
/* 进行中状态 */
.progress-step.active .step-indicator {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}
.step-number { font-weight: 600; color: #909399; }
.progress-step.active .step-number, .progress-step.completed .step-number { color: white; }
.step-label { font-size: 12px; color: #909399; }
.progress-step.active .step-label { color: #303133; font-weight: 500; }

/* --- 内容区域布局 --- */
.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 空状态 Logo */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.logo-icon {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
.logo-text {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
}

/* 消息列表 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.content-body {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
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
  padding-right: 16px;
}
/* 消息头像 */
.message-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.message-avatar :deep(.el-icon) {
  color: white;
  font-size: 18px;
}
.message-content {
  flex: 1;
  min-width: 0;
}

/* Markdown 正文通用样式 */
.content-text {
  font-size: 15px;
  line-height: 1.8;
  color: #2c3e50;
}

/* 行内代码优化 (例如 `npm install`) */
.content-text :deep(code:not(pre code)) {
  padding: 0.2em 0.4em;
  margin: 0 2px;
  font-size: 85%;
  background-color: #eff1f3; /* 浅灰背景 */
  color: #d63200;            /* 橘红色文字 */
  border-radius: 4px;
  font-family: monospace;
}

/* 列表样式优化 */
.content-text :deep(ul), .content-text :deep(ol) {
  padding-left: 20px;
  margin-bottom: 16px;
}
.content-text :deep(li) {
  margin-bottom: 6px;
}

/* 标题优化 */
.content-text :deep(h1), .content-text :deep(h2), .content-text :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1a1a1a;
}
.content-text :deep(h1) { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.content-text :deep(h2) { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }

/* 打字机光标 */
.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 16px;
  background-color: #409eff;
  margin-left: 4px;
  vertical-align: middle;
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
/* 加载中三个点 */
.typing-indicator span {
  width: 6px;
  height: 6px;
  background-color: #909399;
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
</style>