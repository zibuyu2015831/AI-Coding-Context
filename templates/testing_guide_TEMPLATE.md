# 测试文档模板

> **用途**: 记录项目的测试策略、测试用例和测试结果  
> **适用场景**: 所有需要测试的项目

---

# [项目名称] - 测试文档

## 📋 测试概览

### 测试策略

- **测试金字塔**:

  - 单元测试: 70%
  - 集成测试: 20%
  - E2E测试: 10%

- **测试框架**: [Jest / Pytest / JUnit / Go test / 其他]
- **覆盖率目标**: [80%+ / 具体数字]
- **CI集成**: [是/否，工具名称]

---

## 🧪 测试类型

### 单元测试

**目的**: 测试单个函数/方法的正确性

**框架**: [Jest / Vitest / Pytest / unittest / 其他]

**运行命令**:

```bash
# 运行所有测试
[npm test / pytest / go test ./... / cargo test]

# 运行特定文件
[npm test -- user.test.ts / pytest tests/test_user.py]

# 生成覆盖率报告
[npm test -- --coverage / pytest --cov]
```

**示例**:

```[language]
// 文件: tests/unit/user.test.ts
describe('User', () => {
  it('should create user with valid data', () => {
    const user = new User({ name: 'Test' })
    expect(user.name).toBe('Test')
  })

  it('should throw error for invalid email', () => {
    expect(() => new User({ email: 'invalid' })).toThrow()
  })
})
```

**覆盖的模块**:

- [ ] API层
- [ ] 业务逻辑层
- [ ] 工具函数
- [ ] 数据验证

---

### 集成测试

**目的**: 测试模块间的协作

**框架**: [Supertest / TestContainers / Spring Test / 其他]

**运行命令**:

```bash
[npm run test:integration / pytest tests/integration]
```

**示例**:

```[language]
// 文件: tests/integration/api.test.ts
describe('API Integration', () => {
  beforeAll(async () => {
    // 启动测试数据库
    await setupTestDatabase()
  })

  it('should create and retrieve user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test' })
      .expect(201)

    const userId = response.body.id

    const getResponse = await request(app)
      .get(`/api/users/${userId}`)
      .expect(200)

    expect(getResponse.body.name).toBe('Test')
  })
})
```

**覆盖的场景**:

- [ ] API端到端流程
- [ ] 数据库交互
- [ ] 外部服务集成（使用Mock）
- [ ] 消息队列处理

---

### E2E测试

**目的**: 测试完整的用户流程

**框架**: [Playwright / Cypress / Selenium / 其他]

**运行命令**:

```bash
[npx playwright test / npx cypress run]
```

**示例**:

```[language]
// 文件: e2e/login.spec.ts
test('user can login', async ({ page }) => {
  await page.goto('https://app.com/login')
  await page.fill('[name=email]', 'test@example.com')
  await page.fill('[name=password]', 'password')
  await page.click('button[type=submit]')

  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('h1')).toContainText('Dashboard')
})
```

**覆盖的用户流程**:

- [ ] 用户注册/登录
- [ ] 核心业务流程
- [ ] 错误处理流程

---

## 📊 测试覆盖率

### 当前覆盖率

| 模块     | 行覆盖率  | 分支覆盖率 | 函数覆盖率 |
| -------- | --------- | ---------- | ---------- |
| API层    | [90%]     | [85%]      | [95%]      |
| 业务逻辑 | [85%]     | [80%]      | [90%]      |
| 工具函数 | [95%]     | [90%]      | [100%]     |
| **总计** | **[88%]** | **[83%]**  | **[92%]**  |

### 未覆盖的代码

- [列出重要的未覆盖代码]
- [说明为什么未覆盖]

---

## 🔧 测试工具

### 测试环境

- **测试数据库**: [Docker container / In-memory / 测试环境]
- **Mock工具**: [Jest mock / pytest-mock / mockito]
- **测试数据**: [Faker / Factory / Fixtures]

### 辅助工具

- **覆盖率报告**: [Istanbul / coverage.py / cargo-tarpaulin]
- **性能测试**: [k6 / JMeter / 其他]
- **快照测试**: [Jest snapshot / 其他]

---

## ⚡ 性能测试

### 负载测试

**工具**: [k6 / Apache JMeter / Locust]

**测试场景**:

```javascript
// k6示例
export default function () {
  const response = http.get("https://api.com/users");
  check(response, {
    "status is 200": (r) => r.status === 200,
    "response time < 200ms": (r) => r.timings.duration < 200,
  });
}
```

**性能指标**:

- **响应时间**: < 200ms (P95)
- **吞吐量**: > 1000 req/s
- **错误率**: < 0.1%

---

## 🔒 安全测试

### 安全扫描

- **SAST**: [SonarQube / Semgrep / 其他]
- **DAST**: [OWASP ZAP / Burp Suite]
- **依赖扫描**: [npm audit / Snyk / Dependabot]

### 常见安全测试

- [ ] SQL注入测试
- [ ] XSS测试
- [ ] CSRF测试
- [ ] 认证/授权测试

---

## 🚀 CI/CD集成

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: [npm install / pip install -r requirements.txt]
      - name: Run tests
        run: [npm test / pytest]
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📝 测试数据管理

### Fixtures

**位置**: `tests/fixtures/`

**示例**:

```[language]
// tests/fixtures/users.ts
export const mockUser = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com'
}

export const mockUsers = [mockUser, ...]
```

### 数据库迁移

**测试前**: 运行迁移创建测试数据库schema  
**测试后**: 清理测试数据

---

## 🐛 调试测试

### 调试命令

```bash
# 只运行失败的测试
[npm test -- --onlyFailures / pytest --lf]

# 详细输出
[npm test -- --verbose / pytest -vv]

# 调试模式
[node --inspect-brk node_modules/.bin/jest / pytest --pdb]
```

### 常见问题

**问题1**: 测试不稳定（flaky tests）

- **原因**: 异步时序问题
- **解决**: 使用waitFor/await正确处理异步

**问题2**: 测试运行缓慢

- **原因**: 过多的E2E测试
- **解决**: 增加单元测试比例

---

## ✅ 测试清单

### 新功能开发

- [ ] 编写单元测试
- [ ] 编写集成测试（如需要）
- [ ] 更新E2E测试（如影响用户流程）
- [ ] 运行全部测试确认无回归
- [ ] 检查覆盖率是否达标

### Bug修复

- [ ] 编写重现bug的测试
- [ ] 修复代码
- [ ] 确认测试通过
- [ ] 检查无其他测试失败

---

## 📚 测试最佳实践

1. **测试命名清晰** - 测试名称应描述测试内容
2. **独立性** - 测试间不应有依赖
3. **可重复性** - 每次运行结果一致
4. **快速执行** - 单元测试应在秒级完成
5. **有意义的断言** - 断言应验证核心逻辑

---

## 🔄 持续改进

### 测试指标监控

- **覆盖率趋势**: [链接到覆盖率报告]
- **测试执行时间**: [趋势图]
- **失败率**: [监控flaky tests]

### 改进计划

- [ ] [具体改进项1]
- [ ] [具体改进项2]

---

## 📅 文档元信息

- **创建日期**: YYYY-MM-DD
- **最后更新**: YYYY-MM-DD
- **维护者**: [团队/个人]
