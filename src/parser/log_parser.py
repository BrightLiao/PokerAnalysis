"""
Poker Now 日志解析器
负责读取CSV文件并解析各类事件
"""

import csv
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum


class EventType(Enum):
    """事件类型枚举"""
    HAND_START = "hand_start"
    HAND_END = "hand_end"
    PLAYER_STACKS = "player_stacks"
    SMALL_BLIND = "small_blind"
    BIG_BLIND = "big_blind"
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOW = "show"
    COLLECTED = "collected"
    UNCALLED_BET = "uncalled_bet"
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_QUIT = "player_quit"
    PLAYER_APPROVED = "player_approved"
    PLAYER_ADDING = "player_adding"
    UNKNOWN = "unknown"


class LogEvent:
    """日志事件基类"""
    def __init__(self, entry: str, timestamp: datetime, order: int, event_type: EventType):
        self.entry = entry
        self.timestamp = timestamp
        self.order = order
        self.event_type = event_type
    
    def __repr__(self):
        return f"<{self.event_type.value} at {self.timestamp}>"


class PokerNowLogParser:
    """Poker Now 日志解析器"""
    
    def __init__(self):
        # 玩家名称和ID的正则表达式
        self.player_pattern = re.compile(r'"([^"]+) @ ([^"]+)"')
        # 数字金额的正则表达式
        self.amount_pattern = re.compile(r'\d+(?:\.\d+)?')
        
    def parse_file(self, filepath: str) -> List[Dict]:
        """
        解析CSV日志文件
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            解析后的事件列表（按时间正序排列）
        """
        events = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                event = self._parse_row(row)
                if event:
                    events.append(event)
        
        # Poker Now的日志是倒序的，需要反转
        events.reverse()
        
        return events
    
    def _parse_row(self, row: Dict) -> Optional[Dict]:
        """
        解析单行数据
        
        Args:
            row: CSV行数据字典
            
        Returns:
            解析后的事件字典
        """
        entry = row.get('entry', '').strip()
        at = row.get('at', '').strip()
        order = row.get('order', '').strip()
        
        if not entry or not at:
            return None
        
        # 解析时间戳
        try:
            timestamp = datetime.fromisoformat(at.replace('Z', '+00:00'))
        except:
            return None
        
        # 解析order
        try:
            order_int = int(order)
        except:
            order_int = 0
        
        # 识别事件类型
        event_type, parsed_data = self._identify_event_type(entry)
        
        return {
            'entry': entry,
            'timestamp': timestamp,
            'order': order_int,
            'event_type': event_type,
            **parsed_data
        }
    
    def _identify_event_type(self, entry: str) -> Tuple[EventType, Dict]:
        """
        识别事件类型并提取相关数据
        
        Args:
            entry: 日志条目文本
            
        Returns:
            (事件类型, 提取的数据字典)
        """
        entry_lower = entry.lower()
        
        # 手牌开始
        if '-- starting hand #' in entry_lower:
            hand_id = self._extract_hand_id(entry)
            dealer = self._extract_player(entry, 'dealer:')
            return EventType.HAND_START, {
                'hand_id': hand_id,
                'dealer': dealer
            }
        
        # 手牌结束
        if '-- ending hand #' in entry_lower:
            hand_id = self._extract_hand_id(entry)
            return EventType.HAND_END, {'hand_id': hand_id}
        
        # 玩家筹码
        if 'player stacks:' in entry_lower:
            stacks = self._extract_player_stacks(entry)
            return EventType.PLAYER_STACKS, {'stacks': stacks}
        
        # 小盲注
        if 'posts a small blind of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.SMALL_BLIND, {
                'player': player,
                'amount': amount
            }
        
        # 大盲注
        if 'posts a big blind of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.BIG_BLIND, {
                'player': player,
                'amount': amount
            }
        
        # 弃牌
        if '" folds' in entry:
            player = self._extract_player(entry)
            return EventType.FOLD, {'player': player}
        
        # 过牌
        if '" checks' in entry:
            player = self._extract_player(entry)
            return EventType.CHECK, {'player': player}
        
        # 跟注
        if '" calls' in entry:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.CALL, {
                'player': player,
                'amount': amount
            }
        
        # 下注
        if '" bets' in entry:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.BET, {
                'player': player,
                'amount': amount
            }
        
        # 加注
        if '" raises to' in entry:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.RAISE, {
                'player': player,
                'amount': amount
            }
        
        # All-in (可能在bet/raise/call中包含)
        if 'all-in' in entry_lower or 'all in' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.ALL_IN, {
                'player': player,
                'amount': amount
            }
        
        # Flop
        if 'flop:' in entry_lower:
            cards = self._extract_cards(entry)
            return EventType.FLOP, {'cards': cards}
        
        # Turn
        if 'turn:' in entry_lower:
            cards = self._extract_cards(entry)
            return EventType.TURN, {'cards': cards}
        
        # River
        if 'river:' in entry_lower:
            cards = self._extract_cards(entry)
            return EventType.RIVER, {'cards': cards}
        
        # 展示手牌
        if '" shows' in entry:
            player = self._extract_player(entry)
            cards = self._extract_cards(entry)
            return EventType.SHOW, {
                'player': player,
                'cards': cards
            }
        
        # 收集底池
        if '" collected' in entry and 'from pot' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.COLLECTED, {
                'player': player,
                'amount': amount
            }
        
        # 未跟注退回
        if 'uncalled bet of' in entry_lower:
            player = self._extract_player(entry, 'returned to')
            amount = self._extract_amount(entry)
            return EventType.UNCALLED_BET, {
                'player': player,
                'amount': amount
            }
        
        # 玩家加入/离开/买入/补码
        # 玩家离场（暂离，可能还会回来）
        if 'stand up with the stack of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.PLAYER_LEAVE, {
                'player': player,
                'stack': amount
            }
        
        # 玩家退出（带走筹码）
        if 'quits the game with a stack of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.PLAYER_QUIT, {
                'player': player,
                'stack': amount
            }
        
        # 管理员批准入场（初始买入）
        if 'approved the player' in entry_lower and 'with a stack of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.PLAYER_APPROVED, {
                'player': player,
                'stack': amount
            }
        
        # 玩家加入游戏
        if 'joined the game with a stack of' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.PLAYER_JOIN, {
                'player': player,
                'stack': amount
            }
        
        # 补码（adding chips）
        if 'adding' in entry_lower and 'chips' in entry_lower:
            player = self._extract_player(entry)
            amount = self._extract_amount(entry)
            return EventType.PLAYER_ADDING, {
                'player': player,
                'amount': amount
            }
        
        return EventType.UNKNOWN, {}
    
    def _extract_player(self, entry: str, keyword: str = None) -> Optional[Dict[str, str]]:
        """
        提取玩家信息
        
        Args:
            entry: 日志条目
            keyword: 可选的关键词，用于定位玩家名称位置
            
        Returns:
            {'name': 玩家名, 'id': 玩家ID}
        """
        if keyword:
            # 查找关键词后的玩家
            keyword_pos = entry.lower().find(keyword.lower())
            if keyword_pos != -1:
                search_text = entry[keyword_pos:]
                match = self.player_pattern.search(search_text)
            else:
                match = self.player_pattern.search(entry)
        else:
            match = self.player_pattern.search(entry)
        
        if match:
            return {
                'name': match.group(1),
                'id': match.group(2)
            }
        return None
    
    def _extract_amount(self, entry: str) -> Optional[float]:
        """
        提取金额
        
        先移除玩家标识（"玩家名 @ ID"格式），避免匹配到玩家名或ID中的数字
        """
        # 移除所有玩家标识部分
        entry_without_players = self.player_pattern.sub('', entry)
        match = self.amount_pattern.search(entry_without_players)
        if match:
            return float(match.group(0))
        return None
    
    def _extract_hand_id(self, entry: str) -> Optional[str]:
        """提取手牌ID"""
        match = re.search(r'#(\d+)', entry)
        if match:
            return match.group(1)
        
        # 也尝试提取 (id: xxx) 格式
        match = re.search(r'\(id: ([a-z0-9]+)\)', entry)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_cards(self, entry: str) -> List[str]:
        """
        提取牌面信息
        
        Returns:
            卡牌列表，如 ['A♠', 'K♥', 'Q♦']
        """
        cards = []
        
        # 匹配卡牌格式: 数字/字母 + 花色符号
        # 支持: 10♥, J♣, Q♦, K♠, A♥ 等
        card_pattern = re.compile(r'(10|[2-9JQKA])[♠♥♦♣♤♡♢♧]')
        matches = card_pattern.findall(entry)
        
        if matches:
            # 重新匹配完整的卡牌（包括花色）
            full_card_pattern = re.compile(r'(10|[2-9JQKA])([♠♥♦♣♤♡♢♧])')
            for match in full_card_pattern.finditer(entry):
                cards.append(match.group(0))
        
        return cards
    
    def _extract_player_stacks(self, entry: str) -> Dict[str, float]:
        """
        提取所有玩家的筹码信息
        
        Returns:
            {玩家标识: 筹码数}
        """
        stacks = {}
        
        # 匹配格式: #位置号 "玩家名 @ ID" (筹码数)
        pattern = re.compile(r'#(\d+) "([^@]+) @ ([^"]+)" \((\d+(?:\.\d+)?)\)')
        
        for match in pattern.finditer(entry):
            position = int(match.group(1))
            name = match.group(2)
            player_id = match.group(3)
            stack = float(match.group(4))
            
            player_key = f"{name} @ {player_id}"
            stacks[player_key] = {
                'position': position,
                'name': name,
                'id': player_id,
                'stack': stack
            }
        
        return stacks


