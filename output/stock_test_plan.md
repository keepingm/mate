{
  "modules": [
    {
      "module_id": "M1",
      "name": "UserManagement",
      "classes": [
        "Client",
        "ClientRepository",
        "ClientRepositoryImpl",
        "UserManagementService",
        "RegistrationRequestDTO",
        "RegistrationResponseDTO",
        "LoginRequestDTO",
        "LoginResponseDTO",
        "LoginOtpVerificationRequestDTO",
        "LoginOtpVerificationResponseDTO",
        "ForgotPasswordRequestDTO",
        "ForgotPasswordOtpVerificationRequestDTO",
        "ForgotPasswordOtpVerificationResponseDTO"
      ],
      "responsibility_summary": "负责用户账户的注册、登录、两因素认证（OTP）、忘记密码流程、用户身份校验及会话管理。",
      "reasons": {
        "cohesion": "所有类均围绕用户身份管理、认证验证流程设计，共同支撑用例1（用户及安全）。",
        "coupling": "与其他模块如订单或账户服务解耦，仅通过身份验证接口交互，易于模拟和独立测试。",
        "requirements_trace": [
          "2.1.1 Use Case 1: User & Security",
          "3.6 Software System Attributes - Security",
          "3.3 Interface Requirements - User Interface"
        ]
      },
      "features": [
        {
          "name": "userRegistration",
          "methods": [
            "UserManagementService.register"
          ],
          "requirements": "（Registration）用户填写基本信息→验证邮箱/电话→系统生成client_id并分配默认角色。"
        },
        {
          "name": "userLoginWithOtp",
          "methods": [
            "UserManagementService.login",
            "UserManagementService.login_otp_verification"
          ],
          "requirements": "登录时用户名密码验证；触发邮件/短信OTP（两因素认证可选）；验证OTP后建立会话。"
        },
        {
          "name": "forgotPasswordFlow",
          "methods": [
            "UserManagementService.forgot_password",
            "UserManagementService.forgot_password_otp_verification"
          ],
          "requirements": "用户提交账号标识→接收输入OTP→设置新密码生效。"
        }
      ]
    },
    {
      "module_id": "M2",
      "name": "MarketData",
      "classes": [
        "Stock",
        "StockRepository",
        "StockRepositoryImpl",
        "MarketDataService",
        "GetMarketWatchRequestDTO",
        "GetMarketWatchResponseDTO",
        "GetHistoricalDataRequestDTO",
        "GetHistoricalDataResponseDTO"
      ],
      "responsibility_summary": "负责市场数据的获取与展示，包括近实时价格显示、历史趋势和EOD统计，实现数据查询及图表呈现接口。",
      "reasons": {
        "cohesion": "功能围绕市场数据查询和更新，核心类间依赖紧密支持使用用例2（市场数据展示）。",
        "coupling": "通过仓库模式访问数据，主要依赖于外部行情数据源，模块内聚明显，接口清晰可模拟。",
        "requirements_trace": [
          "2.1.2 Use Case 2: Market Data Display",
          "3.4 Logical Database Requirements - prices and EOD history",
          "5.1 Assumptions and Dependencies - Market data"
        ]
      },
      "features": [
        {
          "name": "getMarketWatchPrices",
          "methods": [
            "MarketDataService.GetPrice"
          ],
          "requirements": "用户打开‘Market Watch’窗口查看报价列表；系统每约5分钟刷新价格，更新趋势图和EOD报表。"
        },
        {
          "name": "getHistoricalData",
          "methods": [
            "MarketDataService.GetHistoricalData"
          ],
          "requirements": "用户查看个股历史价格和P/L统计；提供指定时间范围历史数据查询功能。"
        }
      ]
    },
    {
      "module_id": "M3",
      "name": "OrderManagement",
      "classes": [
        "Order",
        "OrderRepository",
        "OrderRepositoryImpl",
        "OrderService",
        "PlaceOrderRequestDTO",
        "PlaceOrderResponseDTO",
        "CancelOrderRequestDTO",
        "CancelOrderResponseDTO",
        "ModifyOrderRequestDTO",
        "ModifyOrderResponseDTO",
        "GetOrderHistoryRequestDTO",
        "GetOrderHistoryResponseDTO"
      ],
      "responsibility_summary": "负责用户订单的创建、修改、取消、执行状态管理及历史记录查询，处理订单验证和与交易所交互。",
      "reasons": {
        "cohesion": "订单实体、仓库及服务协同支撑用例3（订单下单与执行流程），专责订单生命周期管理。",
        "coupling": "与交易所通信层隔离，通过订单状态更新与账户、资金模块交互，模块边界明确，易于模拟外部交互。",
        "requirements_trace": [
          "2.1.3 Use Case 3: Order Placement & Execution",
          "3.1 Performance Requirements - 交易高并发，响应时间",
          "4 Verification - 功能及性能测试"
        ]
      },
      "features": [
        {
          "name": "placeOrder",
          "methods": [
            "OrderService.place_order"
          ],
          "requirements": "用户在交易页面选择买/卖、工具、数量及订单类型后提交订单；系统完成验证并发送至交易所。"
        },
        {
          "name": "cancelOrder",
          "methods": [
            "OrderService.cancel_order"
          ],
          "requirements": "未成交订单可取消，系统接受取消请求并更新订单状态，完成相应业务逻辑。"
        },
        {
          "name": "modifyOrder",
          "methods": [
            "OrderService.modify_order"
          ],
          "requirements": "用户可修改未完全成交的订单的类型和数量，系统进行合法性校验后执行修改。"
        },
        {
          "name": "getOrderHistory",
          "methods": [
            "OrderService.get_order_history"
          ],
          "requirements": "用户查看历史订单列表及详情，支持分页查询和状态过滤。"
        }
      ]
    },
    {
      "module_id": "M4",
      "name": "AccountManagement",
      "classes": [
        "AccountService",
        "DemateAccount",
        "DemateAccountRepository",
        "DemateAccountRepositoryImpl",
        "Position",
        "PositionRepository",
        "PositionRepositoryImpl",
        "GetAccountSummaryRequestDTO",
        "GetAccountSummaryResponseDTO",
        "ExportAccountReportsRequestDTO",
        "ExportAccountReportsResponseDTO"
      ],
      "responsibility_summary": "负责账户余额、仓位、保证金及盈亏报表计算与展示，支持资金查询及相关报表的导出。",
      "reasons": {
        "cohesion": "账户与仓位实体及服务实现资金管理、盈亏计算和报表功能，紧密配合支撑用例4（账户与资金）需求。",
        "coupling": "通过仓库接口与数据库交互，依赖订单模块状态更新，模块边界清晰，便于独立模拟。",
        "requirements_trace": [
          "2.1.4 Use Case 4: Accounts & Funds",
          "3.4 Logical Database Requirements - 虚拟钱包资金与持仓信息",
          "4 Verification - 账户资金及报表验证"
        ]
      },
      "features": [
        {
          "name": "calculateMarginAndPL",
          "methods": [
            "AccountService.calculate_margin",
            "AccountService.calculate_pl"
          ],
          "requirements": "系统计算并展示用户当前保证金及盈亏情况，包括实时/近实时MTM信息。"
        },
        {
          "name": "getBalance",
          "methods": [
            "AccountService.get_balance"
          ],
          "requirements": "用户查询账户余额和资金情况，实时显示可用余额。"
        },
        {
          "name": "exportAccountReports",
          "methods": [
            "AccountService.export_account_reports"
          ],
          "requirements": "用户可导出账户相关报表，包括盈亏报告、行业分布及股权分布饼图。"
        }
      ]
    }
  ]
}