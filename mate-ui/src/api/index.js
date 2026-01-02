import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 300000 // 5分钟超时，因为流式返回可能需要较长时间
})

/**
 * 获取历史对话列表
 */
export const getHistoryList = () => {
  return api.get('/history/list')
}

/**
 * 获取对话详情
 * @param {string} id - 对话ID
 */
export const getHistoryDetail = (id) => {
  return api.get(`/history/detail/${id}`)
}

/**
 * 使用fetch实现真正的流式请求
 * 支持两种格式：
 * 1. SSE格式 (text/event-stream): data: {...}\n\n
 * 2. 普通文本流: 每行一个JSON对象或纯文本
 * 
 * @param {File} file - 文档文件
 * @param {Function} onStageUpdate - 阶段更新回调函数 (stage: string, stageIndex: number) => void
 * @param {Function} onChunk - 流式数据回调函数 (chunk: string) => void
 * @param {Function} onComplete - 完成回调函数 (taskId: string) => void
 * @param {Function} onError - 错误回调函数 (error: Error) => void
 */
export const uploadDocumentStream = async (file, onStageUpdate, onChunk, onComplete, onError) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000/'
    const response = await fetch(`${baseURL}/run`, {
      method: 'GET'
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    const contentType = response.headers.get('content-type') || ''

    // 判断是否为SSE格式
    const isSSE = contentType.includes('text/event-stream')

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true })
      
      if (isSSE) {
        // SSE格式处理: data: {...}\n\n
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // 保留最后一个不完整的事件

        for (const event of events) {
          if (event.trim()) {
            const lines = event.split('\n')
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const dataStr = line.substring(6) // 去掉 "data: " 前缀
                try {
                  const json = JSON.parse(dataStr)
                  handleStreamData(json, onStageUpdate, onChunk, onComplete)
                } catch (e) {
                  // 如果不是JSON，直接作为文本处理
                  onChunk && onChunk(dataStr)
                }
              }
            }
          }
        }
      } else {
        // 普通文本流处理
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留最后不完整的行

        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line)
              handleStreamData(json, onStageUpdate, onChunk, onComplete)
            } catch (e) {
              // 如果不是JSON，直接作为文本块处理
              onChunk && onChunk(line)
            }
          }
        }
      }
    }

    // 处理剩余的buffer
    if (buffer.trim()) {
      if (isSSE) {
        const lines = buffer.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6)
            try {
              const json = JSON.parse(dataStr)
              handleStreamData(json, onStageUpdate, onChunk, onComplete)
            } catch (e) {
              onChunk && onChunk(dataStr)
            }
          }
        }
      } else {
        try {
          const json = JSON.parse(buffer)
          handleStreamData(json, onStageUpdate, onChunk, onComplete)
        } catch (e) {
          onChunk && onChunk(buffer)
        }
      }
    }
  } catch (error) {
    onError && onError(error)
  }
}

/**
 * 处理流式数据
 */
function handleStreamData(json, onStageUpdate, onChunk, onComplete) {
  if (json.type === 'stage') {
    onStageUpdate && onStageUpdate(json.data, json.index)
  } else if (json.type === 'chunk') {
    onChunk && onChunk(json.data)
  } else if (json.type === 'complete') {
    onComplete && onComplete(json.taskId)
  } else if (json.data) {
    // 如果没有type字段，但可能有data字段，直接作为chunk处理
    onChunk && onChunk(json.data)
  }
}

/**
 * 调用 /run 接口实现流式响应
 * 后端返回 text/plain 格式的纯文本流
 * 
 * @param {Function} onChunk - 流式数据回调函数 (chunk: string) => void
 * @param {Function} onComplete - 完成回调函数 () => void
 * @param {Function} onError - 错误回调函数 (error: Error) => void
 */
export const runStream = async (onChunk, onComplete, onError) => {
  try {
    // 优先尝试直接连接后端（如果CORS已配置），否则使用代理
    // 如果后端已设置CORS，直接连接可以避免代理缓冲问题
    const useDirectConnection = process.env.VUE_APP_USE_DIRECT_CONNECTION === 'true'
    let apiPath
    if (useDirectConnection) {
      // 直接连接后端（需要后端设置CORS）
      apiPath = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000'
    } else {
      // 使用代理路径
      apiPath = process.env.VUE_APP_API_BASE_URL || '/api'
    }
    
    console.log(`[流式] 连接地址: ${apiPath}/run`)
    
    const response = await fetch(`${apiPath}/run`, {
      method: 'GET',
      headers: {
        'Accept': 'text/plain',
        'Cache-Control': 'no-cache' // 禁用缓存
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 检查响应是否支持流式传输
    if (!response.body) {
      throw new Error('响应不支持流式传输')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let receivedBytes = 0
    let chunkCount = 0

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        // 处理最后剩余的buffer（不传stream参数表示这是最后的数据）
        try {
          const finalChunk = decoder.decode()
          if (finalChunk && onChunk) {
            receivedBytes += finalChunk.length
            chunkCount++
            console.log(`[流式] 收到最终chunk: ${finalChunk.length} 字符, 总计: ${receivedBytes} 字符, ${chunkCount} 个chunks`)
            onChunk(finalChunk)
          }
        } catch (e) {
          // 忽略解码错误
        }
        console.log(`[流式] 接收完成，共收到 ${chunkCount} 个chunks，${receivedBytes} 字符`)
        break
      }

      // 解码数据块，stream: true 表示还有更多数据
      let chunk
      try {
        chunk = decoder.decode(value, { stream: true })
      } catch (e) {
        console.error('解码错误:', e)
        continue
      }
      
      // 立即处理每个chunk，实现流式显示
      if (chunk) {
        receivedBytes += chunk.length
        chunkCount++
        // 每10个chunk打印一次日志，避免日志过多
        if (chunkCount % 10 === 0 || chunk.length > 100) {
          console.log(`[流式] 收到chunk #${chunkCount}: ${chunk.length} 字符, 累计: ${receivedBytes} 字符`)
        }
        
        // 直接同步调用，确保实时更新
        if (onChunk) {
          onChunk(chunk)
        }
      }
    }

    // 调用完成回调
    if (onComplete) {
      onComplete()
    }
  } catch (error) {
    console.error('[流式] 错误:', error)
    if (onError) {
      onError(error)
    }
  }
}

export default api

