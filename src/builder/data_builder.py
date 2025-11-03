"""
数据构建器
将解析后的事件转换为结构化的Hand、Action、Player对象
"""

import re
from typing import List, Dict
from collections import defaultdict

from ..models.hand import Hand
from ..models.action import Action, ActionType, Street
from ..models.player import Player
from ..parser.log_parser import EventType
from ..parser.ledger_parser import LedgerParser


class DataBuilder:
    """数据构建器"""
    
    def __init__(self):
        self.hands: List[Hand] = []
        self.players: Dict[str, Player] = {}
        self.current_hand: Hand = None
        self.current_street: Street = Street.PREFLOP
        # 跟踪待记录的买入/离场事件 {player_key: [{'type': ..., 'amount': ...}]}
        self.pending_chip_events: Dict[str, List[Dict]] = defaultdict(list)
        # 跟踪玩家最后的离场类型 {player_key: 'quit' or 'leave'}
        self.player_last_leave_type: Dict[str, str] = {}
    
    @staticmethod
    def normalize_player_name(name: str) -> str:
        """
        标准化玩家名称，去除数字后缀
        
        例如：
        - "黄笃读" -> "黄笃读"
        - "黄笃读2" -> "黄笃读"
        - "player123" -> "player"
        - "yx" -> "yx"
        
        Args:
            name: 原始玩家名称
            
        Returns:
            标准化后的名称
        """
        # 去除末尾的数字
        normalized = re.sub(r'\d+$', '', name)
        # 如果去除后为空（纯数字名称），返回原名称
        return normalized if normalized else name
    
    def build_from_events(self, events: List[Dict], ledger_file: str = 'log/ledger.csv', 
                         merge_similar_players: bool = False) -> tuple[List[Hand], Dict[str, Player]]:
        """
        从事件列表构建数据模型
        
        Args:
            events: 解析后的事件列表
            ledger_file: ledger文件路径（可选）
            merge_similar_players: 是否合并相似名称的玩家（例如"黄笃读"和"黄笃读2"）
            
        Returns:
            (hands, players)
        """
        for event in events:
            self._process_event(event)
        
        # 完成最后一手牌
        if self.current_hand:
            self._finalize_hand()
        
        # 使用ledger数据计算真实盈亏
        self._load_ledger_data(ledger_file)
        
        # 合并相似名称的玩家（如果启用）
        if merge_similar_players:
            self._merge_similar_players()
        
        return self.hands, self.players
    
    def _process_event(self, event: Dict):
        """处理单个事件"""
        event_type = event['event_type']
        
        if event_type == EventType.HAND_START:
            self._handle_hand_start(event)
        
        elif event_type == EventType.HAND_END:
            self._handle_hand_end(event)
        
        elif event_type == EventType.PLAYER_STACKS:
            self._handle_player_stacks(event)
        
        elif event_type == EventType.SMALL_BLIND:
            self._handle_small_blind(event)
        
        elif event_type == EventType.BIG_BLIND:
            self._handle_big_blind(event)
        
        elif event_type == EventType.FLOP:
            self._handle_flop(event)
        
        elif event_type == EventType.TURN:
            self._handle_turn(event)
        
        elif event_type == EventType.RIVER:
            self._handle_river(event)
        
        elif event_type in [EventType.FOLD, EventType.CHECK, EventType.CALL, 
                           EventType.BET, EventType.RAISE, EventType.ALL_IN]:
            self._handle_action(event)
        
        # 买入/离场/补码事件
        elif event_type == EventType.PLAYER_APPROVED:
            self._handle_player_approved(event)
        
        elif event_type == EventType.PLAYER_JOIN:
            self._handle_player_join(event)
        
        elif event_type == EventType.PLAYER_QUIT:
            self._handle_player_quit(event)
        
        elif event_type == EventType.PLAYER_LEAVE:
            self._handle_player_leave(event)
        
        elif event_type == EventType.PLAYER_ADDING:
            self._handle_player_adding(event)
        
        elif event_type == EventType.SHOW:
            self._handle_showdown(event)
        
        elif event_type == EventType.COLLECTED:
            self._handle_collected(event)
        
        # 保存原始事件到当前手牌
        if self.current_hand:
            self.current_hand.raw_events.append(event)
    
    def _handle_hand_start(self, event: Dict):
        """处理手牌开始"""
        # 如果有未完成的手牌，先完成它
        if self.current_hand:
            self._finalize_hand()
        
        # 创建新手牌
        hand_id = event.get('hand_id', 'unknown')
        hand_number = int(hand_id) if hand_id.isdigit() else len(self.hands) + 1
        
        self.current_hand = Hand(
            hand_id=hand_id,
            hand_number=hand_number,
            timestamp=event['timestamp'],
            dealer=event.get('dealer')
        )
        
        self.current_street = Street.PREFLOP
    
    def _handle_hand_end(self, event: Dict):
        """处理手牌结束"""
        # 手牌结束时完成当前手牌
        if self.current_hand:
            self._finalize_hand()
    
    def _handle_player_stacks(self, event: Dict):
        """处理玩家筹码信息"""
        if not self.current_hand:
            return
        
        stacks = event.get('stacks', {})
        for player_key, player_info in stacks.items():
            name = player_info['name']
            player_id = player_info['id']
            stack = player_info['stack']
            position = player_info.get('position')
            
            # 添加到当前手牌
            self.current_hand.add_player(name, player_id, stack, position)
            
            # 确保玩家在全局玩家字典中
            if player_key not in self.players:
                self.players[player_key] = Player(name=name, player_id=player_id)
            
            # 记录玩家参与的手牌
            self.players[player_key].add_hand(self.current_hand.hand_id, stack)
            
            # 处理待记录的买入/离场事件
            if player_key in self.pending_chip_events and self.pending_chip_events[player_key]:
                # 检查是否是玩家的第一手牌
                is_first_hand = len(self.players[player_key].hand_ids) == 1
                
                # 累计买入金额
                buyin_amount = 0
                for evt in self.pending_chip_events[player_key]:
                    # initial_join 只在第一手时不记录，后续出现则记录（理论上不应该有）
                    if evt['type'] == 'initial_join' and is_first_hand:
                        continue  # 第一手的初始买入不记录
                    # rejoin 和 adding 总是记录
                    buyin_amount += evt['amount']
                
                # 记录买入
                if buyin_amount > 0:
                    current_buyin = self.players[player_key].hand_buyins.get(self.current_hand.hand_id, 0)
                    self.players[player_key].hand_buyins[self.current_hand.hand_id] = current_buyin + buyin_amount
                
                # 清空该玩家的待处理事件
                self.pending_chip_events[player_key] = []
    
    def _handle_small_blind(self, event: Dict):
        """处理小盲注"""
        if not self.current_hand:
            return
        
        amount = event.get('amount', 0)
        self.current_hand.small_blind = amount
        
        # 创建小盲行动
        player = event.get('player')
        if player:
            action = Action(
                action_type=ActionType.SMALL_BLIND,
                player_name=player['name'],
                player_id=player['id'],
                amount=amount,
                street=Street.PREFLOP,
                timestamp=event['timestamp']
            )
            self.current_hand.add_action(action)
    
    def _handle_big_blind(self, event: Dict):
        """处理大盲注"""
        if not self.current_hand:
            return
        
        amount = event.get('amount', 0)
        self.current_hand.big_blind = amount
        
        # 创建大盲行动
        player = event.get('player')
        if player:
            action = Action(
                action_type=ActionType.BIG_BLIND,
                player_name=player['name'],
                player_id=player['id'],
                amount=amount,
                street=Street.PREFLOP,
                timestamp=event['timestamp']
            )
            self.current_hand.add_action(action)
    
    def _handle_flop(self, event: Dict):
        """处理翻牌"""
        if not self.current_hand:
            return
        
        cards = event.get('cards', [])
        # Flop应该有3张牌，但我们提取所有的
        self.current_hand.flop = cards[:3] if len(cards) >= 3 else cards
        self.current_street = Street.FLOP
    
    def _handle_turn(self, event: Dict):
        """处理转牌"""
        if not self.current_hand:
            return
        
        cards = event.get('cards', [])
        # Turn格式: "Turn: 10♥, J♣, J♠ [J♦]"
        # 最后一张是turn牌
        if cards:
            self.current_hand.turn = cards[-1]
        self.current_street = Street.TURN
    
    def _handle_river(self, event: Dict):
        """处理河牌"""
        if not self.current_hand:
            return
        
        cards = event.get('cards', [])
        # River格式: "River: 10♥, J♣, J♠, J♦ [5♠]"
        # 最后一张是river牌
        if cards:
            self.current_hand.river = cards[-1]
        self.current_street = Street.RIVER
    
    def _handle_action(self, event: Dict):
        """处理玩家行动"""
        if not self.current_hand:
            return
        
        player = event.get('player')
        if not player:
            return
        
        # 映射事件类型到行动类型
        event_to_action = {
            EventType.FOLD: ActionType.FOLD,
            EventType.CHECK: ActionType.CHECK,
            EventType.CALL: ActionType.CALL,
            EventType.BET: ActionType.BET,
            EventType.RAISE: ActionType.RAISE,
            EventType.ALL_IN: ActionType.ALL_IN,
        }
        
        action_type = event_to_action.get(event['event_type'])
        if not action_type:
            return
        
        action = Action(
            action_type=action_type,
            player_name=player['name'],
            player_id=player['id'],
            amount=event.get('amount', 0),
            street=self.current_street,
            timestamp=event['timestamp']
        )
        
        self.current_hand.add_action(action)
    
    def _handle_showdown(self, event: Dict):
        """处理摊牌"""
        if not self.current_hand:
            return
        
        player = event.get('player')
        cards = event.get('cards', [])
        
        if player and cards:
            self.current_hand.add_showdown(
                player['name'],
                player['id'],
                cards
            )
    
    def _handle_collected(self, event: Dict):
        """处理收集底池"""
        if not self.current_hand:
            return
        
        player = event.get('player')
        amount = event.get('amount', 0)
        
        if player:
            self.current_hand.set_winner(
                player['name'],
                player['id'],
                amount
            )
    
    def _handle_player_approved(self, event: Dict):
        """
        处理玩家批准入场（初始买入）
        
        注意：approved 和 join 通常成对出现，我们只记录 join 事件避免重复
        """
        # 不做记录，等待 join 事件
        pass
    
    def _handle_player_join(self, event: Dict):
        """
        处理玩家入场
        
        区分三种情况：
        1. 初始买入（第一次join）
        2. 重新买入（quit后再join）
        3. sit back（leave后再join，不是新买入）
        """
        player = event.get('player')
        amount = event.get('stack', 0)
        
        if player:
            player_key = f"{player['name']} @ {player['id']}"
            
            # 情况1：初始买入（第一次）
            if player_key not in self.players:
                self.pending_chip_events[player_key].append({
                    'type': 'initial_join',
                    'amount': amount
                })
                self.player_last_leave_type[player_key] = None
            
            # 情况2：重新买入（之前quit过）
            elif self.player_last_leave_type.get(player_key) == 'quit':
                self.pending_chip_events[player_key].append({
                    'type': 'rejoin',
                    'amount': amount
                })
                self.player_last_leave_type[player_key] = None
            
            # 情况3：sit back（之前只是leave）
            else:
                # 不记录，只是回座
                pass
    
    def _handle_player_quit(self, event: Dict):
        """处理玩家退出（带走筹码）"""
        player = event.get('player')
        amount = event.get('stack', 0)
        
        if player:
            player_key = f"{player['name']} @ {player['id']}"
            self.player_last_leave_type[player_key] = 'quit'
            # 不记录到 pending_chip_events
    
    def _handle_player_leave(self, event: Dict):
        """处理玩家暂离（stand up）"""
        player = event.get('player')
        amount = event.get('stack', 0)
        
        if player:
            player_key = f"{player['name']} @ {player['id']}"
            self.player_last_leave_type[player_key] = 'leave'
            # 不记录到 pending_chip_events
    
    def _handle_player_adding(self, event: Dict):
        """处理补码（adding chips）"""
        player = event.get('player')
        amount = event.get('amount', 0)
        
        if player:
            player_key = f"{player['name']} @ {player['id']}"
            # 记录补码（正数），标记为 adding 类型
            self.pending_chip_events[player_key].append({
                'type': 'adding',  # 重要：adding 不同于 rejoin
                'amount': amount
            })
    
    def _finalize_hand(self):
        """完成当前手牌"""
        if self.current_hand:
            self.hands.append(self.current_hand)
            self.current_hand = None
            self.current_street = Street.PREFLOP
    
    def _load_ledger_data(self, ledger_file: str):
        """
        从ledger文件加载真实的财务数据，并计算每手牌的盈利
        
        Args:
            ledger_file: ledger.csv文件路径
        """
        try:
            ledger_parser = LedgerParser()
            entries = ledger_parser.parse_file(ledger_file)
            
            if not entries:
                print(f"警告: 未找到ledger文件或文件为空，使用默认盈亏计算")
                return
            
            player_data = ledger_parser.calculate_player_totals(entries)
            
            # 更新玩家财务数据
            for player_key, data in player_data.items():
                if player_key in self.players:
                    self.players[player_key].set_ledger_data(
                        total_buy_in=data['total_buy_in'],
                        total_buy_out=data['total_buy_out'],
                        final_stack=data['final_stack'],
                        sessions=data['sessions']
                    )
                else:
                    # 如果ledger中有玩家但events中没有（可能只买入未打牌）
                    print(f"警告: ledger中的玩家 {player_key} 在游戏日志中未找到")
            
            # 计算每手牌的盈利
            self._calculate_hand_profits()
            
            # 验证零和规则
            is_zero_sum, total = ledger_parser.verify_zero_sum(player_data)
            if is_zero_sum:
                print(f"✓ 零和规则验证通过（总盈亏: {total:.2f}）")
            else:
                print(f"⚠️  警告: 盈亏总和不为0，差值: {total:.2f}")
            
            # 验证筹码一致性
            self._verify_stack_consistency()
                
        except Exception as e:
            print(f"警告: 加载ledger数据失败: {e}")
            print("将使用默认盈亏计算")
    
    def _calculate_hand_profits(self):
        """
        计算每手牌的盈利
        
        盈利 = 筹码变化 - 买入/离场
        """
        # 跟踪每个玩家的筹码变化
        player_stacks = {}  # {player_key: current_stack}
        
        for hand_idx, hand in enumerate(self.hands):
            # 计算每个玩家在这手牌中的盈亏
            for player_key in hand.players.keys():
                if player_key not in self.players:
                    continue
                
                # 本手开始时的筹码
                stack_before = hand.players[player_key]['stack']
                
                # 本手的买入/离场（从 hand_buyins 读取）
                buyin_change = self.players[player_key].hand_buyins.get(hand.hand_id, 0)
                
                # 本手结束后的筹码
                # 找玩家的下一手牌（可能跳过若干手）
                next_player_hand = None
                next_player_hand_idx = None
                for future_idx in range(hand_idx + 1, len(self.hands)):
                    if player_key in self.hands[future_idx].players:
                        next_player_hand = self.hands[future_idx]
                        next_player_hand_idx = future_idx
                        break
                
                if next_player_hand is not None:
                    # 玩家还有后续手牌
                    # 检查下一手是否有买入记录
                    next_hand_buyin = self.players[player_key].hand_buyins.get(next_player_hand.hand_id, 0)
                    
                    if next_hand_buyin > 0:
                        # 有买入记录，需要区分是"补码"还是"重新买入"
                        # 如果玩家连续参与（中间没有跳过手牌），说明是补码
                        is_continuous = (next_player_hand_idx == hand_idx + 1)
                        
                        if is_continuous:
                            # 补码（adding），玩家连续参与
                            # 下一手的starting_stack包含了补码，需要扣除
                            stack_after = next_player_hand.players[player_key]['stack'] - next_hand_buyin
                        else:
                            # 重新买入（rejoin），中间quit了，筹码归零
                            stack_after = 0
                    else:
                        # 没有买入记录，正常连续参与
                        stack_after = next_player_hand.players[player_key]['stack']
                else:
                    # 没有后续手牌，使用final_stack
                    stack_after = self.players[player_key].final_stack
                
                # 真实盈利计算
                # 盈利 = 筹码变化
                # 注意：starting_stack 已经包含了本手的买入，所以不能再扣除
                # 
                # 例如：quit后重新买入289
                # - starting_stack = 289（包含买入）
                # - next_hand starting_stack = 289（没变）
                # - 盈利 = 289 - 289 = 0（打平）
                # 
                # buyin只是记录买入行为，不影响每手盈利计算
                # 总盈利验证：sum(hand_profits) = final_stack - 初始筹码 - sum(buyins)
                hand_profit = stack_after - stack_before
                
                # 记录到玩家
                if hand.hand_id not in self.players[player_key].hand_profits:
                    self.players[player_key].hand_profits[hand.hand_id] = hand_profit
    
    def _verify_stack_consistency(self):
        """
        验证所有玩家的筹码一致性
        
        注意：由于玩家可能中途买入/离场，逐手计算的盈利可能与ledger不完全一致。
        这是预期行为，真实盈亏以ledger为准。
        """
        print("\n筹码验证:")
        print("-" * 80)
        
        all_close = True
        for player_key, player in self.players.items():
            summary = player.get_stack_summary()
            calculated = summary['calculated_profit_from_hands']
            ledger = summary['total_profit']
            diff = abs(calculated - ledger)
            diff_pct = (diff / abs(ledger) * 100) if ledger != 0 else 0
            
            # 如果差异小于1%或绝对值小于10，认为基本一致
            if diff < 10 or diff_pct < 1:
                status = "✓"
            elif player.sessions > 1:
                # 多次进场的玩家，差异是预期的
                status = "○"
                all_close = False
            else:
                status = "!"
                all_close = False
            
            print(f"{status} {player.name:12s}: 逐手={calculated:+8.1f}, "
                  f"ledger={ledger:+8.1f}, 差值={diff:6.1f} "
                  f"({player.sessions}次进场)")
        
        print("-" * 80)
        if all_close:
            print("✓ 所有玩家筹码验证通过")
        else:
            print("ℹ️  部分玩家有差异（多次进场导致），真实盈亏以ledger为准")
    
    def _merge_similar_players(self):
        """
        合并相似名称的玩家（例如"黄笃读"和"黄笃读2"）
        
        将数字后缀不同但基础名称相同的玩家合并为一个玩家
        """
        print("\n玩家名称合并:")
        print("-" * 80)
        
        # 1. 按标准化名称分组玩家
        name_groups = defaultdict(list)
        for player_key, player in self.players.items():
            normalized_name = self.normalize_player_name(player.name)
            name_groups[normalized_name].append((player_key, player))
        
        # 2. 找出需要合并的组（有多个玩家）
        merge_count = 0
        for normalized_name, player_list in name_groups.items():
            if len(player_list) > 1:
                # 需要合并
                print(f"合并玩家: {', '.join([p.name for _, p in player_list])} -> {normalized_name}")
                self._merge_player_group(normalized_name, player_list)
                merge_count += 1
        
        if merge_count == 0:
            print("未发现需要合并的玩家")
        else:
            print(f"✓ 成功合并 {merge_count} 组玩家")
        print("-" * 80)
    
    def _merge_player_group(self, target_name: str, player_list: List[tuple[str, Player]]):
        """
        合并一组玩家
        
        Args:
            target_name: 合并后的目标名称
            player_list: 需要合并的玩家列表 [(player_key, player), ...]
        """
        # 使用第一个玩家作为主玩家
        main_key, main_player = player_list[0]
        main_player.name = target_name  # 更新为标准化名称
        
        # 合并其他玩家的数据
        for player_key, player in player_list[1:]:
            # 合并财务数据
            main_player.total_buy_in += player.total_buy_in
            main_player.total_buy_out += player.total_buy_out
            main_player.final_stack += player.final_stack
            main_player.sessions += player.sessions
            main_player.total_profit += player.total_profit
            
            # 合并手牌数据
            main_player.hands_played += player.hands_played
            main_player.hand_ids.extend(player.hand_ids)
            main_player.starting_stacks.update(player.starting_stacks)
            main_player.hand_profits.update(player.hand_profits)
            main_player.hand_buyins.update(player.hand_buyins)
            
            # 更新所有手牌中的玩家引用
            for hand in self.hands:
                # 更新 hand.players
                if player_key in hand.players:
                    hand.players[main_key] = hand.players.pop(player_key)
                
                # 更新 hand.winners
                if player_key in hand.winners:
                    if main_key in hand.winners:
                        hand.winners[main_key] += hand.winners.pop(player_key)
                    else:
                        hand.winners[main_key] = hand.winners.pop(player_key)
                
                # 更新所有 actions
                for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
                    for action in hand.actions[street]:
                        if action.player_full_id == player_key:
                            action.player_name = target_name
                            # player_id 保持为 main_player 的 id（从 main_key 提取）
                            action.player_id = main_key.split(' @ ')[1]
                
                # 更新 showdowns
                if player_key in hand.showdowns:
                    hand.showdowns[main_key] = hand.showdowns.pop(player_key)
            
            # 从玩家字典中删除被合并的玩家
            del self.players[player_key]


