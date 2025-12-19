# Vue3 + Python Notepad Docker 部署指南

## 快速开始

### 前提条件
- Docker
- Docker Compose

### 部署步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd bmadtest
```

2. **构建并启动服务**
```bash
docker-compose up -d --build
```

3. **访问应用**
- 前端：http://localhost
- API：http://localhost/api
- WebSocket：ws://localhost/ws

### 常用命令

**查看服务状态**
```bash
docker-compose ps
```

**查看日志**
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
```

**停止服务**
```bash
docker-compose down
```

**重新构建并启动**
```bash
docker-compose up -d --build
```

### 数据持久化

文件数据存储在 `./files/notes/` 目录下。确保在宿主机上备份此目录以防止数据丢失。

### 环境变量配置

如需自定义配置，可以在 `docker-compose.yml` 中修改环境变量：

```yaml
environment:
  - PYTHONPATH=/app
  - PYTHONUNBUFFERED=1
  # 其他环境变量...
```

### 端口配置

默认端口配置：
- 前端：80
- 后端：8000（容器内部）

如需修改前端端口，编辑 `docker-compose.yml` 中的 ports 配置：
```yaml
ports:
  - "8080:80"  # 将宿主机的 8080 端口映射到容器的 80 端口
```

### 故障排除

1. **端口被占用**
   - 修改 docker-compose.yml 中的端口映射
   - 或停止占用端口的服务

2. **权限问题**
   - 确保 `./files` 目录有适当的写权限
   - 运行：`chmod -R 755 ./files`

3. **构建失败**
   - 清理 Docker 缓存：`docker system prune -a`
   - 重新构建：`docker-compose build --no-cache`

### 生产环境建议

1. **使用 HTTPS**
   - 配置 SSL 证书
   - 使用反向代理（如 Traefik 或 Nginx）

2. **安全配置**
   - 修改默认密码
   - 限制 API 访问频率
   - 使用防火墙

3. **监控**
   - 配置日志收集
   - 设置健康检查
   - 监控资源使用情况

4. **备份**
   - 定期备份 `./files` 目录
   - 考虑使用云存储