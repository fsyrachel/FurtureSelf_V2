# 前端接口和交互逻辑说明文档

## 📋 概述

本文档说明信件提交、状态轮询和失败重试的完整交互流程。后端已实现自动重试机制（最多3次），前端需要处理失败后的用户重试流程。

**⚠️ 重要提示**: 对于所有需要用户填写和选择的内容（Current Profile、Future Profile、写信、聊天），**前端必须在提交前进行验证**，不符合 schema 时要弹窗提示用户，而不是让后端处理这些验证错误。

---

## ✅ 前端数据验证（重要！）

### 为什么需要前端验证？

1. **用户体验**: 立即反馈错误，用户无需等待网络请求
2. **减少服务器负载**: 避免无效请求到达后端
3. **数据质量**: 确保提交的数据符合 schema 要求
4. **避免后端错误**: 防止因数据格式错误导致的 400 错误

### ⚠️ 验证原则

**所有用户填写/选择的内容必须在提交前进行前端验证，不符合规则时弹窗提示用户，不允许提交。**

---

## 📝 各模块验证规则

### 1. Current Profile (F2.1) - 当前档案

**接口**: `POST /api/v1/profile/current`

#### 验证规则

**demo_data (基本信息)**
```javascript
{
  name: string,        // 必填，1-50字符
  age: number,         // 必填，18-100之间的整数
  gender: string,      // 必填，至少1字符
  status: string,      // 必填，至少1字符
  field: string,       // 必填，至少1字符
  interests: string,   // 必填，至少1字符
  location: string,    // 必填，至少1字符
  future_location: string  // 必填，至少1字符
}
```

**vals_data (价值观问卷)**
```javascript
// 对象，所有值必须是 1.0-5.0 之间的浮点数
// 示例: { "value1": 3.5, "value2": 4.0, ... }
// 验证: Object.values(vals_data).every(v => v >= 1.0 && v <= 5.0)
```

**bfi_data (人格特质问卷)**
```javascript
// 对象，所有值必须是 1.0-5.0 之间的浮点数
// 示例: { "trait1": 2.5, "trait2": 4.5, ... }
// 验证: Object.values(bfi_data).every(v => v >= 1.0 && v <= 5.0)
```

#### 前端验证示例

```javascript
function validateCurrentProfile(data) {
  const errors = [];
  
  // 验证 demo_data
  if (!data.demo_data.name || data.demo_data.name.length < 1 || data.demo_data.name.length > 50) {
    errors.push('姓名必须在1-50字符之间');
  }
  
  if (!data.demo_data.age || data.demo_data.age < 18 || data.demo_data.age > 100) {
    errors.push('年龄必须在18-100之间');
  }
  
  // 验证其他必填字段
  const requiredFields = ['gender', 'status', 'field', 'interests', 'location', 'future_location'];
  for (const field of requiredFields) {
    if (!data.demo_data[field] || data.demo_data[field].length < 1) {
      errors.push(`${getFieldLabel(field)}不能为空`);
    }
  }
  
  // 验证 vals_data
  if (!data.vals_data || Object.keys(data.vals_data).length === 0) {
    errors.push('价值观问卷必须填写');
  } else {
    const invalidValues = Object.values(data.vals_data).filter(v => v < 1.0 || v > 5.0);
    if (invalidValues.length > 0) {
      errors.push('价值观问卷的评分必须在1.0-5.0之间');
    }
  }
  
  // 验证 bfi_data
  if (!data.bfi_data || Object.keys(data.bfi_data).length === 0) {
    errors.push('人格特质问卷必须填写');
  } else {
    const invalidValues = Object.values(data.bfi_data).filter(v => v < 1.0 || v > 5.0);
    if (invalidValues.length > 0) {
      errors.push('人格特质问卷的评分必须在1.0-5.0之间');
    }
  }
  
  if (errors.length > 0) {
    showErrorModal('请检查以下问题：\n' + errors.join('\n'));
    return false;
  }
  
  return true;
}

// 使用示例
async function submitCurrentProfile(userId, profileData) {
  // ✅ 先进行前端验证
  if (!validateCurrentProfile(profileData)) {
    return { success: false, error: 'VALIDATION_FAILED' };
  }
  
  // 验证通过后再提交
  const response = await fetch(`/api/v1/profile/current?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profileData)
  });
  
  // ... 处理响应
}
```

---

### 2. Future Profile (F2.2) - 未来档案

**接口**: `POST /api/v1/profile/future`

#### 验证规则

```javascript
{
  profiles: [  // 必填，1-3个档案
    {
      profile_name: string,      // 必填，1-100字符
      future_values: string,    // 必填，10-2000字符
      future_vision: string,     // 必填，10-2000字符
      future_obstacles: string   // 必填，10-2000字符
    }
  ]
}
```

#### 前端验证示例

```javascript
function validateFutureProfile(data) {
  const errors = [];
  
  // 验证 profiles 数组
  if (!data.profiles || !Array.isArray(data.profiles)) {
    errors.push('至少需要创建1个未来档案');
    return false;
  }
  
  if (data.profiles.length < 1 || data.profiles.length > 3) {
    errors.push('未来档案数量必须在1-3个之间');
  }
  
  // 验证每个档案
  data.profiles.forEach((profile, index) => {
    if (!profile.profile_name || profile.profile_name.length < 1 || profile.profile_name.length > 100) {
      errors.push(`档案${index + 1}的名称必须在1-100字符之间`);
    }
    
    if (!profile.future_values || profile.future_values.length < 10 || profile.future_values.length > 2000) {
      errors.push(`档案${index + 1}的未来价值观必须在10-2000字符之间`);
    }
    
    if (!profile.future_vision || profile.future_vision.length < 10 || profile.future_vision.length > 2000) {
      errors.push(`档案${index + 1}的未来愿景必须在10-2000字符之间`);
    }
    
    if (!profile.future_obstacles || profile.future_obstacles.length < 10 || profile.future_obstacles.length > 2000) {
      errors.push(`档案${index + 1}的未来障碍必须在10-2000字符之间`);
    }
  });
  
  if (errors.length > 0) {
    showErrorModal('请检查以下问题：\n' + errors.join('\n'));
    return false;
  }
  
  return true;
}
```

---

### 3. Letter (F3.1.2) - 提交信件

**接口**: `POST /api/v1/letters/submit`

#### 验证规则

```javascript
{
  content: string  // 必填，50-5000字符
}
```

#### 前端验证示例

```javascript
function validateLetter(content) {
  if (!content || content.trim().length < 50) {
    showErrorModal('信件内容至少需要50个字符，当前：' + (content?.length || 0) + '字符');
    return false;
  }
  
  if (content.length > 5000) {
    showErrorModal('信件内容不能超过5000个字符，当前：' + content.length + '字符');
    return false;
  }
  
  return true;
}

