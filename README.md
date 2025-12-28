# Vue3 + Python Notepad 应用

一个简单的在线文本编辑器，支持实时自动保存和文件管理。

## 功能特性

- ✅ 实时文本编辑与自动保存
- ✅ URL驱动的文件访问
- ✅ 文件列表管理（需口令验证）
- ✅ WebSocket实时通信
- ✅ 响应式设计
- ✅ 文件大小限制（100KB）
- ✅ 文件名验证与安全过滤
- ✅ 统一容器部署

## 技术栈

- **前端**: Vue 3, TypeScript, Vite, Pinia, Vue Router
- **后端**: Python 3.12, FastAPI, WebSocket
- **部署**: Docker, Nginx, Supervisor

## 快速开始

### Docker 部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd notepad
```

2. **配置环境变量**
```bash
cp .env.example .env
```

3. **启动服务**
```bash
docker compose up -d
```

4. **访问应用**
- 应用地址: http://localhost:7024
- 默认密码: `your_secure_password_change_this`

### 开发环境

1. **安装依赖**
```bash
# 前端
cd frontend && pnpm install && cd ..

# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd ..
```

2. **启动服务**
```bash
# 后端
cd backend && source venv/bin/activate && python main.py

# 前端（新终端）
cd frontend && pnpm dev
```

## 使用说明

### 基本操作

1. **创建/编辑文件**
   - 访问 `http://localhost:7024/notes/filename.txt`
   - 文件不存在时自动创建
   - 内容自动保存

2. **文件列表管理**
   - 访问 `http://localhost:7024/file-list`
   - 输入口令验证
   - 查看、重命名、删除文件

3. **URL分享**
   - 直接分享文件URL
   - 例如：`http://localhost:7024/notes/shared-note.txt`

### 环境变量配置

```bash
# 应用配置
PORT=7024                              # 容器对外端口
FILE_LIST_PASSWORD=your_password        # 文件列表访问密码

# 文件存储
NOTES_DIR=./data             # 容器外映射存储路径
```

## 项目结构

```
notepad/
├── frontend/              # Vue3前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── services/      # API服务
│   │   └── stores/        # 状态管理
│   └── package.json
├── backend/               # FastAPI后端
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   └── requirements.txt
├── docker/                # Docker配置
│   ├── nginx.conf
│   ├── default.conf
│   └── supervisord.conf
├── docker-compose.yml     # 容器编排
├── Dockerfile             # 统一构建文件
└── README.md
```

## 部署架构

### 容器架构
- **Nginx**: 静态文件服务 + API代理 + WebSocket代理
- **Python FastAPI**: API服务 + WebSocket服务
- **Supervisor**: 进程管理

### 网络流程
```
用户请求 → Nginx(80) → 后端(7025)
                ↓
           前端静态文件
```

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   docker compose down
   docker compose up -d --build
   ```

2. **文件不持久化**
   - 检查 `.env` 中的 `NOTES_DIR` 配置
   - 确认数据目录权限

3. **WebSocket连接失败**
   - 检查 Nginx 配置
   - 确认防火墙设置

4. **端口冲突**
   - 修改 `.env` 中的 `PORT` 变量

## 许可证

MIT License