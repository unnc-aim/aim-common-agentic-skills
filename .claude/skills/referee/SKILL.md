# Referee Skill

RoboMaster 裁判系统通信协议智能查询 skill。基于 RAG（检索增强生成）技术，提供向量语义搜索，由 Claude Code 直接处理查询结果。

## Trigger

当用户提到以下内容时激活：
- `/referee` 命令
- 查询 RoboMaster 协议、裁判系统、通信协议
- 询问命令码（如 "0x0001 是什么"）
- 询问数据格式、通信链路等协议相关问题

## Capabilities

1. **智能文档切片** - 按命令码、章节、协议类型精确切分（104 个切片）
2. **向量语义搜索** - 支持模糊匹配和自然语言查询
3. **命令码精确查找** - 通过命令码 ID 快速定位
4. **元数据过滤** - 支持按类型、链路、发送方等反向查询
5. **JSON 输出** - 支持程序化处理

## Setup

### 首次使用

1. 安装依赖：
```bash
pip3 install chromadb
```

2. 初始化知识库：
```bash
cd .claude/skills/referee
python3 vectorstore.py chunks.json
```

这将：
- 加载预生成的 104 个文档切片
- 向量化并存储到本地数据库（~30 秒）
- 创建 vectorstore/ 目录

## Usage in Claude Code

当 skill 被激活时，Claude 应该：

### 1. 执行查询获取相关内容

```bash
# 自然语言查询
python3 .claude/skills/referee/query.py "如何获取机器人血量"

# 命令码精确查询
python3 .claude/skills/referee/query.py 0x0003

# 列出所有命令码
python3 .claude/skills/referee/query.py --list

# JSON 格式输出（用于程序化处理）
python3 .claude/skills/referee/query.py --json "图传链路波特率"
```

### 2. 分析检索结果

查询工具会返回相关的文档切片，包含：
- 命令码的完整数据格式
- 章节的详细说明
- 自定义协议的定义

### 3. 生成回答

基于检索到的内容，Claude 直接：
- 理解用户问题
- 分析相关切片
- 生成准确、详细的回答
- 引用来源（命令码、章节等）

### 4. 提供后续建议

- 相关命令码
- 相关章节
- 使用示例

## Examples

### 示例 1: 查询命令码

**用户:** 0x0201 是什么命令？

**Claude 执行:**
```bash
python3 .claude/skills/referee/query.py 0x0201
```

**输出:**
```
📋 命令码: 0X0201
📝 描述: 机器人性能体系数据，固定以 10Hz 频率发送
📏 数据长度: 13 字节
📡 链路类型: 常规链路
🔄 发送方/接收方: 主控模块→对应机器人

============================================================

表 1-11 0x0201
[详细数据格式表格...]
```

**Claude 回答:**
"0x0201 是机器人性能体系数据命令码，以 10Hz 频率从主控模块发送到对应机器人。数据长度为 13 字节，包含机器人 ID 和等级信息。[根据表格详细解释各字段...]"

### 示例 2: 自然语言查询

**用户:** 如何获取机器人的实时位置？

**Claude 执行:**
```bash
python3 .claude/skills/referee/query.py "如何获取机器人的实时位置"
```

**输出:**
```
🔍 查询: 如何获取机器人的实时位置
📊 找到 3 个相关结果

============================================================
结果 1
============================================================
类型: command_code
命令码: 0X0203
描述: 机器人位置数据，固定以 1Hz 频率发送
数据长度: 16 字节
链路: 常规链路

表 1-13 0x0203
[位置数据格式...]
```

**Claude 回答:**
"要获取机器人实时位置，使用命令码 0x0203。该命令以 1Hz 频率发送，包含：
- x 坐标（4 字节，单位：米）
- y 坐标（4 字节，单位：米）
- 朝向角度（4 字节，单位：度，正北为 0 度）

这是通过主控模块发送到对应机器人的常规链路数据。"

### 示例 3: JSON 格式（程序化处理）

**Claude 执行:**
```bash
python3 .claude/skills/referee/query.py --json "射击数据"
```

**输出:**
```json
{
  "total": 2,
  "results": [
    {
      "chunk_id": "cmd_0X0207",
      "content": "...",
      "metadata": {
        "type": "command_code",
        "cmd_id": "0X0207",
        "description": "实时射击数据",
        ...
      }
    }
  ]
}
```

Claude 可以解析 JSON 并提取关键信息。

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
python3 query.py [选项] <查询内容>

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
query.py (向量检索)
    ↓
返回相关切片
    ↓
Claude Code (分析和回答)
    ↓
用户得到答案
```

**优势：**
- ✅ 无需额外 API 调用
- ✅ 无额外成本
- ✅ 利用 Claude Code 的上下文理解能力
- ✅ 更灵活的回答方式
- ✅ 可以结合其他工具和代码

### 切片策略

1. **命令码切片**
   - 识别命令码表格行（`| 0x0001 | ...`）
   - 查找对应的数据格式表格（`表 1-5 0x0001`）
   - 提取完整的表格和相关说明
   - 生成元数据（命令码、长度、描述等）

2. **章节切片**
   - 按 Markdown 标题层级（#, ##, ###）分割
   - 跳过纯图片章节
   - 保留上下文信息

3. **自定义协议切片**
   - 提取 "自定义客户端协议" 章节
   - 按 ### 子章节分割
   - 保留完整的协议定义

### 向量化

- 使用 ChromaDB 作为向量数据库
- 默认使用 sentence-transformers 嵌入模型
- 支持元数据过滤和混合检索

### 查询流程

1. 用户输入 → 向量化
2. 相似度搜索 → 检索 top-k 切片
3. 返回结构化结果
4. Claude Code 分析并生成回答

## Performance

- **初始化**: ~30 秒（一次性）
- **查询延迟**: <100ms（向量检索）
- **存储空间**: ~10MB（向量数据库）

## Limitations

- 知识库是静态的，仅包含初始化时的协议文档
- 需要手动重新初始化以更新协议版本
- 向量搜索质量依赖于嵌入模型

## Troubleshooting

### 知识库未初始化

```bash
cd .claude/skills/referee
python3 vectorstore.py chunks.json
```

### 依赖缺失

```bash
pip3 install chromadb
```

### 协议文档路径错误

编辑 `init.sh`，修改 `PROTOCOL_DOC` 变量

## allowed-tools

- `Bash(*)` - 执行查询脚本和初始化命令