// 使用示例（已在文档中）
const handleSubmit = async () => {
  // ✅ 先进行前端验证
  if (!validateLetter(content)) {
    return;  // 验证失败，不提交
  }
  
  // 验证通过后再提交
  const result = await submitLetter(userId, content);
  // ...
};
```

---

### 4. Chat Message (F3.2.2) - 发送聊天消息

**接口**: `POST /api/v1/chat/{future_profile_id}/send`

#### 验证规则

```javascript
{
  content: string  // 必填，1-1000字符
}
```

#### 前端验证示例

```javascript
function validateChatMessage(content) {
  if (!content || content.trim().length < 1) {
    showErrorModal('消息内容不能为空');
    return false;
  }
  
  if (content.length > 1000) {
    showErrorModal('消息内容不能超过1000个字符，当前：' + content.length + '字符');
    return false;
  }
  
  return true;
}
```

#### 重试机制说明

**⚠️ 重要特性**:
- ✅ **AI错误不计次**: 如果AI服务调用失败（网络错误、超时等），用户消息不会被保存，**不会占用5次限制**
- ✅ **手动重试**: AI错误时前端需要弹窗提示用户，让用户手动重试
- ✅ **自动回滚**: 后端会自动回滚用户消息，确保数据一致性

**错误处理**:
- `500 LLM_ERROR`: AI服务错误，不计次，需要弹窗让用户重试
- `403 MESSAGE_LIMIT_EXCEEDED`: 已达到5条消息上限，发送按钮变成"生成报告"按钮
- `404 Profile data incomplete`: 数据不完整，需要检查用户档案

#### 前端实现示例（带重试机制）

```javascript
async function sendChatMessage(futureProfileId, content) {
  // ✅ 先进行前端验证
  if (!validateChatMessage(content)) {
    return { success: false, error: 'VALIDATION_FAILED' };
  }
  
  try {
    const response = await fetch(`/api/v1/chat/${futureProfileId}/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    
    if (response.status === 200) {
      // 成功：返回AI回复
      const data = await response.json();
      return { success: true, message: data };
    } else if (response.status === 403) {
      // 达到5条限制（理论上不应该到达这里，因为前端会先检查）
      const error = await response.json();
      if (error.detail === 'MESSAGE_LIMIT_EXCEEDED') {
        // 触发按钮切换为"生成报告"
        return { success: false, error: 'MESSAGE_LIMIT_EXCEEDED' };
      }
    } else if (response.status === 500) {
      // AI服务错误：不计次，需要弹窗让用户重试
      const error = await response.json();
      if (error.detail === 'LLM_ERROR') {
        // 弹窗提示用户重试
        const shouldRetry = await showRetryModal(
          'AI服务暂时不可用，是否重试？',
          '您的消息未发送，不会占用次数限制'
        );
        
        if (shouldRetry) {
          // 用户选择重试，递归调用
          return await sendChatMessage(futureProfileId, content);
        } else {
          return { success: false, error: 'LLM_ERROR', canRetry: true };
        }
      }
    } else if (response.status === 404) {
      // 数据不完整
      const error = await response.json();
      showErrorModal('用户档案数据不完整，请先完善个人信息');
      return { success: false, error: 'PROFILE_INCOMPLETE' };
    } else {
      throw new Error('发送消息失败');
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    // 网络错误：弹窗让用户重试
    const shouldRetry = await showRetryModal(
      '网络错误，是否重试？',
      '您的消息未发送，不会占用次数限制'
    );
    
    if (shouldRetry) {
      return await sendChatMessage(futureProfileId, content);
    }
    
    return { success: false, error: 'NETWORK_ERROR', canRetry: true };
  }
}

// 重试确认弹窗
function showRetryModal(title, message) {
  return new Promise((resolve) => {
    // 使用你的 UI 库显示确认弹窗
    // 例如：使用 Ant Design、Material-UI、Element UI 等
    const userChoice = confirm(`${title}\n${message}\n\n点击"确定"重试，点击"取消"放弃发送`);
    resolve(userChoice);
  });
}
```

#### 聊天组件示例（带重试）

```javascript
function ChatPage({ futureProfileId }) {
  const [messages, setMessages] = useState([]);
  const [inputContent, setInputContent] = useState('');
  const [isSending, setIsSending] = useState(false);
  const userId = getUserId();
  
  const handleSend = async () => {
    if (isSending) return; // 防止重复发送
    
    // 前端验证
    if (!validateChatMessage(inputContent)) {
      return;
    }
    
    setIsSending(true);
    
    // 先显示用户消息（乐观更新）
    const userMessage = {
      id: Date.now(),
      sender: 'USER',
      content: inputContent,
      created_at: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // 保存输入内容（用于重试）
    const contentToSend = inputContent;
    setInputContent(''); // 清空输入框
    
    // 发送消息
    const result = await sendChatMessage(futureProfileId, contentToSend);
    
    if (result.success) {
      // 成功：添加AI回复
      setMessages(prev => [...prev, result.message]);
    } else {
      // 失败：移除用户消息（因为后端已回滚）
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      
      // 恢复输入内容（如果用户想重试）
      if (result.canRetry) {
        setInputContent(contentToSend);
      }
    }
    
    setIsSending(false);
  };
  
  return (
    <div>
      {/* 消息列表 */}
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender.toLowerCase()}`}>
            {msg.content}
          </div>
        ))}
      </div>
      
      {/* 输入框 */}
      <div className="input-area">
        <textarea
          value={inputContent}
          onChange={(e) => setInputContent(e.target.value)}
          placeholder="输入消息..."
          disabled={isSending}
        />
        <button onClick={handleSend} disabled={isSending}>
          {isSending ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
}
```

---

### 5. 通用验证工具函数

```javascript
// 统一的错误提示函数
function showErrorModal(message) {
  // 使用你的 UI 库显示模态框
  // 例如：使用 Ant Design、Material-UI、Element UI 等
  alert(message);  // 简单示例，实际应该使用更好的 UI 组件
}

