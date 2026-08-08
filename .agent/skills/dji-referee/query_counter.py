#!/usr/bin/env python3
"""
Referee 查询计数器和文档打开工具
跟踪查询次数，超过阈值时提示用户直接查看文档
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


class QueryCounter:
    """查询计数器"""

    def __init__(self, counter_file: str = None):
        if counter_file is None:
            counter_file = Path.home() / ".claude" / "referee_query_count.json"

        self.counter_file = Path(counter_file)
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)

        # 协议文档路径
        self.doc_path = Path(__file__).parent / "RoboMaster_2026_Protocol.md"
        if not self.doc_path.exists():
            # 尝试查找原始文档
            possible_paths = [
                Path.home() / "Downloads" / "RoboMaster 2026 机甲大师高校系列赛通信协议 V1.2.0（20260209）" / "RoboMaster 2026 机甲大师高校系列赛通信协议 V1.2.0（20260209）.md",
                Path(__file__).parent / "protocol.md"
            ]
            for p in possible_paths:
                if p.exists():
                    self.doc_path = p
                    break

    def _load_counter(self) -> dict:
        """加载计数器"""
        if not self.counter_file.exists():
            return {"count": 0, "last_reset": datetime.now().isoformat()}

        try:
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
                # 检查是否需要重置（超过 1 小时）
                last_reset = datetime.fromisoformat(data.get("last_reset", datetime.now().isoformat()))
                if datetime.now() - last_reset > timedelta(hours=1):
                    return {"count": 0, "last_reset": datetime.now().isoformat()}
                return data
        except:
            return {"count": 0, "last_reset": datetime.now().isoformat()}

    def _save_counter(self, data: dict):
        """保存计数器"""
        with open(self.counter_file, 'w') as f:
            json.dump(data, f)

    def increment(self) -> int:
        """增加计数并返回当前值"""
        data = self._load_counter()
        data["count"] += 1
        self._save_counter(data)
        return data["count"]

    def reset(self):
        """重置计数器"""
        data = {"count": 0, "last_reset": datetime.now().isoformat()}
        self._save_counter(data)

    def get_count(self) -> int:
        """获取当前计数"""
        return self._load_counter()["count"]

    def should_suggest_manual_search(self, threshold: int = 5) -> bool:
        """是否应该建议手动搜索"""
        return self.get_count() >= threshold

    def open_document(self):
        """打开协议文档"""
        if not self.doc_path.exists():
            print(f"⚠️  协议文档未找到: {self.doc_path}")
            print("请将协议文档放置在以下位置之一：")
            print(f"  - {Path(__file__).parent / 'RoboMaster_2026_Protocol.md'}")
            print(f"  - {Path(__file__).parent / 'protocol.md'}")
            return False

        try:
            # macOS
            subprocess.run(['open', str(self.doc_path)], check=True)
            return True
        except:
            try:
                # Linux
                subprocess.run(['xdg-open', str(self.doc_path)], check=True)
                return True
            except:
                print(f"⚠️  无法自动打开文档，请手动打开: {self.doc_path}")
                return False


def check_and_suggest(force: bool = False) -> bool:
    """
    检查查询次数并建议手动搜索

    返回 True 表示应该继续查询，False 表示应该停止
    """
    counter = QueryCounter()

    # 如果使用 --force，重置计数器并继续
    if force:
        counter.reset()
        return True

    # 增加计数
    count = counter.increment()

    # 检查是否超过阈值
    if count > 5:
        print("\n" + "="*60)
        print("💡 提示：你已经查询了 5 次以上")
        print("="*60)
        print()
        print("建议直接打开协议文档使用 Cmd+F (macOS) 或 Ctrl+F (Linux/Windows) 搜索，")
        print("这样可能更快找到你需要的信息。")
        print()

        # 尝试打开文档
        if counter.open_document():
            print(f"✓ 已打开协议文档")
            print()

        print("如果仍想使用查询工具，请添加 --force 或 -f 参数：")
        print(f"  python3 query_simple.py --force \"你的查询\"")
        print()
        print("计数器将在 1 小时后自动重置。")
        print("="*60)
        return False

    return True


def main():
    """命令行工具"""
    import argparse

    parser = argparse.ArgumentParser(description="Referee 查询计数器管理")
    parser.add_argument('--reset', action='store_true', help='重置计数器')
    parser.add_argument('--count', action='store_true', help='显示当前计数')
    parser.add_argument('--open', action='store_true', help='打开协议文档')

    args = parser.parse_args()

    counter = QueryCounter()

    if args.reset:
        counter.reset()
        print("✓ 计数器已重置")
    elif args.count:
        count = counter.get_count()
        print(f"当前查询次数: {count}")
        if count >= 5:
            print("💡 建议使用 Cmd+F 直接搜索文档")
    elif args.open:
        counter.open_document()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
