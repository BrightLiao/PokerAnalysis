"""
手牌数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from .action import Action, Street


@dataclass
class Hand:
    """手牌模型"""
    hand_id: str
    hand_number: int  # 手牌序号
    timestamp: datetime
    
    # 玩家信息
    dealer: Optional[Dict[str, str]] = None  # {'name': xxx, 'id': xxx}
    players: Dict[str, Dict] = field(default_factory=dict)  # 玩家标识 -> {'name', 'id', 'stack', 'position'}
    
    # 盲注
    small_blind: float = 0.0
    big_blind: float = 0.0
    
    # 公共牌
    flop: List[str] = field(default_factory=list)
    turn: Optional[str] = None
    river: Optional[str] = None
    
    # 行动序列
    actions: Dict[Street, List[Action]] = field(default_factory=lambda: {
        Street.PREFLOP: [],
        Street.FLOP: [],
        Street.TURN: [],
        Street.RIVER: []
    })
    
    # 摊牌信息
    showdowns: Dict[str, List[str]] = field(default_factory=dict)  # 玩家 -> 手牌
    
    # 底池和结算
    pot_size: float = 0.0
    winners: Dict[str, float] = field(default_factory=dict)  # 玩家 -> 赢得金额
    
    # 原始事件（用于调试）
    raw_events: List[Dict] = field(default_factory=list)
    
    def __repr__(self):
        return f"<Hand #{self.hand_number} ({self.hand_id}): {len(self.players)} players, pot: {self.pot_size}>"
    
    @property
    def board(self) -> List[str]:
        """完整牌面"""
        board = self.flop.copy()
        if self.turn:
            board.append(self.turn)
        if self.river:
            board.append(self.river)
        return board
    
    @property
    def went_to_flop(self) -> bool:
        """是否看到翻牌"""
        return len(self.flop) > 0
    
    @property
    def went_to_turn(self) -> bool:
        """是否看到转牌"""
        return self.turn is not None
    
    @property
    def went_to_river(self) -> bool:
        """是否看到河牌"""
        return self.river is not None
    
    @property
    def went_to_showdown(self) -> bool:
        """是否到摊牌"""
        return len(self.showdowns) > 0
    
    def add_action(self, action: Action):
        """添加行动"""
        if action.street in self.actions:
            self.actions[action.street].append(action)
    
    def add_player(self, name: str, player_id: str, stack: float, position: int = None):
        """添加玩家"""
        player_key = f"{name} @ {player_id}"
        self.players[player_key] = {
            'name': name,
            'id': player_id,
            'stack': stack,
            'position': position
        }
    
    def set_winner(self, player_name: str, player_id: str, amount: float):
        """设置赢家"""
        player_key = f"{player_name} @ {player_id}"
        self.winners[player_key] = amount
        self.pot_size = max(self.pot_size, amount)
    
    def add_showdown(self, player_name: str, player_id: str, cards: List[str]):
        """添加摊牌信息"""
        player_key = f"{player_name} @ {player_id}"
        self.showdowns[player_key] = cards
    
    def get_actions_by_player(self, player_key: str) -> List[Action]:
        """获取特定玩家的所有行动"""
        all_actions = []
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            for action in self.actions[street]:
                if action.player_full_id == player_key:
                    all_actions.append(action)
        return all_actions
    
    def get_aggressive_actions_count(self, player_key: str) -> int:
        """获取玩家的激进行动次数"""
        actions = self.get_actions_by_player(player_key)
        return sum(1 for a in actions if a.is_aggressive)
    
    def get_passive_actions_count(self, player_key: str) -> int:
        """获取玩家的被动行动次数"""
        actions = self.get_actions_by_player(player_key)
        return sum(1 for a in actions if a.is_passive)
    
    def player_vpip(self, player_key: str) -> bool:
        """玩家是否主动入池（VPIP）"""
        preflop_actions = self.actions[Street.PREFLOP]
        for action in preflop_actions:
            if action.player_full_id == player_key:
                # 主动投入筹码（除了大小盲）
                if action.action_type.value in ['call', 'bet', 'raise', 'all_in']:
                    return True
        return False
    
    def player_pfr(self, player_key: str) -> bool:
        """玩家是否翻牌前加注（PFR）"""
        preflop_actions = self.actions[Street.PREFLOP]
        for action in preflop_actions:
            if action.player_full_id == player_key:
                if action.action_type.value in ['raise', 'bet']:
                    return True
        return False

