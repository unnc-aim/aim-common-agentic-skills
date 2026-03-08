# Referee Skill

RoboMaster 裁判系统通信协议智能查询 skill。基于 RAG（检索增强生成）技术，支持自然语言查询、命令码精确查找和语义搜索。

## Trigger

当用户提到以下内容时激活：
- `/referee` 命令
- 查询 RoboMaster 协议、裁判系统、通信协议
- 询问命令码（如 "0x0001 是什么"）
- 询问数据格式、通信链路等协议相关问题

## Capabilities

1. **智能文档切片** - 按命令码、章节、协议类型精确切分
2. **向量语义搜索** - 支持模糊匹配和自然语言查询
3. **命令码精确查找** - 通过命令码 ID 快速定位
4. **AI 增强回答** - 使用 Claude API 生成详细解释
5. **反向查询** - 支持按类型、链路、发送方等元数据过滤

## Setup

### 首次使用

1. 安装依赖：
```bash
pip3 install chromadb anthropic
```

2. 初始化知识库：
```bash
.claude/skills/referee/init.sh
```

这将：
- 解析协议文档（2000+ 行）
- 生成结构化切片（命令码、章节、自定义协议）
- 向量化并存储到本地数据库

### 配置 API Key（可选）

如需 AI 增强回答，设置环境变量：
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

或在查询时指定：
```bash
python3 query.py --api-key "your-key" "查询内容"
```

## Usage

### 基本查询

```bash
# 自然语言查询
python3 .claude/skills/referee/query.py "如何获取机器人血量？"
python3 .claude/skills/referee/query.py "图传链路的波特率是多少"
python3 .claude/skills/referee/query.py "实时射击数据的格式"

# 命令码精确查询
python3 .claude/skills/referee/query.py 0x0003
python3 .claude/skills/referee/query.py 0x0201

# 列出所有命令码
python3 .claude/skills/referee/query.py --list

# 查看知识库统计
python3 .claude/skills/referee/query.py --stats
```

### 高级选项

```bash
# 禁用 AI，仅显示检索结果
python3 .claude/skills/referee/query.py --no-ai "查询内容"

# 返回更多结果
python3 .claude/skills/referee/query.py -n 5 "查询内容"

# 指定 API key
python3 .claude/skills/referee/query.py --api-key "sk-..." "查询内容"
```

## Claude Code Integration

当 skill 被激活时，Claude 应该：

1. **识别查询意图**
   - 命令码查询 → 使用精确查找
   - 概念性问题 → 使用语义搜索
   - 列表请求 → 使用 --list

2. **执行查询**
   ```bash
   python3 .claude/skills/referee/query.py "<用户问题>"
   ```

3. **解释结果**
   - 如果启用了 AI，结果已经是格式化的回答
   - 如果禁用 AI，需要 Claude 解释检索到的原始内容

4. **提供后续建议**
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

[详细数据格式表格...]
```

### 示例 2: 自然语言查询

**用户:** 如何获取机器人的实时位置？

**Claude 执行:**
```bash
python3 .claude/skills/referee/query.py "如何获取机器人的实时位置"
```

**输出:**
```
🤖 AI 回答:
机器人的实时位置通过命令码 0x0203 获取。该命令以 1Hz 频率发送，
包含以下数据：
- x 坐标（4 字节，单位：米）
- y 坐标（4 字节，单位：米）
- 朝向角度（4 字节，单位：度，正北为 0 度）

数据格式：
[详细表格...]

参考来源: 0X0203
```

### 示例 3: 列出所有命令码

**用户:** 列出所有可用的命令码

**Claude 执行:**
```bash
python3 .claude/skills/referee/query.py --list
```

## Document Structure

知识库包含以下类型的切片：

1. **命令码切片** (command_code)
   - 元数据：cmd_id, data_length, description, sender_receiver, link_type
   - 内容：完整的数据格式表格和说明

2. **章节切片** (section)
   - 元数据：title, level, section
   - 内容：章节文本内容

3. **自定义协议切片** (custom_protocol)
   - 元数据：protocol_name, section
   - 内容：协议定义和数据结构

## Technical Details

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
3. 构建上下文 → 传给 Claude API
4. 生成结构化回答

## Limitations

- 知识库是静态的，仅包含初始化时的协议文档
- 需要手动重新初始化以更新协议版本
- AI 回答需要 Claude API key 和网络连接
- 向量搜索质量依赖于嵌入模型

## Troubleshooting

### 知识库未初始化

```bash
.claude/skills/referee/init.sh
```

### 依赖缺失

```bash
pip3 install chromadb anthropic
```

### API Key 未设置

```bash
export ANTHROPIC_API_KEY="your-key"
# 或使用 --no-ai 禁用 AI 功能
```

### 协议文档路径错误

编辑 `init.sh`，修改 `PROTOCOL_DOC` 变量

## allowed-tools

- `Bash(*)` - 执行查询脚本和初始化命令
