"""
玩家统计指标计算
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from ..models.hand import Hand
from ..models.player import Player
from ..models.action import Action, ActionType, Street


@dataclass
class PlayerStatistics:
    """玩家统计指标"""
    player_key: str
    player_name: str
    
    # 基础数据
    total_hands: int = 0
    total_profit: float = 0.0
    
    # VPIP (Voluntarily Put in Pot) - 主动入池率
    vpip_opportunities: int = 0  # VPIP机会次数
    vpip_count: int = 0  # 主动入池次数
    
    # PFR (Pre-Flop Raise) - 翻牌前加注率
    pfr_opportunities: int = 0  # PFR机会次数
    pfr_count: int = 0  # 翻牌前加注次数
    
    # AF (Aggression Factor) - 激进因子
    aggressive_actions: int = 0  # 下注+加注次数
    passive_actions: int = 0  # 跟注次数（不含check）
    
    # 3-Bet - 三次下注
    three_bet_opportunities: int = 0  # 面对加注的机会
    three_bet_count: int = 0  # 再加注次数
    
    # C-Bet (Continuation Bet) - 持续下注
    cbet_opportunities: int = 0  # 翻牌前加注且看到flop的次数
    cbet_count: int = 0  # flop持续下注次数
    
    # 摊牌相关
    went_to_showdown: int = 0  # 到摊牌次数
    won_at_showdown: int = 0  # 摊牌获胜次数
    
    # 看到各街的次数
    saw_flop: int = 0
    saw_turn: int = 0
    saw_river: int = 0
    
    # 位置统计
    position_stats: Dict[str, Dict] = field(default_factory=lambda: defaultdict(lambda: {
        'hands': 0,
        'vpip': 0,
        'pfr': 0
    }))
    
    # 高级指标
    fold_to_cbet_opportunities: int = 0  # 面对C-Bet的机会
    fold_to_cbet_count: int = 0  # 面对C-Bet弃牌次数
    steal_opportunities: int = 0  # 偷盲机会（CO/BTN位置）
    steal_attempts: int = 0  # 偷盲尝试次数
    
    # 弃牌统计
    total_folds: int = 0  # 总弃牌次数
    preflop_folds: int = 0  # 翻牌前弃牌
    postflop_folds: int = 0  # 翻牌后弃牌
    
    # 胜率统计
    hands_won: int = 0  # 赢得手牌数
    
    @property
    def vpip(self) -> float:
        """VPIP - 主动入池率 (%)"""
        if self.vpip_opportunities == 0:
            return 0.0
        return (self.vpip_count / self.vpip_opportunities) * 100
    
    @property
    def pfr(self) -> float:
        """PFR - 翻牌前加注率 (%)"""
        if self.pfr_opportunities == 0:
            return 0.0
        return (self.pfr_count / self.pfr_opportunities) * 100
    
    @property
    def af(self) -> float:
        """AF - 激进因子"""
        if self.passive_actions == 0:
            return float('inf') if self.aggressive_actions > 0 else 0.0
        return self.aggressive_actions / self.passive_actions
    
    @property
    def three_bet_pct(self) -> float:
        """3-Bet率 (%)"""
        if self.three_bet_opportunities == 0:
            return 0.0
        return (self.three_bet_count / self.three_bet_opportunities) * 100
    
    @property
    def cbet_pct(self) -> float:
        """C-Bet率 (%)"""
        if self.cbet_opportunities == 0:
            return 0.0
        return (self.cbet_count / self.cbet_opportunities) * 100
    
    @property
    def wtsd(self) -> float:
        """WTSD - 摊牌率 (%)"""
        if self.saw_flop == 0:
            return 0.0
        return (self.went_to_showdown / self.saw_flop) * 100
    
    @property
    def won_sd_pct(self) -> float:
        """W$SD - 摊牌胜率 (%)"""
        if self.went_to_showdown == 0:
            return 0.0
        return (self.won_at_showdown / self.went_to_showdown) * 100
    
    @property
    def bb_per_100(self) -> float:
        """BB/100 - 每100手大盲收益"""
        if self.total_hands == 0:
            return 0.0
        # 假设大盲为2（需要根据实际情况调整）
        bb = 2.0
        return (self.total_profit / bb / self.total_hands) * 100
    
    @property
    def fold_to_cbet_pct(self) -> float:
        """Fold to C-Bet - 面对持续下注的弃牌率 (%)"""
        if self.fold_to_cbet_opportunities == 0:
            return 0.0
        return (self.fold_to_cbet_count / self.fold_to_cbet_opportunities) * 100
    
    @property
    def steal_pct(self) -> float:
        """Steal率 - 偷盲率 (%)"""
        if self.steal_opportunities == 0:
            return 0.0
        return (self.steal_attempts / self.steal_opportunities) * 100
    
    @property
    def win_rate(self) -> float:
        """赢率 - 赢得手牌的比例 (%)"""
        if self.total_hands == 0:
            return 0.0
        return (self.hands_won / self.total_hands) * 100
    
    @property
    def fold_pct(self) -> float:
        """弃牌率 (%)"""
        if self.total_hands == 0:
            return 0.0
        return (self.total_folds / self.total_hands) * 100
    
    @property
    def preflop_fold_pct(self) -> float:
        """翻牌前弃牌率 (%)"""
        if self.total_hands == 0:
            return 0.0
        return (self.preflop_folds / self.total_hands) * 100
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'player_key': self.player_key,
            'player_name': self.player_name,
            'total_hands': self.total_hands,
            'total_profit': self.total_profit,
            'vpip': round(self.vpip, 2),
            'pfr': round(self.pfr, 2),
            'af': round(self.af, 2) if self.af != float('inf') else 'inf',
            'three_bet_pct': round(self.three_bet_pct, 2),
            'cbet_pct': round(self.cbet_pct, 2),
            'wtsd': round(self.wtsd, 2),
            'won_sd_pct': round(self.won_sd_pct, 2),
            'bb_per_100': round(self.bb_per_100, 2),
            'saw_flop_pct': round((self.saw_flop / self.total_hands * 100) if self.total_hands > 0 else 0, 2),
            'fold_to_cbet_pct': round(self.fold_to_cbet_pct, 2),
            'steal_pct': round(self.steal_pct, 2),
            'win_rate': round(self.win_rate, 2),
            'fold_pct': round(self.fold_pct, 2),
            'preflop_fold_pct': round(self.preflop_fold_pct, 2),
        }


class StatisticsCalculator:
    """统计指标计算器"""
    
    def __init__(self, hands: List[Hand], players: Dict[str, Player]):
        self.hands = hands
        self.players = players
        self.stats: Dict[str, PlayerStatistics] = {}
        
        # 初始化统计对象
        for player_key, player in players.items():
            self.stats[player_key] = PlayerStatistics(
                player_key=player_key,
                player_name=player.name,
                total_hands=player.hands_played,
                total_profit=player.total_profit
            )
    
    def calculate_all(self) -> Dict[str, PlayerStatistics]:
        """计算所有指标"""
        for hand in self.hands:
            self._analyze_hand(hand)
        
        return self.stats
    
    def _analyze_hand(self, hand: Hand):
        """分析单手牌"""
        # 获取翻牌前的行动序列
        preflop_actions = hand.actions[Street.PREFLOP]
        
        # 记录每个玩家在这手牌中的状态
        player_actions = defaultdict(list)
        for action in preflop_actions:
            player_key = action.player_full_id
            player_actions[player_key].append(action)
        
        # 分析每个参与玩家
        for player_key in hand.players.keys():
            if player_key not in self.stats:
                continue
            
            stats = self.stats[player_key]
            
            # 统计VPIP
            self._calculate_vpip(stats, player_key, hand, player_actions[player_key])
            
            # 统计PFR
            self._calculate_pfr(stats, player_key, hand, player_actions[player_key])
            
            # 统计AF
            self._calculate_af(stats, player_key, hand)
            
            # 统计3-Bet
            self._calculate_three_bet(stats, player_key, hand, preflop_actions)
            
            # 统计C-Bet
            self._calculate_cbet(stats, player_key, hand)
            
            # 统计摊牌
            self._calculate_showdown(stats, player_key, hand)
            
            # 统计看到各街
            self._calculate_streets(stats, player_key, hand)
            
            # 统计Fold to C-Bet
            self._calculate_fold_to_cbet(stats, player_key, hand)
            
            # 统计偷盲
            self._calculate_steal(stats, player_key, hand)
            
            # 统计弃牌
            self._calculate_folds(stats, player_key, hand)
            
            # 统计胜率
            self._calculate_win_rate(stats, player_key, hand)
            
            # 统计位置相关指标
            self._calculate_position_stats(stats, player_key, hand, player_actions[player_key])
    
    def _calculate_vpip(self, stats: PlayerStatistics, player_key: str, 
                       hand: Hand, preflop_actions: List[Action]):
        """计算VPIP"""
        # 每手牌都是一次VPIP机会（除了小盲/大盲）
        stats.vpip_opportunities += 1
        
        # 检查是否主动入池
        for action in preflop_actions:
            # 主动投入筹码：call, bet, raise（不包括盲注）
            if action.action_type in [ActionType.CALL, ActionType.BET, 
                                     ActionType.RAISE, ActionType.ALL_IN]:
                stats.vpip_count += 1
                break
    
    def _calculate_pfr(self, stats: PlayerStatistics, player_key: str,
                      hand: Hand, preflop_actions: List[Action]):
        """计算PFR"""
        # 每手牌都是一次PFR机会
        stats.pfr_opportunities += 1
        
        # 检查是否翻牌前加注
        for action in preflop_actions:
            if action.action_type in [ActionType.RAISE, ActionType.BET]:
                stats.pfr_count += 1
                break
    
    def _calculate_af(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """计算激进因子"""
        all_actions = hand.get_actions_by_player(player_key)
        
        for action in all_actions:
            # 跳过盲注
            if action.action_type in [ActionType.SMALL_BLIND, ActionType.BIG_BLIND]:
                continue
            
            # 激进行动：bet, raise
            if action.action_type in [ActionType.BET, ActionType.RAISE, ActionType.ALL_IN]:
                stats.aggressive_actions += 1
            # 被动行动：call（不包括check）
            elif action.action_type == ActionType.CALL:
                stats.passive_actions += 1
    
    def _calculate_three_bet(self, stats: PlayerStatistics, player_key: str,
                            hand: Hand, preflop_actions: List[Action]):
        """计算3-Bet"""
        # 查找是否有人在该玩家之前加注
        player_acted = False
        faced_raise = False
        made_three_bet = False
        
        for action in preflop_actions:
            if action.player_full_id == player_key:
                player_acted = True
                # 如果之前有人加注，且该玩家再加注
                if faced_raise and action.action_type in [ActionType.RAISE, ActionType.BET]:
                    made_three_bet = True
                    break
            else:
                # 其他玩家的加注（在该玩家行动前）
                if not player_acted and action.action_type in [ActionType.RAISE, ActionType.BET]:
                    faced_raise = True
        
        if faced_raise:
            stats.three_bet_opportunities += 1
            if made_three_bet:
                stats.three_bet_count += 1
    
    def _calculate_cbet(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """计算C-Bet"""
        # 检查是否翻牌前加注
        preflop_raised = False
        for action in hand.actions[Street.PREFLOP]:
            if (action.player_full_id == player_key and 
                action.action_type in [ActionType.RAISE, ActionType.BET]):
                preflop_raised = True
                break
        
        # 如果翻牌前加注且看到flop
        if preflop_raised and hand.went_to_flop:
            # 检查玩家是否还在牌局中（没有fold）
            folded = False
            for action in hand.actions[Street.PREFLOP]:
                if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                    folded = True
                    break
            
            if not folded:
                stats.cbet_opportunities += 1
                
                # 检查flop是否下注
                for action in hand.actions[Street.FLOP]:
                    if (action.player_full_id == player_key and 
                        action.action_type in [ActionType.BET, ActionType.RAISE]):
                        stats.cbet_count += 1
                        break
    
    def _calculate_showdown(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """计算摊牌统计"""
        if player_key in hand.showdowns:
            stats.went_to_showdown += 1
            
            # 检查是否赢了
            if player_key in hand.winners and hand.winners[player_key] > 0:
                stats.won_at_showdown += 1
    
    def _calculate_streets(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """统计看到各街的次数"""
        # 检查玩家是否在各个阶段还在牌局中
        
        # 看到flop - 检查玩家在preflop没有fold
        if hand.went_to_flop:
            folded_preflop = False
            for action in hand.actions[Street.PREFLOP]:
                if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                    folded_preflop = True
                    break
            if not folded_preflop:
                stats.saw_flop += 1
        
        # 看到turn
        if hand.went_to_turn:
            folded = False
            for street in [Street.PREFLOP, Street.FLOP]:
                for action in hand.actions[street]:
                    if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                        folded = True
                        break
                if folded:
                    break
            if not folded:
                stats.saw_turn += 1
        
        # 看到river
        if hand.went_to_river:
            folded = False
            for street in [Street.PREFLOP, Street.FLOP, Street.TURN]:
                for action in hand.actions[street]:
                    if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                        folded = True
                        break
                if folded:
                    break
            if not folded:
                stats.saw_river += 1
    
    def get_statistics(self, player_key: str) -> Optional[PlayerStatistics]:
        """获取指定玩家的统计数据"""
        return self.stats.get(player_key)
    
    def get_all_statistics(self) -> Dict[str, PlayerStatistics]:
        """获取所有玩家的统计数据"""
        return self.stats
    
    def _calculate_fold_to_cbet(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """计算Fold to C-Bet"""
        # 检查是否有对手在翻牌前加注后在flop下注
        preflop_raiser = None
        for action in hand.actions[Street.PREFLOP]:
            if action.action_type in [ActionType.RAISE, ActionType.BET]:
                preflop_raiser = action.player_full_id
        
        # 如果有人翻牌前加注，且该玩家不是加注者，且看到flop
        if preflop_raiser and preflop_raiser != player_key and hand.went_to_flop:
            # 检查加注者是否在flop下注
            raiser_cbet = False
            for action in hand.actions[Street.FLOP]:
                if action.player_full_id == preflop_raiser and action.action_type in [ActionType.BET, ActionType.RAISE]:
                    raiser_cbet = True
                    break
            
            if raiser_cbet:
                # 该玩家面对C-Bet
                stats.fold_to_cbet_opportunities += 1
                
                # 检查该玩家是否弃牌
                for action in hand.actions[Street.FLOP]:
                    if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                        stats.fold_to_cbet_count += 1
                        break
    
    def _calculate_steal(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """计算偷盲率"""
        # 获取玩家位置
        player_position = None
        if player_key in hand.players:
            player_position = hand.players[player_key].get('position')
        
        # 偷盲机会：在CO或BTN位置，且前面没有人加注
        # 简化：检查是否在庄家位置附近
        if hand.dealer and hand.dealer.get('name') + ' @ ' + hand.dealer.get('id') == player_key:
            # 该玩家是庄家
            stats.steal_opportunities += 1
            
            # 检查是否尝试偷盲（加注）
            for action in hand.actions[Street.PREFLOP]:
                if action.player_full_id == player_key and action.action_type in [ActionType.RAISE, ActionType.BET]:
                    stats.steal_attempts += 1
                    break
    
    def _calculate_folds(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """统计弃牌"""
        # 翻牌前弃牌
        for action in hand.actions[Street.PREFLOP]:
            if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                stats.total_folds += 1
                stats.preflop_folds += 1
                return
        
        # 翻牌后弃牌
        for street in [Street.FLOP, Street.TURN, Street.RIVER]:
            for action in hand.actions[street]:
                if action.player_full_id == player_key and action.action_type == ActionType.FOLD:
                    stats.total_folds += 1
                    stats.postflop_folds += 1
                    return
    
    def _calculate_win_rate(self, stats: PlayerStatistics, player_key: str, hand: Hand):
        """统计胜率"""
        # 检查是否赢得底池
        if player_key in hand.winners and hand.winners[player_key] > 0:
            stats.hands_won += 1
    
    def _calculate_position_stats(self, stats: PlayerStatistics, player_key: str,
                                  hand: Hand, preflop_actions: List[Action]):
        """统计位置相关指标"""
        # 简化位置分类
        player_info = hand.players.get(player_key)
        if not player_info:
            return
        
        # 根据庄家位置判断相对位置
        position_name = "unknown"
        if hand.dealer:
            dealer_key = f"{hand.dealer['name']} @ {hand.dealer['id']}"
            if dealer_key == player_key:
                position_name = "BTN"  # 庄家
            # 简化处理，可以后续改进
        
        # 统计该位置的手牌数
        stats.position_stats[position_name]['hands'] += 1
        
        # 统计该位置的VPIP
        vpip_in_position = False
        for action in preflop_actions:
            if action.action_type in [ActionType.CALL, ActionType.BET, 
                                     ActionType.RAISE, ActionType.ALL_IN]:
                vpip_in_position = True
                break
        if vpip_in_position:
            stats.position_stats[position_name]['vpip'] += 1
        
        # 统计该位置的PFR
        pfr_in_position = False
        for action in preflop_actions:
            if action.action_type in [ActionType.RAISE, ActionType.BET]:
                pfr_in_position = True
                break
        if pfr_in_position:
            stats.position_stats[position_name]['pfr'] += 1
    
    def print_summary(self):
        """打印统计摘要"""
        print("=" * 120)
        print("玩家统计指标")
        print("=" * 120)
        print(f"{'玩家':<12s} {'手牌':>5s} {'VPIP':>6s} {'PFR':>6s} {'AF':>6s} "
              f"{'3-Bet':>6s} {'C-Bet':>6s} {'Steal':>6s} {'Fold':>6s} {'胜率':>6s} {'盈亏':>10s}")
        print("-" * 120)
        
        # 按盈利排序
        sorted_stats = sorted(self.stats.items(), 
                            key=lambda x: x[1].total_profit, 
                            reverse=True)
        
        for player_key, stats in sorted_stats:
            af_str = f"{stats.af:.1f}" if stats.af != float('inf') else "∞"
            profit_str = f"{stats.total_profit:+.1f}"
            
            print(f"{stats.player_name:<12s} "
                  f"{stats.total_hands:5d} "
                  f"{stats.vpip:6.1f} "
                  f"{stats.pfr:6.1f} "
                  f"{af_str:>6s} "
                  f"{stats.three_bet_pct:6.1f} "
                  f"{stats.cbet_pct:6.1f} "
                  f"{stats.steal_pct:6.1f} "
                  f"{stats.fold_pct:6.1f} "
                  f"{stats.win_rate:6.1f} "
                  f"{profit_str:>10s}")
        
        print("=" * 120)

