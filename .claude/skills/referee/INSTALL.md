# Referee Skill - 安装和使用指南

## 快速安装

```bash
# 1. 安装 Python 依赖（仅需 chromadb）
pip3 install chromadb

# 2. 初始化知识库
cd /Users/LijieZhou/Development/aim-claude-skills/.claude/skills/referee
python3 vectorstore.py chunks.json

# 3. 测试查询
python3 query.py --stats
python3 query.py 0x0001
```

## 依赖说明

- **chromadb**: 向量数据库（必需）
- ~~**anthropic**: Claude API 客户端~~（已移除，使用 Claude Code 自身能力）

## 架构变更

### 旧架构（已废弃）
```
用户 → Claude Code → 向量检索 → 调用 Claude API → 回答
                                    ↑
                              额外成本和延迟
```

### 新架构（当前）
```
用户 → Claude Code → 向量检索 → Claude Code 分析 → 回答
                                    ↑
                              无额外成本，更快
```

## 使用示例

### 1. 命令码查询

```bash
python3 query.py 0x0003
```

### 2. 自然语言查询

```bash
# 直接查询，Claude Code 会分析结果
python3 query.py "如何获取机器人血量"
```

### 3. JSON 格式（程序化处理）

```bash
python3 query.py --json "图传链路波特率"
```

## 文档已切片完成

✅ 已生成 104 个切片：
- 19 个命令码切片
- 50 个章节切片
- 35 个自定义协议切片

下一步：安装 chromadb 后运行向量化。

## 为什么移除 anthropic 依赖？

1. **Claude Code 本身就是 Claude** - 无需再调用 API
2. **零额外成本** - 不产生额外的 API 费用
3. **更快响应** - 省去一次网络往返
4. **更好集成** - 可以结合对话历史和其他工具
5. **简化依赖** - 只需要 chromadb 一个依赖

## 工作流程

1. 用户在 Claude Code 中提问
2. Claude Code 调用 `query.py` 进行向量检索
3. `query.py` 返回相关的文档切片
4. Claude Code 直接分析切片内容并生成回答
5. 用户得到准确、详细的答案

这样的架构更简洁、更高效！
