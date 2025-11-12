# API 接口文档 

## 📘 文档说明

- **版本**: v1.5 
- **基础架构**: System Architecture v1.7
- **数据库**: DB Schema v1.3 


## 🌐 基础信息

### Base URL
- **开发环境**: `http://localhost:8000/api/v1`
- **生产环境**: `https://your-api.onrender.com/api/v1`

### 认证方式
- **P1 阶段**: 匿名 UUID (存储在前端 localStorage)
- **传递方式**: Query Parameter `user_id` 或 Request Body

### Content-Type
- `application/json`

### 字符编码
- `UTF-8`

---

## 📋 全局响应格式

### 成功响应
```json
{
  "data": { ... },
  "timestamp": "2024-11-09T12:34:56Z"
}
```

### 错误响应
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  },
  "timestamp": "2024-11-09T12:34:56Z"
}
```

### HTTP 状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 202 | Accepted | 异步任务已接受 |
| 400 | Bad Request | 请求参数错误 |
| 403 | Forbidden | 禁止访问（如超过限制） |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

---

## 🔐 模块一：用户与认证

### 1.1 初始化匿名用户 (F1.1)

**POST** `/user/init`

#### 功能描述
- P0 核心功能
- 零摩擦匿名登录
- 根据用户状态进行路由

#### 请求体
```json
{
  "anonymous_user_id": "uuid-123-abc"  // 可选，如为null则创建新用户
}
```

#### 响应 (200 OK)

**情况1: 新用户**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ONBOARDING"
}
```

**情况2: 已有用户**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ACTIVE"
}
```

#### 状态说明

| Status | 含义 | 前端路由 |
|--------|------|----------|
| ONBOARDING | 新用户，未完成档案 | → F2.1 问卷页 |
| ACTIVE | 已完成档案 | → F6.1 首页 |

#### 业务逻辑
1. 检查 `anonymous_user_id` 是否存在于数据库
2. 如不存在 → 创建新用户，`status = 'ONBOARDING'`
3. 如存在 → 返回现有用户状态

---

## 📝 模块二：档案管理

### 2.1 提交当前档案 (F2.1) 

**POST** `/profile/current`

#### 功能描述
- P0 核心功能
- 提交4部分新问卷：基本信息、价值观(PVQ)、人格(BFI)
- 数据存储到 DB v1.3 的4个独立JSONB字段

#### 请求体 (v1.5 完整版)
```json
{
  "demo_data": {
    "name": "张三",
    "age": 25,
    "gender": "男",
    "status": "研究生",
    "field": "计算机科学",
    "interests": "人工智能",
    "location": "上海",
    "future_location": "新加坡"
  },
  "vals_data": {
    "self_direction": 5,    // 自主性 (1-5)
    "stimulation": 4,       // 刺激性 (1-5)
    "hedonism": 4,          // 享乐主义 (1-5)
    "achievement": 5,       // 成就 (1-5)
    "power": 2,             // 权力 (1-5)
    "security": 5,          // 安全 (1-5)
    "conformity": 3,        // 顺从 (1-5)
    "tradition": 2,         // 传统 (1-5)
    "benevolence": 4,       // 仁慈 (1-5)
    "universalism": 5       // 普世 (1-5)
  },
  "bfi_data": {
    "extraversion": 4.5,        // 外向性 (1-5)
    "agreeableness": 3.5,       // 宜人性 (1-5)
    "conscientiousness": 5.0,   // 尽责性 (1-5)
    "neuroticism": 2.0,         // 神经质 (1-5)
    "openness": 4.0             // 开放性 (1-5)
  }
}
```

#### 数据验证规则

**demo_data 验证**:
- `name`: 字符串，1-50字符
- `age`: 整数，18-100
- `gender`: 字符串，非空
- `status`: 字符串，非空
- `field`: 字符串，非空
- `interests`: 字符串，非空
- `location`: 字符串，非空
- `future_location`: 字符串，非空

**vals_data 验证**:
- 所有字段: 整数，范围 1-5 (Likert 5点量表)

**bfi_data 验证**:
- 所有字段: 浮点数，范围 1.0-5.0 (Likert 5点量表)



#### 响应 (200 OK)
```json
{
  "status": "CURRENT_PROFILE_SAVED"
}
```

#### 错误响应

**400 Bad Request** - 验证失败
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": {
      "field": "vals_data.self_direction",
      "error": "值必须在1-5之间"
    }
  }
}
```

