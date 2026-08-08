#!/usr/bin/env python3
"""
向量存储和检索模块
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class RefereeVectorStore:
    """裁判系统协议向量存储"""

    def __init__(self, persist_dir: str = None):
        if persist_dir is None:
            persist_dir = str(Path(__file__).parent / "vectorstore")

        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="robomaster_protocol",
            metadata={"description": "RoboMaster 2026 通信协议"}
        )

    def ingest_chunks(self, chunks_file: str):
        """导入切片到向量数据库"""
        chunks_data = json.loads(Path(chunks_file).read_text(encoding='utf-8'))
        chunks = chunks_data['chunks']

        print(f"正在向量化 {len(chunks)} 个切片...")

        # 准备数据
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            content = chunk['content']
            metadata = chunk['metadata']

            # 构建增强的文本内容（用于更好的检索）
            enhanced_content = self._enhance_content(content, metadata)

            ids.append(chunk_id)
            documents.append(enhanced_content)
            metadatas.append(metadata)

        # 批量添加到向量数据库
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(f"✓ 已向量化并存储 {len(chunks)} 个切片")

    def _enhance_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """增强内容以提高检索质量"""
        enhanced = content

        # 为命令码添加额外的上下文
        if metadata['type'] == 'command_code':
            prefix = f"命令码 {metadata['cmd_id']}: {metadata['description']}\n"
            prefix += f"数据长度: {metadata['data_length']} 字节\n"
            prefix += f"发送方/接收方: {metadata['sender_receiver']}\n"
            prefix += f"数据链路: {metadata['link_type']}\n\n"
            enhanced = prefix + content

        # 为自定义协议添加上下文
        elif metadata['type'] == 'custom_protocol':
            prefix = f"自定义客户端协议: {metadata['protocol_name']}\n\n"
            enhanced = prefix + content

        return enhanced

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """查询向量数据库"""
        where = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )

        # 格式化结果
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'chunk_id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def query_by_cmd_id(self, cmd_id: str) -> Optional[Dict[str, Any]]:
        """通过命令码精确查询"""
        cmd_id = cmd_id.upper()
        if not cmd_id.startswith('0X'):
            cmd_id = '0X' + cmd_id

        results = self.collection.get(
            where={"cmd_id": cmd_id}
        )

        if results['ids']:
            return {
                'chunk_id': results['ids'][0],
                'content': results['documents'][0],
                'metadata': results['metadatas'][0]
            }
        return None

    def list_all_cmd_ids(self) -> List[str]:
        """列出所有命令码"""
        results = self.collection.get(
            where={"type": "command_code"}
        )

        cmd_ids = []
        if results['metadatas']:
            cmd_ids = sorted(set(m['cmd_id'] for m in results['metadatas']))

        return cmd_ids

    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        count = self.collection.count()

        # 按类型统计
        cmd_count = len(self.collection.get(where={"type": "command_code"})['ids'])
        section_count = len(self.collection.get(where={"type": "section"})['ids'])
        protocol_count = len(self.collection.get(where={"type": "custom_protocol"})['ids'])

        return {
            'total_chunks': count,
            'command_codes': cmd_count,
            'sections': section_count,
            'custom_protocols': protocol_count
        }


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python vectorstore.py <chunks.json>")
        sys.exit(1)

    chunks_file = sys.argv[1]
    store = RefereeVectorStore()

    print("正在初始化向量数据库...")
    store.ingest_chunks(chunks_file)

    stats = store.get_stats()
    print(f"\n数据库统计:")
    print(f"  总切片数: {stats['total_chunks']}")
    print(f"  命令码: {stats['command_codes']}")
    print(f"  章节: {stats['sections']}")
    print(f"  自定义协议: {stats['custom_protocols']}")


if __name__ == '__main__':
    main()
