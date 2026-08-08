# 添加新文档到 Referee 知识库

## 功能说明

支持将新的 RoboMaster 相关文档添加到现有知识库，自动切片并合并。

## 使用方法

### 1. 添加新文档

```bash
python3 add_document.py add <文档路径> --name <文档名称>
```

**示例：**
```bash
# 添加新的协议文档
python3 add_document.py add ~/Downloads/RoboMaster_2027_Protocol.md --name "2027协议"

# 添加规则手册
python3 add_document.py add ~/Documents/RoboMaster_Rules.md --name "规则手册"
```

### 2. 查看知识库内容

```bash
python3 add_document.py list
```

**输出示例：**
```
📚 知识库统计:
   总切片数: 156

📄 包含的文档:
   1. 2026通信协议
      切片数: 104
      路径: /path/to/protocol_2026.md

   2. 2027协议
      切片数: 52
      路径: /path/to/protocol_2027.md

📊 切片类型分布:
   命令码: 25
   章节: 95
   自定义协议: 36
```

## 工作流程

1. **解析新文档** - 使用相同的切片策略（命令码、章节、协议）
2. **添加来源标记** - 每个切片标记来源文档
3. **避免冲突** - 自动处理重复的 chunk_id
4. **备份原文件** - 自动备份为 `.json.backup`
5. **合并保存** - 更新 chunks.json

## 文档格式要求

支持的文档格式：
- ✅ Markdown (.md)
- ✅ 包含命令码表格（`| 0x0001 | ...`）
- ✅ 包含数据格式表格（`表 1-5 0x0001`）
- ✅ 标准的 Markdown 标题层级

## 切片策略

新文档会使用相同的切片策略：

1. **命令码切片**
   - 识别命令码表格
   - 查找对应的数据格式表格
   - 提取完整定义

2. **章节切片**
   - 按 Markdown 标题分割
   - 保留上下文信息

3. **自定义协议切片**
   - 提取协议定义章节
   - 按子章节分割

## 示例场景

### 场景 1: 添加新版本协议

```bash
# 2027 年新协议发布
python3 add_document.py add RoboMaster_2027_Protocol.md --name "2027协议"

# 查看更新后的知识库
python3 add_document.py list

# 测试查询
python3 query_simple.py "2027 新增的命令码"
```

### 场景 2: 添加补充文档

```bash
# 添加规则手册
python3 add_document.py add RoboMaster_Rules_2026.md --name "2026规则"

# 添加技术规范
python3 add_document.py add Technical_Specs.md --name "技术规范"

# 查询时会搜索所有文档
python3 query_simple.py "机器人尺寸限制"
```

### 场景 3: 管理侧预处理

作为维护者，你可以：

```bash
# 1. 添加多个文档
python3 add_document.py add doc1.md --name "文档1"
python3 add_document.py add doc2.md --name "文档2"

# 2. 生成新的 chunks.json
# chunks.json 现在包含所有文档的切片

# 3. 分发给用户
# 用户只需要下载更新后的 chunks.json
```

## 注意事项

1. **备份** - 每次添加文档前会自动备份原 chunks.json
2. **冲突处理** - 重复的 chunk_id 会自动重命名（添加 _v2 后缀）
3. **来源追踪** - 每个切片都标记了来源文档
4. **增量更新** - 不会删除现有切片，只会添加新切片

## 恢复备份

如果添加文档后发现问题：

```bash
# 恢复备份
cp chunks.json.backup chunks.json

# 或者重新开始
rm chunks.json
# 重新运行 ingest.py 生成基础知识库
```

## 高级用法

### 指定输出文件

```bash
# 生成到不同的文件
python3 add_document.py add new_doc.md --name "新文档" --output custom_chunks.json
```

### 批量添加

```bash
#!/bin/bash
# 批量添加多个文档

for doc in docs/*.md; do
    name=$(basename "$doc" .md)
    python3 add_document.py add "$doc" --name "$name"
done
```

## 查询更新后的知识库

添加文档后，查询工具会自动使用更新后的 chunks.json：

```bash
# 查询会搜索所有文档
python3 query_simple.py "你的问题"

# 查看统计
python3 query_simple.py --stats
```

## 故障排除

### 问题：文档解析失败

**原因：** 文档格式不符合预期

**解决：** 检查文档是否包含标准的 Markdown 格式和表格

### 问题：切片数量异常

**原因：** 文档结构特殊

**解决：** 查看日志输出，确认切片统计是否合理

### 问题：查询结果不包含新文档

**原因：** chunks.json 未更新

**解决：** 确认 add_document.py 执行成功，检查 chunks.json 文件大小是否增加
