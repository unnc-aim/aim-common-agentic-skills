# Referee Skill

RoboMaster 裁判系统通信协议智能查询工具。

## 特性

- 🎯 **精确切片** - 按命令码、章节、协议类型智能分割文档
- 🔍 **语义搜索** - 支持自然语言模糊查询
- ⚡ **快速检索** - 向量化存储，毫秒级响应
- 🤖 **AI 增强** - Claude API 生成详细解释
- 📊 **元数据过滤** - 支持按类型、链路等反向查询

## 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 初始化知识库

```bash
./init.sh
```

这将解析协议文档并生成向量数据库（约需 30 秒）。

### 3. 开始查询

```bash
# 自然语言查询
python3 query.py "如何获取机器人血量？"

# 命令码查询
python3 query.py 0x0003

# 列出所有命令码
python3 query.py --list
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

| 字节偏移量 | 大小 | 说明 |
| --- | --- | --- |
| 0 | 1 | 本机器人 ID |
| 1 | 1 | 机器人等级 |
...
```

### 自然语言查询（需要 API Key）

```bash
$ export ANTHROPIC_API_KEY="your-key"
$ python3 query.py "图传链路的波特率是多少"

🤖 AI 正在分析...

============================================================
AI 回答:
============================================================

图传链路的波特率为 921600。

根据协议文档，裁判系统串口有三种数据链路：
1. 常规链路：波特率 115200
2. 图传链路：波特率 921600  ← 你询问的
3. 雷达无线链路：通过电磁波传输

图传链路由裁判系统选手端和图传模块进行数据转发，从图传模块
（发送端）的串口接收数据。

============================================================
参考来源: section_串口协议格式
```

### 列出所有命令码

```bash
$ python3 query.py --list

📋 共有 42 个命令码:

  0X0001: 比赛状态数据，固定以 1Hz 频率发送...
  0X0002: 比赛结果数据，比赛结束触发发送...
  0X0003: 机器人血量数据，固定以 3Hz 频率发送...
  ...
```

## 文件结构

```
.claude/skills/referee/
├── ingest.py           # 文档解析和切片
├── vectorstore.py      # 向量存储和检索
├── query.py            # 查询 CLI 工具
├── init.sh             # 初始化脚本
├── SKILL.md            # Skill 定义
├── requirements.txt    # Python 依赖
├── chunks.json         # 切片数据（生成）
└── vectorstore/        # 向量数据库（生成）
```

## 命令行选项

```bash
python3 query.py [选项] <查询内容>

选项:
  --list              列出所有命令码
  --stats             显示知识库统计
  --no-ai             禁用 AI，仅显示检索结果
  --api-key KEY       指定 Claude API Key
  -n, --num-results N 返回 N 个结果（默认 3）
```

## 切片策略

### 命令码切片

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

### 章节切片

按 Markdown 标题层级分割：
- `#` 一级标题（如 "串口协议"）
- `##` 二级标题（如 "命令码 ID 和常规链路数据说明"）
- `###` 三级标题（如 "选手端下发数据"）

跳过纯图片章节和过短内容。

### 自定义协议切片

提取 "自定义客户端协议" 章节下的所有子协议：
- KeyboardMouseControl
- CustomControl
- GameStatus
- RobotDynamicStatus
- ...

## 技术栈

- **向量数据库**: ChromaDB
- **嵌入模型**: sentence-transformers (默认)
- **LLM**: Claude Opus 4.6 (可选)
- **语言**: Python 3.8+

## 配置

### 修改协议文档路径

编辑 `init.sh`：
```bash
PROTOCOL_DOC="/path/to/your/protocol.md"
```

### 使用自定义嵌入模型

编辑 `vectorstore.py`，修改 ChromaDB 配置。

### 调整检索参数

在 `query.py` 中修改 `n_results` 默认值。

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

### 问题：AI 回答失败

**解决：**
1. 检查 API Key 是否正确
2. 检查网络连接
3. 使用 `--no-ai` 降级到简单模式

### 问题：查询结果不准确

**解决：**
1. 增加返回结果数：`-n 5`
2. 使用更具体的查询词
3. 直接使用命令码查询

## 性能

- **初始化时间**: ~30 秒（一次性）
- **查询延迟**: <100ms（向量检索）
- **AI 回答延迟**: 2-5 秒（取决于网络）
- **存储空间**: ~10MB（向量数据库）

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
