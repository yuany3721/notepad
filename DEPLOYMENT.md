# 生产环境部署指南

## 安全配置步骤

### 1. 配置环境变量

复制环境变量模板并修改敏感信息：

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，修改以下敏感配置：
nano .env
```

**必须修改的配置：**
- `FILE_LIST_PASSWORD` - 设置强密码（建议使用随机生成的密码）
- `JWT_SECRET_KEY` - 设置随机密钥（建议使用 32 位以上随机字符串）

**生成强密码和密钥的方法：**
```bash
# 生成密码
openssl rand -base64 32

# 生成 JWT 密钥
openssl rand -hex 32
```

### 2. 文件权限设置

```bash
# 创建文件目录
mkdir -p files

# 设置适当的权限
chmod 755 files
```

### 3. 部署到服务器

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件...

# 构建并启动
docker-compose up -d --build
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试 API
curl http://localhost/api/health
```

## 环境变量说明

| 变量名 | 说明 | 默认值 | 是否必须修改 |
|--------|------|--------|------------|
| `FILE_LIST_PASSWORD` | 文件列表访问密码 | admin123 | **是** |
| `JWT_SECRET_KEY` | JWT 签名密钥 | your-secret-key | **是** |
| `NOTES_DIR` | 文件存储目录 | /app/data | 否 |
| `MAX_FILE_SIZE` | 最大文件大小（字节） | 100000 | 否 |
| `JWT_EXPIRE_MINUTES` | JWT 过期时间（分钟） | 1440 | 否 |

## 安全建议

1. **定期更换密码**
   - 建议每 3 个月更换一次 `FILE_LIST_PASSWORD`
   - 每年更换一次 `JWT_SECRET_KEY`

2. **使用 HTTPS**
   - 配置反向代理（Nginx/Traefik）
   - 申请 SSL 证书（Let's Encrypt）

3. **备份策略**
   - 定期备份 `./files` 目录
   - 备份 `.env` 文件（存储在安全位置）

4. **监控**
   - 监控容器资源使用
   - 设置日志轮转
   - 配置告警机制

## 故障排除

1. **密码错误**
   - 检查 `.env` 文件中的 `FILE_LIST_PASSWORD`
   - 重启容器：`docker-compose restart backend`

2. **JWT 错误**
   - 检查 `.env` 文件中的 `JWT_SECRET_KEY`
   - 清除浏览器 localStorage 中的 token

3. **权限问题**
   - 确保 `files` 目录有写权限
   - 检查 Docker 容器用户权限