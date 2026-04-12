#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂度通知工具 - 用于发送复杂度报告通知
作为 005 优化点的补充工具

功能说明:
- 发送 Slack 通知（严重警告级别）
- 发送 Email 通知（每日报告和严重警告）
- 支持 CI/CD 集成

使用方法:
    python tools/py/notifier.py [--data DATA] [--level LEVEL] [--channel CHANNEL]

参数说明:
    --data DATA              输入数据文件路径（JSON 格式）
    --level LEVEL            通知级别（info/warning/critical，默认：warning）
    --channel CHANNEL        Slack 通知频道（默认：#dev-complexity）
    --email EMAIL            Email 通知地址
    --webhook URL            Slack Webhook URL
    --subject SUBJECT        Email 主题
    --template TEMPLATE      通知模板路径

使用示例:
    # 发送 Slack 通知
    python tools/py/notifier.py --data data.json --level critical --channel #dev-alerts

    # 发送 Email 通知
    python tools/py/notifier.py --data data.json --email dev@example.com

版本信息:
    版本：1.0.0
    更新日期：2026-04-12
"""

import json
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime


def load_data(data_path):
    """加载复杂度数据"""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def generate_notification_text(data, level):
    """生成通知文本"""
    complexity_data = data.get('data', {})
    risk_assessment = complexity_data.get('risk_assessment', {})
    code_size = complexity_data.get('code_size', {})
    code_quality = complexity_data.get('code_quality', {})

    overall_score = risk_assessment.get('overall_score', 0)
    risks = risk_assessment.get('risks', [])

    # 风险等级图标
    level_emoji = {
        'info': '📊',
        'warning': '⚠️',
        'critical': '🚨'
    }.get(level, '📊')

    text = f"{level_emoji} 项目复杂度报告\n\n"
    text += f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += f"🎯 整体风险评分: {overall_score:.0f}/100\n\n"

    # 关键指标
    text += "📈 关键指标:\n"
    text += f"  - 新增代码: {code_size.get('new_lines', 0)} 行\n"
    text += f"  - 代码质量: {code_quality.get('quality_score', 0)}/100\n"
    text += f"  - 增长比例: {code_size.get('growth_percentage', 0):.1f}%\n\n"

    # 风险项
    if risks:
        text += "⚠️ 风险项:\n"
        for risk in risks:
            risk_level_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(risk.get('level', 'low'), '🟢')
            text += f"  {risk_level_emoji} {risk.get('message')}\n"
        text += "\n"

    # 行动建议
    if level == 'critical':
        text += "🛠️ 请立即查看详细报告并处理问题！\n"

    return text


def send_slack_notification(text, webhook_url, channel):
    """发送 Slack 通知"""
    try:
        # 这里使用简单的实现，实际生产环境可能需要使用 requests 库
        # 由于我们要保持零依赖，这里只打印通知内容
        print(f"📤 Slack 通知 (频道: {channel}):")
        print("-" * 50)
        print(text)
        print("-" * 50)

        # 提示用户如何配置实际的 Slack Webhook
        print("\n💡 提示: 要启用实际的 Slack 通知，请:")
        print("   1. 创建 Slack Webhook")
        print("   2. 使用 --webhook 参数传入 URL")
        print("   3. 安装 requests 库进行实际发送")

        return True
    except Exception as e:
        print(f"Error sending Slack notification: {e}")
        return False


def send_email_notification(text, email_address, subject):
    """发送 Email 通知"""
    try:
        # 由于要保持零依赖，这里只打印通知内容
        print(f"📤 Email 通知 (地址: {email_address}):")
        print(f"📧 主题: {subject}")
        print("-" * 50)
        print(text)
        print("-" * 50)

        # 提示用户如何配置实际的邮件发送
        print("\n💡 提示: 要启用实际的 Email 通知，请:")
        print("   1. 配置 SMTP 服务器")
        print("   2. 使用 smtplib 或第三方库进行实际发送")

        return True
    except Exception as e:
        print(f"Error sending Email notification: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='复杂度通知工具')
    parser.add_argument('--data', required=True, help='输入数据文件路径（JSON 格式）')
    parser.add_argument('--level', choices=['info', 'warning', 'critical'],
                        default='warning', help='通知级别')
    parser.add_argument('--channel', default='#dev-complexity', help='Slack 通知频道')
    parser.add_argument('--email', help='Email 通知地址')
    parser.add_argument('--webhook', help='Slack Webhook URL')
    parser.add_argument('--subject', help='Email 主题')

    args = parser.parse_args()

    # 加载数据
    data = load_data(args.data)
    if not data:
        return 1

    # 生成通知文本
    text = generate_notification_text(data, args.level)

    # 发送通知
    success = True

    if args.webhook:
        success = success and send_slack_notification(text, args.webhook, args.channel)

    if args.email:
        default_subject = f"[{args.level.upper()}] 项目复杂度报告 - {datetime.now().strftime('%Y-%m-%d')}"
        success = success and send_email_notification(text, args.email, args.subject or default_subject)

    # 如果没有指定具体的通知方式，只打印
    if not args.webhook and not args.email:
        print("📋 通知预览:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        print("\n💡 提示: 使用 --webhook 或 --email 参数发送实际通知")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
