#!/usr/bin/env python3
"""
文档体系搭建后验证工具 - 简化版
用于验证路径E检测流程的可行性
"""

import os
import re
import sys
import yaml
import glob
from pathlib import Path
from datetime import datetime

class DocumentSystemValidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.dev_docs = self.project_root / "dev_docs"
        self.issues = {
            "critical": [],
            "warning": [],
            "info": []
        }
        self.scores = {}
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_file_exists(self, filepath, required=True):
        """检查文件是否存在"""
        full_path = self.project_root / filepath
        exists = full_path.exists()
        
        if required and not exists:
            self.issues["critical"].append(f"缺失必需文件: {filepath}")
        elif not exists:
            self.issues["warning"].append(f"缺失文件: {filepath}")
            
        return exists
        
    def extract_yaml_frontmatter(self, content):
        """提取YAML frontmatter"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            try:
                return yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError:
                self.issues["warning"].append("YAML frontmatter格式错误")
                return {}
        return {}
        
    def validate_structure(self):
        """第一层：结构完整性验证"""
        self.log("开始结构完整性验证...")
        score = 0
        total = 40  # 总分40分
        
        # 1.1 核心组件检测 (24分)
        core_files = [
            ("dev_docs/AI_Coding_Context.md", 8),
            ("dev_docs/_analysis/generation_plan.md", 4),
            ("dev_docs/_analysis/generation_progress.md", 4),
            ("AI_RULES.md", 8)
        ]
        
        for filepath, points in core_files:
            if self.check_file_exists(filepath):
                score += points
                self.log(f"✅ {filepath}")
            else:
                self.log(f"❌ {filepath}", "ERROR")
                
        # 1.2 目录结构检测 (8分)
        required_dirs = [
            ("dev_docs/_analysis", 3),
            ("dev_docs/plans", 3), 
            ("dev_docs/knowledge", 2)
        ]
        
        for dirpath, points in required_dirs:
            full_path = self.project_root / dirpath
            if full_path.exists() and full_path.is_dir():
                score += points
                self.log(f"✅ 目录: {dirpath}")
            else:
                self.log(f"❌ 目录: {dirpath}", "ERROR")
                
        # 1.3 交叉引用检测 (8分)
        if self.dev_docs.exists():
            main_doc_path = self.dev_docs / "AI_Coding_Context.md"
            if main_doc_path.exists():
                content = main_doc_path.read_text(encoding='utf-8')
                
                # 检查内部链接
                internal_links = re.findall(r'\[.*?\]\((\.\./)?(.*?\.md)\)', content)
                broken_links = 0
                
                for prefix, link in internal_links:
                    link_path = self.dev_docs / link
                    if not link_path.exists():
                        broken_links += 1
                        self.issues["warning"].append(f"断链: {link}")
                        
                if broken_links == 0:
                    score += 8
                    self.log("✅ 无断链")
                else:
                    self.log(f"⚠️ 发现 {broken_links} 个断链")
                    
        self.scores["structure"] = min(score, total)
        self.log(f"结构完整性得分: {score}/{total}")
        return score >= total * 0.7  # 70%通过率
        
    def validate_content(self):
        """第二层：内容可用性验证"""
        self.log("开始内容可用性验证...")
        score = 0
        total = 35  # 总分35分
        
        # 2.1 信息密度检测 (14分)
        main_doc_path = self.dev_docs / "AI_Coding_Context.md"
        if main_doc_path.exists():
            content = main_doc_path.read_text(encoding='utf-8')
            
            lines = len(content.split('\n'))
            code_blocks = len(re.findall(r'```', content))
            internal_links = len(re.findall(r'\[.*?\]\((\.\./)?.*?\.md\)', content))
            nav_sections = len(re.findall(r'^##', content, re.MULTILINE))
            
            self.log(f"主文档统计: {lines}行, {code_blocks}代码块, {internal_links}内链, {nav_sections}导航章节")
            
            # 评分标准
            if 200 <= lines <= 500: score += 4
            if code_blocks >= 3: score += 4  
            if internal_links >= 10: score += 3
            if nav_sections >= 5: score += 3
            
        # 2.2 场景覆盖度检测 (12分)
        required_scenarios = [
            "新功能", "Bug修复", "代码审查", "部署", "新人", 
            "技术栈", "性能优化", "安全"
        ]
        
        if main_doc_path.exists():
            content = main_doc_path.read_text(encoding='utf-8')
            covered = 0
            
            for scenario in required_scenarios:
                if scenario in content:
                    covered += 1
                    
            score += (covered / len(required_scenarios)) * 12
            self.log(f"场景覆盖度: {covered}/{len(required_scenarios)}")
            
        # 2.3 AI规则有效性检测 (9分)
        ai_rules_path = self.project_root / "AI_RULES.md"
        if ai_rules_path.exists():
            content = ai_rules_path.read_text(encoding='utf-8')
            
            # 检查章节完整性
            required_sections = ["项目规范", "编码规范", "注意事项"]
            sections_found = 0
            
            for section in required_sections:
                if section in content:
                    sections_found += 1
                    
            score += (sections_found / len(required_sections)) * 6
            
            # 检查规则数量
            rules = re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)
            if len(rules) >= 5:
                score += 3
                
            self.log(f"AI规则章节: {sections_found}/{len(required_sections)}, 规则数: {len(rules)}")
            
        self.scores["content"] = min(int(score), total)
        self.log(f"内容可用性得分: {int(score)}/{total}")
        return int(score) >= total * 0.6  # 60%通过率
        
    def validate_evolution(self):
        """第三层：演进适应性验证"""
        self.log("开始演进适应性验证...")
        score = 0
        total = 25  # 总分25分
        
        # 3.1 变更检测机制检测 (10分)
        main_doc_path = self.dev_docs / "AI_Coding_Context.md"
        if main_doc_path.exists():
            content = main_doc_path.read_text(encoding='utf-8')
            yaml_data = self.extract_yaml_frontmatter(content)
            
            required_fields = ["title", "summary", "verified_at", "related_files"]
            fields_found = 0
            
            for field in required_fields:
                if field in yaml_data and yaml_data[field]:
                    fields_found += 1
                    
            score += (fields_found / len(required_fields)) * 6
            
            # 检查子文档的关联性声明
            subdocs = list(self.dev_docs.glob("*.md"))
            docs_with_related = 0
            
            for doc in subdocs:
                if doc.name == "AI_Coding_Context.md":
                    continue
                    
                content = doc.read_text(encoding='utf-8')
                doc_yaml = self.extract_yaml_frontmatter(content)
                
                if "related_files" in doc_yaml and doc_yaml["related_files"]:
                    docs_with_related += 1
                    
            if len(subdocs) > 1:  # 排除主文档
                related_ratio = docs_with_related / (len(subdocs) - 1)
                score += related_ratio * 4
                
            self.log(f"YAML完整性: {fields_found}/{len(required_fields)}, 关联声明: {docs_with_related}/{len(subdocs)-1}")
            
        # 3.2 增量更新可行性检测 (10分)
        analysis_files = [
            ("dev_docs/_analysis/generation_plan.md", 3),
            ("dev_docs/_analysis/generation_progress.md", 3),
            ("dev_docs/_analysis/project_analysis_report.md", 4)
        ]
        
        for filepath, points in analysis_files:
            if self.check_file_exists(filepath):
                score += points
                
        # 3.3 知识沉淀机制检测 (5分)
        knowledge_dir = self.dev_docs / "knowledge"
        if knowledge_dir.exists():
            subdirs = ["troubleshooting", "patterns", "performance"]
            existing = 0
            
            for subdir in subdirs:
                if (knowledge_dir / subdir).exists():
                    existing += 1
                    
            score += (existing / len(subdirs)) * 3
            
            # 检查README
            if (knowledge_dir / "README.md").exists():
                score += 2
                
            self.log(f"知识库子目录: {existing}/{len(subdirs)}")
            
        self.scores["evolution"] = min(int(score), total)
        self.log(f"演进适应性得分: {int(score)}/{total}")
        return int(score) >= total * 0.6  # 60%通过率
        
    def generate_report(self):
        """生成验证报告"""
        total_score = sum(self.scores.values())
        max_score = 100
        
        # 评级
        if total_score >= 90:
            grade = "优秀 🟢"
            status = "文档体系完整且高质量"
        elif total_score >= 70:
            grade = "良好 ✅"
            status = "文档体系基本完整，有改进空间"
        elif total_score >= 50:
            grade = "一般 🟡"
            status = "文档体系存在明显问题，需要修复"
        else:
            grade = "较差 🔴"
            status = "文档体系不完整，建议重新生成"
            
        report = f"""# 文档体系搭建后验证报告