def test_builder():
    """测试数据构建器"""
    from ..parser.log_parser import PokerNowLogParser
    
    print("测试数据构建器\n")
    print("=" * 80)
    
    # 解析日志
    parser = PokerNowLogParser()
    events = parser.parse_file('poker_now_log_pgleW51Lpe_LURB2EJlJSqety.csv')
    
    # 构建数据
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
    for player_key, player in sorted(players.items()):
        print(f"{player.name:15s} | 手牌: {player.hands_played:3d} | 盈亏: {player.total_profit:8.1f}")
    
    # 显示前几手牌
    print("\n" + "=" * 80)
    print("前5手牌详情:")
    print("=" * 80)
    for i, hand in enumerate(hands[:5]):
        print(f"\n手牌 #{hand.hand_number} ({hand.hand_id})")
        print(f"  时间: {hand.timestamp}")
        print(f"  玩家数: {len(hand.players)}")
        print(f"  盲注: {hand.small_blind}/{hand.big_blind}")
        print(f"  底池: {hand.pot_size}")
        
        if hand.flop:
            print(f"  Flop: {', '.join(hand.flop)}")
        if hand.turn:
            print(f"  Turn: {hand.turn}")
        if hand.river:
            print(f"  River: {hand.river}")
        
        print(f"  行动数: preflop={len(hand.actions[Street.PREFLOP])}, "
              f"flop={len(hand.actions[Street.FLOP])}, "
              f"turn={len(hand.actions[Street.TURN])}, "
              f"river={len(hand.actions[Street.RIVER])}")
        
        if hand.winners:
            print(f"  赢家: {list(hand.winners.keys())}")
        
        if hand.showdowns:
            print(f"  摊牌: {len(hand.showdowns)} 位玩家")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_builder()

