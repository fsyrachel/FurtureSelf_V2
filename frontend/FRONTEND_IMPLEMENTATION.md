# 前端完整实现指南 (v1.3)

## 📁 文件结构

```
frontend/src/
├── services/
│   └── api.ts                    # ✅ 已创建 - API 客户端
├── stores/
│   └── userStore.ts              # ✅ 已存在 - 用户状态管理
├── components/
│   ├── questionnaire/            # F2.1 问卷组件
│   │   ├── DemoForm.tsx
│   │   ├── PVQForm.tsx
│   │   ├── BFIForm.tsx
│   │   └── StoryForm.tsx
│   ├── future/                   # F2.2 未来档案组件
│   │   ├── FutureProfileCard.tsx
│   │   └── FutureProfileForm.tsx
│   ├── letter/                   # F3.1 信件组件
│   │   ├── LetterEditor.tsx
│   │   └── ReplyCard.tsx
│   ├── chat/                     # F3.2 聊天组件
│   │   └── ChatBox.tsx
│   └── common/                   # 通用组件
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Textarea.tsx
│       ├── ProgressBar.tsx
│       └── LoadingSpinner.tsx
└── pages/
    ├── HomePage.tsx
    ├── OnboardingPage.tsx
    ├── ProfileQuestionnairePage.tsx
    ├── FutureProfilePage.tsx
    ├── WriteLetterPage.tsx
    ├── InboxPage.tsx
    ├── LetterReplyPage.tsx
    ├── ChatPage.tsx
    └── ReportPage.tsx
```

---

## 🔧 核心工具函数

### `src/utils/validation.ts`

```typescript
/**
 * 数据验证工具
 */

export const validateDemoData = (data: any): string[] => {
  const errors: string[] = [];
  
  if (!data.name || data.name.length < 1) {
    errors.push('请输入姓名');
  }
  if (!data.age || data.age < 18 || data.age > 100) {
    errors.push('年龄必须在18-100之间');
  }
  if (!data.status) {
    errors.push('请选择当前状态');
  }
  if (!data.field) {
    errors.push('请输入专业领域');
  }
  if (!data.location) {
    errors.push('请输入当前位置');
  }
  if (!data.future_location) {
    errors.push('请输入期望位置');
  }
  
  return errors;
};

export const validateValsData = (data: any): string[] => {
  const errors: string[] = [];
  const fields = [
    'self_direction', 'stimulation', 'hedonism', 'achievement', 'power',
    'security', 'conformity', 'tradition', 'benevolence', 'universalism'
  ];
  
  fields.forEach(field => {
    const value = data[field];
    if (value === undefined || value < 1 || value > 7) {
      errors.push(`${field} 必须是1-7之间的数字`);
    }
  });
  
  return errors;
};

export const validateBFIData = (data: any): string[] => {
  const errors: string[] = [];
  const fields = [
    'extraversion', 'agreeableness', 'conscientiousness', 
    'neuroticism', 'openness'
  ];
  
  fields.forEach(field => {
    const value = data[field];
    if (value === undefined || value < 1.0 || value > 5.0) {
      errors.push(`${field} 必须是1.0-5.0之间的数字`);
    }
  });
  
  return errors;
};

export const validateStoryData = (data: any): string[] => {
  const errors: string[] = [];
  
  if (!data.proud_moment || data.proud_moment.length < 50) {
    errors.push('骄傲时刻至少需要50字');
  }
  if (!data.turning_point || data.turning_point.length < 50) {
    errors.push('转折点至少需要50字');
  }
  if (!data.difficult_moment || data.difficult_moment.length < 50) {
    errors.push('困难时刻至少需要50字');
  }
  
  return errors;
};

export const validateFutureProfile = (data: any): string[] => {
  const errors: string[] = [];
  
  if (!data.profile_name || data.profile_name.length < 1) {
    errors.push('请输入人设名称');
  }
  if (!data.future_values || data.future_values.length < 50) {
    errors.push('价值观至少需要50字');
  }
  if (!data.future_vision || data.future_vision.length < 50) {
    errors.push('愿景至少需要50字');
  }
  if (!data.future_obstacles || data.future_obstacles.length < 50) {
    errors.push('障碍至少需要50字');
  }
  if (data.profile_name.length > 100) {
    errors.push('人设名称最多100字');
  }
  if (data.future_values.length > 2000) {
    errors.push('价值观最多2000字');
  }
  if (data.future_vision.length > 2000) {
    errors.push('愿景最多2000字');
  }
  if (data.future_obstacles.length > 2000) {
    errors.push('障碍最多2000字');
  }
  
  return errors;
};
```

---

## 🎨 通用组件

### `src/components/common/Button.tsx`

```typescript
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  disabled = false,
  loading = false,
  className = '',
}) => {
  const baseClasses = 'px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 active:bg-blue-100',
  };
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          处理中...
        </span>
      ) : (
        children
      )}
    </button>
  );
};
```