> 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 框架版本: v3.0 (路径E验证)
> 项目根目录: {self.project_root}

## 🎯 总体评估

### 综合评分: {total_score}/{max_score} {grade}

| 评估维度 | 得分 | 权重 | 状态 |
|---------|------|------|------|
| 结构完整性 | {self.scores.get('structure', 0)}/40 | 40% | {'✅' if self.scores.get('structure', 0) >= 28 else '⚠️'} |
| 内容可用性 | {self.scores.get('content', 0)}/35 | 35% | {'✅' if self.scores.get('content', 0) >= 21 else '⚠️'} |
| 演进适应性 | {self.scores.get('evolution', 0)}/25 | 25% | {'✅' if self.scores.get('evolution', 0) >= 15 else '⚠️'} |

## 📊 验证结论

**状态**: {status}

**质量基线**: 本次验证建立了文档体系的初始质量基线，用于后续健康检查对比。

## ⚠️ 发现的问题

"""
        
        # 问题分类
        if self.issues["critical"]:
            report += "### 🔴 严重问题 (必须修复)\n"
            for issue in self.issues["critical"]:
                report += f"- {issue}\n"
            report += "\n"
            
        if self.issues["warning"]:
            report += "### 🟡 警告问题 (建议修复)\n"
            for issue in self.issues["warning"]:
                report += f"- {issue}\n"
            report += "\n"
            
        if self.issues["info"]:
            report += "### 🔵 参考信息\n"
            for issue in self.issues["info"]:
                report += f"- {issue}\n"
            report += "\n"
            
        # 建议行动
        report += """## 🎯 建议行动

