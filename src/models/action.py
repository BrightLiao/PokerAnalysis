"""
玩家行动数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Street(Enum):
    """街道枚举"""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class ActionType(Enum):
    """行动类型枚举"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"
    SMALL_BLIND = "small_blind"
    BIG_BLIND = "big_blind"


@dataclass
class Action:
    """玩家行动模型"""
    action_type: ActionType
    player_name: str
    player_id: str
    amount: float = 0.0
    street: Street = Street.PREFLOP
    timestamp: datetime = None
    
    def __repr__(self):
        if self.amount > 0:
            return f"<{self.action_type.value} by {self.player_name}: {self.amount} at {self.street.value}>"
        return f"<{self.action_type.value} by {self.player_name} at {self.street.value}>"
    
    @property
    def player_full_id(self) -> str:
        """玩家完整标识"""
        return f"{self.player_name} @ {self.player_id}"
    
    @property
    def is_aggressive(self) -> bool:
        """是否是激进行动（下注、加注）"""
        return self.action_type in [ActionType.BET, ActionType.RAISE, ActionType.ALL_IN]
    
    @property
    def is_passive(self) -> bool:
        """是否是被动行动（过牌、跟注）"""
        return self.action_type in [ActionType.CHECK, ActionType.CALL]

