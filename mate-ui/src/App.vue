<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 左侧侧边栏 -->
      <el-aside width="280px" class="sidebar">
        <AppSidebar
          :history-list="historyList"
          :active-history-id="currentHistoryId"
          :active-module="activeModule"
          @logo-click="handleLogoClick"
          @module-select="handleModuleSelect"
          @history-select="handleHistorySelect"
        />
      </el-aside>
      
      <!-- 主体部分 -->
      <el-container class="main-container">
        <!-- Header -->
        <el-header height="64px" class="app-header-wrapper">
          <AppHeader
            :current-model="selectedModel"
            :user-name="userName"
            :user-role="userRole"
            @model-change="handleModelChange"
            @user-action="handleUserAction"
          />
        </el-header>
        
        <!-- 主页面 -->
        <el-main class="main-content">
          <!-- 新建会话页面 -->
          <div v-if="activeModule === 'new-chat'" class="content-wrapper">
            <!--
              注意：这里传递的是 currentContent (computed计算属性)，
              而不是 currentContentChunks (数组)
            -->
            <!-- 增加 @stage-click 事件监听 -->
            <ResultDisplay
              ref="resultDisplay"
              :content="currentContent"
              :current-stage="currentStage"
              :current-stage-index="currentStageIndex"
              :generating="generating"
              :current-title="currentTitle"
              @stage-click="handleStageClick"
            />

            <!-- 底部开始按钮 -->
            <DocumentUpload
              :generating="generating"
              @start="handleStart"
            />
          </div>

          <!-- 模块 A 页面 -->
          <ModuleA v-else-if="activeModule === 'module-a'" />

          <!-- 模块 B 页面 -->
          <ModuleB v-else-if="activeModule === 'module-b'" />

          <!-- 模块 C 页面 -->
          <div v-else-if="activeModule === 'module-c'" class="module-placeholder">
            <el-empty description="模块 C 功能开发中..." />
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import AppSidebar from './components/AppSidebar.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import DocumentUpload from './components/DocumentUpload.vue'
import AppHeader from './components/AppHeader.vue'
import ModuleA from './components/ModuleA.vue'
import ModuleB from './components/ModuleB.vue'
import { getHistoryList, getHistoryDetail } from './api' // 移除了 runStream，改用原生 fetch

