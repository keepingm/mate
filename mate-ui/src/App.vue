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
            <ResultDisplay
              ref="resultDisplay"
              :content="currentContent"
              :current-stage="currentStage"
              :current-stage-index="currentStageIndex"
              :generating="generating"
              :current-title="currentTitle"
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
          
          <!-- 模块 C 页面（可以后续添加） -->
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
import { getHistoryList, getHistoryDetail, runStream } from './api'

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
      activeModule: 'new-chat'
    }
  },
  computed: {
    currentContent() {
      // 实时join所有chunks
      return this.currentContentChunks.join('')
    }
  },
  mounted() {
    this.loadHistoryList()
  },
  methods: {
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
      // 重新加载历史列表
      this.loadHistoryList()
    },
    
    /**
     * 模块选择
     */
    handleModuleSelect(module) {
      this.activeModule = module
      
      // 根据模块执行不同操作
      switch (module) {
        case 'new-chat':
          this.handleNewChat()
          break
        case 'module-a':
          // 切换到模块 A，清空当前会话内容
          this.currentHistoryId = null
          this.currentTitle = ''
          this.currentContentChunks = []
          this.currentStage = ''
          this.currentStageIndex = -1
          this.generating = false
          break
        case 'module-b':
          // 切换到模块 B，清空当前会话内容
          this.currentHistoryId = null
          this.currentTitle = ''
          this.currentContentChunks = []
          this.currentStage = ''
          this.currentStageIndex = -1
          this.generating = false
          break
        case 'module-c':
          // 切换到模块 C，清空当前会话内容
          this.currentHistoryId = null
          this.currentTitle = ''
          this.currentContentChunks = []
          this.currentStage = ''
          this.currentStageIndex = -1
          this.generating = false
          break
      }
    },
    
    /**
     * 新建对话
     */
    handleNewChat() {
      // 清空当前内容
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
      // 这里可以添加切换模型后的逻辑，比如重新加载配置等
    },
    
    /**
     * 处理用户操作
     */
    handleUserAction(action) {
      switch (action) {
        case 'profile':
          // 打开个人资料
          console.log('打开个人资料')
          break
        case 'settings':
          // 打开设置
          console.log('打开设置')
          break
        case 'logout':
          // 退出登录
          console.log('退出登录')
          // 这里可以添加退出登录的逻辑
          break
      }
    },
    
    /**
     * 开始生成
     */
    async handleStart() {
      this.generating = true
      this.currentContentChunks = [] // 清空chunks数组
      this.currentStageIndex = 0
      this.currentStage = this.stages[0]
      this.currentTitle = 'LLM 响应生成'
      
      try {
        await runStream(
          // 流式数据回调 - 每次收到chunk立即添加到数组
          (chunk) => {
            if (chunk) {
              // 使用push方法，Vue会自动检测数组变化并更新视图
              this.currentContentChunks.push(chunk)
            }
          },
          // 完成回调
          () => {
            this.generating = false
            this.currentStageIndex = 4 // 所有阶段完成
            // 重新加载历史列表
            this.loadHistoryList()
          },
          // 错误回调
          (error) => {
            console.error('生成失败:', error)
            this.generating = false
            this.currentContentChunks.push('\n\n[错误] ' + error.message)
          }
        )
      } catch (error) {
        console.error('生成失败:', error)
        this.generating = false
        this.currentContentChunks.push('\n\n[错误] ' + (error.message || '生成过程中发生错误'))
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
        },
        {
          id: '3',
          title: '支付系统接口测试',
          createTime: new Date(Date.now() - 172800000).toISOString()
        },
        {
          id: '4',
          title: '商品管理功能测试',
          createTime: new Date(Date.now() - 259200000).toISOString()
        },
        {
          id: '5',
          title: '库存管理系统测试',
          createTime: new Date(Date.now() - 345600000).toISOString()
        }
      ]
    },
    
    /**
     * 获取模拟历史详情（用于开发环境）
     */
    getMockHistoryDetail(id) {
      return {
        id: id,
        title: '用户管理系统测试用例',
        content: '这是模拟的测试用例内容...',
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
