# ETF网格设计系统 - 前端

## 项目结构

```
frontend/src/
├── app/                          # 应用程序级配置
│   ├── AppRouter.jsx            # 路由配置
│   ├── AppLayout.jsx            # 布局组件
│   ├── AppHeader.jsx            # 头部组件
│   └── AppFooter.jsx            # 底部组件
├── pages/                       # 页面级组件
│   ├── HomePage/                # 首页
│   └── AnalysisPage/            # 分析页面
├── features/                    # 业务功能模块
│   ├── analysis/                # 分析功能
│   ├── etf/                     # ETF相关功能
│   └── history/                 # 历史记录功能
├── shared/                      # 共享资源
│   ├── components/              # 通用组件
│   ├── hooks/                   # 自定义Hooks
│   ├── utils/                   # 工具函数
│   ├── services/                # API服务
│   └── constants/               # 常量定义
└── assets/                      # 静态资源
```

## 开发规范

### 导入路径
- 使用别名路径：`@shared/utils`, `@features/analysis`
- 避免复杂的相对路径：`../../../shared/utils`

### 组件规范
- 每个组件文件包含单一组件
- 使用JSDoc注释描述组件功能
- Props使用PropTypes或TypeScript定义

### 代码风格
- 使用Prettier进行代码格式化
- 遵循ESLint规则
- 统一的文件命名：PascalCase for components, camelCase for utils

## 开发脚本

```bash
# 开发服务器
npm run dev

# 构建项目
npm run build

# 代码检查
npm run lint

# 自动修复代码问题
npm run lint:fix

# 代码格式化
npm run format

# 检查未使用的导入
npm run check-unused

# 清理构建缓存
npm run clean
```

## 技术栈

- **框架**: React 18
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **路由**: React Router DOM
- **图标**: Lucide React
- **代码质量**: ESLint + Prettier

## 项目特点

- 🏗️ 模块化架构设计
- 📱 响应式布局
- 🎯 组件化开发
- 🔧 类型安全
- 🚀 高性能构建
- 📊 代码质量保证

## 开发指南

1. **组件开发**: 遵循单一职责原则，每个组件专注一个功能
2. **状态管理**: 使用React Hooks进行状态管理
3. **API调用**: 通过共享服务进行API调用
4. **错误处理**: 统一的错误处理机制
5. **性能优化**: 使用React.memo和useCallback优化性能

## 部署

项目支持多种部署方式：
- 静态文件部署
- Docker容器部署
- CDN加速部署

## 贡献指南

请遵循项目代码规范和开发流程，确保代码质量和可维护性。