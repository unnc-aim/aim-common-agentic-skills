#!/usr/bin/env bash
set -euo pipefail

# Referee Skill 安装脚本
# 将 skill 复制到用户的 .claude 目录

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_CLAUDE_DIR="${HOME}/.claude/skills/referee"

echo "🚀 安装 Referee Skill..."
echo ""

# 创建目标目录
mkdir -p "$USER_CLAUDE_DIR"

# 复制必要文件
echo "📦 复制文件到 $USER_CLAUDE_DIR"
cp "$SCRIPT_DIR/query_simple.py" "$USER_CLAUDE_DIR/"
cp "$SCRIPT_DIR/chunks.json" "$USER_CLAUDE_DIR/"
cp "$SCRIPT_DIR/SKILL.md" "$USER_CLAUDE_DIR/"
cp "$SCRIPT_DIR/README_SIMPLE.md" "$USER_CLAUDE_DIR/README.md"

# 添加执行权限
chmod +x "$USER_CLAUDE_DIR/query_simple.py"

echo ""
echo "✅ 安装完成！"
echo ""
echo "文件已复制到: $USER_CLAUDE_DIR"
echo ""
echo "使用方法:"
echo "  python3 ~/.claude/skills/referee/query_simple.py '如何获取机器人血量'"
echo "  python3 ~/.claude/skills/referee/query_simple.py 0x0003"
echo "  python3 ~/.claude/skills/referee/query_simple.py --list"
echo ""
echo "💡 提示: 这是零依赖版本，无需安装任何包！"
