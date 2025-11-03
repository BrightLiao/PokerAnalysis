"""
JSON数据持久化
"""

import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from ..models.hand import Hand
from ..models.player import Player
from ..models.action import Action, Street, ActionType


class JSONStorage:
    """JSON存储"""
    
    @staticmethod
    def serialize_hand(hand: Hand) -> Dict:
        """序列化手牌对象"""
        return {
            'hand_id': hand.hand_id,
            'hand_number': hand.hand_number,
            'timestamp': hand.timestamp.isoformat(),
            'dealer': hand.dealer,
            'players': hand.players,
            'small_blind': hand.small_blind,
            'big_blind': hand.big_blind,
            'flop': hand.flop,
            'turn': hand.turn,
            'river': hand.river,
            'actions': {
                street.value: [
                    {
                        'action_type': action.action_type.value,
                        'player_name': action.player_name,
                        'player_id': action.player_id,
                        'amount': action.amount,
                        'street': action.street.value,
                        'timestamp': action.timestamp.isoformat() if action.timestamp else None
                    }
                    for action in actions
                ]
                for street, actions in hand.actions.items()
            },
            'showdowns': hand.showdowns,
            'pot_size': hand.pot_size,
            'winners': hand.winners,
        }
    
    @staticmethod
    def deserialize_hand(data: Dict) -> Hand:
        """反序列化手牌对象"""
        hand = Hand(
            hand_id=data['hand_id'],
            hand_number=data['hand_number'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            dealer=data.get('dealer'),
        )
        
        hand.players = data['players']
        hand.small_blind = data['small_blind']
        hand.big_blind = data['big_blind']
        hand.flop = data['flop']
        hand.turn = data.get('turn')
        hand.river = data.get('river')
        hand.showdowns = data.get('showdowns', {})
        hand.pot_size = data['pot_size']
        hand.winners = data.get('winners', {})
        
        # 反序列化actions
        for street_str, actions_data in data['actions'].items():
            street = Street(street_str)
            for action_data in actions_data:
                action = Action(
                    action_type=ActionType(action_data['action_type']),
                    player_name=action_data['player_name'],
                    player_id=action_data['player_id'],
                    amount=action_data['amount'],
                    street=Street(action_data['street']),
                    timestamp=datetime.fromisoformat(action_data['timestamp']) if action_data.get('timestamp') else None
                )
                hand.actions[street].append(action)
        
        return hand
    
    @staticmethod
    def serialize_player(player: Player) -> Dict:
        """序列化玩家对象"""
        return {
            'name': player.name,
            'player_id': player.player_id,
            'hands_played': player.hands_played,
            'total_profit': player.total_profit,
            'total_buy_in': player.total_buy_in,
            'total_buy_out': player.total_buy_out,
            'final_stack': player.final_stack,
            'sessions': player.sessions,
            'hand_ids': player.hand_ids,
            'starting_stacks': player.starting_stacks,
            'hand_profits': player.hand_profits,
            'hand_buyins': player.hand_buyins,
        }
    
    @staticmethod
    def deserialize_player(data: Dict) -> Player:
        """反序列化玩家对象"""
        player = Player(
            name=data['name'],
            player_id=data['player_id'],
        )
        player.hands_played = data['hands_played']
        player.total_profit = data['total_profit']
        player.total_buy_in = data.get('total_buy_in', 0.0)
        player.total_buy_out = data.get('total_buy_out', 0.0)
        player.final_stack = data.get('final_stack', 0.0)
        player.sessions = data.get('sessions', 0)
        player.hand_ids = data['hand_ids']
        player.starting_stacks = data.get('starting_stacks', {})
        player.hand_profits = data.get('hand_profits', {})
        player.hand_buyins = data.get('hand_buyins', {})
        
        return player
    
    @staticmethod
    def save_data(hands: List[Hand], players: Dict[str, Player], output_dir: str = 'data'):
        """
        保存数据到JSON文件
        
        Args:
            hands: 手牌列表
            players: 玩家字典
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存手牌数据
        hands_data = [JSONStorage.serialize_hand(hand) for hand in hands]
        hands_file = output_path / 'hands.json'
        with open(hands_file, 'w', encoding='utf-8') as f:
            json.dump(hands_data, f, ensure_ascii=False, indent=2)
        
        # 保存玩家数据
        players_data = {
            key: JSONStorage.serialize_player(player)
            for key, player in players.items()
        }
        players_file = output_path / 'players.json'
        with open(players_file, 'w', encoding='utf-8') as f:
            json.dump(players_data, f, ensure_ascii=False, indent=2)
        
        # 保存摘要信息
        summary = {
            'total_hands': len(hands),
            'total_players': len(players),
            'date_range': {
                'start': hands[0].timestamp.isoformat() if hands else None,
                'end': hands[-1].timestamp.isoformat() if hands else None,
            },
            'generated_at': datetime.now().isoformat(),
        }
        summary_file = output_path / 'summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return {
            'hands_file': str(hands_file),
            'players_file': str(players_file),
            'summary_file': str(summary_file),
        }
    
    @staticmethod
    def load_data(data_dir: str = 'data') -> tuple[List[Hand], Dict[str, Player]]:
        """
        从JSON文件加载数据
        
        Args:
            data_dir: 数据目录
            
        Returns:
            (hands, players)
        """
        data_path = Path(data_dir)
        
        # 加载手牌
        hands_file = data_path / 'hands.json'
        with open(hands_file, 'r', encoding='utf-8') as f:
            hands_data = json.load(f)
        hands = [JSONStorage.deserialize_hand(data) for data in hands_data]
        
        # 加载玩家
        players_file = data_path / 'players.json'
        with open(players_file, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        players = {
            key: JSONStorage.deserialize_player(data)
            for key, data in players_data.items()
        }
        
        return hands, players


def test_storage():
    """测试存储功能"""
    from ..parser.log_parser import PokerNowLogParser
    from ..builder.data_builder import DataBuilder
    
    print("测试JSON存储\n")
    print("=" * 80)
    
    # 解析和构建数据
    parser = PokerNowLogParser()
    events = parser.parse_file('poker_now_log_pgleW51Lpe_LURB2EJlJSqety.csv')
    
    builder = DataBuilder()
    hands, players = builder.build_from_events(events)
    
    print(f"构建了 {len(hands)} 手牌, {len(players)} 位玩家\n")
    
    # 保存数据
    print("保存数据...")
    files = JSONStorage.save_data(hands, players, 'data')
    print("✓ 数据已保存:")
    for key, filepath in files.items():
        print(f"  - {key}: {filepath}")
    
    # 加载数据
    print("\n加载数据...")
    loaded_hands, loaded_players = JSONStorage.load_data('data')
    print(f"✓ 数据已加载:")
    print(f"  - 手牌数: {len(loaded_hands)}")
    print(f"  - 玩家数: {len(loaded_players)}")
    
    # 验证数据
    print("\n验证数据完整性...")
    assert len(hands) == len(loaded_hands), "手牌数量不匹配"
    assert len(players) == len(loaded_players), "玩家数量不匹配"
    
    # 检查第一手牌
    original = hands[0]
    loaded = loaded_hands[0]
    assert original.hand_id == loaded.hand_id, "手牌ID不匹配"
    assert original.pot_size == loaded.pot_size, "底池不匹配"
    assert len(original.players) == len(loaded.players), "玩家数不匹配"
    
    print("✓ 数据完整性验证通过")
    
    print("\n" + "=" * 80)
    print("测试完成!")


if __name__ == '__main__':
    test_storage()