// 字符计数显示（实时反馈）
function CharacterCounter({ text, min, max }) {
  const length = text?.length || 0;
  const isValid = length >= min && length <= max;
  
  return (
    <div className={isValid ? 'text-green' : 'text-red'}>
      {length} / {min}-{max} 字符
    </div>
  );
}

// 使用示例
<textarea 
  value={content}
  onChange={(e) => setContent(e.target.value)}
  placeholder="写下你想对未来的自己说的话..."
/>
<CharacterCounter text={content} min={50} max={5000} />
```

---

### 6. 验证最佳实践

1. **实时验证**: 在用户输入时显示字符计数和验证提示
2. **提交前验证**: 点击提交按钮时再次完整验证
3. **友好提示**: 使用清晰的错误消息，指出具体问题
4. **防止提交**: 验证失败时禁用提交按钮或阻止表单提交
5. **高亮错误**: 在界面上高亮显示有问题的字段

---

## 🔌 核心接口

### 1. 提交信件

**接口**: `POST /api/v1/letters/submit`

**请求参数**:
```json
{
  "content": "信件内容（50-5000字符）"
}
```

**Query参数**: `user_id` (必填)

**响应** (202 Accepted):
```json
{
  "letter_id": "uuid",
  "status": "SUBMITTED"
}
```

**重要特性**:
- ✅ **支持重试**: 如果用户之前提交的信件状态为 `FAILED` 或 `PENDING`，可以重新调用此接口
- ✅ **自动处理**: 后端会自动更新现有信件并重新触发处理
- ❌ **防止重复**: 如果状态为 `REPLIES_READY`（已成功），会返回 400 错误

---

### 2. 轮询信件状态

**接口**: `GET /api/v1/letters/status`

**Query参数**: `user_id` (必填)

**响应** (200 OK):

**情况1: 处理中**
```json
{
  "status": "PENDING",
  "content": null
}
```

**情况2: 处理成功**
```json
{
  "status": "REPLIES_READY",
  "content": null
}
```

**情况3: 处理失败**
```json
{
  "status": "FAILED",
  "content": "信件完整内容..."
}
```

**关键说明**:
- `content` 字段：
  - 当 `status` 为 `FAILED` 时，返回完整信件内容（用于恢复）
  - 当 `status` 为 `PENDING` 或 `REPLIES_READY` 时，`content` 为 `null`
- **用途**: 仅在失败时返回内容，让前端可以恢复用户已写的内容

---

## 🔄 完整交互流程

### 场景1: 正常流程（成功）

```
1. 用户在写信页输入内容
   ↓
2. 调用 POST /letters/submit
   ↓
3. 收到 202 响应，跳转到等待页
   ↓
4. 开始轮询 GET /letters/status（每3秒一次）
   ↓
5. 收到 status: "PENDING", content: null（继续等待）
   ↓
6. 继续轮询...
   ↓
7. 收到 status: "REPLIES_READY", content: null
   ↓
8. 跳转到收信箱页面 ✅
```

### 场景2: 失败后重试

```
1. 用户在写信页输入内容
   ↓
2. 调用 POST /letters/submit
   ↓
3. 收到 202 响应，跳转到等待页
   ↓
4. 开始轮询 GET /letters/status
   ↓
5. 收到 status: "PENDING", content: "..."
   ↓
6. 继续轮询...
   ↓
7. 收到 status: "FAILED", content: "信件内容..."
   ↓
8. 自动跳回写信页
   ↓
9. 使用响应中的 content 恢复编辑框内容
   ↓
10. 显示错误提示："处理失败，请修改后重新提交"
    ↓
11. 用户修改内容后，再次调用 POST /letters/submit（使用相同接口）
    ↓