**400 Bad Request** - 档案已存在
```json
{
  "error": {
    "code": "PROFILE_ALREADY_EXISTS",
    "message": "当前档案已存在，无法重复创建"
  }
}
```

#### 后端实现要点
1. 将3个JSON对象分别存入 `current_profiles` 表的4个独立字段
2. 所有字段必须在存储前加密
3. 验证所有必填字段和数据范围
4. 用户状态保持为 `ONBOARDING` (等待 F2.2)

---

### 2.2 创建未来档案 (F2.2) 

**POST** `/profile/future`

#### 功能描述
- P0 核心功能
- 提交3部分新问卷：价值观、愿景、障碍
- **V1核心妥协**: API层同步拼接3个字段生成 `profile_description`
- 最多创建3个未来档案
- 完成后更新用户状态为 `ACTIVE`

#### 请求体 (v1.5 完整版)
```json
{
  "profiles": [
    {
      "profile_name": "UX研究员",
      "future_values": "我希望我的工作能够真正帮助到他人，让产品更加人性化。我相信通过深入了解用户需求，可以创造出更有意义的产品体验。",
      "future_vision": "我理想的状态是在一家注重用户体验的科技公司工作，领导一个小型研究团队，专注于AI产品的用户体验研究。我希望能够平衡工作与生活，同时保持对新技术的好奇心。",
      "future_obstacles": "我担心我的技术背景不够扎实，可能在与工程师沟通时遇到困难。同时，我也担心从学术界转向工业界后，研究的深度会受到影响。"
    },
    {
      "profile_name": "继续读博的我",
      "future_values": "我希望能够在学术界做出原创性的贡献，推动人机交互领域的发展。",
      "future_vision": "我理想的状态是成为一名助理教授，在顶尖高校建立自己的实验室...",
      "future_obstacles": "我担心学术界的竞争压力和不确定性..."
    }
  ]
}
```

#### 数据验证规则
- `profile_name`: 字符串，1-100字符，必填
- `future_values`: 字符串，最小10字符，最大2000字符，必填
- `future_vision`: 字符串，最小10字符，最大2000字符，必填
- `future_obstacles`: 字符串，最小10字符，最大2000字符，必填
- `profiles` 数组: 最少1个，最多3个

#### 响应 (200 OK)
```json
{
  "status": "ACTIVE",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_profiles": [
    {
      "future_profile_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "profile_name": "UX研究员"
    },
    {
      "future_profile_id": "8d0f7780-8536-51ef-a55c-f18gd2g01bf8",
      "profile_name": "继续读博的我"
    }
  ]
}
```

#### 错误响应

**403 Forbidden** - 超过数量限制
```json
{
  "error": {
    "code": "PROFILE_LIMIT_EXCEEDED",
    "message": "最多只能创建3个未来档案",
    "details": {
      "max_allowed": 3,
      "current_count": 3
    }
  }
}
```

#### 后端实现要点 (V1核心妥协)
1. 遍历 `profiles` 数组
2. 对每个profile:
   - 存储原始3个字段: `future_values`, `future_vision`, `future_obstacles`
   - **同步拼接**: `profile_description = future_values + "\n\n" + future_vision + "\n\n" + future_obstacles`
   - 存储拼接后的 `profile_description` (P1 AI将只读这个字段)
3. 向量化 `profile_description` 并存入 `vector_memory` 表
4. 更新用户状态: `UPDATE users SET status='ACTIVE'`

---

## ✉️ 模块三：信件交互

### 3.1 提交信件 (F3.1.2) - 异步

**POST** `/letters/submit`

