"""
测试数据构建器
"""

from src.parser.log_parser import PokerNowLogParser
from src.builder.data_builder import DataBuilder
from src.models.action import Street

def main():
    print("=" * 80)
    print("测试数据构建器")
    print("=" * 80)
    print()
    
    # 解析日志
    parser = PokerNowLogParser()
    log_file = 'poker_now_log_pgleW51Lpe_LURB2EJlJSqety.csv'
    print(f"正在解析文件: {log_file}")
    events = parser.parse_file(log_file)
    print(f"✓ 解析了 {len(events)} 条事件\n")
    
    # 构建数据
    print("正在构建数据模型...")
    builder = DataBuilder()
    hands, players = builder.build_from_events(events)
    
    print(f"✓ 构建完成:")
    print(f"  - 手牌数: {len(hands)}")
    print(f"  - 玩家数: {len(players)}")
    print()
    
    # 显示玩家信息
    print("=" * 80)
    print("玩家统计:")
    print("=" * 80)
    print(f"{'玩家':<20s} | {'手牌数':>6s} | {'盈亏':>10s}")
    print("-" * 80)
    for player_key, player in sorted(players.items(), key=lambda x: x[1].total_profit, reverse=True):
        profit_str = f"{player.total_profit:+.1f}" if player.total_profit != 0 else "0.0"
        print(f"{player.name:<20s} | {player.hands_played:6d} | {profit_str:>10s}")
    
    # 显示前几手牌
    print("\n" + "=" * 80)
    print("前3手牌详情:")
    print("=" * 80)
    for i, hand in enumerate(hands[:3]):
        print(f"\n【手牌 #{hand.hand_number}】 ID: {hand.hand_id}")
        print(f"时间: {hand.timestamp}")
        print(f"盲注: {hand.small_blind}/{hand.big_blind}")
        print(f"玩家数: {len(hand.players)}")
        
        # 显示玩家列表
        print(f"玩家: ", end="")
        player_names = [info['name'] for info in hand.players.values()]
        print(", ".join(player_names))
        
        # 显示牌面
        if hand.flop:
            print(f"Flop:  {' '.join(hand.flop)}")
        if hand.turn:
            print(f"Turn:  {hand.turn}")
        if hand.river:
            print(f"River: {hand.river}")
        
        # 显示行动统计
        action_counts = []
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            count = len(hand.actions[street])
            if count > 0:
                action_counts.append(f"{street.value}:{count}")
        print(f"行动: {', '.join(action_counts)}")
        
        # 显示赢家
        if hand.winners:
            for winner_key, amount in hand.winners.items():
                winner_name = winner_key.split(' @ ')[0]
                print(f"赢家: {winner_name} 收获 {amount}")
        
        # 显示摊牌
        if hand.showdowns:
            print(f"摊牌: {len(hand.showdowns)} 位玩家")
            for player_key, cards in hand.showdowns.items():
                player_name = player_key.split(' @ ')[0]
                print(f"  - {player_name}: {' '.join(cards)}")
    
    # 选择一手牌展示详细行动
    print("\n" + "=" * 80)
    print("详细行动示例（第10手牌）:")
    print("=" * 80)
    if len(hands) >= 10:
        hand = hands[9]  # 第10手
        print(f"手牌 #{hand.hand_number}")
        
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            actions = hand.actions[street]
            if actions:
                print(f"\n{street.value.upper()}:")
                for action in actions:
                    if action.amount > 0:
                        print(f"  - {action.player_name} {action.action_type.value} {action.amount}")
                    else:
                        print(f"  - {action.player_name} {action.action_type.value}")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("整体统计:")
    print("=" * 80)
    
    total_pot = sum(hand.pot_size for hand in hands)
    hands_to_flop = sum(1 for hand in hands if hand.went_to_flop)
    hands_to_showdown = sum(1 for hand in hands if hand.went_to_showdown)
    
    print(f"总手牌数: {len(hands)}")
    print(f"总底池: {total_pot:.1f}")
    print(f"平均底池: {total_pot/len(hands):.1f}")
    print(f"看到翻牌: {hands_to_flop} ({hands_to_flop/len(hands)*100:.1f}%)")
    print(f"到摊牌: {hands_to_showdown} ({hands_to_showdown/len(hands)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

