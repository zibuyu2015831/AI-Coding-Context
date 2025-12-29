# 项目重要文件优先级参考

## 📋 说明

此文档定义了项目扫描工具在应用省略策略时，应该优先保留的重要文件列表。
这些文件对于理解项目结构、配置和入口点至关重要。

---

## 🎯 重要文件分类

### 1. 项目根配置文件 (最高优先级)

#### 通用项目文件

- `README.md` / `README.rst` / `README.txt` - 项目说明文档
- `LICENSE` / `LICENSE.md` / `LICENSE.txt` - 许可证文件
- `CHANGELOG.md` / `CHANGELOG.txt` - 变更日志
- `.gitignore` - Git 忽略规则
- `.editorconfig` - 编辑器配置

#### 文档文件

- `CONTRIBUTING.md` - 贡献指南
- `CODE_OF_CONDUCT.md` - 行为准则
- `SECURITY.md` - 安全政策

---

### 2. 语言特定配置文件

#### JavaScript / TypeScript / Node.js

**配置文件**:

- `package.json` - NPM 包配置 (最重要)
- `package-lock.json` - 依赖锁定
- `yarn.lock` / `pnpm-lock.yaml` - 其他包管理器锁定
- `tsconfig.json` - TypeScript 配置
- `jsconfig.json` - JavaScript 配置
- `.npmrc` / `.yarnrc` - 包管理器配置

**构建工具**:

- `webpack.config.js` - Webpack 配置
- `vite.config.js` / `vite.config.ts` - Vite 配置
- `rollup.config.js` - Rollup 配置
- `babel.config.js` / `.babelrc` - Babel 配置
- `next.config.js` - Next.js 配置
- `nuxt.config.js` - Nuxt.js 配置
- `vue.config.js` - Vue CLI 配置

**代码质量**:

- `.eslintrc.js` / `.eslintrc.json` - ESLint 配置
- `.prettierrc` / `.prettierrc.js` - Prettier 配置
- `jest.config.js` - Jest 测试配置
- `vitest.config.ts` - Vitest 测试配置

**入口文件**:

- `index.js` / `index.ts` - 通用入口
- `main.js` / `main.ts` - 主入口
- `app.js` / `app.ts` - 应用入口
- `server.js` / `server.ts` - 服务端入口

#### Python

**配置文件**:

- `setup.py` - Python 包安装配置
- `setup.cfg` - Setup 配置
- `pyproject.toml` - 现代 Python 项目配置
- `requirements.txt` - 依赖列表
- `Pipfile` / `Pipfile.lock` - Pipenv 配置
- `poetry.lock` / `pyproject.toml` - Poetry 配置
- `environment.yml` - Conda 环境配置

**代码质量**:

- `.flake8` - Flake8 配置
- `.pylintrc` - Pylint 配置
- `mypy.ini` / `.mypy.ini` - MyPy 类型检查
- `pytest.ini` - Pytest 配置
- `tox.ini` - Tox 测试配置

**入口文件**:

- `__init__.py` - 包初始化
- `__main__.py` - 主入口
- `main.py` - 主程序
- `app.py` - 应用入口
- `manage.py` - Django 管理入口
- `wsgi.py` / `asgi.py` - Web 服务器网关

#### Java / Kotlin

**配置文件**:

- `pom.xml` - Maven 配置
- `build.gradle` / `build.gradle.kts` - Gradle 配置
- `settings.gradle` - Gradle 设置
- `gradlew` / `gradlew.bat` - Gradle Wrapper
- `application.properties` - Spring Boot 配置
- `application.yml` / `application.yaml` - Spring Boot YAML 配置

**入口文件**:

- `Application.java` - Spring Boot 应用入口
- `Main.java` - 主类

#### Go

**配置文件**:

- `go.mod` - Go 模块定义
- `go.sum` - Go 依赖校验和
- `Makefile` - 构建脚本

**入口文件**:

- `main.go` - 主入口

#### Rust

**配置文件**:

- `Cargo.toml` - Rust 包配置
- `Cargo.lock` - 依赖锁定

**入口文件**:

- `main.rs` - 主入口
- `lib.rs` - 库入口

#### C / C++

**配置文件**:

- `CMakeLists.txt` - CMake 配置
- `Makefile` - Make 构建配置
- `configure` / `configure.ac` - Autoconf 配置
- `meson.build` - Meson 构建配置

**入口文件**:

- `main.c` / `main.cpp` - 主入口

#### Ruby

**配置文件**:

- `Gemfile` - Gem 依赖
- `Gemfile.lock` - Gem 锁定
- `Rakefile` - Rake 任务

**入口文件**:

- `config.ru` - Rack 应用配置

#### PHP

**配置文件**:

- `composer.json` - Composer 配置
- `composer.lock` - Composer 锁定

**入口文件**:

- `index.php` - 入口文件