#### 功能描述
- P0 核心功能
- 提交信件，立即返回202
- 推送异步任务到Worker
- Worker为所有未来人设生成回信

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 请求体
```json
{
  "content": "亲爱的未来的我：你好。此刻的我正站在人生的十字路口，内心充满了迷茫与期待。我正在认真思考，是应该继续走上学术研究的道路，攻读博士，还是应该迈向工业界，去面对一个更加复杂、真实的世界。两条路都在召唤我——前者代表着深入探索与独立思考的机会，后者则意味着实践与影响的可能。我希望，当你读到这封信时，能够回望此刻的犹豫与不安，并为自己当初的选择感到由衷的平静。我对“用户研究”充满热情，这种热情来自于我对人和技术之间关系的好奇。我喜欢观察人们在使用产品时的表情、语言与行为变化，喜欢思考他们真正的需求、动机与情感世界。我相信，技术的意义不在于复杂的算法，而在于它能否真正改善人的体验。然而，每当我回顾自己的学习背景，就会担心自己在技术层面的积累不够扎实，似乎缺少那种能与工程师或数据科学家平等对话的底气。这种焦虑让我在追求理想的过程中有些犹豫。也许，读博可以让我在理论与研究方法上更加深入，成为能在学术与实践之间搭建桥梁的人；而进入工业界，或许能让我更快地看到研究的成果如何真正落地、如何影响用户与社会。两条路都各有意义，我不希望被恐惧驱动，而是希望被信念与价值感指引。未来的我，我希望你已经学会接受不确定，并相信“路径”并不是唯一的答案。无论你最终选择了哪条路，请记得，你当初的出发点是热爱，是想要理解人、理解世界、理解技术背后的温度。愿你继续带着这份初心，勇敢地生活，坚定地创造。"
}
```

#### 数据验证
- `content`: 字符串，最小50字符，最大5000字符

#### 响应 (202 Accepted)
```json
{
  "letter_id": "1a2b3c4d-5e6f-7g8h-9i10-j11k12l13m14",
  "status": "SUBMITTED"
}
```

#### 异步处理流程
1. 立即返回 202
2. 存储信件到数据库 (`status = 'PENDING'`)
3. 推送 `process_letter` 任务到Redis
4. Worker执行:
   - 向量化信件内容
   - 为每个未来人设生成回信（调用F4.3 AI链）
   - 存储回信到 `letter_replies` 表
   - 更新信件状态: `status = 'REPLIES_READY'`

---

### 3.2 检查回信状态 (F6.6) - 轮询

**GET** `/letters/status`

#### 功能描述
- P0 核心功能
- 前端轮询此接口（3-5秒间隔）
- 检查回信是否生成完成

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 响应 (200 OK)

**生成中**
```json
{
  "status": "PENDING"
}
```

**已完成**
```json
{
  "status": "REPLIES_READY"
}
```

#### 前端轮询策略
```javascript
// 伪代码
async function pollLetterStatus(userId) {
  const maxAttempts = 60; // 3分钟 (60 * 3秒)
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    const response = await fetch(`/letters/status?user_id=${userId}`);
    const data = await response.json();
    
    if (data.status === 'REPLIES_READY') {
      return true; // 跳转到收信箱
    }
    
    await sleep(3000); // 等待3秒
    attempts++;
  }
  
  throw new Error('超时');
}
```

---

### 3.3 获取收信箱 (F6.5)

**GET** `/letters/inbox/latest`

#### 功能描述
- P0 核心功能
- 获取最新信件和所有回信列表
- 包含每个回信的 `chat_status`

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 响应 (200 OK)
```json
{
  "letter_id": "1a2b3c4d-5e6f-7g8h-9i10-j11k12l13m14",
  "letter_content_snippet": "亲爱的未来的我，我现在正处于人生的十字路口...",
  "replies": [
    {
      "reply_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
      "future_profile_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "from_profile_name": "UX研究员",
      "chat_status": "NOT_STARTED"
    },
    {
      "reply_id": "q6r7s8t9-u0v1-w2x3-y4z5-a6b7c8d9e0f1",
      "future_profile_id": "8d0f7780-8536-51ef-a55c-f18gd2g01bf8",
      "from_profile_name": "继续读博",
      "chat_status": "COMPLETED"
    }
  ]
}
```

