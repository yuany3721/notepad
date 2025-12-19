# Vue3 + Python Notepad 应用

一个简单的在线文本编辑器，支持实时自动保存和文件管理。

## 功能特性

- ✅ 实时文本编辑与自动保存
- ✅ URL驱动的文件访问
- ✅ 文件列表管理（需口令验证）
- ✅ WebSocket实时通信
- ✅ 响应式设计
- ✅ 文件大小限制（10万字符）
- ✅ 文件名验证与安全过滤

## 技术栈

- **前端**: Vue 3, TypeScript, Vite, Pinia, Vue Router
- **后端**: Python, FastAPI, WebSocket

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- pnpm 8+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd vue-python-notepad
```

2. **安装依赖**
```bash
# 安装前端依赖
cd frontend && pnpm install && cd ..

# 设置Python虚拟环境并安装后端依赖
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

3. **配置环境变量**
```bash
# 复制环境变量模板
cp backend/.env.example .env

# 编辑.env文件，设置必要的环境变量
```

4. **启动开发服务器**

**方法一：分别启动**
```bash
# 启动后端服务器（终端1）
cd backend
venv\Scripts\activate  # Windows
python main.py

# 启动前端开发服务器（终端2）
cd frontend
pnpm dev
```

**方法二：同时启动**
```bash
# 在项目根目录
pnpm dev
```

5. **访问应用**
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 使用说明

### 基本操作

1. **创建/编辑文件**
   - 访问 `http://localhost:5173/notes/filename.txt`
   - 如果文件不存在，会自动创建
   - 输入内容会自动保存（500ms延迟）

2. **文件列表**
   - 访问 `http://localhost:5173/file-list`
   - 输入口令（默认：your_secure_password）
   - 查看和管理所有文件

3. **URL分享**
   - 直接分享文件URL给他人
   - 例如：`http://localhost:5173/notes/shared-note.txt`

### 环境变量配置

```bash
# 前端环境变量
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws

# 后端环境变量
NOTES_DIR=./data/notes                    # 文件存储目录
FILE_LIST_PASSWORD=your_secure_password    # 文件列表访问口令
JWT_SECRET_KEY=your_jwt_secret_key        # JWT密钥
JWT_EXPIRE_HOURS=24                       # 令牌过期时间
```

## 项目结构

```
vue-python-notepad/
├── frontend/              # Vue3前端应用
│   ├── src/
│   │   ├── components/    # UI组件
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # 状态管理
│   │   ├── services/      # API服务
│   │   └── router/        # 路由配置
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI后端应用
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── utils/         # 工具函数
│   ├── main.py
│   └── requirements.txt
├── docs/                  # 项目文档
├── package.json           # 根配置文件
└── README.md
```

## 开发指南

### 添加新功能

1. **前端组件**
   - 在 `frontend/src/components/` 中创建组件
   - 在 `frontend/src/views/` 中创建页面
   - 使用 Pinia 管理状态

2. **后端API**
   - 在 `backend/src/api/` 中添加路由
   - 在 `backend/src/services/` 中实现业务逻辑
   - 在 `backend/src/models/` 中定义数据模型

### 测试

```bash
# 运行前端测试
pnpm test:frontend

# 运行后端测试
pnpm test:backend

# 运行所有测试
pnpm test
```

### 构建部署

```bash
# 构建前端
pnpm build

# 生产环境启动
cd backend
venv\Scripts\activate  # Windows
python main.py
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保8000和5173端口未被占用
   - 或修改配置文件中的端口设置

2. **Python依赖问题**
   - 确保使用Python 3.10+
   - 激活虚拟环境后安装依赖

3. **前端代理错误**
   - 检查 `frontend/vite.config.ts` 中的代理配置
   - 确保后端服务器正在运行

4. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认WebSocket URL正确

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License