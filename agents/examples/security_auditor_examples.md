# 安全审计员角色使用示例

**角色**: 安全审计员 (Security Auditor)  
**文档**: [security_auditor.md](../runtime/security_auditor.md)

---

## 📋 目录

- [示例 1: 审计登录接口安全性](#示例1-审计登录接口安全性)
- [示例 2: 审计文件上传功能](#示例2-审计文件上传功能)

---

## 示例 1: 审计登录接口安全性

### 场景说明

审计用户登录接口的安全性,识别潜在漏洞。

### 用户输入

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query).fetchone()

    if user:
        session['user_id'] = user['id']
        return redirect('/dashboard')
    else:
        return "登录失败", 401
```

### 角色响应

````markdown
# 安全审计报告

## 🚨 高危漏洞

### 1. SQL 注入 (CWE-89) - 严重

**风险等级**: 高危  
**CVSS 评分**: 9.8

**漏洞描述**:
直接拼接用户输入到 SQL 语句,存在 SQL 注入风险。

**攻击示例**:

```python
username = "admin' --"
password = "anything"
# 生成SQL: SELECT * FROM users WHERE username='admin' --' AND password='anything'
# 结果: 绕过密码验证
```

**修复方案**:

```python
# 使用参数化查询
query = "SELECT * FROM users WHERE username=? AND password=?"
user = db.execute(query, (username, password)).fetchone()
```

---

### 2. 明文存储密码 (CWE-256) - 严重

**风险等级**: 高危

**问题**: 密码未加密,数据库泄露将导致所有用户密码泄露

**修复方案**:

```python
import bcrypt

# 注册时
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
           (username, password_hash))

# 登录时
user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
if user and bcrypt.checkpw(password.encode(), user['password_hash']):
    # 登录成功
```

---

### 3. 缺少登录失败限制 (CWE-307) - 中危

**风险等级**: 中危

**问题**: 允许无限次登录尝试,易被暴力破解

**修复方案**:

```python
# 使用Redis记录失败次数
def check_login_attempts(username):
    key = f"login_attempts:{username}"
    attempts = redis.get(key) or 0

    if int(attempts) >= 5:
        raise Exception("账号已锁定30分钟")

def record_failed_login(username):
    key = f"login_attempts:{username}"
    redis.incr(key)
    redis.expire(key, 1800)  # 30分钟过期
```

---

## ⚠️ 中危问题

### 4. Session 固定攻击

**问题**: 登录后未重新生成 Session ID

**修复**:

```python
if user:
    session.regenerate()  # 重新生成Session ID
    session['user_id'] = user['id']
```

---

## 📋 修复后的安全代码

```python
import bcrypt
from flask import request, session, redirect
from functools import wraps

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.form.get('username', '')
        key = f"login_attempts:{username}"
        attempts = int(redis.get(key) or 0)

        if attempts >= 5:
            return "账号已锁定,请30分钟后重试", 429

        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
@rate_limit
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        return "用户名和密码不能为空", 400

    # 参数化查询,防止SQL注入
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user and bcrypt.checkpw(password.encode(), user['password_hash']):
        # 登录成功
        session.regenerate()  # 防止Session固定攻击
        session['user_id'] = user['id']
        redis.delete(f"login_attempts:{username}")  # 清除失败记录
        return redirect('/dashboard')
    else:
        # 登录失败
        redis.incr(f"login_attempts:{username}")
        redis.expire(f"login_attempts:{username}", 1800)
        return "用户名或密码错误", 401
```
````

### 关键点说明

- ✅ **漏洞分级**: 高危/中危/低危
- ✅ **CWE 编号**: 标准漏洞分类
- ✅ **攻击示例**: 展示如何利用漏洞
- ✅ **完整修复**: 提供安全的完整实现

---

## 示例 2: 审计文件上传功能

### 场景说明

审计文件上传功能的安全性。

### 用户输入

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(f'/uploads/{filename}')
    return "上传成功"
```

### 角色响应

````markdown
# 文件上传安全审计

## 🚨 高危漏洞

### 1. 任意文件上传 (CWE-434) - 严重

**风险**: 攻击者可上传 webshell,获取服务器控制权

**攻击示例**:

```python
# 上传shell.php
<?php system($_GET['cmd']); ?>
# 访问: /uploads/shell.php?cmd=ls
```

**修复方案**:

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    # 1. 检查文件类型
    if not allowed_file(file.filename):
        return "不允许的文件类型", 400

    # 2. 使用安全的文件名
    filename = secure_filename(file.filename)

    # 3. 生成随机文件名
    import uuid
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"

    # 4. 保存到安全目录(非web可访问)
    filepath = os.path.join('/secure_uploads', new_filename)
    file.save(filepath)

    return {"filename": new_filename}, 200
```

---

### 2. 路径遍历 (CWE-22) - 严重

**风险**: 攻击者可覆盖任意文件

**攻击示例**:

```python
filename = "../../etc/passwd"
# 保存路径: /uploads/../../etc/passwd
```

**修复**: 已在上面的`secure_filename`中解决

---

## 📋 完整的安全上传实现

```python
import os
import uuid
import magic  # python-magic库
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file(file):
    # 1. 检查文件大小
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        raise ValueError("文件大小超过限制")

    # 2. 检查文件扩展名
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        raise ValueError("不允许的文件类型")

    # 3. 检查文件真实类型(MIME)
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)

    allowed_mimes = {'image/png', 'image/jpeg', 'image/gif', 'application/pdf'}
    if file_type not in allowed_mimes:
        raise ValueError("文件类型不匹配")

    return filename

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        filename = validate_file(file)

        # 生成随机文件名
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4()}.{ext}"

        # 保存到安全目录
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)

        return {"filename": new_filename}, 200

    except ValueError as e:
        return {"error": str(e)}, 400
```
````

### 关键点说明

- ✅ **多层防护**: 扩展名+MIME 类型+文件大小
- ✅ **安全文件名**: secure_filename + UUID
- ✅ **路径安全**: 防止路径遍历

---

## 📝 使用建议

1. **认证授权** → 示例 1
2. **文件上传** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