#### 字段说明
- `letter_content_snippet`: 信件前100字 + "..."
- `chat_status`: 
  - `NOT_STARTED` - 未开始聊天，显示"查看回信"按钮
  - `COMPLETED` - 已完成5条消息，禁用聊天按钮

---

### 3.4 获取单封回信 (F3.1.3)

**GET** `/letters/reply/{reply_id}`

#### 功能描述
- P0 核心功能
- 查看完整回信内容
- 包含 `chat_status` 用于前端判断是否可开始聊天

#### Path Parameters
| 参数 | 类型 | 说明 |
|------|------|------|
| reply_id | UUID | 回信UUID |

#### 响应 (200 OK)
```json
{
  "reply_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "future_profile_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "from_profile_name": "UX研究员",
  "content": "亲爱的过去的我，\n\n我记得你现在的感受，那种站在十字路口的迷茫和不安。我想告诉你，你现在所担心的技术背景问题，在未来并没有成为真正的障碍...\n\n（完整回信内容）",
  "chat_status": "NOT_STARTED"
}
```

#### 错误响应

**404 Not Found**
```json
{
  "error": {
    "code": "REPLY_NOT_FOUND",
    "message": "回信不存在"
  }
}
```

---

## 💬 模块四：聊天交互

### 4.1 获取聊天历史 (F3.2.3)

**GET** `/chat/{future_profile_id}/history`

#### 功能描述
- P1 核心功能
- 加载与指定未来人设的聊天记录
- 按时间正序排列

#### Path Parameters
| 参数 | 类型 | 说明 |
|------|------|------|
| future_profile_id | UUID | 未来档案UUID |

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 响应 (200 OK)
```json
[
  {
    "message_id": "m1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
    "sender": "USER",
    "content": "你好，未来的我",
    "created_at": "2024-11-09T10:30:00Z"
  },
  {
    "message_id": "m2p7q8r9-s0t1-u2v3-w4x5-y6z7a8b9c0d1",
    "sender": "AGENT",
    "content": "你好，过去的我。我很高兴能和你对话。",
    "created_at": "2024-11-09T10:30:05Z"
  }
]
```

---

### 4.2 发送聊天消息 (F3.2.2) - 同步 + 5条限制

**POST** `/chat/{future_profile_id}/send`

#### 功能描述
- P1 核心功能
- **关键限制**: 每个未来人设最多5条用户消息
- 同步调用AI（< 8秒 SLA）
- 第5条消息后自动触发F5.1报告生成

#### Path Parameters
| 参数 | 类型 | 说明 |
|------|------|------|
| future_profile_id | UUID | 未来档案UUID |

