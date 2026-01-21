---
title: 容器化项目配置
summary: 定义容器化项目（Docker/Kubernetes）的推荐子文档清单、特殊关注点和核心代码模式。包括 Dockerfile 说明、Docker Compose、K8s 部署等关键规范。
keywords: containerized | docker | kubernetes | k8s | dockerfile | compose | deployment
scope: 容器化项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 容器化项目

> **适用技术**: Docker / Kubernetes / Docker Compose

---

## 🎯 适用技术

- **Docker**: 容器化标准
- **Docker Compose**: 本地多容器编排
- **Kubernetes**: 生产级容器编排
- **Helm**: Kubernetes 包管理
- **Docker Swarm**: 轻量级编排（较少使用）

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `dockerfile_guide.md` | Dockerfile说明 |
| 🔴 高 | `docker_compose.md` | 本地开发环境 |
| 🟡 中 | `kubernetes.md` | K8s部署（如适用） |
| 🟡 中 | `ci_cd.md` | CI/CD流程 |

---

## 🔍 特殊关注点

### Dockerfile 最佳实践

- 使用多阶段构建
- 最小化层数
- 使用 .dockerignore
- 选择合适的基础镜像

### Docker Compose

- 服务定义
- 网络配置
- 卷挂载
- 环境变量

### Kubernetes 部署

- Deployment / StatefulSet
- Service / Ingress
- ConfigMap / Secret
- PersistentVolume

### CI/CD 集成

- 镜像构建
- 镜像推送
- 自动部署

---

## 💻 核心代码模式

### Dockerfile（多阶段构建）

```dockerfile
# 阶段1: 构建
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 阶段2: 运行
FROM node:18-alpine

WORKDIR /app

# 只复制必要的文件
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### .dockerignore

```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.env.local
dist
coverage
.vscode
.idea
*.md
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    volumes:
      - ./src:/app/src
      - /app/node_modules
    depends_on:
      - db
      - redis
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry/myapp:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  app.conf: |
    server {
      listen 80;
      server_name myapp.example.com;
    }

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  database-url: <base64-encoded-value>
  api-key: <base64-encoded-value>
```

### Helm Chart

```yaml
# Chart.yaml
apiVersion: v2
name: myapp
description: A Helm chart for MyApp
version: 1.0.0
appVersion: "1.0.0"

# values.yaml
replicaCount: 3

image:
  repository: myregistry/myapp
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

env:
  - name: NODE_ENV
    value: "production"

secrets:
  databaseUrl: ""
  apiKey: ""

# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 3000
        env:
        {{- range .Values.env }}
        - name: {{ .name }}
          value: {{ .value | quote }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

---

## ⚠️ 常见问题

### 问题 1: 镜像体积过大

**解决方案**: 使用多阶段构建和 Alpine 基础镜像

```dockerfile
# ❌ 错误：单阶段构建
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
CMD ["node", "dist/index.js"]

# ✅ 正确：多阶段构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 问题 2: 容器以 root 运行

**解决方案**: 创建非 root 用户

```dockerfile
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs
```

### 问题 3: 环境变量泄露

**解决方案**: 使用 Kubernetes Secrets

```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: myapp-secrets
      key: database-url
```

---

## 🎯 检查清单

生成容器化项目文档前，确认：

- [ ] 已创建 Dockerfile
- [ ] 已创建 .dockerignore
- [ ] 已创建 docker-compose.yml（本地开发）
- [ ] 已确定是否需要 Kubernetes 部署
- [ ] 已确定镜像仓库（Docker Hub/GHCR/ECR）
- [ ] 已确定 CI/CD 流程
- [ ] 已确定资源限制（CPU/内存）
- [ ] 已确定健康检查配置
- [ ] 已确定环境变量和 Secret 管理

---

**版本**: v3.0  
**路径**: `core/project_types/containerized.md`  
**最后更新**: 2026-01-21
