#!/usr/bin/env python3
"""
Referee 查询工具 - 零依赖版本
直接基于 chunks.json 进行关键词检索，无需向量数据库
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class SimpleRefereeQuery:
    """简单的协议查询器 - 基于关键词匹配"""

    def __init__(self, chunks_file: str = None):
        if chunks_file is None:
            chunks_file = Path(__file__).parent / "chunks.json"

        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.chunks = data['chunks']

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """查询相关切片"""
        # 检查是否是命令码查询
        if self._is_cmd_id(query_text):
            return self._query_cmd_id(query_text.strip().upper())

        # 关键词检索
        return self._keyword_search(query_text, n_results)

    def _is_cmd_id(self, text: str) -> bool:
        """判断是否是命令码"""
        text = text.strip().upper()
        return text.startswith('0X') or (len(text) == 6 and text[0] == '0')

    def _query_cmd_id(self, cmd_id: str) -> List[Dict[str, Any]]:
        """精确查询命令码"""
        if not cmd_id.startswith('0X'):
            cmd_id = '0X' + cmd_id

        for chunk in self.chunks:
            if chunk['metadata'].get('type') == 'command_code' and \
               chunk['metadata'].get('cmd_id') == cmd_id:
                return [chunk]
        return []

    def _keyword_search(self, query_text: str, n_results: int) -> List[Dict[str, Any]]:
        """基于关键词的简单搜索"""
        # 提取查询关键词
        keywords = self._extract_keywords(query_text)

        # 计算每个切片的相关性得分
        scored_chunks = []
        for chunk in self.chunks:
            score = self._calculate_score(chunk, keywords, query_text)
            if score > 0:
                scored_chunks.append((score, chunk))

        # 按得分排序并返回 top-k
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:n_results]]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除标点符号，分词
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()

        # 过滤停用词
        stopwords = {'的', '是', '在', '了', '和', '与', '或', '等', '如何', '什么', '怎么'}
        keywords = [w for w in words if w not in stopwords and len(w) > 1]

        return keywords

    def _calculate_score(self, chunk: Dict[str, Any], keywords: List[str], query_text: str) -> float:
        """计算切片相关性得分"""
        score = 0.0
        content = chunk['content'].lower()
        metadata = chunk['metadata']

        # 完整查询文本匹配（最高权重）
        if query_text.lower() in content:
            score += 10.0

        # 关键词匹配
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 内容匹配
            count = content.count(keyword_lower)
            score += count * 2.0

            # 元数据匹配（更高权重）
            if metadata.get('type') == 'command_code':
                if keyword_lower in metadata.get('description', '').lower():
                    score += 5.0
                if keyword_lower in metadata.get('cmd_id', '').lower():
                    score += 5.0
            elif metadata.get('type') == 'section':
                if keyword_lower in metadata.get('title', '').lower():
                    score += 5.0
            elif metadata.get('type') == 'custom_protocol':
                if keyword_lower in metadata.get('protocol_name', '').lower():
                    score += 5.0

        return score

    def list_commands(self) -> List[Dict[str, Any]]:
        """列出所有命令码"""
        commands = []
        for chunk in self.chunks:
            if chunk['metadata'].get('type') == 'command_code':
                commands.append({
                    'cmd_id': chunk['metadata']['cmd_id'],
                    'description': chunk['metadata']['description'],
                    'data_length': chunk['metadata']['data_length'],
                    'link_type': chunk['metadata']['link_type']
                })
        return sorted(commands, key=lambda x: x['cmd_id'])

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            'total': len(self.chunks),
            'command_codes': 0,
            'sections': 0,
            'custom_protocols': 0
        }

        for chunk in self.chunks:
            chunk_type = chunk['metadata'].get('type')
            if chunk_type == 'command_code':
                stats['command_codes'] += 1
            elif chunk_type == 'section':
                stats['sections'] += 1
            elif chunk_type == 'custom_protocol':
                stats['custom_protocols'] += 1

        return stats


def format_output(results: List[Dict[str, Any]], query_text: str = None, output_json: bool = False):
    """格式化输出"""
    if output_json:
        print(json.dumps({
            'total': len(results),
            'results': results
        }, ensure_ascii=False, indent=2))
        return

    if not results:
        print("❌ 未找到相关内容")
        return

    # 检查是否是命令码查询
    if len(results) == 1 and results[0]['metadata'].get('type') == 'command_code':
        result = results[0]
        print(f"\n📋 命令码: {result['metadata']['cmd_id']}")
        print(f"📝 描述: {result['metadata']['description']}")
        print(f"📏 数据长度: {result['metadata']['data_length']} 字节")
        print(f"📡 链路类型: {result['metadata']['link_type']}")
        print(f"🔄 发送方/接收方: {result['metadata']['sender_receiver']}")
        print(f"\n{'='*60}\n")
        print(result['content'])
        return

    # 普通查询结果
    if query_text:
        print(f"\n🔍 查询: {query_text}")
    print(f"📊 找到 {len(results)} 个相关结果\n")

    for i, result in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"结果 {i}")
        print(f"{'='*60}")

        metadata = result['metadata']
        print(f"类型: {metadata['type']}")

        if metadata['type'] == 'command_code':
            print(f"命令码: {metadata['cmd_id']}")
            print(f"描述: {metadata['description']}")
            print(f"数据长度: {metadata['data_length']} 字节")
            print(f"链路: {metadata['link_type']}")
        elif metadata['type'] == 'section':
            print(f"章节: {metadata['title']}")
        elif metadata['type'] == 'custom_protocol':
            print(f"协议: {metadata['protocol_name']}")

        print(f"\n{result['content'][:800]}")
        if len(result['content']) > 800:
            print("\n... (内容已截断)")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="RoboMaster 裁判系统协议查询工具（零依赖版本）"
    )
    parser.add_argument(
        'query',
        nargs='*',
        help='查询内容（支持自然语言或命令码）'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有命令码'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示知识库统计'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='以 JSON 格式输出'
    )
    parser.add_argument(
        '-n',
        '--num-results',
        type=int,
        default=3,
        help='返回结果数量（默认 3）'
    )

    args = parser.parse_args()

    try:
        querier = SimpleRefereeQuery()

        if args.list:
            commands = querier.list_commands()
            if args.json:
                print(json.dumps({'total': len(commands), 'commands': commands}, ensure_ascii=False, indent=2))
            else:
                print(f"\n📋 共有 {len(commands)} 个命令码:\n")
                for cmd in commands:
                    desc = cmd['description'][:50]
                    print(f"  {cmd['cmd_id']}: {desc}...")

        elif args.stats:
            stats = querier.get_stats()
            print("\n📊 知识库统计:")
            print(f"  总切片数: {stats['total']}")
            print(f"  命令码: {stats['command_codes']}")
            print(f"  章节: {stats['sections']}")
            print(f"  自定义协议: {stats['custom_protocols']}")

        elif args.query:
            query_text = ' '.join(args.query)
            results = querier.query(query_text, n_results=args.num_results)
            format_output(results, query_text, args.json)

        else:
            parser.print_help()

    except FileNotFoundError:
        print("❌ 错误: 未找到 chunks.json 文件")
        print("请确保在 .claude/skills/referee/ 目录下运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
