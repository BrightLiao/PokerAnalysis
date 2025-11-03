#!/usr/bin/env python3
"""
简化版PokerNow实时客户端
快速启动版本
"""

from poker_live_client import PokerLiveClient

# 配置
GAME_URL = "https://www.pokernow.club/games/pglE5APCtuH-6II94E949lSxo"  # 替换为你的游戏URL
BROWSER = "chrome"  # 或 "firefox"
REFRESH_INTERVAL = 2  # 刷新间隔（秒）

# AI 模式选择
AI_MODE = 'assist'  # 可选: 'manual', 'assist', 'auto'
# - 'manual': 完全手动，不使用AI
# - 'assist': AI辅助，给出建议由玩家决策（推荐）
# - 'auto': AI自动，AI决策并自动执行

def main():
    print("=" * 70)
    print("PokerNow 实时监控客户端 - 简化版")
    print("=" * 70)
    print(f"\n游戏URL: {GAME_URL}")
    print(f"浏览器: {BROWSER}")
    print(f"刷新间隔: {REFRESH_INTERVAL}秒")
    
    mode_desc = {
        'manual': '手动模式 - 完全由你决策',
        'assist': '辅助模式 - AI提供建议',
        'auto': '自动模式 - AI自动执行'
    }
    print(f"AI模式: {mode_desc.get(AI_MODE, AI_MODE)}")
    
    print("\n提示: 按 Ctrl+C 可随时退出")
    print("=" * 70)
    
    # 创建客户端
    client = PokerLiveClient(
        game_url=GAME_URL,
        browser=BROWSER,
        ai_mode=AI_MODE
    )
    
    # 运行
    try:
        # 首次运行需要登录
        client.run(auto_login=True)
        
        # 如果已有cookies，可以使用:
        # client.run(auto_login=False)
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序结束")

if __name__ == '__main__':
    main()