12. 重新开始轮询流程...
```

---

## 💻 前端实现示例

### 1. 提交信件函数

```javascript
async function submitLetter(userId, content) {
  try {
    const response = await fetch(
      `/api/v1/letters/submit?user_id=${userId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      }
    );
    
    if (response.status === 202) {
      const data = await response.json();
      // 跳转到等待页
      navigate('/waiting');
      // 开始轮询
      pollLetterStatus(userId);
      return { success: true, letterId: data.letter_id };
    } else if (response.status === 400) {
      const error = await response.json();
      if (error.detail === 'LETTER_ALREADY_SUBMITTED') {
        // 信件已成功处理，跳转到收信箱
        navigate('/inbox');
        return { success: true, alreadySubmitted: true };
      }
      throw new Error(error.detail);
    } else {
      throw new Error('提交失败');
    }
  } catch (error) {
    console.error('提交信件失败:', error);
    showError('提交失败，请重试');
    return { success: false, error: error.message };
  }
}
```

### 2. 轮询状态函数

```javascript
async function pollLetterStatus(userId) {
  const maxAttempts = 60; // 最多轮询60次（3分钟）
  let attempts = 0;
  
  const poll = async () => {
    try {
      const response = await fetch(
        `/api/v1/letters/status?user_id=${userId}`
      );
      
      if (!response.ok) {
        throw new Error('获取状态失败');
      }
      
      const data = await response.json();
      
      // 成功：跳转到收信箱
      if (data.status === 'REPLIES_READY') {
        navigate('/inbox');
        return { success: true };
      }
      
      // 失败：跳回写信页并恢复内容
      if (data.status === 'FAILED') {
        navigate('/write-letter');
        // 恢复信件内容
        if (data.content) {
          setLetterContent(data.content);
        }
        showError('信件处理失败，请修改后重新提交');
        return { success: false, error: 'FAILED', canRetry: true };
      }
      
      // 处理中：继续轮询（PENDING 状态不返回内容）
      if (data.status === 'PENDING') {
        attempts++;
        if (attempts >= maxAttempts) {
          // 超时：跳回写信页（但此时没有内容可恢复）
          navigate('/write-letter');
          showError('处理超时，请重新提交信件');
          return { success: false, error: 'TIMEOUT', canRetry: true };
        }
        
        // 3秒后继续轮询
        setTimeout(poll, 3000);
        return { success: false, status: 'PENDING' };
      }
      
    } catch (error) {
      console.error('轮询失败:', error);
      // 网络错误时，可以继续重试
      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, 3000);
      } else {
        showError('网络错误，请检查连接后重试');
      }
    }
  };
  
  // 开始轮询
  poll();
}
```

### 3. 写信页组件示例

```javascript
function WriteLetterPage() {
  const [content, setContent] = useState('');
  const userId = getUserId(); // 从 localStorage 或其他地方获取
  
  useEffect(() => {
    // 页面加载时，检查是否有本地草稿
    const draft = localStorage.getItem('letter_draft');
    if (draft) {
      setContent(draft);
      localStorage.removeItem('letter_draft'); // 清除草稿
    }
  }, []);
  
  const handleSubmit = async () => {
    if (content.length < 50 || content.length > 5000) {
      showError('信件内容必须在50-5000字符之间');
      return;
    }
    
    const result = await submitLetter(userId, content);
    if (result.success) {
      // 提交成功，跳转到等待页（在 submitLetter 中已处理）
    }
  };
  
  return (
    <div>
      <textarea 
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="写下你想对未来的自己说的话..."
      />
      <button onClick={handleSubmit}>提交</button>
    </div>
  );
}
```

---

## ⚠️ 错误处理

### 常见错误码

| HTTP状态码 | 错误信息 | 处理方式 |
|-----------|---------|---------|
| 400 | `LETTER_ALREADY_SUBMITTED` | 信件已成功处理，跳转到收信箱 |
| 400 | `信件状态为 XXX，无法提交` | 显示错误提示，不允许提交 |
| 404 | `LETTER_NOT_FOUND` | 没有信件，显示空状态 |
| 500 | 服务器错误 | 显示错误提示，允许重试 |

### 错误处理示例

```javascript
async function handleApiError(response) {
  if (response.status === 400) {
    const error = await response.json();
    
    if (error.detail === 'LETTER_ALREADY_SUBMITTED') {
      // 已成功，跳转到收信箱
      navigate('/inbox');
      return;
    }
    
    // 其他400错误
    showError(error.detail || '请求参数错误');
    return;
  }
  
  if (response.status === 404) {
    // 没有信件，可能是首次访问
    return;
  }
  
  if (response.status >= 500) {
    // 服务器错误，允许重试
    showError('服务器错误，请稍后重试');
    return;
  }
}
```

---

## 🔑 关键要点总结

### ✅ 必须实现的功能

1. **状态轮询**: 提交后每3秒轮询一次状态，最多轮询60次（3分钟）
2. **失败处理**: 检测到 `FAILED` 状态时，自动跳回写信页并恢复内容
3. **内容恢复**: 使用轮询响应中的 `content` 字段恢复用户已写的内容
4. **统一接口**: 首次提交和重试都使用同一个 `POST /letters/submit` 接口

### 📝 注意事项

1. **内容保存**: 
   - 轮询时如果收到 `PENDING` 状态，可以保存 `content` 到 `localStorage` 作为备份
   - 失败时优先使用轮询响应中的 `content`，其次使用 `localStorage` 中的备份

2. **状态判断**:
   - `PENDING`: 继续轮询，可选保存内容
   - `REPLIES_READY`: 跳转到收信箱
   - `FAILED`: 跳回写信页，恢复内容，显示错误提示

3. **重试逻辑**:
   - 用户修改内容后，直接调用 `POST /letters/submit`（与首次提交相同）
   - 后端会自动识别是重试还是首次提交
   - 不需要额外的重试接口

4. **用户体验**:
   - 失败时自动恢复内容，用户无需重新输入
   - 显示清晰的错误提示
   - 提供"重新提交"按钮（调用相同的提交接口）

---

## 📞 后端自动重试机制

后端已实现自动重试（前端无需处理）：

- **重试次数**: 最多3次
- **重试间隔**: 指数退避（60秒、120秒、240秒）
- **失败处理**: 3次重试都失败后，状态更新为 `FAILED`
- **前端行为**: 检测到 `FAILED` 状态后，跳回写信页让用户手动重试

---

## 🧪 测试建议

1. **正常流程测试**: 提交→轮询→成功
2. **失败流程测试**: 提交→轮询→失败→恢复内容→重试
3. **超时测试**: 轮询60次后仍未成功，应该跳回写信页
4. **网络错误测试**: 轮询时网络中断，应该继续重试或提示用户

---

## 📊 报告生成接口和交互逻辑

### 1. 触发报告生成

**接口**: `POST /api/v1/reports/generate`

**Query参数**: `user_id` (必填)

**响应** (202 Accepted):
```json
{
  "report_id": "uuid",
  "status": "GENERATING"
}
```

**重要特性**:
- ✅ **支持重试**: 如果报告状态为 `FAILED` 或 `GENERATING`，可以重新调用此接口
- ✅ **自动处理**: 后端会自动重置状态并重新触发处理
- ❌ **防止重复**: 如果状态为 `READY`（已成功），会返回 400 错误

---

### 2. 轮询报告状态

**接口**: `GET /api/v1/reports/status`

**Query参数**: `user_id` (必填)

**响应** (200 OK):

**情况1: 生成中**
```json
{
  "status": "GENERATING"
}
```

**情况2: 生成成功**
```json
{
  "status": "READY"
}
```

**情况3: 生成失败**
```json
{
  "status": "FAILED"
}
```

**关键说明**:
- 报告生成失败时，状态为 `FAILED`，用户可以重新调用 `/generate` 接口重试
- 报告生成成功后，状态为 `READY`，可以调用 `/latest` 接口获取报告内容

---

## 🔄 报告生成完整交互流程

### 场景1: 正常流程（成功）

```
1. 用户完成5条聊天后，自动触发报告生成
   ↓
2. 调用 POST /reports/generate
   ↓
3. 收到 202 响应，跳转到等待页
   ↓
4. 开始轮询 GET /reports/status（每3秒一次）
   ↓
5. 收到 status: "GENERATING"（继续等待）
   ↓
6. 继续轮询...
   ↓
7. 收到 status: "READY"
   ↓
8. 调用 GET /reports/latest 获取报告内容
   ↓
9. 跳转到报告展示页面 ✅
```

### 场景2: 失败后重试

```
1. 用户完成5条聊天后，自动触发报告生成
   ↓
2. 调用 POST /reports/generate
   ↓
3. 收到 202 响应，跳转到等待页
   ↓
4. 开始轮询 GET /reports/status
   ↓
5. 收到 status: "GENERATING"（继续等待）
   ↓
6. 继续轮询...
   ↓
7. 收到 status: "FAILED"
   ↓
8. 显示错误提示："报告生成失败，请重试"
   ↓
9. 用户点击"重新生成"按钮，再次调用 POST /reports/generate（使用相同接口）
   ↓
10. 重新开始轮询流程...
```

---

## 💻 报告生成前端实现示例

### 1. 触发报告生成函数

```javascript
async function generateReport(userId) {
  try {
    const response = await fetch(
      `/api/v1/reports/generate?user_id=${userId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    if (response.status === 202) {
      const data = await response.json();
      // 跳转到等待页
      navigate('/waiting-report');
      // 开始轮询
      pollReportStatus(userId);
      return { success: true, reportId: data.report_id };
    } else if (response.status === 400) {
      const error = await response.json();
      if (error.detail === 'REPORT_ALREADY_GENERATED') {
        // 报告已成功生成，跳转到报告页
        navigate('/report');
        return { success: true, alreadyGenerated: true };
      }
      throw new Error(error.detail);
    } else {
      throw new Error('生成报告失败');
    }
  } catch (error) {
    console.error('生成报告失败:', error);
    showError('生成报告失败，请重试');
    return { success: false, error: error.message };
  }
}
```

### 2. 轮询报告状态函数

```javascript
async function pollReportStatus(userId) {
  const maxAttempts = 60; // 最多轮询60次（3分钟）
  let attempts = 0;
  
  const poll = async () => {
    try {
      const response = await fetch(
        `/api/v1/reports/status?user_id=${userId}`
      );
      
      if (!response.ok) {
        throw new Error('获取状态失败');
      }
      
      const data = await response.json();
      
      // 成功：获取报告内容并跳转
      if (data.status === 'READY') {
        // 获取报告内容
        const reportData = await fetchLatestReport(userId);
        if (reportData.success) {
          navigate('/report', { state: { report: reportData.report } });
        }
        return { success: true };
      }
      
      // 失败：显示错误提示，允许重试
      if (data.status === 'FAILED') {
        showError('报告生成失败，请点击"重新生成"按钮重试');
        // 显示重试按钮
        setShowRetryButton(true);
        return { success: false, error: 'FAILED', canRetry: true };
      }
      
      // 生成中：继续轮询
      if (data.status === 'GENERATING') {
        attempts++;
        if (attempts >= maxAttempts) {
          // 超时：显示错误提示
          showError('报告生成超时，请点击"重新生成"按钮重试');
          setShowRetryButton(true);
          return { success: false, error: 'TIMEOUT', canRetry: true };
        }
        
        // 3秒后继续轮询
        setTimeout(poll, 3000);
        return { success: false, status: 'GENERATING' };
      }
      
    } catch (error) {
      console.error('轮询失败:', error);
      // 网络错误时，可以继续重试
      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, 3000);
      } else {
        showError('网络错误，请检查连接后重试');
        setShowRetryButton(true);
      }
    }
  };
  
  // 开始轮询
  poll();
}
```

### 3. 获取报告内容函数

```javascript
async function fetchLatestReport(userId) {
  try {
    const response = await fetch(
      `/api/v1/reports/latest?user_id=${userId}`
    );
    
    if (response.status === 404) {
      // 报告未准备好
      return { success: false, error: 'REPORT_NOT_READY' };
    }
    
    if (!response.ok) {
      throw new Error('获取报告失败');
    }
    
    const data = await response.json();
    return { success: true, report: data };
  } catch (error) {
    console.error('获取报告失败:', error);
    showError('获取报告失败，请重试');
    return { success: false, error: error.message };
  }
}
```

### 4. 等待页组件示例

```javascript
function WaitingReportPage() {
  const [showRetryButton, setShowRetryButton] = useState(false);
  const userId = getUserId();
  
  useEffect(() => {
    // 页面加载时开始轮询
    pollReportStatus(userId);
  }, [userId]);
  
  const handleRetry = async () => {
    setShowRetryButton(false);
    const result = await generateReport(userId);
    if (result.success) {
      // 重新开始轮询（在 generateReport 中已处理）
    }
  };
  
  return (
    <div>
      <h2>正在生成您的职业洞见报告...</h2>
      <p>这可能需要几分钟时间，请耐心等待</p>
      
      {showRetryButton && (
        <div>
          <p>报告生成失败，请重试</p>
          <button onClick={handleRetry}>重新生成</button>
        </div>
      )}
    </div>
  );
}
```

---

## ⚠️ 报告生成错误处理

### 常见错误码

| HTTP状态码 | 错误信息 | 处理方式 |
|-----------|---------|---------|
| 400 | `REPORT_ALREADY_GENERATED` | 报告已成功生成，跳转到报告页 |
| 400 | `报告状态为 XXX，无法生成` | 显示错误提示，不允许生成 |
| 404 | `REPORT_NOT_FOUND` | 没有报告，显示空状态 |
| 404 | `REPORT_NOT_READY` | 报告未准备好，继续等待或显示提示 |
| 500 | 服务器错误 | 显示错误提示，允许重试 |

### 错误处理示例

```javascript
async function handleReportApiError(response) {
  if (response.status === 400) {
    const error = await response.json();
    
    if (error.detail === 'REPORT_ALREADY_GENERATED') {
      // 已成功，跳转到报告页
      navigate('/report');
      return;
    }
    
    // 其他400错误
    showError(error.detail || '请求参数错误');
    return;
  }
  
  if (response.status === 404) {
    const error = await response.json();
    if (error.detail === 'REPORT_NOT_READY') {
      // 报告未准备好，继续等待
      return;
    }
    // 没有报告，可能是首次访问
    return;
  }
  
  if (response.status >= 500) {
    // 服务器错误，允许重试
    showError('服务器错误，请稍后重试');
    return;
  }
}
```

---

## 🔑 报告生成关键要点总结

### ✅ 必须实现的功能

1. **状态轮询**: 生成后每3秒轮询一次状态，最多轮询60次（3分钟）
2. **失败处理**: 检测到 `FAILED` 状态时，显示错误提示和重试按钮
3. **统一接口**: 首次生成和重试都使用同一个 `POST /reports/generate` 接口
4. **报告获取**: 状态为 `READY` 时，调用 `GET /reports/latest` 获取报告内容

### 📝 注意事项

1. **状态判断**:
   - `GENERATING`: 继续轮询，显示"正在生成"提示
   - `READY`: 获取报告内容，跳转到报告展示页
   - `FAILED`: 显示错误提示，提供重试按钮

2. **重试逻辑**:
   - 用户点击"重新生成"按钮，直接调用 `POST /reports/generate`（与首次生成相同）
   - 后端会自动识别是重试还是首次生成
   - 不需要额外的重试接口

3. **用户体验**:
   - 生成中显示友好的等待提示
   - 失败时显示清晰的错误提示
   - 提供"重新生成"按钮（调用相同的生成接口）

---

## 📞 报告生成后端自动重试机制

后端已实现自动重试（前端无需处理）：

- **重试次数**: 最多3次
- **重试间隔**: 指数退避（60秒、120秒、240秒）
- **失败处理**: 3次重试都失败后，状态更新为 `FAILED`
- **前端行为**: 检测到 `FAILED` 状态后，显示错误提示让用户手动重试

---

## 🧪 报告生成测试建议

1. **正常流程测试**: 生成→轮询→成功→获取报告
2. **失败流程测试**: 生成→轮询→失败→重试
3. **超时测试**: 轮询60次后仍未成功，应该显示超时提示
4. **网络错误测试**: 轮询时网络中断，应该继续重试或提示用户

---

## 💬 实时聊天接口和重试机制

### 1. 发送聊天消息

**接口**: `POST /api/v1/chat/{future_profile_id}/send`

**路径参数**: `future_profile_id` (必填)

**请求体**:
```json
{
  "content": "消息内容（1-1000字符）"
}
```

**Query参数**: `user_id` (必填)

**响应** (200 OK):
```json
{
  "message_id": "uuid",
  "sender": "AGENT",
  "content": "AI回复内容",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**重要特性**:
- ✅ **AI错误不计次**: 如果AI服务调用失败，用户消息不会被保存，**不会占用5次限制**
- ✅ **手动重试**: AI错误时前端需要弹窗提示用户，让用户手动重试
- ✅ **自动回滚**: 后端会自动回滚用户消息，确保数据一致性
- ❌ **次数限制**: 每个未来档案最多发送5条用户消息

---

### 2. 获取聊天历史

**接口**: `GET /api/v1/chat/{future_profile_id}/history`

**路径参数**: `future_profile_id` (必填)

**Query参数**: `user_id` (必填)

**响应** (200 OK):
```json
[
  {
    "message_id": "uuid",
    "sender": "USER",
    "content": "用户消息",
    "created_at": "2024-01-01T12:00:00Z"
  },
  {
    "message_id": "uuid",
    "sender": "AGENT",
    "content": "AI回复",
    "created_at": "2024-01-01T12:01:00Z"
  }
]
```

---

## 🔄 聊天消息完整交互流程

### 场景1: 正常流程（成功）

```
1. 用户输入消息并点击发送
   ↓
2. 前端验证消息内容（1-1000字符）
   ↓
3. 调用 POST /chat/{future_profile_id}/send
   ↓
4. 收到 200 响应，显示AI回复
   ↓
5. 更新消息列表 ✅
```

### 场景2: AI服务错误（不计次，手动重试）

```
1. 用户输入消息并点击发送
   ↓
2. 前端验证消息内容
   ↓
3. 调用 POST /chat/{future_profile_id}/send
   ↓
4. 收到 500 错误，detail: "LLM_ERROR"
   ↓
5. 弹窗提示："AI服务暂时不可用，是否重试？"（可以美化一下）
   ↓
6. 用户选择重试 → 重新调用接口
   用户选择取消 → 保留输入内容，允许稍后重试
   ↓
7. 如果重试成功，显示AI回复 ✅
```

### 场景3: 达到5条限制

```
1. 用户发送第5条消息后，消息计数达到5
   ↓
2. 发送按钮自动变成"生成报告"按钮
   ↓
3. 用户点击"生成报告"按钮
   ↓
4. 调用 POST /reports/generate
   ↓
5. 跳转到报告等待页，开始生成报告 ✅
```

---

## 💻 聊天消息前端实现示例

### 1. 发送消息函数（带重试机制）

```javascript
async function sendChatMessage(futureProfileId, content) {
  // ✅ 先进行前端验证
  if (!validateChatMessage(content)) {
    return { success: false, error: 'VALIDATION_FAILED' };
  }
  
  try {
    const response = await fetch(
      `/api/v1/chat/${futureProfileId}/send?user_id=${getUserId()}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      }
    );
    
    if (response.status === 200) {
      // 成功：返回AI回复
      const data = await response.json();
      return { success: true, message: data };
    } else if (response.status === 403) {
      // 达到5条限制（理论上不应该到达这里，因为前端会先检查）
      const error = await response.json();
      if (error.detail === 'MESSAGE_LIMIT_EXCEEDED') {
        // 触发按钮切换为"生成报告"
        return { success: false, error: 'MESSAGE_LIMIT_EXCEEDED' };
      }
    } else if (response.status === 500) {
      // AI服务错误：不计次，需要弹窗让用户重试
      const error = await response.json();
      if (error.detail === 'LLM_ERROR') {
        // 弹窗提示用户重试
        const shouldRetry = await showRetryModal(
          'AI服务暂时不可用，是否重试？',
          '您的消息未发送，不会占用次数限制'
        );
        
        if (shouldRetry) {
          // 用户选择重试，递归调用
          return await sendChatMessage(futureProfileId, content);
        } else {
          return { success: false, error: 'LLM_ERROR', canRetry: true };
        }
      }
    } else if (response.status === 404) {
      // 数据不完整
      const error = await response.json();
      showErrorModal('用户档案数据不完整，请先完善个人信息');
      return { success: false, error: 'PROFILE_INCOMPLETE' };
    } else {
      throw new Error('发送消息失败');
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    // 网络错误：弹窗让用户重试
    const shouldRetry = await showRetryModal(
      '网络错误，是否重试？',
      '您的消息未发送，不会占用次数限制'
    );
    
    if (shouldRetry) {
      return await sendChatMessage(futureProfileId, content);
    }
    
    return { success: false, error: 'NETWORK_ERROR', canRetry: true };
  }
}

