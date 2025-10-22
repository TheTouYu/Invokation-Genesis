# 项目概述

这是一个《原神》七圣召唤卡牌游戏的前端实现，采用 Next.js v15.2.4 和 React v19 技术栈构建。项目使用 TypeScript 进行类型安全开发，并集成 Tailwind CSS 作为样式框架，通过 shadcn/ui 组件库提供可复用的 UI 组件。

## 项目结构

```
frontend/
├── app/                 # Next.js 13+ App Router 目录
│   ├── globals.css      # 全局样式和 Tailwind 配置
│   ├── layout.tsx       # 根布局组件
│   └── page.tsx         # 首页组件
├── components/          # 可复用的 React 组件
│   └── ui/              # shadcn/ui 组件
├── hooks/               # 自定义 React hooks
├── lib/                 # 工具函数和共享逻辑
├── public/              # 静态资源
├── styles/              # 样式相关文件
├── package.json         # 项目依赖配置
├── next.config.mjs      # Next.js 配置文件
├── tsconfig.json        # TypeScript 配置
├── postcss.config.mjs   # PostCSS 配置
├── tailwind.config.ts   # Tailwind CSS 配置
└── components.json      # shadcn/ui 配置文件
```

## 技术栈

- **框架**: Next.js 15.2.4 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS, CSS Variables
- **UI 库**: shadcn/ui, Radix UI
- **图标**: Lucide React
- **表单处理**: React Hook Form
- **动画**: Tailwind CSS Animate

## 构建与运行

项目提供了标准的 Next.js 命令用于开发和生产构建：

```bash
# 安装依赖 (使用 pnpm)
pnpm install

# 开发模式运行
pnpm dev

# 生产构建
pnpm build

# 启动生产服务器
pnpm start

# 代码检查
pnpm lint
```

## 开发规范

1. **组件**: 使用 TypeScript 编写，遵循 React 最佳实践
2. **样式**: 使用 Tailwind CSS 类进行样式编写，避免内联样式
3. **可访问性**: 利用 Radix UI 组件确保良好的可访问性
4. **国际化**: 项目使用中文，但保留了多语言扩展的能力

## 设计主题

项目采用深色主题设计，以游戏风格的紫色和蓝色为主色调。CSS 配置使用 oklch 颜色空间定义了一系列主题变量，确保在深色模式下提供良好的视觉体验。

## 已实现功能

- **首页**: 介绍七圣召唤游戏特点的主页，包含功能亮点和导航按钮
- **认证流程**: 包含登录和注册页面入口（尚未实现具体功能）
- **响应式设计**: 支持不同屏幕尺寸的响应式布局

## 后续开发

此前端项目通常与后端 API 服务配合使用，实现完整的卡牌对战功能。后续开发可能包括：

- 游戏大厅和匹配功能
- 卡牌浏览和卡组构建
- 实时对战界面
- 用户个人中心
- 游戏历史记录