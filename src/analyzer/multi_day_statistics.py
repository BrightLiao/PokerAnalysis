"""
多日统计分析器
支持跨天统计分析和每日分解
"""

from typing import Dict, List
from collections import defaultdict

from ..models.player import Player
from ..models.hand import Hand
from .statistics import StatisticsCalculator, PlayerStatistics


class MultiDayStatistics:
    """多日统计分析器"""
    
    def __init__(self, hands: List[Hand], players: Dict[str, Player]):
        self.hands = hands
        self.players = players
        self.daily_stats: Dict[str, Dict[str, PlayerStatistics]] = {}  # {date: {player_key: stats}}
    
    def calculate_all_statistics(self) -> tuple[Dict[str, PlayerStatistics], Dict[str, Dict[str, PlayerStatistics]]]:
        """
        计算所有统计指标
        
        Returns:
            (总体统计, 每日统计)
        """
        # 1. 计算总体统计
        calculator = StatisticsCalculator(self.hands, self.players)
        overall_stats = calculator.calculate_all()
        
        # 2. 按日期分组手牌
        daily_hands = self._group_hands_by_date()
        
        # 3. 计算每日统计
        daily_stats = {}
        for date, hands in sorted(daily_hands.items()):
            # 为该日创建临时玩家字典
            daily_players = self._create_daily_players(hands, date)
            
            # 计算该日统计
            daily_calc = StatisticsCalculator(hands, daily_players)
            daily_stats[date] = daily_calc.calculate_all()
        
        self.daily_stats = daily_stats
        return overall_stats, daily_stats
    
    def _group_hands_by_date(self) -> Dict[str, List[Hand]]:
        """按日期分组手牌"""
        daily_hands = defaultdict(list)
        
        for hand in self.hands:
            # 从 hand_id 中提取日期（格式：YYYYMMDD_#X）
            if '_' in hand.hand_id:
                date = hand.hand_id.split('_')[0]
                daily_hands[date].append(hand)
            else:
                # 如果没有日期前缀，归入 "unknown"
                daily_hands['unknown'].append(hand)
        
        return dict(daily_hands)
    
    def _create_daily_players(self, hands: List[Hand], date: str) -> Dict[str, Player]:
        """
        为特定日期创建玩家字典（只包含该日的数据）
        
        Args:
            hands: 该日的手牌列表
            date: 日期字符串
            
        Returns:
            该日的玩家字典
        """
        daily_players = {}
        
        # 从手牌中提取该日参与的玩家
        player_keys = set()
        for hand in hands:
            player_keys.update(hand.players.keys())
        
        # 为每个玩家创建临时对象，只包含该日数据
        for player_key in player_keys:
            if player_key not in self.players:
                continue
            
            full_player = self.players[player_key]
            
            # 创建临时玩家对象
            daily_player = Player(
                name=full_player.name,
                player_id=full_player.player_id
            )
            
            # 筛选该日的手牌数据
            date_prefix = f"{date}_"
            for hand_id in full_player.hand_ids:
                if hand_id.startswith(date_prefix):
                    daily_player.hand_ids.append(hand_id)
                    daily_player.hands_played += 1
                    
                    # 复制该手牌的数据
                    if hand_id in full_player.starting_stacks:
                        daily_player.starting_stacks[hand_id] = full_player.starting_stacks[hand_id]
                    if hand_id in full_player.hand_profits:
                        daily_player.hand_profits[hand_id] = full_player.hand_profits[hand_id]
                        daily_player.total_profit += full_player.hand_profits[hand_id]
                    if hand_id in full_player.hand_buyins:
                        daily_player.hand_buyins[hand_id] = full_player.hand_buyins[hand_id]
            
            daily_players[player_key] = daily_player
        
        return daily_players
    
    def print_summary(self, overall_stats: Dict[str, PlayerStatistics], 
                     daily_stats: Dict[str, Dict[str, PlayerStatistics]]):
        """
        打印统计摘要
        
        Args:
            overall_stats: 总体统计
            daily_stats: 每日统计
        """
        print("\n" + "=" * 120)
        print("多日统计汇总")
        print("=" * 120)
        
        # 1. 总体统计
        print("\n【总体统计】")
        self._print_stats_table(overall_stats)
        
        # 2. 每日统计
        for date in sorted(daily_stats.keys()):
            print(f"\n【{date} 单日统计】")
            self._print_stats_table(daily_stats[date], date_filter=date)
    
    def _print_stats_table(self, stats: Dict[str, PlayerStatistics], date_filter: str = None):
        """
        打印统计表格
        
        Args:
            stats: 统计数据字典
            date_filter: 日期过滤器（如果指定，只计算该日的盈亏）
        """
        print("=" * 120)
        print(f"{'玩家':<12s}  手牌   VPIP    PFR     AF  3-Bet  C-Bet  Steal   Fold     胜率         盈亏")
        print("-" * 120)
        
        # 按盈亏排序（如果有日期过滤，按该日盈亏；否则按总盈亏）
        def get_profit(player_key):
            if player_key not in self.players:
                return 0
            player = self.players[player_key]
            if date_filter:
                # 计算指定日期的盈亏
                profit = sum(p for hand_id, p in player.hand_profits.items() 
                           if hand_id.startswith(f"{date_filter}_"))
            else:
                # 总盈亏
                profit = player.total_profit
            return profit
        
        sorted_stats = sorted(stats.items(), key=lambda x: get_profit(x[0]), reverse=True)
        
        for player_key, stat in sorted_stats:
            if player_key not in self.players:
                continue
            
            player = self.players[player_key]
            period_profit = get_profit(player_key)
            
            print(f"{player.name:<12s}  "
                  f"{stat.total_hands:4d}   "
                  f"{stat.vpip:5.1f}   "
                  f"{stat.pfr:5.1f}   "
                  f"{stat.af:5.1f}  "
                  f"{stat.three_bet_pct:5.1f}  "
                  f"{stat.cbet_pct:5.1f}  "
                  f"{stat.steal_pct:5.1f}   "
                  f"{stat.fold_pct:5.1f}   "
                  f"{stat.win_rate:5.1f}   "
                  f"{period_profit:+10.1f}")
        
        print("=" * 120)


def test_multi_day_stats():
    """测试多日统计"""
    from ..storage.json_storage import JSONStorage
    
    # 加载合并后的数据
    hands, players = JSONStorage.load_data('data/merged')
    
    # 计算统计
    analyzer = MultiDayStatistics(hands, players)
    overall_stats, daily_stats = analyzer.calculate_all_statistics()
    
    # 打印摘要
    analyzer.print_summary(overall_stats, daily_stats)


if __name__ == '__main__':
    test_multi_day_stats()

