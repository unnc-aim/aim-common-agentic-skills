# 查询次数限制功能

## 功能说明

为了提高查询效率，当在单次会话中查询超过 5 次时，系统会自动提示用户直接打开协议文档使用 Cmd+F 搜索。

## 工作原理

1. **计数跟踪** - 每次查询时自动增加计数器
2. **阈值检测** - 超过 5 次查询时触发提示
3. **自动打开文档** - 尝试自动打开协议文档
4. **自动重置** - 计数器在 1 小时后自动重置

## 使用方法

### 正常查询

```bash
# 前 5 次查询正常工作
python3 query_simple.py "如何获取机器人血量"
python3 query_simple.py 0x0003
...

# 第 6 次查询时会看到提示
python3 query_simple.py "射击数据"
```

**输出示例：**
```
============================================================
💡 提示：你已经查询了 5 次以上
============================================================

建议直接打开协议文档使用 Cmd+F (macOS) 或 Ctrl+F (Linux/Windows) 搜索，
这样可能更快找到你需要的信息。

✓ 已打开协议文档

如果仍想使用查询工具，请添加 --force 或 -f 参数：
  python3 query_simple.py --force "你的查询"

计数器将在 1 小时后自动重置。
============================================================
```

### 强制查询（绕过限制）

```bash
# 使用 --force 或 -f 参数
python3 query_simple.py --force "你的查询"
python3 query_simple.py -f 0x0208
```

使用 `--force` 参数会：
- 重置计数器
- 继续执行查询
- 不显示提示信息

### 管理计数器

```bash
# 查看当前查询次数
python3 query_counter.py --count

# 手动重置计数器
python3 query_counter.py --reset

# 手动打开协议文档
python3 query_counter.py --open
```

## 配置

### 文档路径

系统会按以下顺序查找协议文档：

1. `~/.claude/skills/dji-referee/RoboMaster_2026_Protocol.md`
2. `~/.claude/skills/dji-referee/protocol.md`
3. `~/Downloads/RoboMaster 2026 机甲大师高校系列赛通信协议 V1.2.0（20260209）/...`

如果文档未找到，会显示警告信息。

### 计数器存储

计数器数据存储在：
```
~/.claude/referee_query_count.json
```

包含：
- `count`: 当前查询次数
- `last_reset`: 上次重置时间

## 在 Claude Code 中使用

当你在 Claude Code 中使用 `/dji-referee` 时：

**前 5 次查询：**
```
你: /dji-referee 如何获取机器人血量
Claude: [正常返回查询结果]

你: /dji-referee 0x0208 是什么
Claude: [正常返回查询结果]
...
```

**第 6 次查询：**
```
你: /dji-referee 射击数据格式
Claude: 你已经查询了 5 次以上。建议直接打开协议文档使用 Cmd+F 搜索，
       这样可能更快。我已经为你打开了文档。

       如果仍想使用查询工具，可以说 "/dji-referee --force 射击数据格式"
```

**使用 force：**
```
你: /dji-referee --force 射击数据格式
Claude: [正常返回查询结果，计数器已重置]
```

## 设计理念

### 为什么要限制查询次数？

1. **效率考虑** - 频繁查询说明用户可能需要浏览整个文档
2. **用户体验** - 直接在文档中搜索可能更快
3. **资源优化** - 减少不必要的重复查询

### 为什么是 5 次？

- 1-2 次：快速查询特定信息
- 3-5 次：深入了解某个主题
- 6+ 次：可能需要系统性阅读文档

### 为什么提供 --force？

- 用户可能确实需要使用查询工具
- 某些场景下查询工具比手动搜索更方便
- 保持灵活性

## 示例场景

### 场景 1: 快速查询

```bash
# 用户只需要查 1-2 个命令码
python3 query_simple.py 0x0003
python3 query_simple.py 0x0208
# ✓ 正常工作，无提示
```

### 场景 2: 深入研究

```bash
# 用户需要了解整个射击系统
python3 query_simple.py "射击数据"
python3 query_simple.py "发弹量"
python3 query_simple.py "热量"
python3 query_simple.py "弹速"
python3 query_simple.py "射频"
python3 query_simple.py "弹丸类型"
# ⚠️  第 6 次触发提示，建议打开文档
```

### 场景 3: 坚持使用查询工具

```bash
# 用户更喜欢查询工具的格式化输出
python3 query_simple.py --force "弹丸类型"
python3 query_simple.py --force "装甲模块"
# ✓ 继续工作，计数器已重置
```

## 故障排除

### 问题：文档无法自动打开

**原因：** 文档路径未找到

**解决：**
```bash
# 将协议文档复制到正确位置
cp "你的文档路径.md" ~/.claude/skills/dji-referee/protocol.md

# 或手动打开
python3 query_counter.py --open
```

### 问题：计数器未重置

**原因：** 未超过 1 小时

**解决：**
```bash
# 手动重置
python3 query_counter.py --reset
```

### 问题：想禁用此功能

**解决：**
```bash
# 方法 1: 始终使用 --force
alias dji-referee='python3 ~/.claude/skills/dji-referee/query_simple.py --force'

# 方法 2: 删除计数器文件
rm ~/.claude/referee_query_count.json
```

## 技术细节

- **存储**: JSON 文件，轻量级
- **重置**: 基于时间戳，1 小时自动重置
- **文档打开**: 使用系统默认应用（`open` on macOS, `xdg-open` on Linux）
- **依赖**: 零额外依赖，纯 Python 标准库
