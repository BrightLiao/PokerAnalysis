"""
多日数据合并器
合并多个日期的扑克数据，生成跨日统计
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path
from collections import defaultdict

from ..models.player import Player
from ..models.hand import Hand
from ..storage.json_storage import JSONStorage


class MultiDayMerger:
    """多日数据合并器"""
    
    def __init__(self):
        self.merged_hands: List[Hand] = []
        self.merged_players: Dict[str, Player] = {}
        self.daily_stats: Dict[str, Dict] = {}  # {date: {player_key: stats}}
    
    @staticmethod
    def extract_date_from_path(data_dir: str) -> str:
        """
        从路径中提取日期
        
        例如：
        - "data/1024" -> "20251024"
        - "data/20251024" -> "20251024"
        - "data/1025_merged" -> "20251025"
        
        Args:
            data_dir: 数据目录路径
            
        Returns:
            日期字符串（格式：YYYYMMDD）
        """
        # 提取路径中的最后一个目录名
        dir_name = Path(data_dir).name
        
        # 尝试匹配不同格式的日期
        # 格式1: YYYYMMDD (8位数字)
        match = re.search(r'(\d{8})', dir_name)
        if match:
            return match.group(1)
        
        # 格式2: MMDD (4位数字，假设是2025年)
        match = re.search(r'(\d{4})', dir_name)
        if match:
            mmdd = match.group(1)
            return f"2025{mmdd}"
        
        # 如果无法提取，使用目录名
        return dir_name
    
    @staticmethod
    def normalize_player_name(name: str) -> str:
        """
        标准化玩家名称，去除数字后缀
        例如："黄笃读" -> "黄笃读", "黄笃读2" -> "黄笃读", "player123" -> "player"
        """
        normalized = re.sub(r'\d+$', '', name)
        return normalized if normalized else name
    
    def merge_data_dirs(self, data_dirs: List[str], merge_players: bool = True, verbose: bool = True) -> Tuple[List[Hand], Dict[str, Player]]:
        """
        合并多个数据目录
        
        Args:
            data_dirs: 数据目录列表，按日期排序
            merge_players: 是否合并相似名称的玩家
            verbose: 是否显示详细信息
            
        Returns:
            (合并后的手牌列表, 合并后的玩家字典)
        """
        if verbose:
            print("\n" + "=" * 80)
            print("多日数据合并")
            print("=" * 80)
        
        for data_dir in data_dirs:
            date = self.extract_date_from_path(data_dir)
            
            if verbose:
                print(f"\n加载 {data_dir} (日期: {date})...")
            
            try:
                # 加载该日的数据
                hands, players = JSONStorage.load_data(data_dir)
                
                if verbose:
                    print(f"  ✓ 加载了 {len(hands)} 手牌, {len(players)} 位玩家")
                
                # 合并手牌（添加日期前缀）
                self._merge_hands(hands, date)
                
                # 合并玩家数据
                self._merge_players(players, date)
                
            except Exception as e:
                if verbose:
                    print(f"  ⚠️  加载失败: {e}")
                continue
        
        # 合并相似名称的玩家
        if merge_players:
            self._merge_similar_players(verbose)
        
        if verbose:
            print("\n" + "=" * 80)
            print(f"✓ 合并完成:")
            print(f"  - 总手牌数: {len(self.merged_hands)}")
            print(f"  - 总玩家数: {len(self.merged_players)}")
            print(f"  - 覆盖日期: {len(data_dirs)} 天")
            print("=" * 80)
        
        return self.merged_hands, self.merged_players
    
    def _merge_hands(self, hands: List[Hand], date: str):
        """
        合并手牌数据，为 hand_id 添加日期前缀
        
        Args:
            hands: 单日手牌列表
            date: 日期字符串
        """
        for hand in hands:
            # 为 hand_id 添加日期前缀
            original_id = hand.hand_id
            hand.hand_id = f"{date}_{original_id}"
            
            # 更新 players 中的 hand_id 引用（如果需要）
            # 注意：players dict 的 key 不需要改变
            
            self.merged_hands.append(hand)
    
    def _merge_players(self, players: Dict[str, Player], date: str):
        """
        合并玩家数据
        
        Args:
            players: 单日玩家字典
            date: 日期字符串
        """
        for player_key, player in players.items():
            if player_key not in self.merged_players:
                # 第一次遇到该玩家，创建新的 Player
                merged_player = Player(
                    name=player.name,
                    player_id=player.player_id
                )
                self.merged_players[player_key] = merged_player
            else:
                merged_player = self.merged_players[player_key]
            
            # 合并财务数据
            merged_player.total_buy_in += player.total_buy_in
            merged_player.total_buy_out += player.total_buy_out
            merged_player.final_stack = player.final_stack  # 使用最新的
            merged_player.sessions += player.sessions
            merged_player.total_profit += player.total_profit
            
            # 合并手牌数据
            merged_player.hands_played += player.hands_played
            
            # 更新 hand_ids（添加日期前缀）
            for hand_id in player.hand_ids:
                merged_player.hand_ids.append(f"{date}_{hand_id}")
            
            # 合并 starting_stacks（添加日期前缀）
            for hand_id, stack in player.starting_stacks.items():
                merged_player.starting_stacks[f"{date}_{hand_id}"] = stack
            
            # 合并 hand_profits（添加日期前缀）
            for hand_id, profit in player.hand_profits.items():
                merged_player.hand_profits[f"{date}_{hand_id}"] = profit
            
            # 合并 hand_buyins（添加日期前缀）
            for hand_id, buyin in player.hand_buyins.items():
                merged_player.hand_buyins[f"{date}_{hand_id}"] = buyin
    
    def _merge_similar_players(self, verbose: bool = True):
        """
        合并相似名称的玩家（跨天的同一玩家可能有不同ID）
        """
        if verbose:
            print("\n玩家名称合并:")
            print("-" * 80)
        
        # 按标准化名称分组
        name_groups = defaultdict(list)
        for player_key, player in self.merged_players.items():
            normalized_name = self.normalize_player_name(player.name)
            name_groups[normalized_name].append((player_key, player))
        
        # 找出需要合并的组
        merge_count = 0
        for normalized_name, player_list in name_groups.items():
            if len(player_list) > 1:
                if verbose:
                    print(f"合并玩家: {', '.join([p.name for _, p in player_list])} -> {normalized_name}")
                self._merge_player_group(normalized_name, player_list)
                merge_count += 1
        
        if merge_count == 0:
            if verbose:
                print("未发现需要合并的玩家")
        else:
            if verbose:
                print(f"✓ 成功合并 {merge_count} 组玩家")
        
        if verbose:
            print("-" * 80)
    
    def _merge_player_group(self, target_name: str, player_list: List[Tuple[str, Player]]):
        """
        合并一组玩家
        
        Args:
            target_name: 合并后的目标名称
            player_list: 需要合并的玩家列表 [(player_key, player), ...]
        """
        # 使用第一个玩家作为主玩家
        main_key, main_player = player_list[0]
        main_player.name = target_name
        
        # 创建新的玩家key（基于标准化后的名称）
        main_player_id = main_key.split(' @ ')[1]
        new_main_key = f"{target_name} @ {main_player_id}"
        
        # 合并其他玩家的数据
        for player_key, player in player_list[1:]:
            # 合并财务数据
            main_player.total_buy_in += player.total_buy_in
            main_player.total_buy_out += player.total_buy_out
            main_player.final_stack = player.final_stack  # 使用最新的
            main_player.sessions += player.sessions
            main_player.total_profit += player.total_profit
            
            # 合并手牌数据
            main_player.hands_played += player.hands_played
            main_player.hand_ids.extend(player.hand_ids)
            main_player.starting_stacks.update(player.starting_stacks)
            main_player.hand_profits.update(player.hand_profits)
            main_player.hand_buyins.update(player.hand_buyins)
            
            # 提取被合并玩家的ID
            player_id_to_merge = player_key.split(' @ ')[1]
            main_player_id = main_key.split(' @ ')[1]
            
            # 更新所有手牌中的玩家引用
            for hand in self.merged_hands:
                # 更新 hand.players
                if player_key in hand.players:
                    hand.players[new_main_key] = hand.players.pop(player_key)
                
                # 更新 hand.winners
                if player_key in hand.winners:
                    if new_main_key in hand.winners:
                        hand.winners[new_main_key] += hand.winners.pop(player_key)
                    else:
                        hand.winners[new_main_key] = hand.winners.pop(player_key)
                
                # 更新 showdowns
                if player_key in hand.showdowns:
                    hand.showdowns[new_main_key] = hand.showdowns.pop(player_key)
                
                # 更新所有 actions（基于player_id匹配，因为玩家名字可能不同）
                from ..models.action import Street
                for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
                    for action in hand.actions[street]:
                        # 使用player_id匹配，而不是完整的player_key
                        if action.player_id == player_id_to_merge:
                            action.player_name = target_name
                            action.player_id = main_player_id
            
            # 从玩家字典中删除被合并的玩家
            del self.merged_players[player_key]
        
        # 如果主玩家的key也需要更新（名称被标准化了）
        if main_key != new_main_key:
            # 更新所有手牌中主玩家的引用
            for hand in self.merged_hands:
                if main_key in hand.players:
                    hand.players[new_main_key] = hand.players.pop(main_key)
                if main_key in hand.winners:
                    hand.winners[new_main_key] = hand.winners.pop(main_key)
                if main_key in hand.showdowns:
                    hand.showdowns[new_main_key] = hand.showdowns.pop(main_key)
            
            # 更新玩家字典的key
            self.merged_players[new_main_key] = self.merged_players.pop(main_key)
    
    def get_daily_breakdown(self, player_key: str) -> Dict[str, Dict]:
        """
        获取指定玩家的每日数据分解
        
        Args:
            player_key: 玩家标识
            
        Returns:
            {date: {hands: X, profit: Y, ...}}
        """
        if player_key not in self.merged_players:
            return {}
        
        player = self.merged_players[player_key]
        daily_data = defaultdict(lambda: {
            'hands': 0,
            'profit': 0.0,
            'buy_in': 0.0
        })
        
        # 按日期分组统计
        for hand_id in player.hand_ids:
            # 提取日期（格式：YYYYMMDD_#X）
            date = hand_id.split('_')[0]
            daily_data[date]['hands'] += 1
        
        for hand_id, profit in player.hand_profits.items():
            date = hand_id.split('_')[0]
            daily_data[date]['profit'] += profit
        
        for hand_id, buyin in player.hand_buyins.items():
            date = hand_id.split('_')[0]
            daily_data[date]['buy_in'] += buyin
        
        return dict(daily_data)


def test_merger():
    """测试多日合并器"""
    merger = MultiDayMerger()
    
    # 测试数据目录
    data_dirs = [
        'data/1024',
        'data/1025'
    ]
    
    hands, players = merger.merge_data_dirs(data_dirs)
    
    print("\n合并后的玩家:")
    for player_key, player in sorted(players.items(), key=lambda x: x[1].total_profit, reverse=True):
        daily = merger.get_daily_breakdown(player_key)
        print(f"\n{player.name}:")
        print(f"  总手牌: {player.hands_played}")
        print(f"  总盈亏: {player.total_profit:+.1f}")
        print(f"  每日数据:")
        for date, data in sorted(daily.items()):
            print(f"    {date}: {data['hands']}手, {data['profit']:+.1f}")


if __name__ == '__main__':
    test_merger()

