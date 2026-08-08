---
name: dji-referee
description: Query the RoboMaster referee-system communication protocol — command codes (e.g. 0x0003), data formats, link types, and baud rates. Zero-dependency instant lookup via query_simple.py over 104 prebuilt doc slices. Use when the user asks about the RoboMaster protocol, the referee system, a specific command code, or a protocol data field.
---

# DJI Referee Skill

RoboMaster 裁判系统通信协议智能查询 skill。**零依赖，即开即用**。

## Trigger

当用户提到以下内容时激活：
- `/dji-referee` 命令
- 查询 RoboMaster 协议、裁判系统、通信协议
- 询问命令码（如 "0x0001 是什么"）
- 询问数据格式、通信链路等协议相关问题

## Capabilities

1. **智能文档切片** - 按命令码、章节、协议类型精确切分（104 个切片）
2. **关键词智能匹配** - 基于评分算法的快速检索
3. **命令码精确查找** - 通过命令码 ID 快速定位
4. **零依赖** - 纯 Python 标准库，无需安装任何包
5. **即开即用** - 无需初始化，直接查询

## Setup

**无需任何设置！** 直接使用即可。

所有数据已预生成在 `chunks.json` 文件中（152KB）。

## Usage in Claude Code

当 skill 被激活时（用户使用 `/dji-referee` 或询问协议相关问题），Claude 应该：

### 1. 执行查询获取相关内容

**重要：使用 `query_simple.py`，不是 `query.py`！**

```bash
# 自然语言查询
python3 ~/.claude/skills/dji-referee/query_simple.py "如何获取机器人血量"

# 命令码精确查询
python3 ~/.claude/skills/dji-referee/query_simple.py 0x0003

# 列出所有命令码
python3 ~/.claude/skills/dji-referee/query_simple.py --list

# JSON 格式输出（用于程序化处理）
python3 ~/.claude/skills/dji-referee/query_simple.py --json "图传链路波特率"
```

### 2. 后处理和精准回答

查询工具返回相关切片后，Claude 需要：
- **理解用户真正的需求**
- **从多个结果中提取关键信息**
- **简化并精准地回答**
- **提供使用示例和建议**

### 3. 回答示例

**用户问:** `/dji-referee 如何获取机器人血量？`

**Claude 执行:**
```bash
python3 ~/.claude/skills/dji-referee/query_simple.py "如何获取机器人血量"
```

**工具返回:** 命令码 0x0003 的完整定义（包含数据格式表格）

**Claude 回答:**
"要获取机器人血量，使用命令码 **0x0003**。该命令以 3Hz 频率发送，包含：
- 己方各机器人血量（每个 2 字节）
- 前哨站血量（2 字节）
- 基地血量（2 字节）

注意：若机器人未上场或被罚下，血量为 0。"

## Examples

### 示例 1: 查询命令码

**用户:** `/dji-referee 0x0201 是什么命令？`

**Claude 执行:**
```bash
python3 ~/.claude/skills/dji-referee/query_simple.py 0x0201
```

**输出:**
```
📋 命令码: 0X0201
📝 描述: 机器人性能体系数据，固定以 10Hz 频率发送
📏 数据长度: 13 字节
📡 链路类型: 常规链路
🔄 发送方/接收方: 主控模块→对应机器人

[详细数据格式表格...]
```

**Claude 回答:**
"0x0201 是机器人性能体系数据命令码，以 10Hz 频率从主控模块发送到对应机器人。数据长度为 13 字节，包含机器人 ID 和等级信息。[根据表格详细解释各字段...]"

### 示例 2: 自然语言查询

**用户:** `/dji-referee 图传链路的波特率是多少`

**Claude 执行:**
```bash
python3 ~/.claude/skills/dji-referee/query_simple.py "图传链路波特率"
```

**输出:**
```
🔍 查询: 图传链路波特率
📊 找到 3 个相关结果

[包含串口协议格式章节，说明图传链路波特率为 921600]
```

**Claude 回答:**
"图传链路的波特率为 **921600**。

根据协议文档，裁判系统串口有三种数据链路：
- 常规链路：波特率 115200
- 图传链路：波特率 921600 ← 你询问的
- 雷达无线链路：通过电磁波传输

图传链路由裁判系统选手端和图传模块进行数据转发。"

### 示例 3: 列出所有命令码

**用户:** `/dji-referee 列出所有命令码`

**Claude 执行:**
```bash
python3 ~/.claude/skills/dji-referee/query_simple.py --list
```

**输出:**
```
📋 共有 19 个命令码:

  0X0001: 比赛状态数据，固定以 1Hz 频率发送...
  0X0002: 比赛结果数据，比赛结束触发发送...
  0X0003: 机器人血量数据，固定以 3Hz 频率发送...
  ...
```

## Document Structure

知识库包含以下类型的切片：

1. **命令码切片** (command_code) - 19 个
   - 元数据：cmd_id, data_length, description, sender_receiver, link_type
   - 内容：完整的数据格式表格和说明

2. **章节切片** (section) - 50 个
   - 元数据：title, level, section
   - 内容：章节文本内容

3. **自定义协议切片** (custom_protocol) - 35 个
   - 元数据：protocol_name, section
   - 内容：协议定义和数据结构

## Command Line Options

```bash
python3 query_simple.py [选项] <查询内容>

选项:
  --list              列出所有命令码
  --stats             显示知识库统计
  --json              以 JSON 格式输出
  -n, --num-results N 返回 N 个结果（默认 3）
```

## Technical Details

### 架构设计

```
用户问题
    ↓
Claude Code (你)
    ↓
query_simple.py (关键词检索)
    ↓
返回相关切片
    ↓
Claude Code (分析和回答)
    ↓
用户得到答案
```

**优势：**
- ✅ 无需额外依赖
- ✅ 无需下载模型
- ✅ 无初始化时间
- ✅ 利用 Claude Code 的语义理解能力
- ✅ 更灵活的回答方式

### 查询流程

1. 用户输入 → 关键词提取
2. 评分匹配 → 检索 top-k 切片
3. 返回结构化结果
4. Claude Code 分析并生成回答

## Performance

- **启动时间**: <100ms（无需初始化）
- **查询延迟**: <50ms（纯内存操作）
- **存储空间**: 152KB（仅 chunks.json）
- **依赖**: 0（纯 Python 标准库）

## Troubleshooting

### 问题：找不到 query_simple.py

**解决：**
```bash
# 重新安装 referee skill
npx skills add unnc-aim/aim-common-agentic-skills --skill dji-referee -g
```

### 问题：查询结果不准确

**解决：**
1. 增加返回结果数：`-n 5`
2. 使用更具体的查询词
3. 直接使用命令码查询

## allowed-tools

- `Bash(*)` - 执行查询脚本
