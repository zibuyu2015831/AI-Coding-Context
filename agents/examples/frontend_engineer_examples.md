# 前端工程师角色使用示例

**角色**: 前端工程师 (Frontend Engineer — Base)  
**文档**: [base/frontend_engineer.md](../language_specific/base/frontend_engineer.md)

---

## 📋 目录

- [示例 1: 响应式卡片组件](#示例-1-响应式卡片组件)
- [示例 2: 通用 Hook 设计 — useFetch](#示例-2-通用-hook-设计--usefetch)

---

## 示例 1: 响应式卡片组件

### 场景说明

需要一个跨设备适配的卡片组件，包含图片、标题、描述三个区域，支持点击跳转。

### 用户输入

```markdown
# 需求

- 实现响应式卡片组件
- 移动端单列、平板两列、桌面三列
- 支持图片懒加载、标题截断、描述行数限制
- 整卡可点击，键盘可访问（Enter/Space）
```

### 角色响应

````markdown
# Card 组件设计

## 1. API 设计

| Prop          | 类型    | 必填 | 说明                          |
| ------------- | ------- | ---- | ----------------------------- |
| imageUrl      | string  | 是   | 图片地址                      |
| imageAlt      | string  | 是   | 无障碍 alt 文本               |
| title         | string  | 是   | 卡片标题（≤ 2 行截断）        |
| description   | string  | 否   | 描述（默认 ≤ 3 行截断）       |
| descriptionLines | number | 否  | 描述最大行数，默认 3          |
| href          | string  | 否   | 点击跳转地址（提供则整卡可点）|
| onClick       | function| 否   | 自定义点击处理（与 href 互斥）|

## 2. 关键实现要点

### 响应式布局

- 容器使用 CSS Grid 而非 flex（更好控制等高）
- 断点：`<640px` 1 列、`640-1024px` 2 列、`>1024px` 3 列
- 用容器查询（`@container`）替代媒体查询，支持嵌入到任意宽度的父容器

### 图片懒加载

- 优先用原生 `loading="lazy"`，老浏览器降级为 IntersectionObserver
- 提供 LQIP（low-quality image placeholder）或骨架屏避免布局抖动
- 设置 `aspect-ratio` 或固定 `width/height` 防止 CLS

### 文本截断

- 标题用 `-webkit-line-clamp: 2` + `display: -webkit-box`
- 描述用 props.descriptionLines 控制，CSS 变量传入：`--desc-lines: ${descriptionLines}`

### 整卡可点击 + 键盘可访问

- 不要把 `onClick` 直接挂在 div 上（无障碍灾难）
- 推荐方案：用 `<a>` 包裹整卡（href 模式）；或最外层 div 加 `role="button" tabindex="0"`，并处理 Enter/Space keydown
- 焦点可见：`:focus-visible` 加 outline

## 3. 示例代码（框架无关 HTML 结构）

```html
<a class="card" href="{{href}}" aria-label="{{title}}">
  <div class="card__image" style="aspect-ratio: 16/9;">
    <img src="{{imageUrl}}" alt="{{imageAlt}}" loading="lazy" />
  </div>
  <h3 class="card__title">{{title}}</h3>
  <p class="card__desc" style="--desc-lines: {{descriptionLines}};">
    {{description}}
  </p>
</a>
```

## 4. 验收清单

- [ ] 移动端 / 平板 / 桌面三个断点视觉无塌陷
- [ ] 键盘 Tab 可聚焦，Enter/Space 触发跳转
- [ ] 图片加载前不发生 CLS
- [ ] Lighthouse Accessibility ≥ 95
````

### 关键点说明

- ✅ **无障碍优先**: 整卡可点击的"陷阱"主动避开（用 a 标签 / role + keyboard handler）
- ✅ **性能保障**: aspect-ratio 防 CLS、loading="lazy" 减首屏
- ✅ **可定制**: descriptionLines 等 props 让组件可被消费方调整

---

## 示例 2: 通用 Hook 设计 — useFetch

### 场景说明

封装通用的数据获取 Hook，要求支持 loading / error / 数据缓存 / 取消请求 / 重试。

### 用户输入

```markdown
# 需求

- 封装一个 useFetch(url, options) Hook
- 支持 loading / error / data 三态
- 组件卸载时自动取消请求
- 同 URL 短时间内（5 秒）复用上次结果
- 失败可手动 retry
```

### 角色响应

````markdown
# useFetch Hook 设计

## 1. API 签名

```typescript
type FetchOptions = {
  cache?: boolean | number;       // true=默认 5s，number=指定秒数，false=不缓存
  retryOnError?: boolean;          // 错误时是否暴露 retry 函数
  dependencies?: unknown[];        // 触发重新请求的依赖
};

type FetchResult<T> = {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retry: () => void;
};

function useFetch<T>(url: string, options?: FetchOptions): FetchResult<T>;
```

## 2. 关键实现要点

### 取消请求

- 用 AbortController，组件卸载时调用 abort()
- React: 在 useEffect cleanup 调用；Vue: 在 onUnmounted 调用

### 缓存复用

- 模块级 Map<url, { data, timestamp }>
- 命中且未过期 → 直接 return data，不发请求
- 缓存键设计：URL + method + body hash（避免不同请求误命中）

### 重试

- retry 函数清掉缓存后强制重发
- 不要做"自动重试"——业务侧才知道哪些错误应该重试（例如 5xx 重试、4xx 不重试）

### 依赖触发

- 监听 dependencies 数组，变化时取消当前请求 + 重新发起

## 3. 边界与陷阱

- ❌ 不要在 Hook 里做"乐观更新"——那是业务层职责
- ❌ 不要把 fetch 错误吞掉——返回 error 让业务决定
- ❌ 不要默认开启重试——可能造成 DDoS 自家后端
- ✅ 一定要处理 race condition：旧请求返回时若 url 已变，丢弃结果

## 4. 测试用例

- [ ] 正常获取 → loading: true → loading: false + data
- [ ] 网络错误 → loading: false + error
- [ ] 组件卸载时请求中 → 不更新已卸载组件的状态（无 React warning）
- [ ] 同 URL 5s 内重复调用 → 仅发 1 次请求
- [ ] dependencies 变化 → 旧请求取消，新请求发出
- [ ] retry → 清缓存 + 重发请求
````

### 关键点说明

- ✅ **职责单一**: 只管 fetch + state，不做业务决策（重试/乐观更新）
- ✅ **资源安全**: AbortController + cleanup 防内存泄漏与状态错乱
- ✅ **可测性**: API 设计天然便于单元测试

---

## 📝 使用建议

| 场景 | 参考示例 |
|------|---------|
| UI 组件设计（响应式 / 无障碍 / 性能） | 示例 1 |
| 逻辑封装（Hook / Composable / Service） | 示例 2 |

---

**示例版本**: v1.0  
**最后更新**: 2026-04-25