#### 请求体
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "你对我的担忧有什么建议吗？"
}
```

#### 数据验证
- `content`: 字符串，最小1字符，最大1000字符

#### 响应 (201 Created) - 消息1-5

```json
{
  "message_id": "m3x4y5z6-a7b8-c9d0-e1f2-g3h4i5j6k7l8",
  "sender": "AGENT",
  "content": "关于你的担忧，我的建议是：首先，技术背景可以通过学习补足，但对用户的同理心和研究能力是更难培养的。你的计算机背景反而是优势...",
  "created_at": "2024-11-09T10:35:10Z"
}
```

#### 错误响应 (403 Forbidden) - 消息6+

```json
{
  "error": {
    "code": "MESSAGE_LIMIT_EXCEEDED",
    "message": "您已达到5条消息的限制",
    "details": {
      "max_messages": 5,
      "current_count": 5
    }
  }
}
```

#### 业务逻辑
1. 检查用户消息数量 (`sender='USER'`)
2. 如果 >= 5条 → 返回403
3. 如果 < 5条:
   - 存储用户消息
   - 调用F4.4 AI链（RAG检索 + LLM生成）
   - 存储AI回复
   - 如果这是第5条 → 更新 `letter_replies.chat_status = 'COMPLETED'`

#### 性能要求
- SLA: < 8秒响应时间
- 超时: 返回 504 Gateway Timeout

---

## 📊 模块五：报告生成

### 5.1 触发报告生成 (F5.1) - 异步

**POST** `/report/generate`

#### 功能描述
- P1 核心功能
- 由前端在第5条消息后自动触发
- 异步生成WOOP框架的职业洞见报告

#### 请求体
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 响应 (202 Accepted)
```json
{
  "report_id": "r1s2t3u4-v5w6-x7y8-z9a0-b1c2d3e4f5g6",
  "status": "GENERATING",
  "message": "报告生成已开始"
}
```

#### 异步处理流程
1. 立即返回 202
2. 创建报告记录 (`status = 'GENERATING'`)
3. 推送 `generate_report` 任务到Redis
4. Worker执行:
   - 加载完整聊天记录
   - 调用F4.5 AI链生成WOOP报告
   - 更新报告状态: `status = 'READY'`

---

### 5.2 检查报告状态 (F5.3) - 轮询

**GET** `/report/status`

#### 功能描述
- P1 核心功能
- 前端轮询此接口（5秒间隔）
- 检查报告是否生成完成

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 响应 (200 OK)

**生成中**
```json
{
  "status": "GENERATING"
}
```

**已完成**
```json
{
  "status": "READY"
}
```

---

### 5.3 获取报告 (F5.2)

**GET** `/report/latest`

#### 功能描述
- P1 核心功能
- 获取WOOP框架的职业洞见报告
- 只返回状态为READY的报告

#### Query Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户UUID |

#### 响应 (200 OK)
```json
{
  "report_id": "r1s2t3u4-v5w6-x7y8-z9a0-b1c2d3e4f5g6",
  "status": "READY",
  "content": {
    "W": "你的愿望是成为一名优秀的UX研究员，希望能够通过深入的用户研究来影响产品设计，创造更有意义的用户体验。",
    "O": "理想的结果是，你能够在3年内成为团队的核心成员，领导重要的研究项目，并在工作与生活之间找到良好的平衡。你希望被认可为既懂技术又懂用户的跨界人才。",
    "O": "主要的障碍包括：1) 对技术背景不够扎实的担忧，害怕在与工程师沟通时遇到困难 2) 对从学术界转向工业界后研究深度可能下降的顾虑 3) 职业转换期的不确定感和自我怀疑。",
    "P": "你的行动计划包括：1) 报名参加UX专业课程，系统学习用户研究方法论 2) 在当前项目中主动承担用户研究相关任务，积累实践经验 3) 建立个人作品集，记录研究案例 4) 加入UX社群，建立人脉网络 5) 保持对新技术的学习，将技术背景转化为优势而非劣势。"
  },
  "created_at": "2024-11-09T11:00:00Z"
}
```

#### WOOP框架说明
- **W (Wish)**: 愿望 - 用户的核心职业目标
- **O (Outcome)**: 结果 - 实现愿望后的理想状态
- **O (Obstacle)**: 障碍 - 阻碍实现愿望的内外部因素
- **P (Plan)**: 计划 - 具体可执行的行动步骤

#### 错误响应

**404 Not Found** - 无可用报告
```json
{
  "error": {
    "code": "REPORT_NOT_FOUND",
    "message": "暂无可用报告"
  }
}
```

---

## ⚠️ 错误码参考

### 用户相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| INVALID_USER_ID | 400 | 用户ID格式无效 |
| USER_NOT_FOUND | 404 | 用户不存在 |

### 档案相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| VALIDATION_ERROR | 400 | 数据验证失败 |
| PROFILE_ALREADY_EXISTS | 400 | 档案已存在 |
| PROFILE_INCOMPLETE | 400 | 档案信息不完整 |
| PROFILE_LIMIT_EXCEEDED | 403 | 超过未来档案数量限制(3个) |

### 信件相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| LETTER_NOT_FOUND | 404 | 信件不存在 |
| REPLY_NOT_FOUND | 404 | 回信不存在 |
| LETTER_TOO_SHORT | 400 | 信件内容过短(<50字) |
| LETTER_TOO_LONG | 400 | 信件内容过长(>5000字) |

### 聊天相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| MESSAGE_LIMIT_EXCEEDED | 403 | 超过聊天消息限制(5条) |
| FUTURE_PROFILE_NOT_FOUND | 404 | 未来档案不存在 |

### 报告相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| REPORT_NOT_FOUND | 404 | 报告不存在 |
| REPORT_GENERATING | 425 | 报告生成中，请稍后 |

### 系统相关
| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| LLM_TIMEOUT | 504 | AI服务超时 |
| LLM_ERROR | 500 | AI服务错误 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

---

## 🔄 完整用户旅程示例

### 步骤1: 初始化用户
```http
POST /api/v1/user/init
Content-Type: application/json

