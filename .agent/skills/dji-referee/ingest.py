#!/usr/bin/env python3
"""
RoboMaster 协议文档智能切片和向量化工具
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DocumentChunk:
    """文档切片"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str


class ProtocolDocumentSlicer:
    """RoboMaster 协议文档切片器"""

    def __init__(self, doc_path: str):
        self.doc_path = Path(doc_path)
        self.content = self.doc_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.chunks: List[DocumentChunk] = []

    def parse(self) -> List[DocumentChunk]:
        """解析文档并生成切片"""
        self._extract_command_codes()
        self._extract_sections()
        self._extract_custom_client_protocol()
        return self.chunks

    def _extract_command_codes(self):
        """提取所有命令码及其详细定义"""
        # 匹配命令码表格行：| 0x0001 | 11 | 比赛状态数据...
        cmd_pattern = re.compile(r'\|\s*(0x[0-9A-Fa-f]{4})\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|')

        # 匹配数据表格：表 1-5 0x0001
        table_pattern = re.compile(r'^表\s+[\d-]+\s+(0x[0-9A-Fa-f]{4})')

        # 第一步：收集所有命令码的基本信息
        cmd_info = {}
        for i, line in enumerate(self.lines):
            match = cmd_pattern.search(line)
            if match:
                cmd_id = match.group(1).upper()
                data_len = match.group(2)
                description = match.group(3).strip()

                # 提取发送方/接收方信息（下一列）
                next_cols = line.split('|')
                sender_receiver = next_cols[4].strip() if len(next_cols) > 4 else ""
                link_type = next_cols[5].strip() if len(next_cols) > 5 else ""

                cmd_info[cmd_id] = {
                    'cmd_id': cmd_id,
                    'data_length': data_len,
                    'description': description,
                    'sender_receiver': sender_receiver,
                    'link_type': link_type,
                    'line_num': i
                }

        # 第二步：为每个命令码查找对应的详细表格
        processed_cmds = set()

        for i, line in enumerate(self.lines):
            match = table_pattern.match(line.strip())
            if match:
                cmd_id = match.group(1).upper()
                if cmd_id not in cmd_info:
                    continue

                # 提取表格内容（从当前行到下一个空行或下一个表格）
                table_lines = [line]
                j = i + 1
                while j < len(self.lines):
                    next_line = self.lines[j]
                    # 遇到新的表格或章节标题，停止
                    if (next_line.strip().startswith('表 ') or
                        next_line.strip().startswith('#') or
                        (next_line.strip() == '' and j > i + 3)):
                        break
                    table_lines.append(next_line)
                    j += 1

                # 继续向后查找相关说明（直到遇到下一个表格或图片标记）
                while j < len(self.lines):
                    next_line = self.lines[j]
                    if (next_line.strip().startswith('表 ') or
                        next_line.strip().startswith('![Image]') or
                        table_pattern.match(next_line.strip())):
                        break
                    if next_line.strip():  # 非空行
                        table_lines.append(next_line)
                    j += 1

                # 生成切片
                chunk_content = '\n'.join(table_lines)
                chunk = DocumentChunk(
                    content=chunk_content,
                    metadata={
                        'type': 'command_code',
                        'cmd_id': cmd_id,
                        'data_length': cmd_info[cmd_id]['data_length'],
                        'description': cmd_info[cmd_id]['description'],
                        'sender_receiver': cmd_info[cmd_id]['sender_receiver'],
                        'link_type': cmd_info[cmd_id]['link_type'],
                        'section': '串口协议'
                    },
                    chunk_id=f"cmd_{cmd_id}"
                )
                self.chunks.append(chunk)
                processed_cmds.add(cmd_id)

        # 第三步：为没有详细表格的命令码生成基本切片
        for cmd_id, info in cmd_info.items():
            if cmd_id not in processed_cmds:
                # 生成基本信息切片
                chunk_content = f"命令码: {cmd_id}\n"
                chunk_content += f"数据长度: {info['data_length']} 字节\n"
                chunk_content += f"描述: {info['description']}\n"
                if info['sender_receiver']:
                    chunk_content += f"发送方/接收方: {info['sender_receiver']}\n"
                if info['link_type']:
                    chunk_content += f"数据链路: {info['link_type']}\n"

                chunk = DocumentChunk(
                    content=chunk_content,
                    metadata={
                        'type': 'command_code',
                        'cmd_id': cmd_id,
                        'data_length': info['data_length'],
                        'description': info['description'],
                        'sender_receiver': info['sender_receiver'],
                        'link_type': info['link_type'],
                        'section': '串口协议',
                        'has_detail_table': False
                    },
                    chunk_id=f"cmd_{cmd_id}"
                )
                self.chunks.append(chunk)

    def _extract_sections(self):
        """提取章节内容（不包含命令码表格）"""
        section_pattern = re.compile(r'^(#{1,3})\s+(.+)$')
        current_section = []
        current_title = ""
        current_level = 0

        for i, line in enumerate(self.lines):
            match = section_pattern.match(line)

            if match:
                # 保存上一个章节
                if current_section and current_title:
                    self._save_section_chunk(current_title, current_section, current_level)

                # 开始新章节
                current_level = len(match.group(1))
                current_title = match.group(2).strip()
                current_section = [line]
            else:
                # 跳过命令码表格行和数据表格（已在 _extract_command_codes 中处理）
                if (line.strip().startswith('| 0x') or
                    line.strip().startswith('表 ') and '0x' in line):
                    continue
                current_section.append(line)

        # 保存最后一个章节
        if current_section and current_title:
            self._save_section_chunk(current_title, current_section, current_level)

    def _save_section_chunk(self, title: str, lines: List[str], level: int):
        """保存章节切片"""
        content = '\n'.join(lines).strip()

        # 跳过太短的章节（少于 50 字符）
        if len(content) < 50:
            return

        # 跳过只包含图片的章节
        if content.count('![Image]') > len(content) / 20:
            return

        chunk = DocumentChunk(
            content=content,
            metadata={
                'type': 'section',
                'title': title,
                'level': level,
                'section': title
            },
            chunk_id=f"section_{title.replace(' ', '_')}"
        )
        self.chunks.append(chunk)

    def _extract_custom_client_protocol(self):
        """提取自定义客户端协议定义"""
        # 查找 "# 自定义客户端协议" 章节
        start_idx = None
        for i, line in enumerate(self.lines):
            if line.strip() == '# 自定义客户端协议':
                start_idx = i
                break

        if start_idx is None:
            return

        # 提取每个协议定义（### 开头的子章节）
        protocol_pattern = re.compile(r'^###\s+(.+)$')
        current_protocol = []
        current_name = ""

        for i in range(start_idx, len(self.lines)):
            line = self.lines[i]
            match = protocol_pattern.match(line)

            if match:
                # 保存上一个协议
                if current_protocol and current_name:
                    self._save_protocol_chunk(current_name, current_protocol)

                # 开始新协议
                current_name = match.group(1).strip()
                current_protocol = [line]
            else:
                current_protocol.append(line)

        # 保存最后一个协议
        if current_protocol and current_name:
            self._save_protocol_chunk(current_name, current_protocol)

    def _save_protocol_chunk(self, name: str, lines: List[str]):
        """保存自定义客户端协议切片"""
        content = '\n'.join(lines).strip()

        if len(content) < 50:
            return

        chunk = DocumentChunk(
            content=content,
            metadata={
                'type': 'custom_protocol',
                'protocol_name': name,
                'section': '自定义客户端协议'
            },
            chunk_id=f"protocol_{name.replace(' ', '_')}"
        )
        self.chunks.append(chunk)

    def save_chunks(self, output_path: str):
        """保存切片到 JSON 文件"""
        output = {
            'document': str(self.doc_path),
            'total_chunks': len(self.chunks),
            'chunks': [
                {
                    'chunk_id': chunk.chunk_id,
                    'content': chunk.content,
                    'metadata': chunk.metadata
                }
                for chunk in self.chunks
            ]
        }

        Path(output_path).write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"✓ 已保存 {len(self.chunks)} 个切片到 {output_path}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python ingest.py <协议文档路径>")
        sys.exit(1)

    doc_path = sys.argv[1]
    output_path = Path(__file__).parent / "chunks.json"

    print(f"正在解析文档: {doc_path}")
    slicer = ProtocolDocumentSlicer(doc_path)
    chunks = slicer.parse()

    print(f"\n切片统计:")
    print(f"  命令码切片: {sum(1 for c in chunks if c.metadata['type'] == 'command_code')}")
    print(f"  章节切片: {sum(1 for c in chunks if c.metadata['type'] == 'section')}")
    print(f"  自定义协议切片: {sum(1 for c in chunks if c.metadata['type'] == 'custom_protocol')}")
    print(f"  总计: {len(chunks)}")

    slicer.save_chunks(str(output_path))


if __name__ == '__main__':
    main()

