"""
德州扑克日志分析系统 - 主程序
阶段一：数据解析和建模
"""

import argparse
import sys
from pathlib import Path
from typing import List

from src.parser.log_parser import PokerNowLogParser
from src.builder.data_builder import DataBuilder
from src.storage.json_storage import JSONStorage
from src.analyzer.statistics import StatisticsCalculator
from src.analyzer.multi_day_statistics import MultiDayStatistics
from src.builder.multi_day_merger import MultiDayMerger


def parse_log(log_file: str, ledger_file: str = 'log/ledger.csv', output_dir: str = 'data', 
              merge_players: bool = False, verbose: bool = True):
    """
    解析日志文件并保存数据
    
    Args:
        log_file: CSV日志文件路径
        ledger_file: Ledger文件路径
        output_dir: 输出目录
        merge_players: 是否合并相似名称的玩家
        verbose: 是否显示详细信息
    """
    if verbose:
        print("=" * 80)
        print("德州扑克日志分析系统 - 数据解析")
        print("=" * 80)
        print()
    
    # 检查文件是否存在
    if not Path(log_file).exists():
        print(f"❌ 错误: 找不到文件 {log_file}")
        return False
    
    try:
        # 1. 解析日志
        if verbose:
            print(f"步骤 1/3: 解析日志文件...")
            print(f"  文件: {log_file}")
        
        parser = PokerNowLogParser()
        events = parser.parse_file(log_file)
        
        if verbose:
            print(f"  ✓ 成功解析 {len(events)} 条事件")
        
        # 2. 构建数据模型
        if verbose:
            print(f"\n步骤 2/3: 构建数据模型...")
        
        builder = DataBuilder()
        hands, players = builder.build_from_events(events, ledger_file=ledger_file, 
                                                   merge_similar_players=merge_players)
        
        if verbose:
            print(f"  ✓ 构建了 {len(hands)} 手牌")
            print(f"  ✓ 识别了 {len(players)} 位玩家")
        
        # 3. 保存数据
        if verbose:
            print(f"\n步骤 3/3: 保存数据...")
        
        files = JSONStorage.save_data(hands, players, output_dir)
        
        if verbose:
            print(f"  ✓ 数据已保存到 {output_dir}/")
            for key, filepath in files.items():
                filesize = Path(filepath).stat().st_size / 1024
                print(f"      - {Path(filepath).name} ({filesize:.1f} KB)")
        
        # 显示摘要
        if verbose:
            print("\n" + "=" * 80)
            print("数据摘要:")
            print("=" * 80)
            
            total_pot = sum(hand.pot_size for hand in hands)
            hands_to_flop = sum(1 for hand in hands if hand.went_to_flop)
            hands_to_showdown = sum(1 for hand in hands if hand.went_to_showdown)
            
            print(f"\n手牌统计:")
            print(f"  总手牌数: {len(hands)}")
            print(f"  看到翻牌: {hands_to_flop} ({hands_to_flop/len(hands)*100:.1f}%)")
            print(f"  到摊牌: {hands_to_showdown} ({hands_to_showdown/len(hands)*100:.1f}%)")
            print(f"  总底池: {total_pot:.1f}")
            print(f"  平均底池: {total_pot/len(hands):.1f}")
            
            print(f"\n玩家统计:")
            print(f"  总玩家数: {len(players)}")
            print(f"\n  盈亏排名:")
            sorted_players = sorted(players.items(), key=lambda x: x[1].total_profit, reverse=True)
            for player_key, player in sorted_players:
                profit_str = f"{player.total_profit:+.1f}"
                print(f"    {player.name:15s}: {profit_str:>10s} ({player.hands_played} 手)")
            
            print("\n" + "=" * 80)
            print("✓ 解析完成!")
            print("=" * 80)
        
        return True
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def load_and_display(data_dir: str = 'data'):
    """
    加载并显示已保存的数据
    
    Args:
        data_dir: 数据目录
    """
    print("=" * 80)
    print("加载已保存的数据")
    print("=" * 80)
    print()
    
    try:
        # 检查目录是否存在
        if not Path(data_dir).exists():
            print(f"❌ 错误: 数据目录不存在 {data_dir}")
            return False
        
        # 加载数据
        print("正在加载数据...")
        hands, players = JSONStorage.load_data(data_dir)
        
        print(f"✓ 加载了 {len(hands)} 手牌")
        print(f"✓ 加载了 {len(players)} 位玩家")
        
        # 显示摘要
        print("\n" + "=" * 80)
        print("数据摘要:")
        print("=" * 80)
        
        if hands:
            print(f"\n时间范围:")
            print(f"  开始: {hands[0].timestamp}")
            print(f"  结束: {hands[-1].timestamp}")
        
        total_pot = sum(hand.pot_size for hand in hands)
        print(f"\n手牌统计:")
        print(f"  总手牌数: {len(hands)}")
        print(f"  总底池: {total_pot:.1f}")
        print(f"  平均底池: {total_pot/len(hands) if hands else 0:.1f}")
        
        print(f"\n玩家排名:")
        sorted_players = sorted(players.items(), key=lambda x: x[1].total_profit, reverse=True)
        for player_key, player in sorted_players:
            profit_str = f"{player.total_profit:+.1f}"
            print(f"  {player.name:15s}: {profit_str:>10s} ({player.hands_played} 手)")
        
        print("\n" + "=" * 80)
        
        return True
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def merge_multi_day(data_dirs: List[str], output_dir: str = 'data/merged'):
    """
    合并多天的数据
    
    Args:
        data_dirs: 数据目录列表
        output_dir: 输出目录
    """
    try:
        print("=" * 80)
        print("德州扑克日志分析系统 - 多日数据合并")
        print("=" * 80)
        
        # 合并数据
        merger = MultiDayMerger()
        hands, players = merger.merge_data_dirs(data_dirs, verbose=True)
        
        # 保存合并后的数据
        print(f"\n保存合并数据到 {output_dir}...")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        JSONStorage.save_data(hands, players, output_dir)
        
        # 显示每位玩家的每日数据
        print("\n" + "=" * 80)
        print("玩家每日数据汇总")
        print("=" * 80)
        
        for player_key, player in sorted(players.items(), 
                                        key=lambda x: x[1].total_profit, reverse=True):
            daily = merger.get_daily_breakdown(player_key)
            
            print(f"\n{player.name}:")
            print(f"  总计: {player.hands_played}手, {player.total_profit:+.1f}")
            print(f"  每日:")
            for date, data in sorted(daily.items()):
                print(f"    {date}: {data['hands']:3d}手, {data['profit']:+8.1f}")
        
        print("\n" + "=" * 80)
        print("✓ 多日数据合并完成!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def analyze_statistics(data_dir: str = 'data'):
    """
    分析统计指标
    
    Args:
        data_dir: 数据目录
    """
    print("=" * 100)
    print("德州扑克日志分析系统 - 统计分析")
    print("=" * 100)
    print()
    
    try:
        # 检查目录是否存在
        if not Path(data_dir).exists():
            print(f"❌ 错误: 数据目录不存在 {data_dir}")
            print(f"   请先运行: python main.py parse <日志文件>")
            return False
        
        # 加载数据
        print("正在加载数据...")
        hands, players = JSONStorage.load_data(data_dir)
        print(f"✓ 加载了 {len(hands)} 手牌, {len(players)} 位玩家\n")
        
        # 检测是否是多日数据（hand_id 中包含日期前缀）
        is_multi_day = False
        dates = set()
        if hands:
            for hand in hands:
                if '_' in hand.hand_id:
                    date = hand.hand_id.split('_')[0]
                    dates.add(date)
            is_multi_day = len(dates) > 1
        
        # 计算统计指标
        print("正在计算统计指标...")
        
        if is_multi_day:
            print(f"检测到多日数据 ({len(dates)} 天)")
            analyzer = MultiDayStatistics(hands, players)
            overall_stats, daily_stats = analyzer.calculate_all_statistics()
            print(f"✓ 计算完成\n")
            
            # 打印多日统计摘要
            analyzer.print_summary(overall_stats, daily_stats)
            return True
        
        # 单日数据分析
        calculator = StatisticsCalculator(hands, players)
        stats = calculator.calculate_all()
        print(f"✓ 计算完成\n")
        
        # 显示统计结果
        calculator.print_summary()
        
        # 显示风格对比
        print("\n" + "=" * 100)
        print("玩家风格对比:")
        print("=" * 100)
        print()
        
        # 找出最紧的玩家
        min_vpip = min(stats.values(), key=lambda s: s.vpip if s.vpip_opportunities > 0 else 100)
        print(f"  最紧玩家（最低VPIP）: {min_vpip.player_name:15s} - VPIP {min_vpip.vpip:.1f}%")
        
        # 找出最松的玩家  
        max_vpip = max(stats.values(), key=lambda s: s.vpip)
        print(f"  最松玩家（最高VPIP）: {max_vpip.player_name:15s} - VPIP {max_vpip.vpip:.1f}%")
        
        # 找出最激进的玩家
        max_af = max(stats.values(), key=lambda s: s.af if s.af != float('inf') else 0)
        print(f"  最激进玩家（最高AF）: {max_af.player_name:15s} - AF {max_af.af:.2f}")
        
        # 找出最被动的玩家
        min_af = min(stats.values(), key=lambda s: s.af if s.af != float('inf') else 0)
        print(f"  最被动玩家（最低AF）: {min_af.player_name:15s} - AF {min_af.af:.2f}")
        
        # 找出PFR最高的玩家
        max_pfr = max(stats.values(), key=lambda s: s.pfr)
        print(f"  最爱加注（最高PFR）: {max_pfr.player_name:15s} - PFR {max_pfr.pfr:.1f}%")
        
        # 找出C-Bet最高的玩家
        max_cbet = max(stats.values(), key=lambda s: s.cbet_pct if s.cbet_opportunities > 0 else 0)
        if max_cbet.cbet_opportunities > 0:
            print(f"  最爱持续下注（C-Bet）: {max_cbet.player_name:15s} - C-Bet {max_cbet.cbet_pct:.1f}%")
        
        print("\n" + "=" * 100)
        print("✓ 分析完成!")
        print("=" * 100)
        
        return True
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='德州扑克日志分析系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 解析日志文件（使用默认ledger路径）
  python main.py parse poker_log.csv
  
  # 解析并指定ledger文件和输出目录
  python main.py parse poker_log.csv -l log/ledger_20251024.csv -o data/1024
  
  # 解析并合并相似名称的玩家（如"黄笃读"和"黄笃读2"）
  python main.py parse log/log_20251025.csv -l log/ledger_20251025.csv -o data/1025 -m
  
  # 合并多天的数据
  python main.py merge data/1024 data/1025 data/1026 -o data/merged
  
  # 分析合并后的统计
  python main.py stats -d data/merged
  
  # 加载并显示已保存的数据
  python main.py load -d data
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # parse 命令
    parse_parser = subparsers.add_parser('parse', help='解析日志文件')
    parse_parser.add_argument('log_file', help='CSV日志文件路径')
    parse_parser.add_argument('-l', '--ledger', default='log/ledger.csv', help='Ledger文件路径 (默认: log/ledger.csv)')
    parse_parser.add_argument('-o', '--output', default='data', help='输出目录 (默认: data)')
    parse_parser.add_argument('-m', '--merge', action='store_true', help='合并相似名称的玩家（如"黄笃读"和"黄笃读2"）')
    parse_parser.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    
    # load 命令
    load_parser = subparsers.add_parser('load', help='加载已保存的数据')
    load_parser.add_argument('-d', '--data-dir', default='data', help='数据目录 (默认: data)')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='分析统计指标')
    stats_parser.add_argument('-d', '--data-dir', default='data', help='数据目录 (默认: data)')
    
    # merge 命令
    merge_parser = subparsers.add_parser('merge', help='合并多天的数据')
    merge_parser.add_argument('data_dirs', nargs='+', help='数据目录列表（按日期顺序）')
    merge_parser.add_argument('-o', '--output', default='data/merged', help='输出目录 (默认: data/merged)')
    
    args = parser.parse_args()
    
    if args.command == 'parse':
        success = parse_log(args.log_file, ledger_file=args.ledger, output_dir=args.output, 
                          merge_players=args.merge, verbose=not args.quiet)
        sys.exit(0 if success else 1)
    
    elif args.command == 'load':
        success = load_and_display(args.data_dir)
        sys.exit(0 if success else 1)
    
    elif args.command == 'stats':
        success = analyze_statistics(args.data_dir)
        sys.exit(0 if success else 1)
    
    elif args.command == 'merge':
        success = merge_multi_day(args.data_dirs, args.output)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