def test_parser():
    """测试解析器"""
    parser = PokerNowLogParser()
    
    # 测试样例
    test_entries = [
        {
            'entry': '-- starting hand #91 (id: pu8envt0lo0k)  (No Limit Texas Hold\'em) (dealer: "ldl @ Fyu1zC3WxZ") --',
            'at': '2025-10-24T17:33:56.222Z',
            'order': '176132723622200'
        },
        {
            'entry': 'Player stacks: #2 "ldl @ Fyu1zC3WxZ" (379) | #4 "jx @ y1rG7j-rqe" (253)',
            'at': '2025-10-24T17:33:56.222Z',
            'order': '176132723622201'
        },
        {
            'entry': '"ldl @ Fyu1zC3WxZ" posts a small blind of 1',
            'at': '2025-10-24T17:33:56.222Z',
            'order': '176132723622204'
        },
        {
            'entry': '"jx @ y1rG7j-rqe" posts a big blind of 2',
            'at': '2025-10-24T17:33:56.222Z',
            'order': '176132723622205'
        },
        {
            'entry': '"ldl @ Fyu1zC3WxZ" raises to 7',
            'at': '2025-10-24T17:32:53.577Z',
            'order': '176132717357700'
        },
        {
            'entry': 'Flop:  [10♥, J♣, J♠]',
            'at': '2025-10-24T17:32:57.581Z',
            'order': '176132717758100'
        },
        {
            'entry': 'Turn: 10♥, J♣, J♠ [J♦]',
            'at': '2025-10-24T17:33:04.436Z',
            'order': '176132718443600'
        },
        {
            'entry': 'River: 10♥, J♣, J♠, J♦ [5♠]',
            'at': '2025-10-24T17:33:13.937Z',
            'order': '176132719393700'
        },
    ]
    
    print("测试解析器功能：\n")
    for test_entry in test_entries:
        result = parser._parse_row(test_entry)
        if result:
            print(f"原始: {test_entry['entry'][:60]}...")
            print(f"类型: {result['event_type'].value}")
            print(f"数据: {result}")
            print("-" * 80)


if __name__ == '__main__':
    test_parser()

