# FutureSelf Frontend

未来自我项目的前端应用，基于 React 18 + TypeScript + Vite。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **数据获取**: TanStack Query (React Query)
- **表单**: React Hook Form + Zod
- **样式**: Tailwind CSS
- **图标**: Lucide React

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── main.tsx        # 应用入口
│   ├── App.tsx         # 根组件
│   ├── index.css       # 全局样式
│   ├── pages/          # 页面组件
│   │   ├── HomePage.tsx              # F6.1: 首页
│   │   ├── OnboardingPage.tsx        # 入职引导
│   │   ├── ProfileQuestionnairePage.tsx  # F2.1: 问卷
│   │   ├── FutureProfilePage.tsx     # F2.2: 创建人设
│   │   ├── WriteLetterPage.tsx       # F3.1.2: 写信
│   │   ├── InboxPage.tsx             # F6.5: 收信箱
│   │   ├── LetterReplyPage.tsx       # F3.1.3: 读信
│   │   ├── ChatPage.tsx              # F3.2.2: 聊天
│   │   └── ReportPage.tsx            # F5.2: 报告
│   ├── stores/         # Zustand 状态管理
│   │   └── userStore.ts  # F1.1: 用户状态
│   ├── components/     # 可复用组件
│   ├── hooks/          # 自定义 Hooks
│   ├── services/       # API 服务
│   ├── types/          # TypeScript 类型
│   └── utils/          # 工具函数
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 快速开始

### 1. 安装依赖

```bash
npm install
# 或
pnpm install
```

### 2. 配置环境变量

创建 `.env.local` 文件:

```bash
VITE_API_URL=http://localhost:8000
VITE_APP_ENV=development
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

## 核心功能模块

### 1. 用户管理 (F1.1)
- **Store**: `userStore.ts`
- 匿名用户初始化
- localStorage 持久化
- 路由守卫 (ONBOARDING vs ACTIVE)

### 2. 入职流程
- **OnboardingPage**: 引导页面
- **ProfileQuestionnairePage**: F2.1 当前档案问卷
- **FutureProfilePage**: F2.2 创建1-3个未来人设

### 3. 核心交互
- **WriteLetterPage**: F3.1.2 写信（异步提交）
- **InboxPage**: F6.5 + F6.6 收信箱（轮询状态）
- **LetterReplyPage**: F3.1.3 阅读回信
- **ChatPage**: F3.2.2 实时聊天（5条限制）

### 4. 洞见报告
- **ReportPage**: F5.1 + F5.3 + F5.2 生成并查看 WOOP 报告

### 5. 导航
- **HomePage**: F6.1 简化首页（写信 + 收信箱）
- **Reset**: F6.7 重置会话（仅开发环境）

## 核心流程

### 用户旅程
```
1. App.tsx 初始化 → userStore.initializeUser()
2. 根据 status 路由:
   - ONBOARDING → /onboarding
   - ACTIVE → /
3. 完整流程:
   入职 → 问卷 → 创建人设 → 写信 → 等待回信 → 阅读 → 聊天(5条) → 查看报告
```

### 状态管理 (Zustand)
```typescript
// userStore
{
  userId: string | null
  status: 'ONBOARDING' | 'ACTIVE' | null
  initializeUser: () => Promise<void>  // F1.1
  reset: () => void                    // F6.7
}
```

### 轮询机制
- **F6.6**: 回信状态轮询（3-5秒间隔）
- **F5.3**: 报告状态轮询（5秒间隔）

## 开发规范

### 代码风格
```bash
# ESLint
npm run lint

# TypeScript 类型检查
tsc --noEmit
```

### 组件规范
- 使用函数组件 + Hooks
- Props 使用 TypeScript 接口
- 组件文件使用 PascalCase (e.g., `HomePage.tsx`)

### API 调用
- 使用 TanStack Query 进行数据获取
- Axios 实例配置在 `services/api.ts`
- 错误处理统一在拦截器中

## 构建与部署

### 构建生产版本
```bash
npm run build
```

输出目录: `dist/`

### 预览生产构建
```bash
npm run preview
```

### 部署到 Vercel
```bash
# 方式1: 连接 GitHub 仓库自动部署
# 方式2: 使用 Vercel CLI
npx vercel --prod
```

环境变量配置:
- `VITE_API_URL`: 后端 API 地址（生产环境）
- `VITE_APP_ENV`: `production`

## 关键依赖说明

- **react-router-dom**: 客户端路由
- **zustand**: 轻量级状态管理（替代 Redux）
- **@tanstack/react-query**: 异步状态管理和缓存
- **react-hook-form**: 高性能表单库
- **zod**: TypeScript-first 表单验证
- **axios**: HTTP 客户端
- **lucide-react**: 图标库

## 常见问题

### Q: API 请求 CORS 错误?
A: 确保后端配置了正确的 CORS_ORIGINS，包含前端地址。

### Q: localStorage 数据持久化失败?
A: 检查浏览器是否禁用了 localStorage，或清空缓存重试。

### Q: 页面刷新后状态丢失?
A: Zustand persist 中间件已配置，检查 `localStorage.getItem('user-storage')`。

## 许可证

MIT License