### `src/components/common/Textarea.tsx`

```typescript
import React from 'react';

interface TextareaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
  minLength?: number;
  maxLength?: number;
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
}

export const Textarea: React.FC<TextareaProps> = ({
  value,
  onChange,
  placeholder,
  rows = 4,
  minLength,
  maxLength,
  label,
  hint,
  error,
  required = false,
}) => {
  const charCount = value.length;
  const isValid = (!minLength || charCount >= minLength) && (!maxLength || charCount <= maxLength);
  
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        minLength={minLength}
        maxLength={maxLength}
        className={`w-full px-4 py-3 border rounded-lg resize-none focus:outline-none focus:ring-2 transition-all ${
          error ? 'border-red-500 focus:ring-red-200' : 'border-gray-300 focus:ring-blue-200'
        }`}
      />
      
      <div className="flex justify-between items-center mt-2">
        <div>
          {hint && !error && (
            <p className="text-sm text-gray-500">{hint}</p>
          )}
          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}
        </div>
        
        {(minLength || maxLength) && (
          <p className={`text-sm ${isValid ? 'text-gray-500' : 'text-orange-500'}`}>
            {charCount}
            {minLength && ` / 最少${minLength}`}
            {maxLength && ` / 最多${maxLength}`}
          </p>
        )}
      </div>
    </div>
  );
};
```

---

## 📋 F2.1 问卷组件

### `src/components/questionnaire/PVQForm.tsx`

```typescript
/**
 * PVQ-10 价值观问卷
 * 10个维度，每个1-7分（Likert量表）
 */

import React, { useState } from 'react';
import { ValsData } from '../../services/api';

interface PVQFormProps {
  values: ValsData;
  onChange: (values: ValsData) => void;
}

const PVQ_ITEMS = [
  { key: 'self_direction', label: '自主性', description: '独立思考和行动的自由' },
  { key: 'stimulation', label: '刺激性', description: '追求新鲜和刺激的体验' },
  { key: 'hedonism', label: '享乐主义', description: '追求快乐和感官满足' },
  { key: 'achievement', label: '成就', description: '展示个人能力和获得成功' },
  { key: 'power', label: '权力', description: '控制和影响他人的能力' },
  { key: 'security', label: '安全', description: '保障自己和亲人的安全' },
  { key: 'conformity', label: '顺从', description: '遵守规则和期待' },
  { key: 'tradition', label: '传统', description: '尊重和维护传统文化' },
  { key: 'benevolence', label: '仁慈', description: '关心他人的幸福' },
  { key: 'universalism', label: '普世', description: '理解、欣赏和包容所有人' },
];

export const PVQForm: React.FC<PVQFormProps> = ({ values, onChange }) => {
  const handleChange = (key: keyof ValsData, value: number) => {
    onChange({ ...values, [key]: value });
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">价值观问卷说明</h3>
        <p className="text-sm text-blue-700">
          请根据以下价值观对您的重要程度打分，1分表示"完全不重要"，7分表示"非常重要"
        </p>
      </div>

      {PVQ_ITEMS.map(({ key, label, description }) => (
        <div key={key} className="border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h4 className="font-medium text-gray-900">{label}</h4>
              <p className="text-sm text-gray-600">{description}</p>
            </div>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              {values[key as keyof ValsData] || 4}分
            </span>
          </div>

          <input
            type="range"
            min="1"
            max="7"
            step="1"
            value={values[key as keyof ValsData] || 4}
            onChange={(e) => handleChange(key as keyof ValsData, parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />

          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1 (不重要)</span>
            <span>4 (一般)</span>
            <span>7 (非常重要)</span>
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 🏠 F2.2 未来档案表单

### `src/components/future/FutureProfileForm.tsx`

```typescript
/**
 * F2.2 未来档案表单 (v1.3)
 * 3个文本框：价值观、愿景、障碍
 */

import React, { useState } from 'react';
import { FutureProfileItem } from '../../services/api';
import { Textarea } from '../common/Textarea';
import { Button } from '../common/Button';
import { validateFutureProfile } from '../../utils/validation';

interface FutureProfileFormProps {
  onSubmit: (profile: FutureProfileItem) => void;
  onCancel: () => void;
}

