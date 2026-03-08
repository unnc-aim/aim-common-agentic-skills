#!/usr/bin/env python3
"""
Referee 查询命令行工具
"""
import sys
import argparse
from pathlib import Path
from typing import Optional
import anthropic

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from vectorstore import RefereeVectorStore


class RefereeQuery:
    """裁判系统协议查询器"""

    def __init__(self, api_key: Optional[str] = None):
        self.store = RefereeVectorStore()

        # 初始化 Claude API（如果提供了 API key）
        self.client = None
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)

    def query(self, query_text: str, use_ai: bool = True, n_results: int = 3):
        """执行查询"""
        print(f"\n🔍 查询: {query_text}\n")

        # 检查是否是命令码查询
        if query_text.strip().upper().startswith('0X') or \
           (len(query_text.strip()) == 6 and query_text.strip()[0] == '0'):
            return self._query_cmd_id(query_text.strip())

        # 向量检索
        results = self.store.query(query_text, n_results=n_results)

        if not results:
            print("❌ 未找到相关内容")
            return

        # 如果启用 AI 且有 API key，使用 Claude 生成回答
        if use_ai and self.client:
            self._ai_answer(query_text, results)
        else:
            self._simple_answer(results)

    def _query_cmd_id(self, cmd_id: str):
        """精确查询命令码"""
        result = self.store.query_by_cmd_id(cmd_id)

        if not result:
            print(f"❌ 未找到命令码 {cmd_id}")
            return

        print(f"📋 命令码: {result['metadata']['cmd_id']}")
        print(f"📝 描述: {result['metadata']['description']}")
        print(f"📏 数据长度: {result['metadata']['data_length']} 字节")
        print(f"📡 链路类型: {result['metadata']['link_type']}")
        print(f"🔄 发送方/接收方: {result['metadata']['sender_receiver']}")
        print(f"\n{'='*60}\n")
        print(result['content'])

    def _simple_answer(self, results):
        """简单输出检索结果"""
        for i, result in enumerate(results, 1):
            print(f"{'='*60}")
            print(f"结果 {i} - {result['metadata'].get('cmd_id', result['metadata'].get('title', 'N/A'))}")
            print(f"类型: {result['metadata']['type']}")
            if result['metadata']['type'] == 'command_code':
                print(f"描述: {result['metadata']['description']}")
            print(f"{'='*60}\n")
            print(result['content'][:500])  # 只显示前 500 字符
            print("\n")

    def _ai_answer(self, query_text: str, results):
        """使用 Claude AI 生成回答"""
        # 构建上下文
        context = "\n\n---\n\n".join([
            f"[来源: {r['metadata'].get('cmd_id', r['metadata'].get('title', 'N/A'))}]\n{r['content']}"
            for r in results
        ])

        prompt = f"""你是 RoboMaster 裁判系统协议专家。基于以下协议文档内容回答用户问题。

用户问题: {query_text}

相关协议内容:
{context}

请提供准确、详细的回答。如果涉及命令码，请说明其用途、数据格式和使用场景。"""

        print("🤖 AI 正在分析...\n")

        try:
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            answer = message.content[0].text
            print(f"{'='*60}")
            print("AI 回答:")
            print(f"{'='*60}\n")
            print(answer)
            print(f"\n{'='*60}")
            print(f"参考来源: {', '.join([r['metadata'].get('cmd_id', r['chunk_id']) for r in results])}")

        except Exception as e:
            print(f"❌ AI 查询失败: {e}")
            print("\n降级到简单输出模式:\n")
            self._simple_answer(results)

    def list_commands(self):
        """列出所有命令码"""
        cmd_ids = self.store.list_all_cmd_ids()
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
        description="RoboMaster 裁判系统协议查询工具"
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
        '--no-ai',
        action='store_true',
        help='禁用 AI 回答，仅显示检索结果'
    )
    parser.add_argument(
        '--api-key',
        help='Claude API Key（可选，用于 AI 回答）'
    )
    parser.add_argument(
        '-n',
        '--num-results',
        type=int,
        default=3,
        help='返回结果数量（默认 3）'
    )

    args = parser.parse_args()

    # 从环境变量获取 API key
    api_key = args.api_key
    if not api_key:
        import os
        api_key = os.getenv('ANTHROPIC_API_KEY')

    querier = RefereeQuery(api_key=api_key if not args.no_ai else None)

    if args.list:
        querier.list_commands()
    elif args.stats:
        querier.stats()
    elif args.query:
        query_text = ' '.join(args.query)
        querier.query(query_text, use_ai=not args.no_ai, n_results=args.num_results)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
