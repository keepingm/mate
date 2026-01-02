<template>
  <div class="app-sidebar">
    <!-- Logo / 产品名称区 -->
    <div class="sidebar-header" @click="handleLogoClick">
      <div class="logo-section">
        <el-icon class="logo-icon"><ChatDotRound /></el-icon>
        <span class="product-name">Mate AI</span>
      </div>
    </div>

    <!-- 主功能模块区 -->
    <div class="sidebar-modules">
      <div class="modules-title">功能模块</div>
      <el-menu
        :default-active="activeModule"
        class="modules-menu"
        @select="handleModuleSelect"
      >
        <el-menu-item index="new-chat">
          <el-icon><Edit /></el-icon>
          <span>新建会话</span>
        </el-menu-item>
        <el-menu-item index="module-a">
          <el-icon><Document /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="module-b">
          <el-icon><FolderOpened /></el-icon>
          <span>模块 B</span>
        </el-menu-item>
        <el-menu-item index="module-c">
          <el-icon><Setting /></el-icon>
          <span>模块 C</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 历史会话列表 -->
    <div class="sidebar-history">
      <div class="history-title">历史会话</div>
      <div class="history-list">
        <div
          v-for="item in historyList"
          :key="item.id"
          class="history-item"
          :class="{ active: item.id === activeHistoryId }"
          @click="handleHistorySelect(item.id)"
        >
          <el-icon class="history-icon"><ChatLineRound /></el-icon>
          <div class="history-content">
            <div class="history-item-title">
              {{ item.title || '未命名会话' }}
            </div>
            <div class="history-item-time">
              {{ formatTime(item.createTime) }}
            </div>
          </div>
        </div>

        <div v-if="historyList.length === 0" class="empty-history">
          <el-empty description="暂无历史记录" :image-size="80" />
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { 
  ChatDotRound, 
  Document, 
  FolderOpened, 
  Setting,
  ChatLineRound
} from '@element-plus/icons-vue'

export default {
  name: 'AppSidebar',
  components: {
    ChatDotRound,
    Document,
    FolderOpened,
    Setting,
    ChatLineRound
  },
  props: {
    historyList: {
      type: Array,
      default: () => []
    },
    activeHistoryId: {
      type: String,
      default: null
    },
    activeModule: {
      type: String,
      default: 'new-chat'
    }
  },
  emits: ['logo-click', 'module-select', 'history-select'],
  methods: {
    handleLogoClick() {
      this.$emit('logo-click')
    },
    handleModuleSelect(key) {
      this.$emit('module-select', key)
    },
    handleHistorySelect(id) {
      this.$emit('history-select', id)
    },
    formatTime(time) {
      if (!time) return ''
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (days === 0) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      } else if (days === 1) {
        return '昨天'
      } else if (days < 7) {
        return `${days}天前`
      } else {
        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      }
    }
  }
}
</script>

<style scoped>

  .app-sidebar {
    width: 280px;
    height: 100%;
    background: #f7f7f7;
    border-right: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      "Inter",
      "PingFang SC",
      "Hiragino Sans GB",
      "Microsoft YaHei",
      Arial,
      sans-serif;
  }

  
  /* ===== Logo 区（与侧边栏背景保持一致） ===== */
  .sidebar-header {
    padding: 20px;
    background: transparent;        /* 关键：不再是白色 */
    cursor: pointer;
  }
  
  .sidebar-header:hover {
    background: rgba(0, 0, 0, 0.02); /* 极弱 hover，不突兀 */
  }
  
  .logo-section {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .logo-icon {
    font-size: 26px;
    color: #409eff;
  }
  
  /* .product-name {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    letter-spacing: 0.4px;
  } */

  .product-name {
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
  letter-spacing: 0.2px;
}

  
  /* ===== 主功能模块 ===== */
  .sidebar-modules {
    flex-shrink: 0;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .modules-title {
    padding: 14px 20px 8px;
    font-size: 11px;
    font-weight: 500;
    color: #020202;
    letter-spacing: 0.6px;
    text-transform: none;
  }
  
  .modules-menu {
    border: none;
    background: transparent;
  }
  

  .modules-menu :deep(.el-menu-item) {
  height: 35px;
  line-height: 30px;
  margin: 0 12px 6px;
  border-radius: 10px;

  font-size: 17px;
  font-weight: 5;
  color: #030303;
}

  
  .modules-menu :deep(.el-menu-item:hover) {
    background-color: #eef1f6;
  }
  
  .modules-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

  
  .modules-menu :deep(.el-menu-item .el-icon) {
    margin-right: 8px;
    font-size: 18px;
  }
  
  /* ===== 历史会话 ===== */
  .sidebar-history {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .history-title {
    padding: 14px 20px 8px;
    font-size: 11px;
    font-weight: 500;
    color: #6b7280;
    letter-spacing: 0.6px;
    text-transform: none;
  }
  
  .history-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px 12px;
  }
  
  .history-item {
    display: flex;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
  }
  
  .history-item:hover {
    background-color: #eef1f6;
  }
  
  .history-item.active {
    background-color: #ecf5ff;
    border-left: 3px solid #409eff;
  }
  
  .history-icon {
    font-size: 18px;
    color: #909399;
  }
  
  .history-item.active .history-icon {
    color: #409eff;
  }
  
  .history-item-title {
  font-size: 13.5px;
  font-weight: 500;
  color: #1f2937;
}

  
  .history-item.active .history-item-title {
    color: #409eff;
    font-weight: 600;
  }
  
  .history-item-time {
    font-size: 11px;
    color: #9ca3af;
  }

  
  .empty-history {
    padding: 40px 20px;
    text-align: center;
  }
  
  /* 滚动条 */
  .history-list::-webkit-scrollbar {
    width: 6px;
  }
  .history-list::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }
  </style>
  
