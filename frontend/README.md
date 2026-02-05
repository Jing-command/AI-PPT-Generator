# AI PPT Generator - Frontend

基于 React + TypeScript + Tailwind CSS 的 AI PPT 生成器前端。

## 🚀 功能特性

- **用户认证**: JWT 登录/注册
- **PPT 管理**: 创建、编辑、删除
- **AI 生成**: 对话式生成 PPT
- **单页编辑**: 独立幻灯片编辑
- **撤销/重做**: 操作历史
- **导出下载**: PPTX/PDF/图片
- **模板系统**: 预设模板选择

## 🛠 技术栈

- **框架**: React 18 + TypeScript
- **构建**: Vite
- **样式**: Tailwind CSS
- **状态**: Zustand
- **路由**: React Router v6
- **HTTP**: Axios
- **UI 组件**: Headless UI
- **图标**: Lucide React

## 📦 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 📁 项目结构

```
src/
├── components/          # UI 组件
│   ├── common/         # 通用组件
│   ├── auth/           # 认证相关
│   ├── ppt/            # PPT 相关
│   └── editor/         # 编辑器相关
├── pages/              # 页面
├── hooks/              # 自定义 Hooks
├── stores/             # Zustand 状态
├── services/           # API 服务
├── utils/              # 工具函数
├── types/              # TypeScript 类型
└── App.tsx             # 应用入口
```

## 🔑 环境变量

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📄 许可证

MIT