export const FutureProfileForm: React.FC<FutureProfileFormProps> = ({
  onSubmit,
  onCancel,
}) => {
  const [profile, setProfile] = useState<FutureProfileItem>({
    profile_name: '',
    future_values: '',
    future_vision: '',
    future_obstacles: '',
  });

  const [errors, setErrors] = useState<string[]>([]);

  const handleSubmit = () => {
    const validationErrors = validateFutureProfile(profile);
    
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setErrors([]);
    onSubmit(profile);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        创建未来人设
      </h2>

      <div className="space-y-6">
        {/* 人设名称 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            人设名称 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={profile.profile_name}
            onChange={(e) => setProfile({ ...profile, profile_name: e.target.value })}
            placeholder="例如：UX研究员"
            maxLength={100}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
        </div>

        {/* 模块一：价值观 */}
        <Textarea
          value={profile.future_values}
          onChange={(value) => setProfile({ ...profile, future_values: value })}
          label="模块一：价值观"
          placeholder="你希望这个未来职业能够带给你什么？你想要通过工作实现什么价值？"
          hint="至少50字，描述你对这个职业的价值期待"
          minLength={50}
          maxLength={2000}
          rows={6}
          required
        />

        {/* 模块二：愿景 */}
        <Textarea
          value={profile.future_vision}
          onChange={(value) => setProfile({ ...profile, future_vision: value })}
          label="模块二：愿景"
          placeholder="你理想的工作状态是什么样的？描述一下3年后你在这个职业中的日常生活..."
          hint="至少50字，具体描述你的理想状态"
          minLength={50}
          maxLength={2000}
          rows={6}
          required
        />

        {/* 模块三：障碍 */}
        <Textarea
          value={profile.future_obstacles}
          onChange={(value) => setProfile({ ...profile, future_obstacles: value })}
          label="模块三：障碍"
          placeholder="你担心什么可能阻碍你实现这个未来？有哪些内部或外部的挑战？"
          hint="至少50字，诚实地面对可能的困难"
          minLength={50}
          maxLength={2000}
          rows={6}
          required
        />
      </div>

      {/* 错误提示 */}
      {errors.length > 0 && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-medium text-red-800 mb-2">请修正以下错误：</h4>
          <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 按钮 */}
      <div className="flex gap-4 mt-8">
        <Button variant="outline" onClick={onCancel} className="flex-1">
          取消
        </Button>
        <Button onClick={handleSubmit} className="flex-1">
          创建人设
        </Button>
      </div>
    </div>
  );
};
```

---

## 💬 F3.2 聊天组件

### `src/components/chat/ChatBox.tsx`

```typescript
/**
 * F3.2 聊天组件
 * 支持：
 * - 历史消息展示
 * - 发送新消息
 * - 5条消息限制
 * - 自动滚动
 */

import React, { useState, useEffect, useRef } from 'react';
import { ChatMessageResponse, ChatMessageSend } from '../../services/api';
import { Button } from '../common/Button';

interface ChatBoxProps {
  futureProfileId: string;
  futureProfileName: string;
  userId: string;
  messages: ChatMessageResponse[];
  onSendMessage: (message: ChatMessageSend) => Promise<void>;
  maxMessages?: number;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
  futureProfileId,
  futureProfileName,
  userId,
  messages,
  onSendMessage,
  maxMessages = 5,
}) => {
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const userMessageCount = messages.filter(m => m.sender === 'USER').length;
  const canSendMore = userMessageCount < maxMessages;

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !canSendMore || isSending) return;

    setIsSending(true);

    try {
      await onSendMessage({
        user_id: userId,
        content: input.trim(),
      });
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('发送失败，请重试');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-[800px] bg-white rounded-2xl shadow-xl">
      {/* 头部 */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <h2 className="text-xl font-bold text-gray-900">
          与 {futureProfileName} 对话
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          已发送 {userMessageCount} / {maxMessages} 条消息
        </p>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.message_id}
            className={`flex ${message.sender === 'USER' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] px-4 py-3 rounded-2xl ${
                message.sender === 'USER'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              <p className={`text-xs mt-2 ${
                message.sender === 'USER' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {new Date(message.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="p-6 border-t border-gray-200">
        {!canSendMore ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <p className="text-yellow-800 font-medium">
              已达到{maxMessages}条消息限制
            </p>
            <p className="text-sm text-yellow-700 mt-1">
              系统正在为您生成总结报告...
            </p>
          </div>
        ) : (
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="输入你的问题..."
              disabled={isSending}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isSending}
              loading={isSending}
            >
              发送
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
```

---

## ✅ 后续开发步骤

1. **安装依赖**
   ```bash
   cd frontend
   npm install axios zustand
   ```

2. **创建组件**
   - 复制上述代码到对应文件
   - 确保所有import路径正确

3. **页面集成**
   - 在 `pages/` 目录下实现各页面
   - 使用路由连接各页面

4. **测试**
   - 启动后端: `cd backend && python -m uvicorn app.main:app --reload`
   - 启动前端: `cd frontend && npm run dev`
   - 测试完整流程

5. **样式优化**
   - 使用 Tailwind CSS
   - 确保响应式设计

---

## 📚 参考文档

- [API 接口文档 v1.5](../docs/API_v1.5.md)
- [数据库架构 v1.3](../docs/DATABASE_v1.3.md)
- [React 文档](https://react.dev/)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)
- [Tailwind CSS 文档](https://tailwindcss.com/)

---

**状态**: ✅ 核心组件已完成  
**版本**: v1.3  
**最后更新**: 2024-11-09

