# API接口文档

## 基础URL
```
开发环境: http://localhost:8080/api
生产环境: 通过环境变量 VUE_APP_API_BASE_URL 配置
```

## 接口列表

### 1. 获取历史对话列表

**接口地址:** `GET /history/list`

**请求参数:** 无

**响应示例:**
```json
{
  "data": [
    {
      "id": "1",
      "title": "用户管理系统测试用例",
      "createTime": "2024-01-01T10:00:00.000Z"
    },
    {
      "id": "2",
      "title": "订单管理模块测试用例",
      "createTime": "2024-01-02T10:00:00.000Z"
    }
  ]
}
```

---

### 2. 获取对话详情

**接口地址:** `GET /history/detail/:id`

**路径参数:**
- `id` (string): 对话ID

**响应示例:**
```json
{
  "data": {
    "id": "1",
    "title": "用户管理系统测试用例",
    "content": "测试用例的详细内容...",
    "stage": "测试运行",
    "stageIndex": 4
  }
}
```

**字段说明:**
- `stage`: 当前阶段名称（测试计划、测试设计、测试评审、测试开发、测试运行）
- `stageIndex`: 阶段索引（0-4，-1表示未开始）

---

### 3. 上传文档并生成测试用例（流式返回）

**接口地址:** `POST /test/generate`

**请求格式:** `multipart/form-data`

**请求参数:**
- `file` (File): 需求文档文件（支持 .doc, .docx, .pdf, .txt, .md 格式）

**响应格式:** 流式返回，支持两种格式

#### 格式1: SSE格式 (推荐)
**Content-Type:** `text/event-stream`

**响应示例:**
```
data: {"type":"stage","data":"测试计划","index":0}\n\n
data: {"type":"chunk","data":"根据需求文档，制定测试计划..."}\n\n
data: {"type":"chunk","data":"测试范围包括..."}\n\n
data: {"type":"stage","data":"测试设计","index":1}\n\n
data: {"type":"chunk","data":"设计测试用例..."}\n\n
data: {"type":"stage","data":"测试评审","index":2}\n\n
data: {"type":"chunk","data":"评审测试用例..."}\n\n
data: {"type":"stage","data":"测试开发","index":3}\n\n
data: {"type":"chunk","data":"开发自动化测试脚本..."}\n\n
data: {"type":"stage","data":"测试运行","index":4}\n\n
data: {"type":"chunk","data":"执行测试..."}\n\n
data: {"type":"complete","taskId":"task-123456"}\n\n
```

#### 格式2: 普通文本流
**Content-Type:** `text/plain` 或 `application/json`

**响应示例:**
```
{"type":"stage","data":"测试计划","index":0}
{"type":"chunk","data":"根据需求文档，制定测试计划..."}
{"type":"chunk","data":"测试范围包括..."}
{"type":"stage","data":"测试设计","index":1}
{"type":"chunk","data":"设计测试用例..."}
{"type":"stage","data":"测试评审","index":2}
{"type":"chunk","data":"评审测试用例..."}
{"type":"stage","data":"测试开发","index":3}
{"type":"chunk","data":"开发自动化测试脚本..."}
{"type":"stage","data":"测试运行","index":4}
{"type":"chunk","data":"执行测试..."}
{"type":"complete","taskId":"task-123456"}
```

**JSON数据格式说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 数据类型：`stage`（阶段更新）、`chunk`（文本块）、`complete`（完成） |
| data | string | 阶段名称（type=stage时）或文本内容（type=chunk时） |
| index | number | 阶段索引（0-4，仅type=stage时有效）<br>0: 测试计划<br>1: 测试设计<br>2: 测试评审<br>3: 测试开发<br>4: 测试运行 |
| taskId | string | 任务ID（仅type=complete时有效） |

**错误响应:**
- HTTP状态码: 4xx 或 5xx
- 前端会通过错误回调处理

---

## 阶段说明

系统包含5个阶段，按顺序执行：

1. **测试计划** (index: 0)
2. **测试设计** (index: 1)
3. **测试评审** (index: 2)
4. **测试开发** (index: 3)
5. **测试运行** (index: 4)

每个阶段完成后，系统会发送 `stage` 类型的消息，更新当前阶段。在整个过程中，会持续发送 `chunk` 类型的消息，包含生成的内容。所有阶段完成后，发送 `complete` 类型的消息。

