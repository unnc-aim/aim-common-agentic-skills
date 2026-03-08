#!/usr/bin/env bash
set -euo pipefail

# Referee Skill 初始化脚本

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTOCOL_DOC="/Users/LijieZhou/Downloads/RoboMaster 2026 机甲大师高校系列赛通信协议 V1.2.0（20260209）/RoboMaster 2026 机甲大师高校系列赛通信协议 V1.2.0（20260209）.md"

echo "🚀 初始化 Referee Skill..."

# 检查 Python 依赖
echo "📦 检查依赖..."
python3 -c "import chromadb" 2>/dev/null || {
    echo "❌ chromadb 未安装"
    echo "请运行: pip3 install chromadb"
    exit 1
}

python3 -c "import anthropic" 2>/dev/null || {
    echo "⚠️  anthropic 未安装（可选，用于 AI 回答）"
    echo "如需 AI 功能，请运行: pip3 install anthropic"
}

# 检查协议文档
if [[ ! -f "$PROTOCOL_DOC" ]]; then
    echo "❌ 协议文档未找到: $PROTOCOL_DOC"
    echo "请确保文档路径正确"
    exit 1
fi

# 步骤 1: 文档切片
echo ""
echo "📄 步骤 1/2: 解析和切片协议文档..."
python3 "$SKILL_DIR/ingest.py" "$PROTOCOL_DOC"

# 步骤 2: 向量化
echo ""
echo "🔢 步骤 2/2: 向量化并存储..."
python3 "$SKILL_DIR/vectorstore.py" "$SKILL_DIR/chunks.json"

echo ""
echo "✅ 初始化完成！"
echo ""
echo "使用方法:"
echo "  python3 $SKILL_DIR/query.py '如何获取机器人血量？'"
echo "  python3 $SKILL_DIR/query.py 0x0003"
echo "  python3 $SKILL_DIR/query.py --list"
echo "  python3 $SKILL_DIR/query.py --stats"