export default {
  name: 'App',
  components: {
    AppSidebar,
    ResultDisplay,
    DocumentUpload,
    AppHeader,
    ModuleA,
    ModuleB
  },
  data() {
    return {
      historyList: [],
      currentHistoryId: null,
      currentContentChunks: [], // 使用数组存储chunks，确保响应式更新
      currentTitle: '',
      currentStage: '',
      currentStageIndex: -1,
      generating: false,
      stages: ['测试计划', '测试设计', '测试评审', '测试开发', '测试运行'],
      selectedModel: 'gpt-4',
      userName: '张三',
      userRole: '普通用户',
      activeModule: 'new-chat',
      stageHistory: ['', '', '', '', '']
    }
  },
  computed: {
    // 将数组中的所有 chunk 拼接成一个字符串，传给 ResultDisplay 进行 Markdown 渲染
    currentContent() {
      return this.currentContentChunks.join('')
    }
  },
  mounted() {
    this.loadHistoryList()
  },
  methods: {

    /**
     * 加载不同阶段对话
     * @param index
     */
    handleStageClick(index) {
      // 安全检查：如果正在生成，或者没有该阶段的历史数据，则不跳转
      if (this.generating) return

      const historyContent = this.stageHistory[index]
      console.log(this.stageHistory.length)
      if (historyContent) {
        console.log('回看阶段:', this.stages[index])
        // 1. 替换当前显示内容
        this.currentContentChunks = [historyContent]
        // 2. 高亮点击的步骤
        this.currentStageIndex = index
        // 3. 更新标题
        this.currentStage = this.stages[index]
      }
    },
    /**
     * 加载历史对话列表
     */
    async loadHistoryList() {
      try {
        const response = await getHistoryList()
        this.historyList = response.data || []

        // 如果有历史记录，默认选中第一个
        if (this.historyList.length > 0 && !this.currentHistoryId) {
          this.handleHistorySelect(this.historyList[0].id)
        }
      } catch (error) {
        console.error('加载历史列表失败:', error)
        // 开发环境使用模拟数据
        this.historyList = this.getMockHistoryList()
      }
    },

    /**
     * 选择历史对话
     */
    async handleHistorySelect(id) {
      this.currentHistoryId = id
      try {
        const response = await getHistoryDetail(id)
        const detail = response.data
        this.currentTitle = detail.title || ''
        // 确保是数组格式
        this.currentContentChunks = detail.content ? [detail.content] : []
        this.currentStage = detail.stage || ''
        this.currentStageIndex = detail.stageIndex !== undefined ? detail.stageIndex : -1
      } catch (error) {
        console.error('加载对话详情失败:', error)
        // 开发环境使用模拟数据
        const mockDetail = this.getMockHistoryDetail(id)
        this.currentTitle = mockDetail.title || ''
        this.currentContentChunks = mockDetail.content ? [mockDetail.content] : []
        this.currentStage = mockDetail.stage || ''
        this.currentStageIndex = mockDetail.stageIndex !== undefined ? mockDetail.stageIndex : -1
      }
    },

    /**
     * Logo 点击事件
     */
    handleLogoClick() {
      // 回到首页，清空当前内容
      this.currentHistoryId = null
      this.currentTitle = ''
      this.currentContentChunks = []
      this.currentStage = ''
      this.currentStageIndex = -1
      this.generating = false
      this.activeModule = 'new-chat'
      this.loadHistoryList()
    },

    /**
     * 模块选择
     */
    handleModuleSelect(module) {
      this.activeModule = module

      // 切换模块时清空当前会话内容
      if (module !== 'new-chat') {
        this.currentHistoryId = null
        this.currentTitle = ''
        this.currentContentChunks = []
        this.currentStage = ''
        this.currentStageIndex = -1
        this.generating = false
      } else {
        this.handleNewChat()
      }
    },

    /**
     * 新建对话
     */
    handleNewChat() {
      this.currentHistoryId = null
      this.currentTitle = ''
      this.currentContentChunks = []
      this.currentStage = ''
      this.currentStageIndex = -1
      this.generating = false
    },

    /**
     * 处理模型切换
     */
    handleModelChange(model) {
      this.selectedModel = model
      console.log('切换模型:', model)
    },

    /**
     * 处理用户操作
     */
    handleUserAction(action) {
      switch (action) {
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
    },

    /**
     * 开始生成 - 核心修改部分
     * 使用 fetch 处理 NDJSON 流式数据
     */
    async handleStart({ project, prompt }) {
      // 1. 初始化状态
      this.generating = true
      this.currentContentChunks = []
      this.currentStageIndex = -1
      this.currentTitle = prompt || '测试生成任务'
      // 重置历史记录槽位
      this.stageHistory = ['', '', '', '', '']

      try {
        // 直接连接后端，绕过代理（根据你之前的反馈）
        const response = await fetch(`http://127.0.0.1:5000/run?project=${encodeURIComponent(project)}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })

        if (!response.ok) throw new Error(`请求失败: ${response.statusText}`)

        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let buffer = ''
        let isReading = true

        while (isReading) {
          const { done, value } = await reader.read()
          if (done) {
            isReading = false
            break
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop()

          for (const line of lines) {
            if (!line.trim()) continue

            try {
              const msg = JSON.parse(line)

              if (msg.type === 'stage') {
                // 【场景 A：切换阶段】

                // 1. 在清空前，先将"上一个阶段"的内容归档到 history
                // (前提是上一个阶段是有效的，即 index >= 0)
                if (this.currentStageIndex >= 0 && this.currentStageIndex < 5) {
                  this.stageHistory[this.currentStageIndex] = this.currentContentChunks.join('')
                }

                // 2. 更新状态到新阶段
                this.currentStageIndex = msg.data.index
                this.currentStage = msg.data.name

                // 3. 清空屏幕
                this.currentContentChunks = []
              }
              else if (msg.type === 'content') {
                // 【场景 B：追加内容】
                this.currentContentChunks.push(msg.data)
              }
            } catch (e) {
              console.warn('JSON Parse Error', e)
            }
          }
        }

        // 【循环结束后】：非常重要！
        // 因为最后一个阶段完成后，不会再有新的 'stage' 信号来触发归档
        // 所以必须手动保存最后一个阶段的内容
        if (this.currentStageIndex >= 0 && this.currentStageIndex < 5) {
          this.stageHistory[this.currentStageIndex] = this.currentContentChunks.join('')
        }

        // 结束处理
        this.generating = false
        // 确保进度条显示完成
        if (this.currentStageIndex < 4) this.currentStageIndex = 4

        if (this.loadHistoryList) this.loadHistoryList()

      } catch (error) {
        console.error('生成失败:', error)
        this.generating = false
        this.currentContentChunks.push(`\n\n> **[系统错误]**: ${error.message}`)
      }
    },

    /**
     * 获取模拟历史列表（用于开发环境）
     */
    getMockHistoryList() {
      return [
        {
          id: '1',
          title: '用户管理系统测试用例',
          createTime: new Date().toISOString()
        },
        {
          id: '2',
          title: '订单管理模块测试用例',
          createTime: new Date(Date.now() - 86400000).toISOString()
        }
      ]
    },

    /**
     * 获取模拟历史详情（用于开发环境）
     */
    getMockHistoryDetail(id) {
      return {
        id: id,
        title: '模拟测试详情 ' + id,
        content: '# 测试运行\n\n这里是模拟的测试内容...',
        stage: '测试运行',
        stageIndex: 4
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #ffffff;
  overflow: hidden;
}

.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.app-header-wrapper {
  padding: 0;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
}

.main-content {
  flex: 1;
  overflow: hidden;
  background: #ffffff;
  position: relative;
  padding: 20px;
}

.content-wrapper {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: transparent;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.module-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
</style>
