#!/usr/bin/env python3
"""
PokerNow 实时监控客户端
支持实时获取牌局信息并在命令行进行行动
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

# 添加pokernowclient到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pokernowclient/PokerNow'))

from PokerNow.pokernow_client import PokerClient
from PokerNow.models import PlayerState

try:
    from gemini_advisor import GeminiPokerAdvisor
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"[INFO] Gemini AI 不可用: {e}")
    GEMINI_AVAILABLE = False


class PokerLiveClient:
    """实时扑克客户端"""
    
    def __init__(self, game_url, browser='firefox', cookie_path='poker_cookies.pkl', ai_mode='assist'):
        """
        初始化客户端
        
        Args:
            game_url: pokernow游戏URL
            browser: 浏览器类型 ('firefox' 或 'chrome')
            cookie_path: cookie存储路径
            ai_mode: AI模式
                - 'manual': 完全手动，不使用AI
                - 'assist': AI辅助，给出建议由玩家决策（默认）
                - 'auto': AI自动，AI决策并自动执行
        """
        self.game_url = game_url
        self.driver = self._init_driver(browser)
        self.client = PokerClient(self.driver, cookie_path)
        self.running = False
        self.last_state = None
        self._last_action_context = {}  # 保存上次行动的上下文
        self._countdown_active = False  # 倒计时是否活跃
        self._countdown_start_time = 0  # 倒计时开始时间
        self._countdown_limit = 30  # 倒计时限制
        
        # AI 模式设置
        valid_modes = ['manual', 'assist', 'auto']
        if ai_mode not in valid_modes:
            print(f"⚠️  无效的AI模式 '{ai_mode}'，使用默认模式 'assist'")
            ai_mode = 'assist'
        
        self.ai_mode = ai_mode
        self.use_ai = ai_mode in ['assist', 'auto'] and GEMINI_AVAILABLE
        self.ai_advisor = None
        
        # 显示模式信息
        mode_names = {
            'manual': '手动模式 - 完全由玩家决策',
            'assist': '辅助模式 - AI给出建议，玩家决策',
            'auto': '自动模式 - AI自动决策并执行'
        }
        print(f"🎮 运行模式: {mode_names.get(ai_mode, ai_mode)}")
        
        # 初始化 Gemini AI
        if self.use_ai:
            try:
                self.ai_advisor = GeminiPokerAdvisor()
                print("✓ Gemini AI 已启用")
            except Exception as e:
                print(f"✗ 无法初始化 Gemini AI: {e}")
                self.use_ai = False
                if ai_mode == 'auto':
                    print("⚠️  自动模式需要AI，将切换到手动模式")
                    self.ai_mode = 'manual'
        
    def _init_driver(self, browser):
        """初始化WebDriver"""
        if browser.lower() == 'firefox':
            options = FirefoxOptions()
            # 可选：无头模式
            # options.add_argument('--headless')
            return webdriver.Firefox(options=options)
        elif browser.lower() == 'chrome':
            options = ChromeOptions()
            # 可选：无头模式
            # options.add_argument('--headless')
            return webdriver.Chrome(options=options)
        else:
            raise ValueError(f"不支持的浏览器: {browser}")
    
    def login_and_navigate(self):
        """登录并导航到游戏"""
        print("=" * 70)
        print("PokerNow 实时监控客户端")
        print("=" * 70)
        # print("\n请在浏览器中完成登录...")
        # print("登录完成后，程序将自动导航到游戏页面")
        
        # # 导航到登录页面
        # self.client.navigate('https://www.pokernow.club/')
        
        # input("\n按回车键继续（确保已登录）...")
        
        # # 保存cookies
        # self.client.cookie_manager.save_cookies()
        # print("✓ Cookies已保存")
        
        # 导航到游戏
        print(f"\n导航到游戏: {self.game_url}")
        self.client.navigate(self.game_url)
        time.sleep(3)  # 等待页面加载
        print("✓ 已进入游戏")
        
    def display_game_state(self, state):
        """显示游戏状态"""
        self._clear_screen()
        
        print("=" * 70)
        print(f"  游戏类型: {state.game_type}    盲注: {'/'.join(map(str, state.blinds))}")
        print("=" * 70)
        
        # 显示底池
        print(f"\n💰 底池: {state.pot_size}")
        
        # 显示公共牌
        if state.community_cards:
            cards_str = "  ".join(state.community_cards)
            print(f"🃏 公共牌: {cards_str}")
        else:
            print("🃏 公共牌: (还未发牌)")
        
        # 显示庄家和当前玩家
        print(f"\n🎲 庄家位置: {state.dealer_position}")
        print(f"👤 当前行动: {state.current_player}")
        
        # 显示所有玩家信息
        print("\n" + "─" * 70)
        print("玩家信息:")
        print("─" * 70)
        
        for i, player in enumerate(state.players, 1):
            status_icon = self._get_status_icon(player.status)
            cards_str = "  ".join(player.cards) if player.cards else "🎴  🎴"
            
            print(f"\n{i}. {status_icon} {player.name}")
            print(f"   筹码: {player.stack}  |  下注: {player.bet_value}")
            print(f"   手牌: {cards_str}")
            
            if player.hand_message:
                print(f"   💬 {player.hand_message}")
        
        # 显示获胜者
        if state.winners:
            print("\n" + "─" * 70)
            print("🏆 获胜者:")
            for winner in state.winners:
                print(f"   {winner['name']} - {winner['stack_info']}")
        
        print("\n" + "=" * 70)
        
        # 如果轮到你
        if state.is_your_turn:
            print("⏰ 轮到你行动了！")
            print("=" * 70)
        
    def _get_status_icon(self, status):
        """获取状态图标"""
        if status == PlayerState.CURRENT:
            return "➡️ "
        elif status == PlayerState.FOLDED:
            return "❌"
        elif status == PlayerState.OFFLINE:
            return "💤"
        else:
            return "✓ "
    
    def _clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def _parse_chip_value(self, value_str):
        """解析筹码数值 - 改进版"""
        if not value_str:
            return 0
        
        # 处理特殊情况
        value_str = str(value_str).strip()
        if value_str == 'All In' or value_str == '':
            return 0
        
        # 打印调试信息
        print(f"[DEBUG] 解析筹码: '{value_str}'")
        
        # 移除所有非数字字符（保留小数点）
        import re
        # 尝试匹配数字（支持逗号分隔和小数点）
        match = re.search(r'([\d,]+(?:\.\d+)?)', value_str)
        if match:
            cleaned = match.group(1).replace(',', '')
            try:
                result = float(cleaned)
                print(f"[DEBUG] 解析结果: {result}")
                return result
            except ValueError:
                print(f"[DEBUG] 解析失败: {cleaned}")
                return 0
        
        print(f"[DEBUG] 未找到数字")
        return 0
    
    def _get_preset_amounts(self, state, is_bet=True):
        """
        获取预设的下注金额
        
        Args:
            state: 游戏状态
            is_bet: True=Bet(无人下注), False=Raise(有人下注)
        
        Returns:
            list: [(显示名称, 金额值), ...]
        """
        pot_size = self._parse_chip_value(state.pot_size)
        
        # 找到自己的玩家
        my_player = None
        for player in state.players:
            if player.cards and any(suit in card for card in player.cards for suit in ['♠', '♥', '♦', '♣']):
                my_player = player
                break
        
        if not my_player:
            return []
        
        my_stack = self._parse_chip_value(my_player.stack)
        
        if is_bet:
            # Bet 选项：1/3 pot, 1/2 pot, 2/3 pot, pot, 1.5 pot, all-in
            amounts = [
                (f"1/3 Pot ({pot_size * 0.33:.0f})", pot_size * 0.33),
                (f"1/2 Pot ({pot_size * 0.5:.0f})", pot_size * 0.5),
                (f"2/3 Pot ({pot_size * 0.67:.0f})", pot_size * 0.67),
                (f"Pot ({pot_size:.0f})", pot_size),
                (f"1.5 Pot ({pot_size * 1.5:.0f})", pot_size * 1.5),
                (f"All-in ({my_stack:.0f})", my_stack)
            ]
        else:
            # Raise 选项：mini raise, 1/2 pot, pot, 1.5 pot, all-in
            # 计算最小加注
            max_bet = 0
            for player in state.players:
                bet_val = self._parse_chip_value(player.bet_value)
                if bet_val > max_bet:
                    max_bet = bet_val
            my_bet = self._parse_chip_value(my_player.bet_value)
            call_amount = max_bet - my_bet
            min_raise = call_amount * 2
            
            amounts = [
                (f"Mini Raise ({min_raise:.0f})", min_raise),
                (f"1/2 Pot ({pot_size * 0.5:.0f})", pot_size * 0.5),
                (f"Pot ({pot_size:.0f})", pot_size),
                (f"1.5 Pot ({pot_size * 1.5:.0f})", pot_size * 1.5),
                (f"All-in ({my_stack:.0f})", my_stack)
            ]
        
        # 过滤掉超过筹码量的选项
        return [(name, amt) for name, amt in amounts if amt <= my_stack]
    
    def get_user_action(self, state):
        """获取用户行动输入（带倒计时和AI建议）"""
        import signal
        import threading
        
        available_actions = self.client.action_helper.get_available_actions()
        
        # 判断是否有人下注
        has_bet = 'Call' in available_actions
        no_bet = 'Check' in available_actions
        
        # 保存状态供 execute_action 使用
        self._last_action_context = {'no_bet': no_bet}
        
        # 获取行动时间限制
        time_limit = self.client.game_state_manager.get_action_time_limit()
        
        # 获取 AI 建议
        ai_advice = None
        if self.use_ai and self.ai_advisor:
            try:
                print("\n🤖 AI 正在分析...")
                ai_advice = self.ai_advisor.get_action_advice(state, available_actions)
                print(f"💡 AI 建议: {ai_advice['action']}" + 
                      (f" {ai_advice['amount']:.0f}" if ai_advice.get('amount') else ""))
                print(f"📝 理由: {ai_advice['reasoning']}")
                
                # 自动模式：直接执行AI建议
                if self.ai_mode == 'auto':
                    print(f"\n⚡ 自动模式：执行 AI 建议")
                    time.sleep(2)  # 短暂延迟让用户看到建议
                    return ai_advice['action'], ai_advice.get('amount')
                    
            except Exception as e:
                print(f"⚠️  AI 分析失败: {e}")
                if self.ai_mode == 'auto':
                    print("⚠️  自动模式下AI失败，使用保守策略")
                    # 自动模式下AI失败，使用默认行动
                    if 'Check' in available_actions:
                        return 'Check', None
                    elif 'Fold' in available_actions:
                        return 'Fold', None
        
        print("\n可用行动:")
        actions_list = []
        action_map = {}  # 选项编号 -> (行动, 金额)
        option_num = 1
        
        # 构建行动选项
        for action in available_actions.keys():
            if action == 'Raise':
                # Bet/Raise 需要显示预设金额
                is_bet = no_bet
                action_display = 'Bet' if is_bet else 'Raise'
                preset_amounts = self._get_preset_amounts(state, is_bet)
                
                if preset_amounts:
                    print(f"\n  {action_display}:")
                    for amt_name, amt_value in preset_amounts:
                        # 标记 AI 推荐的选项（仅在辅助模式）
                        marker = ""
                        if self.ai_mode == 'assist' and ai_advice:
                            if (ai_advice['action'] == 'Raise' and 
                                ai_advice.get('amount') and 
                                abs(ai_advice['amount'] - amt_value) < 1):
                                marker = " 👈 AI推荐"
                        print(f"    {option_num}. {amt_name}{marker}")
                        action_map[option_num] = (action, amt_value)
                        option_num += 1
            else:
                # Check/Call/Fold 不需要金额
                marker = ""
                if self.ai_mode == 'assist' and ai_advice and ai_advice['action'] == action:
                    marker = " 👈 AI推荐"
                print(f"  {option_num}. {action}{marker}")
                action_map[option_num] = (action, None)
                option_num += 1
        
        print(f"  0. 跳过（不行动）")
        if self.ai_mode == 'assist' and ai_advice:
            print(f"  a. 自动执行AI建议")
        
        # 设置超时处理
        def timeout_handler(signum, frame):
            raise TimeoutError("输入超时")
        
        # 定义默认行动
        def get_default_action():
            if 'Check' in available_actions:
                return 'Check', None
            elif 'Fold' in available_actions:
                return 'Fold', None
            else:
                return None, None
        
        # 倒计时进度条显示
        self._countdown_active = True
        self._countdown_start_time = time.time()
        self._countdown_limit = time_limit
        
        def show_countdown():
            """在独立行显示倒计时进度条"""
            while self._countdown_active:
                elapsed = time.time() - self._countdown_start_time
                remaining = max(0, self._countdown_limit - elapsed)
                
                if remaining <= 0:
                    break
                
                # 计算进度
                progress = remaining / self._countdown_limit
                bar_length = 40
                filled_length = int(bar_length * progress)
                
                # 颜色编码
                if remaining <= 5:
                    color = '\033[91m'  # 红色
                elif remaining <= 10:
                    color = '\033[93m'  # 黄色
                else:
                    color = '\033[92m'  # 绿色
                reset = '\033[0m'
                
                # 构建进度条
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # 输出进度条（覆盖同一行）
                print(f'\r{color}⏱  [{bar}] {remaining:.1f}秒{reset}', end='', flush=True)
                
                time.sleep(0.1)
            
            # 清除进度条行
            print('\r' + ' ' * 60 + '\r', end='', flush=True)
        
        # 启动倒计时线程
        countdown_thread = threading.Thread(target=show_countdown, daemon=True)
        countdown_thread.start()
        
        try:
            # 设置超时
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(time_limit)
            
            while True:
                try:
                    # 根据模式显示不同提示
                    if self.ai_mode == 'assist' and ai_advice:
                        prompt_text = "\n请选择行动 (输入数字或 a): "
                    else:
                        prompt_text = "\n请选择行动 (输入数字): "
                    
                    choice = input(prompt_text).strip()
                    signal.alarm(0)  # 取消超时
                    self._countdown_active = False  # 停止倒计时
                    
                    # 处理特殊选项
                    if choice == '0':
                        return None, None
                    
                    if choice.lower() == 'a' and self.ai_mode == 'assist' and ai_advice:
                        # 辅助模式：手动执行 AI 建议
                        return ai_advice['action'], ai_advice.get('amount')
                    
                    # 处理数字选项
                    choice_num = int(choice)
                    if choice_num in action_map:
                        action, amount = action_map[choice_num]
                        return action, amount
                    else:
                        print("❌ 无效选择，请重新输入")
                        # 重新启动倒计时
                        self._countdown_active = True
                        self._countdown_start_time = time.time()
                        countdown_thread_retry = threading.Thread(target=show_countdown, daemon=True)
                        countdown_thread_retry.start()
                        signal.alarm(time_limit)  # 重新设置超时
                        
                except ValueError:
                    print("❌ 请输入有效数字或 'a'")
                    # 重新启动倒计时
                    self._countdown_active = True
                    self._countdown_start_time = time.time()
                    countdown_thread_retry = threading.Thread(target=show_countdown, daemon=True)
                    countdown_thread_retry.start()
                    signal.alarm(time_limit)  # 重新设置超时
                except KeyboardInterrupt:
                    signal.alarm(0)
                    self._countdown_active = False
                    return 'quit', None
                    
        except TimeoutError:
            signal.alarm(0)
            self._countdown_active = False  # 停止倒计时
            default_action, default_amount = get_default_action()
            print(f"\n⏰ 超时！自动执行: {default_action}")
            return default_action, default_amount
    
    def execute_action(self, action, amount=None):
        """执行行动"""
        if action == 'quit':
            return False
        
        if action:
            # 美化显示：Raise -> Bet/Raise
            display_action = action
            if action == 'Raise' and hasattr(self, '_last_action_context'):
                if self._last_action_context.get('no_bet', False):
                    display_action = 'Bet'
                else:
                    display_action = 'Raise'
            
            # 确保金额是整数（重要！）
            if amount is not None:
                amount = int(round(amount))  # 转换为整数
                print(f"[DEBUG] 执行金额: {amount}")
            
            print(f"\n执行行动: {display_action}" + (f" {amount}" if amount else ""))
            self.client.action_helper.perform_action(action, amount)
            print("✓ 行动已执行")
            time.sleep(2)
        
        return True
    
    def monitor_loop(self, refresh_interval=2):
        """监控循环"""
        self.running = True
        print("\n开始监控游戏...")
        print("按 Ctrl+C 随时退出\n")
        
        try:
            while self.running:
                # 获取游戏状态
                state = self.client.game_state_manager.get_game_state()
                
                # 显示状态
                self.display_game_state(state)
                
                # 如果轮到你行动
                if state.is_your_turn:
                    action, amount = self.get_user_action(state)
                    if not self.execute_action(action, amount):
                        break
                else:
                    # 等待一段时间再刷新
                    print(f"\n等待 {refresh_interval} 秒后刷新...")
                    time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("\n正在关闭...")
        if self.driver:
            self.driver.quit()
        print("✓ 已退出")
    
    def run(self, auto_login=True):
        """运行客户端"""
        try:
            if auto_login:
                self.login_and_navigate()
            else:
                self.client.navigate(self.game_url)
                time.sleep(3)
            
            self.monitor_loop()
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PokerNow实时监控客户端')
    parser.add_argument('game_url', help='游戏URL')
    parser.add_argument('--browser', '-b', default='firefox', 
                       choices=['firefox', 'chrome'], help='浏览器类型')
    parser.add_argument('--refresh', '-r', type=int, default=2,
                       help='刷新间隔（秒）')
    parser.add_argument('--no-login', action='store_true',
                       help='跳过登录步骤（已有cookies）')
    
    args = parser.parse_args()
    
    # 创建并运行客户端
    client = PokerLiveClient(
        game_url=args.game_url,
        browser=args.browser
    )
    
    client.run(auto_login=not args.no_login)


if __name__ == '__main__':
    main()

