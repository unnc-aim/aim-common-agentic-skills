# Referee Skill - 安装和使用指南

## 快速安装

```bash
# 1. 安装 Python 依赖
pip3 install chromadb anthropic

# 2. 初始化知识库
cd /Users/LijieZhou/Development/aim-claude-skills/.claude/skills/referee
./init.sh

# 3. 测试查询
python3 query.py --stats
python3 query.py 0x0001
```

## 依赖说明

- **chromadb**: 向量数据库（必需）
- **anthropic**: Claude API 客户端（可选，用于 AI 回答）

## 使用示例

### 1. 命令码查询

```bash
python3 query.py 0x0003
```

### 2. 自然语言查询

```bash
# 需要设置 API Key
export ANTHROPIC_API_KEY="your-key"
python3 query.py "如何获取机器人血量"
```

### 3. 无 AI 模式

```bash
python3 query.py --no-ai "图传链路波特率"
```

## 文档已切片完成

✅ 已生成 104 个切片：
- 19 个命令码切片
- 50 个章节切片
- 35 个自定义协议切片

下一步：安装 chromadb 后运行向量化。
