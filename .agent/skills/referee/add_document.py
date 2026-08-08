#!/usr/bin/env python3
"""
添加新文档到 Referee 知识库
支持用户侧动态添加 RoboMaster 相关文档
"""
import json
import sys
from pathlib import Path

# 导入现有的切片器
sys.path.insert(0, str(Path(__file__).parent))
from ingest import ProtocolDocumentSlicer


def add_document(doc_path: str, chunks_file: str = None, doc_name: str = None):
    """添加新文档到知识库"""
    if chunks_file is None:
        chunks_file = Path(__file__).parent / "chunks.json"

    chunks_file = Path(chunks_file)

    # 读取现有的 chunks
    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_chunks = existing_data['chunks']
        print(f"📚 现有知识库: {len(existing_chunks)} 个切片")
    else:
        existing_chunks = []
        print("📚 创建新知识库")

    # 解析新文档
    print(f"\n📄 正在解析新文档: {doc_path}")
    slicer = ProtocolDocumentSlicer(doc_path)
    new_chunks = slicer.parse()

    print(f"\n新文档切片统计:")
    print(f"  命令码切片: {sum(1 for c in new_chunks if c.metadata['type'] == 'command_code')}")
    print(f"  章节切片: {sum(1 for c in new_chunks if c.metadata['type'] == 'section')}")
    print(f"  自定义协议切片: {sum(1 for c in new_chunks if c.metadata['type'] == 'custom_protocol')}")
    print(f"  总计: {len(new_chunks)}")

    # 添加文档来源标记
    if doc_name:
        for chunk in new_chunks:
            chunk.metadata['source_document'] = doc_name
            # 修改 chunk_id 以避免冲突
            chunk.chunk_id = f"{doc_name}_{chunk.chunk_id}"

    # 检查重复的 chunk_id
    existing_ids = {c['chunk_id'] for c in existing_chunks}
    new_chunk_dicts = []
    duplicates = 0

    for chunk in new_chunks:
        chunk_dict = {
            'chunk_id': chunk.chunk_id,
            'content': chunk.content,
            'metadata': chunk.metadata
        }

        if chunk_dict['chunk_id'] in existing_ids:
            duplicates += 1
            # 添加后缀避免冲突
            chunk_dict['chunk_id'] = f"{chunk_dict['chunk_id']}_v2"

        new_chunk_dicts.append(chunk_dict)
        existing_ids.add(chunk_dict['chunk_id'])

    if duplicates > 0:
        print(f"\n⚠️  发现 {duplicates} 个重复的 chunk_id，已自动重命名")

    # 合并切片
    all_chunks = existing_chunks + new_chunk_dicts

    # 保存更新后的知识库
    output_data = {
        'documents': existing_data.get('documents', []) if chunks_file.exists() else [],
        'total_chunks': len(all_chunks),
        'chunks': all_chunks
    }

    # 添加文档记录
    if doc_name:
        if 'documents' not in output_data:
            output_data['documents'] = []
        output_data['documents'].append({
            'name': doc_name,
            'path': str(doc_path),
            'chunks_count': len(new_chunks)
        })

    # 备份原文件
    if chunks_file.exists():
        backup_file = chunks_file.with_suffix('.json.backup')
        chunks_file.rename(backup_file)
        print(f"\n💾 已备份原文件到: {backup_file}")

    # 保存新文件
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 知识库已更新!")
    print(f"   总切片数: {existing_data.get('total_chunks', 0) if chunks_file.exists() else 0} → {len(all_chunks)}")
    print(f"   新增切片: {len(new_chunks)}")
    print(f"   保存位置: {chunks_file}")

    return len(new_chunks)


def list_documents(chunks_file: str = None):
    """列出知识库中的所有文档"""
    if chunks_file is None:
        chunks_file = Path(__file__).parent / "chunks.json"

    chunks_file = Path(chunks_file)

    if not chunks_file.exists():
        print("❌ 知识库文件不存在")
        return

    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n📚 知识库统计:")
    print(f"   总切片数: {data['total_chunks']}")

    if 'documents' in data and data['documents']:
        print(f"\n📄 包含的文档:")
        for i, doc in enumerate(data['documents'], 1):
            print(f"   {i}. {doc['name']}")
            print(f"      切片数: {doc['chunks_count']}")
            print(f"      路径: {doc['path']}")
    else:
        print("\n   (未记录文档来源信息)")

    # 按类型统计
    chunks = data['chunks']
    cmd_count = sum(1 for c in chunks if c['metadata']['type'] == 'command_code')
    section_count = sum(1 for c in chunks if c['metadata']['type'] == 'section')
    protocol_count = sum(1 for c in chunks if c['metadata']['type'] == 'custom_protocol')

    print(f"\n📊 切片类型分布:")
    print(f"   命令码: {cmd_count}")
    print(f"   章节: {section_count}")
    print(f"   自定义协议: {protocol_count}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="添加新文档到 Referee 知识库"
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # add 命令
    add_parser = subparsers.add_parser('add', help='添加新文档')
    add_parser.add_argument('document', help='文档路径（Markdown 格式）')
    add_parser.add_argument('--name', help='文档名称（用于标识来源）')
    add_parser.add_argument('--output', help='输出的 chunks.json 路径')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出知识库中的文档')
    list_parser.add_argument('--chunks-file', help='chunks.json 路径')

    args = parser.parse_args()

    if args.command == 'add':
        doc_path = Path(args.document)
        if not doc_path.exists():
            print(f"❌ 错误: 文档不存在: {doc_path}")
            sys.exit(1)

        doc_name = args.name or doc_path.stem
        add_document(str(doc_path), args.output, doc_name)

    elif args.command == 'list':
        list_documents(args.chunks_file)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
