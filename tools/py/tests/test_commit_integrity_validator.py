import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 将上级目录添加到 sys.path 以便导入被测模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commit_integrity_validator import parse_how_files, calculate_integrity

class TestCommitIntegrityValidator(unittest.TestCase):

    def test_parse_how_files(self):
        """测试从 commit message 中提取文件路径"""
        message = """prompt(feature): test commit
        WHAT: test
        WHY: test
        HOW:
        - 修改了 src/models/user.py
        - 新增了 src/api/auth.ts 文件
        - 调整了 config/settings.yaml
        - 修改了 README.md
        """
        expected = {'src/models/user.py', 'src/api/auth.ts', 'config/settings.yaml', 'README.md'}
        self.assertEqual(parse_how_files(message), expected)

    def test_parse_how_files_complex(self):
        """测试复杂格式的文件路径提取"""
        message = "HOW: 在 ./src/utils/helper.js 中增加逻辑，并在 tests/test_helper.py 中添加测试。"
        expected = {'src/utils/helper.js', 'tests/test_helper.py'}
        self.assertEqual(parse_how_files(message), expected)

    def test_calculate_integrity_perfect(self):
        """测试完全匹配的情况"""
        msg_files = {'file1.py', 'file2.js'}
        actual_files = {'file1.py', 'file2.js'}
        report = calculate_integrity(msg_files, actual_files)
        
        self.assertEqual(report['score'], 100)
        self.assertEqual(report['status'], 'EXCELLENT')
        self.assertEqual(len(report['suggestions']), 0)

    def test_calculate_integrity_under_reported(self):
        """测试漏报的情况"""
        msg_files = {'file1.py'}
        actual_files = {'file1.py', 'file2.js'} # 漏报了 file2.js
        report = calculate_integrity(msg_files, actual_files)
        
        # 漏报扣 15 分
        self.assertEqual(report['score'], 85)
        self.assertEqual(report['status'], 'GOOD')
        self.assertIn('file2.js', report['under_reported'])

    def test_calculate_integrity_over_reported(self):
        """测试虚报的情况"""
        msg_files = {'file1.py', 'file2.js'} # 虚报了 file2.js
        actual_files = {'file1.py'}
        report = calculate_integrity(msg_files, actual_files)
        
        # 虚报扣 5 分
        self.assertEqual(report['score'], 95)
        self.assertEqual(report['status'], 'EXCELLENT')
        self.assertIn('file2.js', report['over_reported'])

    def test_calculate_integrity_needs_improvement(self):
        """测试低分的情况"""
        msg_files = {'wrong_file.py'}
        actual_files = {'file1.py', 'file2.js'} # 漏报 2 个，虚报 1 个
        report = calculate_integrity(msg_files, actual_files)
        
        # (100 - 15*2 - 5*1) = 65
        self.assertEqual(report['score'], 65)
        self.assertEqual(report['status'], 'NEEDS_IMPROVEMENT')

if __name__ == '__main__':
    unittest.main()
