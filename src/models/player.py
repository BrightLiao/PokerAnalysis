"""
玩家数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Player:
    """玩家模型"""
    name: str
    player_id: str
    
    # 统计数据
    hands_played: int = 0
    total_profit: float = 0.0
    
    # 财务数据（来自ledger）
    total_buy_in: float = 0.0  # 总买入
    total_buy_out: float = 0.0  # 总离场
    final_stack: float = 0.0  # 当前筹码
    sessions: int = 0  # 进场次数
    
    # 手牌历史
    hand_ids: List[str] = field(default_factory=list)
    
    # 初始筹码记录（每手牌）
    starting_stacks: Dict[str, float] = field(default_factory=dict)
    
    # 盈利记录（每手牌） {hand_id: profit}
    hand_profits: Dict[str, float] = field(default_factory=dict)
    
    # 买入记录（每手牌） {hand_id: buyin_amount}，无买入为0
    hand_buyins: Dict[str, float] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(f"{self.name}@{self.player_id}")
    
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name and self.player_id == other.player_id
        return False
    
    def __repr__(self):
        return f"<Player {self.name} (hands: {self.hands_played}, profit: {self.total_profit:.1f})>"
    
    @property
    def full_id(self) -> str:
        """完整标识: 名字 @ ID"""
        return f"{self.name} @ {self.player_id}"
    
    def add_hand(self, hand_id: str, starting_stack: float = None):
        """记录参与的手牌"""
        if hand_id not in self.hand_ids:
            self.hand_ids.append(hand_id)
            self.hands_played += 1
            if starting_stack is not None:
                self.starting_stacks[hand_id] = starting_stack
    
    def add_profit(self, amount: float):
        """增加盈利（或亏损）- 已废弃，使用ledger数据"""
        # 保留此方法以兼容旧代码，但不再使用
        pass
    
    def set_ledger_data(self, total_buy_in: float, total_buy_out: float, 
                       final_stack: float, sessions: int):
        """
        设置来自ledger的财务数据
        
        盈亏 = 离场总金额 + 当前筹码 - 总买入
        """
        self.total_buy_in = total_buy_in
        self.total_buy_out = total_buy_out
        self.final_stack = final_stack
        self.sessions = sessions
        # 计算真实盈亏
        self.total_profit = total_buy_out + final_stack - total_buy_in
    
    def record_hand_result(self, hand_id: str, profit: float, buyin: float = 0):
        """
        记录单手牌结果
        
        Args:
            hand_id: 手牌ID
            profit: 该手牌的盈利（投入-收益）
            buyin: 该手牌的买入金额（如果有）
        """
        self.hand_profits[hand_id] = profit
        self.hand_buyins[hand_id] = buyin
    
    def verify_stack_consistency(self, initial_stack: float = None) -> tuple[bool, str]:
        """
        验证筹码一致性
        
        检查：初始筹码 + 总买入 + 总盈利 = 当前筹码 + 离场金额
        
        Args:
            initial_stack: 初始带入筹码（如果知道）
            
        Returns:
            (是否一致, 说明信息)
        """
        # 计算每手牌盈利总和
        calculated_profit = sum(self.hand_profits.values())
        
        # 计算总买入（从hand_buyins）
        calculated_buyins = sum(self.hand_buyins.values())
        
        # 验证1: 每手盈利总和应该等于total_profit（来自ledger）
        profit_diff = abs(calculated_profit - self.total_profit)
        if profit_diff > 0.01:
            return False, (f"盈利不一致：逐手累计={calculated_profit:.2f}, "
                          f"ledger记录={self.total_profit:.2f}, 差值={profit_diff:.2f}")
        
        # 验证2: 买入总和检查（如果有记录）
        if calculated_buyins > 0 and self.total_buy_in > 0:
            buyin_diff = abs(calculated_buyins - self.total_buy_in)
            if buyin_diff > 0.01:
                return False, (f"买入不一致：逐手累计={calculated_buyins:.2f}, "
                              f"ledger记录={self.total_buy_in:.2f}, 差值={buyin_diff:.2f}")
        
        # 验证3: 筹码守恒 
        # 初始筹码 + 买入 + 盈利 = 当前筹码 + 离场
        if initial_stack is not None:
            left_side = initial_stack + self.total_buy_in + self.total_profit
            right_side = self.final_stack + self.total_buy_out
            stack_diff = abs(left_side - right_side)
            if stack_diff > 0.01:
                return False, (f"筹码守恒失败：初始+买入+盈利={left_side:.2f}, "
                              f"当前+离场={right_side:.2f}, 差值={stack_diff:.2f}")
        
        return True, "筹码验证通过"
    
    def get_stack_summary(self) -> Dict:
        """获取筹码摘要"""
        return {
            'player_name': self.name,
            'total_hands': self.hands_played,
            'total_buy_in': self.total_buy_in,
            'total_buy_out': self.total_buy_out,
            'final_stack': self.final_stack,
            'total_profit': self.total_profit,
            'calculated_profit_from_hands': sum(self.hand_profits.values()),
            'calculated_buyins_from_hands': sum(self.hand_buyins.values()),
            'sessions': self.sessions,
        }

