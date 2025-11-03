"""
Ledger 财务记录解析器
解析Poker Now的ledger.csv文件，获取玩家真实的买入、离场和盈亏数据
"""

import csv
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class LedgerEntry:
    """财务记录条目"""
    player_nickname: str
    player_id: str
    session_start: str
    session_end: str
    buy_in: float
    buy_out: float
    stack: float
    net: float
    
    @property
    def player_key(self) -> str:
        """玩家完整标识"""
        return f"{self.player_nickname} @ {self.player_id}"


class LedgerParser:
    """Ledger解析器"""
    
    def parse_file(self, filepath: str) -> List[LedgerEntry]:
        """
        解析ledger.csv文件
        
        Args:
            filepath: ledger.csv文件路径
            
        Returns:
            财务记录列表
        """
        entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entry = self._parse_row(row)
                    if entry:
                        entries.append(entry)
        except FileNotFoundError:
            print(f"警告: 找不到ledger文件 {filepath}")
            return []
        
        return entries
    
    def _parse_row(self, row: Dict) -> LedgerEntry:
        """解析单行数据"""
        return LedgerEntry(
            player_nickname=row.get('player_nickname', ''),
            player_id=row.get('player_id', ''),
            session_start=row.get('session_start_at', ''),
            session_end=row.get('session_end_at', ''),
            buy_in=float(row.get('buy_in', 0) or 0),
            buy_out=float(row.get('buy_out', 0) or 0),
            stack=float(row.get('stack', 0) or 0),
            net=float(row.get('net', 0) or 0)
        )
    
    def calculate_player_totals(self, entries: List[LedgerEntry]) -> Dict[str, Dict]:
        """
        计算每个玩家的总计数据
        
        Returns:
            {player_key: {
                'nickname': str,
                'player_id': str,
                'total_buy_in': float,
                'total_buy_out': float,
                'final_stack': float,
                'net_profit': float,
                'sessions': int
            }}
        """
        player_data = {}
        
        for entry in entries:
            key = entry.player_key
            
            if key not in player_data:
                player_data[key] = {
                    'nickname': entry.player_nickname,
                    'player_id': entry.player_id,
                    'total_buy_in': 0,
                    'total_buy_out': 0,
                    'final_stack': 0,
                    'net_profit': 0,
                    'sessions': 0
                }
            
            player_data[key]['total_buy_in'] += entry.buy_in
            player_data[key]['total_buy_out'] += entry.buy_out
            player_data[key]['net_profit'] += entry.net
            player_data[key]['sessions'] += 1
            
            # 保留最后一次的筹码（当前筹码）
            if entry.stack > 0:
                player_data[key]['final_stack'] = entry.stack
        
        return player_data
    
    def verify_zero_sum(self, player_data: Dict[str, Dict]) -> tuple[bool, float]:
        """
        验证零和游戏规则（所有玩家盈亏总和应为0）
        
        Returns:
            (是否符合零和规则, 实际总和)
        """
        total = sum(data['net_profit'] for data in player_data.values())
        return abs(total) < 0.01, total


def test_ledger_parser():
    """测试ledger解析器"""
    parser = LedgerParser()
    
    print("测试Ledger解析器")
    print("=" * 80)
    
    # 解析ledger文件
    entries = parser.parse_file('log/ledger.csv')
    print(f"\n✓ 解析了 {len(entries)} 条财务记录")
    
    # 计算玩家总计
    player_data = parser.calculate_player_totals(entries)
    print(f"✓ 识别了 {len(player_data)} 位玩家")
    
    # 显示结果
    print("\n" + "=" * 80)
    print("玩家财务汇总:")
    print("=" * 80)
    print(f"{'玩家':<15s} {'总买入':>10s} {'总离场':>10s} {'当前筹码':>10s} {'净盈亏':>10s}")
    print("-" * 80)
    
    for key, data in sorted(player_data.items(), key=lambda x: x[1]['net_profit'], reverse=True):
        print(f"{data['nickname']:<15s} "
              f"{data['total_buy_in']:10.1f} "
              f"{data['total_buy_out']:10.1f} "
              f"{data['final_stack']:10.1f} "
              f"{data['net_profit']:+10.1f}")
    
    # 验证零和规则
    is_zero_sum, total = parser.verify_zero_sum(player_data)
    print("-" * 80)
    print(f"{'总计':<46s} {total:+10.1f}")
    
    print("\n" + "=" * 80)
    if is_zero_sum:
        print("✓ 零和规则验证通过")
    else:
        print(f"❌ 零和规则验证失败，差值: {total:.2f}")
    print("=" * 80)
    
    return player_data


if __name__ == '__main__':
    test_ledger_parser()

