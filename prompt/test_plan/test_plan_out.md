- `modules`: 模块列表，每个模块包含：
  - `module_id`: 模块的唯一标识（例如 "M1", "M2"...）
  - `name`: 模块的语义名称（例如 "OrderManagement", "InventoryService"），可以根据模块内职责自行命名
  - `classes`: 属于该模块的类名列表
  - `responsibility_summary`: 用简短自然语言描述该模块的核心职责（1–3 句）
  - `reasons`: 用简短自然语言总结本模块划分背后的关键考虑因素，例如：
    - 内聚性来源（共同支撑哪些用例 / 场景）
    - 与其他模块的主要交互及耦合控制
    - 与需求文档中哪些需求条目相关
  - `features`:该模块下细分的功能，每个feature包括一组相互合作完成一组功能需求的函数
  - `name`: feature name
  - `methods`: 该feature下的函数
  - `requirements:`:与该feature下函数相关的需求文档原文，可以冗余，不要遗漏

结果输出到.json 文件，JSON 示例结构如下（只是结构示例，实际内容由你根据推理结果生成）：


{
  "modules": [
    {
      "name": "OrderManagement",
      "classes": ["Order", "OrderItem", "OrderService","OrderDao"],
      "responsibility_summary": "负责订单的创建、修改、状态流转，并为支付和库存模块提供订单相关接口。",
      "reasons": {
        "cohesion": "这些类在订单创建、更新等场景中总是一起工作，类之间有大量方法调用和数据聚合关系。",
        "coupling": "跨模块主要与 Payment 和 Inventory 交互，已通过接口和领域边界控制依赖方向，减少不必要的跨模块耦合。",
        "requirements_trace": ["REQ-1 创建订单", "REQ-2 修改订单", "REQ-3 查询订单"]
      },
      "features":[
          {
              "name":"createOrder",
              "methods":[
                  "OrderService.createOrder",
                  "OrderDao.save"
              ],
              "requirements":"用户创建订单。。。；"
          }, {
              "name":"cancleOrder",
              "methods":[
                  "OrderService.cancleOrder",
                  "OrderDao.update"
              ] ,
              "requirements":"用户可以取消未支付的订单"
          }
      ]
    }
  ]
}