// 重试确认弹窗
function showRetryModal(title, message) {
  return new Promise((resolve) => {
    // 使用你的 UI 库显示确认弹窗
    // 例如：使用 Ant Design、Material-UI、Element UI 等
    const userChoice = confirm(`${title}\n${message}\n\n点击"确定"重试，点击"取消"放弃发送`);
    resolve(userChoice);
  });
}
```

### 2. 聊天组件示例（完整实现）

```javascript
function ChatPage({ futureProfileId }) {
  const [messages, setMessages] = useState([]);
  const [inputContent, setInputContent] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [messageCount, setMessageCount] = useState(0);
  const userId = getUserId();
  
  // 加载聊天历史
  useEffect(() => {
    loadChatHistory();
  }, [futureProfileId]);
  
  const loadChatHistory = async () => {
    try {
      const response = await fetch(
        `/api/v1/chat/${futureProfileId}/history?user_id=${userId}`
      );
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
        // 统计用户消息数量
        const userMsgCount = data.filter(msg => msg.sender === 'USER').length;
        setMessageCount(userMsgCount);
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error);
    }
  };
  
  const handleSend = async () => {
    if (isSending) return; // 防止重复发送
    
    // 检查是否达到5条限制，如果达到则触发生成报告
    if (messageCount >= 5) {
      // 跳转到生成报告流程
      navigate('/generate-report');
      return;
    }
    
    // 前端验证
    if (!validateChatMessage(inputContent)) {
      return;
    }
    
    setIsSending(true);
    
    // 先显示用户消息（乐观更新）
    const userMessage = {
      id: Date.now(),
      sender: 'USER',
      content: inputContent,
      created_at: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // 保存输入内容（用于重试）
    const contentToSend = inputContent;
    setInputContent(''); // 清空输入框
    
    // 发送消息
    const result = await sendChatMessage(futureProfileId, contentToSend);
    
    if (result.success) {
      // 成功：添加AI回复
      setMessages(prev => [...prev, result.message]);
      setMessageCount(prev => prev + 1); // 增加用户消息计数
    } else {
      // 失败：移除用户消息（因为后端已回滚，不计次）
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      
      // 恢复输入内容（如果用户想重试）
      if (result.canRetry) {
        setInputContent(contentToSend);
      }
      
      // 如果是达到限制，更新计数并触发按钮切换
      if (result.error === 'MESSAGE_LIMIT_EXCEEDED') {
        setMessageCount(5);
        // 此时按钮会自动切换为"生成报告"（通过条件渲染）
      }
    }
    
    setIsSending(false);
  };
  
  const handleGenerateReport = async () => {
    // 调用报告生成接口
    const result = await generateReport(userId);
    if (result.success) {
      // 跳转到报告等待页（在 generateReport 中已处理）
    }
  };
  
  return (
    <div className="chat-page">
      {/* 消息列表 */}
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.message_id} className={`message ${msg.sender.toLowerCase()}`}>
            <div className="sender">{msg.sender === 'USER' ? '我' : 'AI'}</div>
            <div className="content">{msg.content}</div>
            <div className="time">{new Date(msg.created_at).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
      
      {/* 输入区域 */}
      <div className="input-area">
        <div className="message-count">
          已发送 {messageCount} / 5 条消息
        </div>
        {messageCount < 5 ? (
          <>
            <textarea
              value={inputContent}
              onChange={(e) => setInputContent(e.target.value)}
              placeholder="输入消息..."
              disabled={isSending}
              maxLength={1000}
            />
            <div className="char-count">
              {inputContent.length} / 1000 字符
            </div>
            <button 
              onClick={handleSend} 
              disabled={isSending || !inputContent.trim()}
            >
              {isSending ? '发送中...' : '发送'}
            </button>
          </>
        ) : (
          <>
            <div className="limit-notice">
              您已完成5条消息，现在可以生成您的职业洞见报告
            </div>
            <button 
              onClick={handleGenerateReport}
              className="generate-report-btn"
            >
              生成报告
            </button>
          </>
        )}
      </div>
    </div>
  );
}
```

---

## ⚠️ 聊天消息错误处理

### 常见错误码

| HTTP状态码 | 错误信息 | 处理方式 |
|-----------|---------|---------|
| 403 | `MESSAGE_LIMIT_EXCEEDED` | 已达到5条限制，发送按钮变成"生成报告"按钮 |
| 404 | `Profile data incomplete` | 显示错误提示，引导完善个人信息 |
| 500 | `LLM_ERROR` | **弹窗让用户重试，不计次** |
| 500 | 其他服务器错误 | 弹窗让用户重试 |

### 错误处理要点

1. **AI错误不计次**: 
   - 收到 `500 LLM_ERROR` 时，用户消息已被后端回滚
   - 前端需要移除已显示的用户消息（如果使用了乐观更新）
   - 弹窗提示用户重试，保留输入内容

2. **达到限制**:
   - 当消息计数达到5条时，发送按钮自动变成"生成报告"按钮
   - 隐藏输入框，显示提示信息
   - 用户点击"生成报告"按钮后，调用报告生成接口

3. **网络错误**:
   - 捕获网络异常，弹窗让用户重试
   - 同样不计次，保留输入内容

---

## 🔑 聊天消息关键要点总结

### ✅ 必须实现的功能

1. **前端验证**: 消息内容必须在1-1000字符之间
2. **次数限制**: 显示已发送消息数量（最多5条）
3. **按钮切换**: 达到5条消息时，发送按钮自动变成"生成报告"按钮
4. **AI错误处理**: AI服务错误时弹窗让用户重试，不计次
5. **消息历史**: 页面加载时获取并显示聊天历史

### 📝 注意事项

1. **乐观更新**:
   - 可以先显示用户消息，但如果AI调用失败，需要移除
   - 因为后端已回滚，用户消息不会被保存

2. **重试机制**:
   - AI错误时弹窗让用户选择是否重试
   - 保留输入内容，方便用户重试
   - 重试时递归调用发送函数

3. **次数统计和按钮切换**:
   - 前端需要统计已发送的用户消息数量
   - 达到5条时，发送按钮自动变成"生成报告"按钮
   - 隐藏输入框，显示提示信息
   - 可以从聊天历史中统计，或从API响应中获取

4. **用户体验**:
   - 发送中显示加载状态
   - 失败时显示清晰的错误提示
   - 提供重试选项（AI错误时）

---

## 📞 聊天消息后端处理机制

后端已实现以下机制（前端无需处理）：

- **AI错误回滚**: AI调用失败时，自动回滚用户消息，不占用次数限制
- **次数检查**: 发送前检查是否达到5条限制
- **状态更新**: 第一条消息时更新 `chat_status` 为 `COMPLETED`
- **事务保证**: 只有AI调用成功后才提交所有更改

---

## 🧪 聊天消息测试建议

1. **正常流程测试**: 发送消息→收到AI回复
2. **AI错误测试**: 模拟AI服务错误→弹窗提示→重试成功
3. **次数限制测试**: 发送5条消息后→发送按钮变成"生成报告"按钮→点击生成报告
4. **网络错误测试**: 网络中断→弹窗提示→重试
5. **并发测试**: 快速连续发送多条消息→确保不会重复计数

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX  
**维护者**: 后端开发团队