### 立即行动 (0-1小时)
"""
        
        if total_score < 70:
            report += """- 修复严重问题
- 补充缺失的核心文件
- 更新断链和错误引用
"""
        else:
            report += """- 优化文档内容密度
- 补充缺失的场景覆盖
- 完善YAML frontmatter
"""
            
        report += """
### 短期改进 (1-7天)
- 根据使用反馈优化文档结构
- 补充知识库内容
- 完善AI规则细节

### 长期优化 (7-30天)
- 建立定期质量检查机制
- 收集用户反馈并持续改进
- 更新质量基线标准

---

**下次验证建议**: 1周后进行首次健康检查，之后每月检查一次。
"""
        
        return report
        
    def run_validation(self):
        """运行完整验证流程"""
        self.log("开始文档体系搭建后验证...")
        
        # 执行三层验证
        structure_ok = self.validate_structure()
        content_ok = self.validate_content()
        evolution_ok = self.validate_evolution()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_path = self.project_root / "dev_docs/_analysis/post_validation_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_path.write_text(report, encoding='utf-8')
        self.log(f"验证报告已保存: {report_path}")
        
        # 总体评估
        total_score = sum(self.scores.values())
        passed = total_score >= 70 and structure_ok and content_ok and evolution_ok
        
        self.log(f"验证完成 - 总分: {total_score}/100, 状态: {'✅ 通过' if passed else '❌ 需改进'}")
        
        return {
            "passed": passed,
            "total_score": total_score,
            "structure_ok": structure_ok,
            "content_ok": content_ok, 
            "evolution_ok": evolution_ok,
            "report_path": str(report_path),
            "issues": self.issues
        }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python post_validation.py <项目根目录>")
        sys.exit(1)
        
    project_root = sys.argv[1]
    
    if not os.path.exists(project_root):
        print(f"错误: 项目根目录不存在: {project_root}")
        sys.exit(1)
        
    validator = DocumentSystemValidator(project_root)
    result = validator.run_validation()
    
    # 返回适当的退出码
    sys.exit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()