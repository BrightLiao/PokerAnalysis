"""
测试日志解析器
"""

from src.parser.log_parser import PokerNowLogParser, EventType
from collections import Counter

def main():
    parser = PokerNowLogParser()
    
    # 解析日志文件
    log_file = 'poker_now_log_pgleW51Lpe_LURB2EJlJSqety.csv'
    print(f"开始解析文件: {log_file}\n")
    
    events = parser.parse_file(log_file)
    
    print(f"✓ 成功解析 {len(events)} 条事件\n")
    
    # 统计事件类型
    event_counts = Counter(event['event_type'] for event in events)
    
    print("=" * 80)
    print("事件类型统计:")
    print("=" * 80)
    for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{event_type.value:20s}: {count:5d} 条")
    
    print("\n" + "=" * 80)
    print("前10条事件示例:")
    print("=" * 80)
    for i, event in enumerate(events[:10]):
        print(f"\n[{i+1}] {event['event_type'].value}")
        print(f"    时间: {event['timestamp']}")
        print(f"    原文: {event['entry'][:70]}...")
        if event['event_type'] == EventType.HAND_START:
            print(f"    手牌ID: {event.get('hand_id')}")
            if event.get('dealer'):
                print(f"    庄家: {event['dealer']['name']}")
        elif event['event_type'] in [EventType.BET, EventType.RAISE, EventType.CALL]:
            if event.get('player'):
                print(f"    玩家: {event['player']['name']}")
            if event.get('amount'):
                print(f"    金额: {event['amount']}")
        elif event['event_type'] in [EventType.FLOP, EventType.TURN, EventType.RIVER]:
            print(f"    牌面: {event.get('cards', [])}")
    
    # 统计手牌数量
    hand_starts = [e for e in events if e['event_type'] == EventType.HAND_START]
    hand_ends = [e for e in events if e['event_type'] == EventType.HAND_END]
    
    print("\n" + "=" * 80)
    print("手牌统计:")
    print("=" * 80)
    print(f"手牌开始: {len(hand_starts)} 次")
    print(f"手牌结束: {len(hand_ends)} 次")
    
    if hand_starts:
        print(f"\n第一手牌ID: {hand_starts[0].get('hand_id')}")
        print(f"最后一手牌ID: {hand_starts[-1].get('hand_id')}")
    
    # 统计玩家
    players = set()
    for event in events:
        if event.get('player'):
            player_info = event['player']
            players.add(f"{player_info['name']} @ {player_info['id']}")
        elif event['event_type'] == EventType.PLAYER_STACKS:
            stacks = event.get('stacks', {})
            for player_key in stacks.keys():
                players.add(player_key)
    
    print("\n" + "=" * 80)
    print("玩家统计:")
    print("=" * 80)
    print(f"发现 {len(players)} 位玩家:")
    for player in sorted(players):
        print(f"  - {player}")
    
    print("\n" + "=" * 80)
    print("解析完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

