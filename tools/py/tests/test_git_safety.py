"""
Git Safety 工具单元测试

测试覆盖:
1. 保护分支检测
2. 危险命令验证
3. 分支名建议
4. 边界情况处理
"""

import unittest
import sys
import os

# 添加父目录到路径以便导入git_safety
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from git_safety import (
    check_current_branch,
    validate_git_command,
    suggest_safe_branch_name,
    DEFAULT_PROTECTED_BRANCHES
)


class TestCheckCurrentBranch(unittest.TestCase):
    """测试保护分支检测功能"""
    
    def test_protected_branch_detection(self):
        """测试保护分支检测"""
        # 注意: 这个测试依赖于实际的Git仓库状态
        # 在CI环境中可能需要mock
        result = check_current_branch()
        self.assertIn('safe', result)
        self.assertIn('current_branch', result)
        self.assertIn('reason', result)
    
    def test_custom_protected_branches(self):
        """测试自定义保护分支列表"""
        custom_branches = ['main', 'production', 'staging']
        result = check_current_branch(custom_branches)
        self.assertIsInstance(result, dict)
        self.assertIn('safe', result)


class TestValidateGitCommand(unittest.TestCase):
    """测试Git命令验证功能"""
    
    def test_dangerous_force_push(self):
        """测试危险命令: git push --force"""
        result = validate_git_command('git push --force')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
        self.assertIn('RED ZONE', result['suggestion'])
    
    def test_dangerous_force_push_short(self):
        """测试危险命令: git push -f"""
        result = validate_git_command('git push -f')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_dangerous_reset_hard(self):
        """测试危险命令: git reset --hard"""
        result = validate_git_command('git reset --hard')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_dangerous_rebase(self):
        """测试危险命令: git rebase"""
        result = validate_git_command('git rebase main')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_dangerous_merge(self):
        """测试危险命令: git merge (非--abort)"""
        result = validate_git_command('git merge feature/test')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_safe_merge_abort(self):
        """测试安全命令: git merge --abort"""
        result = validate_git_command('git merge --abort')
        self.assertTrue(result['safe'])
    
    def test_dangerous_branch_delete(self):
        """测试危险命令: git branch -D"""
        result = validate_git_command('git branch -D old-branch')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_restricted_checkout(self):
        """测试受限命令: git checkout -b"""
        result = validate_git_command('git checkout -b feature/new')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'YELLOW')
        self.assertIn('authorization', result['suggestion'])
    
    def test_restricted_commit(self):
        """测试受限命令: git commit"""
        result = validate_git_command('git commit -m "test"')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'YELLOW')
    
    def test_restricted_push(self):
        """测试受限命令: git push origin"""
        result = validate_git_command('git push origin feature/test')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'YELLOW')
    
    def test_safe_status(self):
        """测试安全命令: git status"""
        result = validate_git_command('git status')
        self.assertTrue(result['safe'])
        self.assertEqual(result['zone'], 'GREEN')
    
    def test_safe_log(self):
        """测试安全命令: git log"""
        result = validate_git_command('git log --oneline')
        self.assertTrue(result['safe'])
        self.assertEqual(result['zone'], 'GREEN')
    
    def test_safe_diff(self):
        """测试安全命令: git diff"""
        result = validate_git_command('git diff HEAD~1')
        self.assertTrue(result['safe'])
        self.assertEqual(result['zone'], 'GREEN')
    
    def test_empty_command(self):
        """测试空命令"""
        result = validate_git_command('')
        self.assertFalse(result['safe'])
        self.assertIn('No command', result['reason'])
    
    def test_none_command(self):
        """测试None命令"""
        result = validate_git_command(None)
        self.assertFalse(result['safe'])


class TestSuggestBranchName(unittest.TestCase):
    """测试分支名建议功能"""
    
    def test_feature_branch(self):
        """测试功能分支建议"""
        result = suggest_safe_branch_name('user points')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'feature/user-points')
        self.assertIn('git checkout -b', result['suggestion'])
    
    def test_bugfix_branch(self):
        """测试bug修复分支建议"""
        result = suggest_safe_branch_name('fix login issue')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'bugfix/fix-login-issue')
    
    def test_refactor_branch(self):
        """测试重构分支建议"""
        result = suggest_safe_branch_name('refactor auth module')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'refactor/refactor-auth-module')
    
    def test_docs_branch(self):
        """测试文档分支建议"""
        result = suggest_safe_branch_name('update documentation')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'docs/update-documentation')
    
    def test_special_characters(self):
        """测试特殊字符处理"""
        result = suggest_safe_branch_name('user@points#system!')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'feature/userpointssystem')
    
    def test_multiple_spaces(self):
        """测试多个空格处理"""
        result = suggest_safe_branch_name('user   points   system')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'feature/user-points-system')
    
    def test_underscores(self):
        """测试下划线处理"""
        result = suggest_safe_branch_name('user_points_system')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'feature/user-points-system')
    
    def test_empty_description(self):
        """测试空描述"""
        result = suggest_safe_branch_name('')
        self.assertTrue(result['safe'])
        self.assertIsNone(result['suggested'])
    
    def test_none_description(self):
        """测试None描述"""
        result = suggest_safe_branch_name(None)
        self.assertTrue(result['safe'])
        self.assertIsNone(result['suggested'])


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_case_insensitive_command(self):
        """测试命令大小写不敏感"""
        result1 = validate_git_command('GIT PUSH --FORCE')
        result2 = validate_git_command('git push --force')
        self.assertEqual(result1['safe'], result2['safe'])
        self.assertEqual(result1['zone'], result2['zone'])
    
    def test_command_with_extra_spaces(self):
        """测试命令中的额外空格"""
        result = validate_git_command('git  push  --force')
        self.assertFalse(result['safe'])
        self.assertEqual(result['zone'], 'RED')
    
    def test_branch_name_with_leading_trailing_hyphens(self):
        """测试首尾连字符处理"""
        result = suggest_safe_branch_name('---user-points---')
        self.assertTrue(result['safe'])
        self.assertEqual(result['suggested'], 'feature/user-points')


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
