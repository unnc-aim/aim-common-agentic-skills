#!/usr/bin/env bash
set -euo pipefail

# Claude Skills 全局安装脚本
# 将所有 skills 安装到用户的 .claude 目录

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_CLAUDE_DIR="${HOME}/.claude/skills"

echo "🚀 安装 Claude Skills..."
echo ""

# 创建目标目录
mkdir -p "$USER_CLAUDE_DIR"

# 安装 Remote Exec Skill
echo "📦 安装 Remote Exec Skill..."
REMOTE_EXEC_DIR="$USER_CLAUDE_DIR/remote-exec"
mkdir -p "$REMOTE_EXEC_DIR"

cp "$REPO_DIR/.claude/skills/remote-exec/remote-exec.sh" "$REMOTE_EXEC_DIR/"
cp "$REPO_DIR/.claude/skills/remote-exec/README.md" "$REMOTE_EXEC_DIR/"
cp "$REPO_DIR/.claude/skills/remote-exec/config.example.json" "$REMOTE_EXEC_DIR/"

chmod +x "$REMOTE_EXEC_DIR/remote-exec.sh"

echo "   ✓ Remote Exec 已安装到: $REMOTE_EXEC_DIR"

# 安装 Referee Skill
echo ""
echo "📦 安装 Referee Skill..."
REFEREE_DIR="$USER_CLAUDE_DIR/referee"
mkdir -p "$REFEREE_DIR"

cp "$REPO_DIR/.claude/skills/referee/query_simple.py" "$REFEREE_DIR/"
cp "$REPO_DIR/.claude/skills/referee/chunks.json" "$REFEREE_DIR/"
cp "$REPO_DIR/.claude/skills/referee/SKILL.md" "$REFEREE_DIR/"
cp "$REPO_DIR/.claude/skills/referee/README_SIMPLE.md" "$REFEREE_DIR/README.md"

# 可选：复制文档添加工具
if [[ -f "$REPO_DIR/.claude/skills/referee/add_document.py" ]]; then
    cp "$REPO_DIR/.claude/skills/referee/add_document.py" "$REFEREE_DIR/"
    cp "$REPO_DIR/.claude/skills/referee/ingest.py" "$REFEREE_DIR/"
    chmod +x "$REFEREE_DIR/add_document.py"
fi

chmod +x "$REFEREE_DIR/query_simple.py"

echo "   ✓ Referee 已安装到: $REFEREE_DIR"

echo ""
echo "✅ 所有 skills 安装完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Remote Exec Skill"
echo "   远程 SSH 执行工具"
echo ""
echo "   使用方法:"
echo "     $REMOTE_EXEC_DIR/remote-exec.sh add dev user@server.com"
echo "     $REMOTE_EXEC_DIR/remote-exec.sh connect dev"
echo "     $REMOTE_EXEC_DIR/remote-exec.sh exec whoami"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Referee Skill"
echo "   RoboMaster 协议查询工具（零依赖）"
echo ""
echo "   使用方法:"
echo "     python3 $REFEREE_DIR/query_simple.py '如何获取机器人血量'"
echo "     python3 $REFEREE_DIR/query_simple.py 0x0003"
echo "     python3 $REFEREE_DIR/query_simple.py --list"
echo ""
if [[ -f "$REFEREE_DIR/add_document.py" ]]; then
echo "   添加新文档:"
echo "     python3 $REFEREE_DIR/add_document.py add <文档路径> --name <文档名>"
echo ""
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示: 所有 skills 均已安装到 $USER_CLAUDE_DIR"
echo "💡 可以在 Claude Code 中直接使用这些 skills"
