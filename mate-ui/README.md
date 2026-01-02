# mate-ui

基于Multi-Agent的测试用例生成系统

## 功能特性

- 📋 文档上传：支持上传需求文档（.doc, .docx, .pdf, .txt, .md格式）
- 🔄 多阶段生成：测试计划、测试设计、测试评审、测试开发、测试运行五个阶段
- 📊 实时进度：可视化进度条展示当前生成阶段
- 💬 流式输出：实时流式返回大模型生成结果
- 📜 历史记录：查看和管理历史生成的测试用例

## 项目结构

```
src/
├── api/              # API接口定义
│   └── index.js     # 接口方法（历史列表、详情查询、文档上传、流式生成）
├── components/       # 组件
│   ├── HistoryList.vue      # 左侧历史对话列表
│   ├── ResultDisplay.vue    # 中间结果展示（支持流式显示和进度条）
│   └── DocumentUpload.vue   # 底部文档上传组件
├── App.vue          # 主应用组件
└── main.js          # 入口文件
```

## 环境配置

1. 复制 `.env.example` 为 `.env`
2. 修改 `.env` 中的 `VUE_APP_API_BASE_URL` 为实际后端API地址

```bash
cp .env.example .env
```

`.env` 文件示例：
```
VUE_APP_API_BASE_URL=http://localhost:8080/api
```

## 后端API接口规范

### 1. 获取历史对话列表
```
GET /api/history/list
Response: {
  data: [
    {
      id: string,
      title: string,
      createTime: string (ISO格式)
    }
  ]
}
```

### 2. 获取对话详情
```
GET /api/history/detail/:id
Response: {
  data: {
    id: string,
    title: string,
    content: string,
    stage: string,
    stageIndex: number
  }
}
```

### 3. 上传文档并生成（流式返回）
```
POST /api/test/generate
Content-Type: multipart/form-data
Body: file (文件)

Response (流式):
支持两种格式：

格式1 - SSE格式 (Content-Type: text/event-stream):
data: {"type":"stage","data":"测试计划","index":0}\n\n
data: {"type":"chunk","data":"生成的文本内容"}\n\n
data: {"type":"complete","taskId":"xxx"}\n\n

格式2 - 普通文本流 (每行一个JSON):
{"type":"stage","data":"测试计划","index":0}
{"type":"chunk","data":"生成的文本内容"}
{"type":"complete","taskId":"xxx"}

JSON字段说明:
- type: "stage" | "chunk" | "complete"
- data: 阶段名称（stage类型）或文本内容（chunk类型）
- index: 阶段索引（0-4，对应五个阶段）
- taskId: 任务ID（complete类型）
```

## 安装依赖

```bash
npm install
```

## 开发运行

```bash
npm run serve
```

## 构建生产版本

```bash
npm run build
```

## 代码检查

```bash
npm run lint
```

## 技术栈

- Vue 3
- Vue CLI
- Axios
- Fetch API (用于流式请求)

## 自定义配置

更多配置请参考 [Vue CLI Configuration Reference](https://cli.vuejs.org/config/).