---

### 3. 框架特定文件

#### React

- `App.tsx` / `App.jsx` - React 应用根组件
- `index.tsx` / `index.jsx` - React 入口

#### Vue

- `App.vue` - Vue 应用根组件
- `main.js` / `main.ts` - Vue 入口

#### Angular

- `angular.json` - Angular 配置
- `app.module.ts` - 应用模块
- `main.ts` - 入口文件

#### Django

- `settings.py` - Django 设置
- `urls.py` - URL 路由
- `wsgi.py` - WSGI 配置

#### Flask

- `app.py` / `application.py` - Flask 应用

#### Spring Boot

- `application.properties` / `application.yml` - 配置文件

---

### 4. 容器化和部署

#### Docker

- `Dockerfile` - Docker 镜像定义
- `docker-compose.yml` - Docker Compose 配置
- `.dockerignore` - Docker 忽略规则

#### Kubernetes

- `deployment.yaml` / `deployment.yml` - K8s 部署配置
- `service.yaml` / `service.yml` - K8s 服务配置

#### CI/CD

- `.github/workflows/*.yml` - GitHub Actions
- `.gitlab-ci.yml` - GitLab CI
- `Jenkinsfile` - Jenkins 流水线
- `.travis.yml` - Travis CI
- `azure-pipelines.yml` - Azure Pipelines

---

### 5. 环境配置

- `.env` - 环境变量
- `.env.example` / `.env.sample` - 环境变量示例
- `.env.local` / `.env.development` / `.env.production` - 环境特定配置

---

## 🏆 优先级定义

### 优先级 1 (最高 - 必须保留)

- README.md
- package.json / setup.py / pom.xml / Cargo.toml / go.mod (语言主配置)
- Dockerfile
- LICENSE

### 优先级 2 (高 - 强烈建议保留)

- tsconfig.json / pyproject.toml / build.gradle
- index._ / main._ / app.\* (入口文件)
- .gitignore
- CHANGELOG.md

### 优先级 3 (中 - 建议保留)

- webpack.config.js / vite.config.ts (构建配置)
- .eslintrc.\* / .prettierrc (代码质量)
- jest.config.js / pytest.ini (测试配置)
- docker-compose.yml

### 优先级 4 (低 - 可省略)

- 锁定文件 (package-lock.json, yarn.lock 等)
- .editorconfig
- 其他辅助配置文件

---

## 💻 实现参考

### Python 实现示例

```python
# 重要文件优先级映射
IMPORTANT_FILES = {
    # 优先级 1 (最高)
    'README.md': 1,
    'README.rst': 1,
    'LICENSE': 1,
    'LICENSE.md': 1,

    # JavaScript/TypeScript
    'package.json': 1,
    'tsconfig.json': 2,

    # Python
    'setup.py': 1,
    'pyproject.toml': 1,
    'requirements.txt': 2,

    # Java
    'pom.xml': 1,
    'build.gradle': 1,

    # Go
    'go.mod': 1,

    # Rust
    'Cargo.toml': 1,

    # Docker
    'Dockerfile': 1,
    'docker-compose.yml': 2,

    # Git
    '.gitignore': 2,

    # 文档
    'CHANGELOG.md': 2,
    'CONTRIBUTING.md': 3,
}

# 重要文件模式
IMPORTANT_PATTERNS = [
    r'^index\.(js|ts|jsx|tsx|py|php)$',  # 入口文件
    r'^main\.(js|ts|go|rs|c|cpp)$',      # 主文件
    r'^app\.(js|ts|jsx|tsx|py)$',        # 应用文件
    r'^__init__\.py$',                    # Python 包
    r'^__main__\.py$',                    # Python 主入口
    r'\.config\.(js|ts)$',                # 配置文件
    r'^\.env',                            # 环境配置
]

def get_file_priority(filename):
    """
    获取文件优先级
    返回: (priority, filename) 元组，priority 越小优先级越高
    """
    # 检查精确匹配
    if filename in IMPORTANT_FILES:
        return (IMPORTANT_FILES[filename], filename)

    # 检查模式匹配
    import re
    for pattern in IMPORTANT_PATTERNS:
        if re.match(pattern, filename):
            return (2, filename)  # 模式匹配的文件为优先级 2

    # 普通文件
    return (100, filename)

def sort_files_by_importance(files):
    """按重要性排序文件列表"""
    return sorted(files, key=get_file_priority)
```

---

## 📝 使用说明

1. **扫描工具集成**: 项目扫描工具应该使用此优先级列表来决定哪些文件优先显示
2. **动态扩展**: 可以根据检测到的项目类型动态添加重要文件
3. **用户自定义**: 应允许用户通过配置文件自定义重要文件列表

---

**文档版本**: v1.0  
**更新日期**: 2025-12-21  
**维护**: AI Coding Context Framework
