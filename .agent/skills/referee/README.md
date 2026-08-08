# Referee Skill

RoboMaster 裁判系统通信协议智能查询工具。

## 特性

- 🎯 **精确切片** - 按命令码、章节、协议类型智能分割文档（104 个切片）
- 🔍 **语义搜索** - 支持自然语言模糊查询
- ⚡ **快速检索** - 向量化存储，毫秒级响应
- 🤖 **Claude 集成** - 由 Claude Code 直接处理查询结果
- 📊 **元数据过滤** - 支持按类型、链路等反向查询
- 💡 **零额外成本** - 无需额外 API 调用

## 快速开始

### 1. 安装依赖

```bash
pip3 install chromadb
```

### 2. 初始化知识库

```bash
cd .claude/skills/referee
python3 vectorstore.py chunks.json
```

这将解析预生成的切片并创建向量数据库（约需 30 秒）。

### 3. 开始查询

```bash
# 自然语言查询
python3 query.py "如何获取机器人血量？"

# 命令码查询
python3 query.py 0x0003

# 列出所有命令码
python3 query.py --list

# JSON 格式输出
python3 query.py --json "图传链路"
```

## 使用示例

### 查询命令码

```bash
$ python3 query.py 0x0201

📋 命令码: 0X0201
📝 描述: 机器人性能体系数据，固定以 10Hz 频率发送
📏 数据长度: 13 字节
📡 链路类型: 常规链路
🔄 发送方/接收方: 主控模块→对应机器人

============================================================

表 1-11 0x0201
[完整数据格式表格...]
```

### 自然语言查询

```bash
$ python3 query.py "图传链路的波特率是多少"

🔍 查询: 图传链路的波特率是多少
📊 找到 3 个相关结果

============================================================
结果 1
============================================================
类型: section
章节: 串口协议格式

## 串口协议格式

通信方式为串口，配置为：常规链路的波特率为 115200，
图传链路的波特率为 921600，8 位数据位，1 位停止位，
无硬件流控，无校验位。
...
```

### 列出所有命令码

```bash
$ python3 query.py --list

📋 共有 19 个命令码:

  0X0001: 比赛状态数据，固定以 1Hz 频率发送...
  0X0002: 比赛结果数据，比赛结束触发发送...
  0X0003: 机器人血量数据，固定以 3Hz 频率发送...
  ...
```

## 架构设计

### 为什么不使用额外的 LLM？

这个 skill 采用 **检索 + Claude Code 分析** 的架构，而不是调用额外的 LLM API：

```
传统 RAG 架构（不推荐）:
用户 → Claude Code → 向量检索 → 调用 Claude API → 回答

本 Skill 架构（推荐）:
用户 → Claude Code → 向量检索 → Claude Code 直接分析 → 回答
```

**优势：**
- ✅ **零额外成本** - 不需要额外的 API 调用
- ✅ **更快响应** - 省去一次网络往返
- ✅ **更好集成** - Claude Code 可以结合其他工具和上下文
- ✅ **更灵活** - 可以根据对话历史调整回答方式
- ✅ **统一体验** - 用户感觉是在和同一个 AI 对话

### 工作流程

1. **用户提问** - "如何获取机器人血量？"
2. **Claude Code 调用查询工具** - `python3 query.py "如何获取机器人血量"`
3. **向量检索** - 返回相关的文档切片（命令码 0x0003）
4. **Claude Code 分析** - 理解切片内容，生成详细回答
5. **返回用户** - 结构化、准确的答案

## 文件结构

```
.claude/skills/referee/
├── ingest.py           # 文档解析和切片（9.4KB）
├── vectorstore.py      # 向量存储和检索（5.5KB）
├── query.py            # 查询 CLI 工具（纯检索，无 LLM）
├── init.sh             # 一键初始化脚本
├── chunks.json         # 预生成的切片数据（152KB）✅
├── SKILL.md            # Skill 定义
├── README.md           # 本文档
├── INSTALL.md          # 安装指南
└── requirements.txt    # Python 依赖（仅 chromadb）
```

## 命令行选项

```bash
python3 query.py [选项] <查询内容>

选项:
  --list              列出所有命令码
  --stats             显示知识库统计
  --json              以 JSON 格式输出（用于程序化处理）
  -n, --num-results N 返回 N 个结果（默认 3）
```

## 切片策略

### 命令码切片（19 个）

每个命令码生成一个独立切片，包含：
- 命令码 ID（如 0x0001）
- 数据长度
- 功能描述
- 发送方/接收方
- 数据链路类型
- 完整的数据格式表格

**元数据示例：**
```json
{
  "type": "command_code",
  "cmd_id": "0X0201",
  "data_length": "13",
  "description": "机器人性能体系数据",
  "sender_receiver": "主控模块→对应机器人",
  "link_type": "常规链路"
}
```

### 章节切片（50 个）

按 Markdown 标题层级分割：
- `#` 一级标题（如 "串口协议"）
- `##` 二级标题（如 "命令码 ID 和常规链路数据说明"）
- `###` 三级标题（如 "选手端下发数据"）

### 自定义协议切片（35 个）

提取 "自定义客户端协议" 章节下的所有子协议：
- KeyboardMouseControl
- CustomControl
- GameStatus
- RobotDynamicStatus
- ...

## 技术栈

- **向量数据库**: ChromaDB
- **嵌入模型**: sentence-transformers (默认)
- **语言**: Python 3.8+
- **集成**: Claude Code

## 性能

- **初始化时间**: ~30 秒（一次性）
- **查询延迟**: <100ms（向量检索）
- **存储空间**: ~10MB（向量数据库）

## 故障排除

### 问题：chromadb 安装失败

**解决：**
```bash
# macOS
brew install cmake
pip3 install chromadb

# Linux
sudo apt-get install cmake
pip3 install chromadb
```

### 问题：协议文档未找到

**解决：**
检查 `init.sh` 中的 `PROTOCOL_DOC` 路径是否正确。

### 问题：查询结果不准确

**解决：**
1. 增加返回结果数：`-n 5`
2. 使用更具体的查询词
3. 直接使用命令码查询

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
