"""
测试JSON存储
"""

from src.parser.log_parser import PokerNowLogParser
from src.builder.data_builder import DataBuilder
from src.storage.json_storage import JSONStorage
import os

def main():
    print("=" * 80)
    print("测试JSON存储")
    print("=" * 80)
    print()
    
    # 解析和构建数据
    print("1. 解析日志文件...")
    parser = PokerNowLogParser()
    events = parser.parse_file('poker_now_log_pgleW51Lpe_LURB2EJlJSqety.csv')
    print(f"   ✓ 解析了 {len(events)} 条事件")
    
    print("\n2. 构建数据模型...")
    builder = DataBuilder()
    hands, players = builder.build_from_events(events)
    print(f"   ✓ 构建了 {len(hands)} 手牌")
    print(f"   ✓ 识别了 {len(players)} 位玩家")
    
    # 保存数据
    print("\n3. 保存数据到JSON文件...")
    files = JSONStorage.save_data(hands, players, 'data')
    print("   ✓ 数据已保存:")
    for key, filepath in files.items():
        filesize = os.path.getsize(filepath) / 1024
        print(f"      - {filepath} ({filesize:.1f} KB)")
    
    # 加载数据
    print("\n4. 从JSON文件加载数据...")
    loaded_hands, loaded_players = JSONStorage.load_data('data')
    print(f"   ✓ 加载了 {len(loaded_hands)} 手牌")
    print(f"   ✓ 加载了 {len(loaded_players)} 位玩家")
    
    # 验证数据完整性
    print("\n5. 验证数据完整性...")
    
    # 验证数量
    assert len(hands) == len(loaded_hands), "❌ 手牌数量不匹配"
    print(f"   ✓ 手牌数量匹配: {len(hands)}")
    
    assert len(players) == len(loaded_players), "❌ 玩家数量不匹配"
    print(f"   ✓ 玩家数量匹配: {len(players)}")
    
    # 验证手牌数据
    for i, (orig, loaded) in enumerate(zip(hands[:5], loaded_hands[:5])):
        assert orig.hand_id == loaded.hand_id, f"❌ 手牌{i}的ID不匹配"
        assert orig.hand_number == loaded.hand_number, f"❌ 手牌{i}的序号不匹配"
        assert abs(orig.pot_size - loaded.pot_size) < 0.01, f"❌ 手牌{i}的底池不匹配"
        assert len(orig.players) == len(loaded.players), f"❌ 手牌{i}的玩家数不匹配"
    print(f"   ✓ 前5手牌数据完整")
    
    # 验证玩家数据
    for player_key in list(players.keys())[:3]:
        orig_player = players[player_key]
        loaded_player = loaded_players[player_key]
        
        assert orig_player.name == loaded_player.name, f"❌ 玩家{player_key}的名字不匹配"
        assert orig_player.hands_played == loaded_player.hands_played, f"❌ 玩家{player_key}的手牌数不匹配"
        assert abs(orig_player.total_profit - loaded_player.total_profit) < 0.01, f"❌ 玩家{player_key}的盈亏不匹配"
    print(f"   ✓ 玩家数据完整")
    
    # 显示一些统计
    print("\n" + "=" * 80)
    print("数据统计:")
    print("=" * 80)
    
    print(f"\n总手牌数: {len(loaded_hands)}")
    print(f"总玩家数: {len(loaded_players)}")
    
    total_pot = sum(hand.pot_size for hand in loaded_hands)
    print(f"总底池: {total_pot:.1f}")
    print(f"平均底池: {total_pot/len(loaded_hands):.1f}")
    
    print(f"\n玩家盈亏排名:")
    sorted_players = sorted(loaded_players.items(), key=lambda x: x[1].total_profit, reverse=True)
    for player_key, player in sorted_players:
        profit_str = f"{player.total_profit:+.1f}"
        print(f"  {player.name:15s}: {profit_str:>10s} ({player.hands_played} 手)")
    
    print("\n" + "=" * 80)
    print("✓ 所有测试通过!")
    print("=" * 80)


if __name__ == '__main__':
    main()