{
  "anonymous_user_id": null
}

→ Response: { "user_id": "xxx", "status": "ONBOARDING" }
```

### 步骤2: 提交当前档案 (F2.1)
```http
POST /api/v1/profile/current?user_id=xxx
Content-Type: application/json

{
  "demo_data": { ... },
  "vals_data": { ... },
  "bfi_data": { ... },
  "story_data": { ... }
}

→ Response: { "status": "CURRENT_PROFILE_SAVED" }
```

### 步骤3: 创建未来档案 (F2.2)
```http
POST /api/v1/profile/future?user_id=xxx
Content-Type: application/json

{
  "profiles": [
    {
      "profile_name": "UX研究员",
      "future_values": "...",
      "future_vision": "...",
      "future_obstacles": "..."
    }
  ]
}

→ Response: { "status": "ACTIVE", "created_profiles": [...] }
```

### 步骤4: 提交信件 (F3.1.2)
```http
POST /api/v1/letters/submit?user_id=xxx
Content-Type: application/json

{
  "content": "亲爱的未来的我..."
}

→ Response: { "letter_id": "yyy", "status": "SUBMITTED" }
```

### 步骤5: 轮询回信状态 (F6.6)
```http
GET /api/v1/letters/status?user_id=xxx

→ Response: { "status": "REPLIES_READY" }
```

### 步骤6: 查看收信箱 (F6.5)
```http
GET /api/v1/inbox/latest?user_id=xxx

→ Response: { "letter_id": "yyy", "replies": [...] }
```

### 步骤7: 阅读回信 (F3.1.3)
```http
GET /api/v1/letters/reply/{reply_id}

→ Response: { "content": "...", "chat_status": "NOT_STARTED" }
```

### 步骤8: 发送聊天消息 (F3.2.2) x5
```http
POST /api/v1/chat/{future_profile_id}/send
Content-Type: application/json

{
  "user_id": "xxx",
  "content": "你好，未来的我"
}

→ Response: { "sender": "AGENT", "content": "..." }
```

### 步骤9: 第5条消息后，前端自动触发报告 (F5.1)
```http
POST /api/v1/report/generate
Content-Type: application/json

{
  "user_id": "xxx"
}

→ Response: { "status": "GENERATING" }
```

### 步骤10: 轮询报告状态 (F5.3)
```http
GET /api/v1/report/status?user_id=xxx

→ Response: { "status": "READY" }
```

### 步骤11: 查看报告 (F5.2)
```http
GET /api/v1/report/latest?user_id=xxx

→ Response: { "content": { "W": "...", "O": "...", ... } }
```

---

## 📌 API设计原则

### 1. 异步优先
- 耗时操作（AI生成）使用异步模式
- 立即返回 202 Accepted
- 提供轮询接口查询状态

### 2. 幂等性
- GET请求天然幂等
- POST请求在合理情况下支持重复提交

### 3. 数据安全
- 所有PII数据必须加密存储
- API传输使用HTTPS
- 验证所有用户输入

### 4. 性能要求
- 同步聊天: < 8秒
- 异步回信: < 5分钟
- 异步报告: < 3分钟

### 5. 错误处理
- 提供清晰的错误码
- 包含可操作的错误信息
- 区分客户端错误和服务端错误

---

## 🔧 开发环境配置

### 环境变量
```env
# API配置
API_BASE_URL=http://localhost:8000
API_VERSION=v1

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/future_self_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI服务
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 限流
MAX_CHAT_MESSAGES=5
MAX_FUTURE_PROFILES=3
```

### 测试API
```bash
# 健康检查
curl http://localhost:8000/health

# API文档
open http://localhost:8000/docs
```


---

**文档版本**: v1.5  
**最后更新**: 2025-11-10  
**维护者**: 开发团队
