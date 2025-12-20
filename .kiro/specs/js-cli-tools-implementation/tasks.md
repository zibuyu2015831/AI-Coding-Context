# Implementation Plan

- [x] 1. 实现 install_hooks.js 核心功能


  - 创建 `tools/js/install_hooks.js` 文件
  - 实现 Git 仓库根目录查找功能
  - 实现 hook 安装逻辑（复制文件、设置权限）
  - 实现 hook 卸载逻辑（删除文件、恢复备份）
  - 实现用户交互（确认覆盖、确认恢复）
  - 添加详细的 JSDoc 文档注释
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.4_



- [ ] 1.1 编写 install_hooks.js 单元测试
  - 测试 `findGitRoot()` 在不同目录层级的行为
  - 测试 hook 安装在文件已存在/不存在时的行为
  - 测试 hook 卸载在有/无备份时的行为


  - 测试跨平台路径处理
  - _Requirements: 1.1, 1.2, 1.5_

- [ ] 2. 实现 commit_template_cli.js 核心功能
  - 创建 `tools/js/commit_template_cli.js` 文件
  - 实现交互式模式（询问类型、WHAT、WHY、HOW）
  - 实现快速模式（解析命令行参数）
  - 实现 commit message 生成逻辑
  - 实现质量评分调用（可选，失败不影响主流程）


  - 实现用户确认执行逻辑
  - 添加详细的 JSDoc 文档注释
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.4_


- [ ] 2.1 编写 commit_template_cli.js 单元测试
  - 测试 `generateCommitMessage()` 格式正确性
  - 测试不同 commit 类型的映射
  - 测试空输入的默认值处理
  - 测试快速模式参数解析
  - _Requirements: 2.2, 2.5_


- [ ] 3. 实现命令行参数解析和帮助信息
  - 为 `install_hooks.js` 添加 `--help`、`--uninstall` 参数支持
  - 为 `commit_template_cli.js` 添加 `--help`、`--quick`、`--type`、`--what`、`--why`、`--how` 参数支持
  - 实现帮助信息显示函数
  - 确保帮助信息与 Python 版本一致

  - _Requirements: 3.3, 5.1, 5.2_

- [ ] 4. 实现跨平台兼容性
  - 使用 `path.join()` 和 `path.resolve()` 处理所有路径
  - 实现跨平台文件权限设置（Windows 跳过 chmod）
  - 测试 Windows 和 Unix 系统的路径分隔符处理
  - 确保用户输入在不同平台上正常工作


  - _Requirements: 3.4, 4.4_

- [ ] 5. 实现错误处理和用户提示
  - 为所有文件操作添加 try-catch 错误处理


  - 实现清晰的错误提示信息
  - 实现成功操作的确认提示
  - 添加操作建议和后续步骤提示
  - 使用 emoji 和格式化文本提升用户体验
  - _Requirements: 3.2, 4.3, 5.3, 5.4, 5.5_




- [ ] 6. 更新工具库文档
  - 更新 `tools/README.md`，将 `install_hooks` 和 `commit_template_cli` 添加到工具清单
  - 更新 `tools/CHANGELOG.md`，记录 v1.3.1 版本变更
  - 确保文档说明两个工具现在都有 Python 和 Node.js 版本
  - _Requirements: 4.5_

- [ ] 7. 端到端集成测试
  - 在临时 Git 仓库中测试完整的 hook 安装/卸载流程
  - 测试交互式模式的完整流程（使用模拟输入）
  - 测试快速模式的参数解析和输出
  - 验证与 Python 版本的输出一致性
  - _Requirements: 3.1_

- [ ] 8. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户
