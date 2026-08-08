#!/usr/bin/env python3
"""
Referee 查询命令行工具 - 纯检索版本
用于 Claude Code skill，由 Claude 直接处理查询结果
"""
import sys
import argparse
import json
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from vectorstore import RefereeVectorStore


class RefereeQuery:
    """裁判系统协议查询器"""

    def __init__(self):
        self.store = RefereeVectorStore()

    def query(self, query_text: str, n_results: int = 3, output_format: str = 'text'):
        """执行查询"""
        # 检查是否是命令码查询
        if query_text.strip().upper().startswith('0X') or \
           (len(query_text.strip()) == 6 and query_text.strip()[0] == '0'):
            return self._query_cmd_id(query_text.strip(), output_format)

        # 向量检索
        results = self.store.query(query_text, n_results=n_results)

        if not results:
            if output_format == 'json':
                print(json.dumps({'error': '未找到相关内容', 'results': []}, ensure_ascii=False))
            else:
                print("❌ 未找到相关内容")
            return

        # 输出结果
        if output_format == 'json':
            self._output_json(results)
        else:
            self._output_text(query_text, results)

    def _query_cmd_id(self, cmd_id: str, output_format: str):
        """精确查询命令码"""
        result = self.store.query_by_cmd_id(cmd_id)

        if not result:
            if output_format == 'json':
                print(json.dumps({'error': f'未找到命令码 {cmd_id}', 'results': []}, ensure_ascii=False))
            else:
                print(f"❌ 未找到命令码 {cmd_id}")
            return

        if output_format == 'json':
            self._output_json([result])
        else:
            print(f"\n📋 命令码: {result['metadata']['cmd_id']}")
            print(f"📝 描述: {result['metadata']['description']}")
            print(f"📏 数据长度: {result['metadata']['data_length']} 字节")
            print(f"📡 链路类型: {result['metadata']['link_type']}")
            print(f"🔄 发送方/接收方: {result['metadata']['sender_receiver']}")
            print(f"\n{'='*60}\n")
            print(result['content'])

    def _output_text(self, query_text: str, results):
        """文本格式输出"""
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

            print(f"\n{result['content'][:800]}")  # 显示前 800 字符
            if len(result['content']) > 800:
                print("\n... (内容已截断)")
            print()

    def _output_json(self, results):
        """JSON 格式输出"""
        output = {
            'total': len(results),
            'results': [
                {
                    'chunk_id': r['chunk_id'],
                    'content': r['content'],
                    'metadata': r['metadata'],
                    'distance': r.get('distance')
                }
                for r in results
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    def list_commands(self, output_format: str = 'text'):
        """列出所有命令码"""
        cmd_ids = self.store.list_all_cmd_ids()

        if output_format == 'json':
            commands = []
            for cmd_id in cmd_ids:
                result = self.store.query_by_cmd_id(cmd_id)
                if result:
                    commands.append({
                        'cmd_id': cmd_id,
                        'description': result['metadata']['description'],
                        'data_length': result['metadata']['data_length'],
                        'link_type': result['metadata']['link_type']
                    })
            print(json.dumps({'total': len(commands), 'commands': commands}, ensure_ascii=False, indent=2))
        else:
            print(f"\n📋 共有 {len(cmd_ids)} 个命令码:\n")
            for cmd_id in cmd_ids:
                result = self.store.query_by_cmd_id(cmd_id)
                if result:
                    desc = result['metadata']['description'][:50]
                    print(f"  {cmd_id}: {desc}...")

    def stats(self):
        """显示数据库统计"""
        stats = self.store.get_stats()
        print("\n📊 知识库统计:")
        print(f"  总切片数: {stats['total_chunks']}")
        print(f"  命令码: {stats['command_codes']}")
        print(f"  章节: {stats['sections']}")
        print(f"  自定义协议: {stats['custom_protocols']}")


def main():
    parser = argparse.ArgumentParser(
        description="RoboMaster 裁判系统协议查询工具（纯检索版本）"
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
        help='以 JSON 格式输出（用于程序化处理）'
    )
    parser.add_argument(
        '-n',
        '--num-results',
        type=int,
        default=3,
        help='返回结果数量（默认 3）'
    )

    args = parser.parse_args()

    querier = RefereeQuery()
    output_format = 'json' if args.json else 'text'

    if args.list:
        querier.list_commands(output_format)
    elif args.stats:
        querier.stats()
    elif args.query:
        query_text = ' '.join(args.query)
        querier.query(query_text, n_results=args.num_results, output_format=output_format)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
