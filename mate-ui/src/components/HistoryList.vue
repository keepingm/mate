<template>
  <div class="history-list">
    <div class="history-header">
      <h2>历史对话</h2>
      <el-button 
        type="primary" 
        @click="handleNewChat"
        class="new-chat-btn"
      >
        <el-icon><Plus /></el-icon>
        新对话
      </el-button>
    </div>
    <div class="history-content">
      <div
        v-for="item in historyList"
        :key="item.id"
        class="history-item"
        :class="{ active: item.id === activeId }"
        @click="handleSelect(item.id)"
      >
        <div class="history-item-title">{{ item.title || '未命名对话' }}</div>
        <div class="history-item-time">{{ formatTime(item.createTime) }}</div>
      </div>
      <div v-if="historyList.length === 0" class="empty-state">
        暂无历史记录
      </div>
    </div>
  </div>
</template>

<script>
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'HistoryList',
  components: {
    Plus
  },
  props: {
    historyList: {
      type: Array,
      default: () => []
    },
    activeId: {
      type: String,
      default: null
    }
  },
  emits: ['select', 'new-chat'],
  methods: {
    handleSelect(id) {
      this.$emit('select', id)
    },
    handleNewChat() {
      this.$emit('new-chat')
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
.history-list {
  width: 280px;
  height: 100%;
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
  border-right: 1px solid #e8e9ea;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.history-header {
  padding: 24px 20px;
  border-bottom: 1px solid #e8e9ea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-header h2 {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.new-chat-btn {
  width: 100%;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
}

.history-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.history-item {
  padding: 16px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s ease;
  position: relative;
}

.history-item:hover {
  background-color: #f8f9fa;
  transform: translateX(2px);
}

.history-item.active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 3px solid #667eea;
  box-shadow: inset 0 0 10px rgba(102, 126, 234, 0.05);
}

.history-item-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.history-item.active .history-item-title {
  color: #667eea;
  font-weight: 600;
}

.history-item-time {
  font-size: 12px;
  color: #999;
}

.history-item.active .history-item-time {
  color: #888;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.history-content::-webkit-scrollbar {
  width: 6px;
}

.history-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.history-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.history-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

