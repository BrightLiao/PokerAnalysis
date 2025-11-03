"""
测试统计指标计算
"""

from src.storage.json_storage import JSONStorage
from src.analyzer.statistics import StatisticsCalculator

def main():
    print("=" * 100)
    print("测试基础指标计算")
    print("=" * 100)
    print()
    
    # 加载数据
    print("1. 加载数据...")
    hands, players = JSONStorage.load_data('data')
    print(f"   ✓ 加载了 {len(hands)} 手牌, {len(players)} 位玩家")
    
    # 计算统计指标
    print("\n2. 计算统计指标...")
    calculator = StatisticsCalculator(hands, players)
    stats = calculator.calculate_all()
    print(f"   ✓ 计算完成")
    
    # 显示统计结果
    print("\n3. 统计结果:")
    print()
    calculator.print_summary()
    
    # 详细展示一个玩家的数据
    print("\n" + "=" * 100)
    print("详细指标示例（第一位玩家）:")
    print("=" * 100)
    
    first_player_key = list(stats.keys())[0]
    player_stats = stats[first_player_key]
    
    print(f"\n玩家: {player_stats.player_name}")
    print(f"玩家Key: {player_stats.player_key}")
    print()
    
    print("基础数据:")
    print(f"  总手牌数: {player_stats.total_hands}")
    print(f"  总盈亏: {player_stats.total_profit:+.1f}")
    print()
    
    print("主动性指标:")
    print(f"  VPIP: {player_stats.vpip:.2f}% ({player_stats.vpip_count}/{player_stats.vpip_opportunities})")
    print(f"  PFR: {player_stats.pfr:.2f}% ({player_stats.pfr_count}/{player_stats.pfr_opportunities})")
    print(f"  3-Bet: {player_stats.three_bet_pct:.2f}% ({player_stats.three_bet_count}/{player_stats.three_bet_opportunities})")
    print()
    
    print("激进度指标:")
    print(f"  AF: {player_stats.af:.2f} (激进行动:{player_stats.aggressive_actions}, 被动行动:{player_stats.passive_actions})")
    print(f"  C-Bet: {player_stats.cbet_pct:.2f}% ({player_stats.cbet_count}/{player_stats.cbet_opportunities})")
    print()
    
    print("摊牌指标:")
    print(f"  WTSD: {player_stats.wtsd:.2f}% ({player_stats.went_to_showdown}/{player_stats.saw_flop})")
    print(f"  W$SD: {player_stats.won_sd_pct:.2f}% ({player_stats.won_at_showdown}/{player_stats.went_to_showdown})")
    print()
    
    print("街道统计:")
    print(f"  看到Flop: {player_stats.saw_flop} 次 ({player_stats.saw_flop/player_stats.total_hands*100:.1f}%)")
    print(f"  看到Turn: {player_stats.saw_turn} 次 ({player_stats.saw_turn/player_stats.total_hands*100:.1f}%)")
    print(f"  看到River: {player_stats.saw_river} 次 ({player_stats.saw_river/player_stats.total_hands*100:.1f}%)")
    print()
    
    print("收益指标:")
    print(f"  BB/100: {player_stats.bb_per_100:.2f}")
    
    # 导出为字典
    print("\n" + "=" * 100)
    print("所有玩家指标（字典格式）:")
    print("=" * 100)
    print()
    
    for player_key, stat in stats.items():
        print(f"{stat.player_name}:")
        stat_dict = stat.to_dict()
        for key, value in stat_dict.items():
            if key not in ['player_key', 'player_name']:
                print(f"  {key}: {value}")
        print()
    
    # 比较指标
    print("=" * 100)
    print("玩家风格对比:")
    print("=" * 100)
    print()
    
    # 找出最紧的玩家
    min_vpip = min(stats.values(), key=lambda s: s.vpip if s.vpip_opportunities > 0 else 100)
    print(f"最紧玩家（最低VPIP）: {min_vpip.player_name} - {min_vpip.vpip:.1f}%")
    
    # 找出最松的玩家  
    max_vpip = max(stats.values(), key=lambda s: s.vpip)
    print(f"最松玩家（最高VPIP）: {max_vpip.player_name} - {max_vpip.vpip:.1f}%")
    
    # 找出最激进的玩家
    max_af = max(stats.values(), key=lambda s: s.af if s.af != float('inf') else 0)
    print(f"最激进玩家（最高AF）: {max_af.player_name} - {max_af.af:.2f}")
    
    # 找出最被动的玩家
    min_af = min(stats.values(), key=lambda s: s.af if s.af != float('inf') else 0)
    print(f"最被动玩家（最低AF）: {min_af.player_name} - {min_af.af:.2f}")
    
    print("\n" + "=" * 100)
    print("✓ 测试完成!")
    print("=" * 100)


if __name__ == '__main__':
    main()

