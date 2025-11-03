#!/usr/bin/env python3
"""
Gemini AI 德州扑克决策顾问
"""

import os
import google.generativeai as genai


class GeminiPokerAdvisor:
    """使用 Gemini 2.5 Flash 提供德州扑克决策建议"""
    
    def __init__(self, api_key=None):
        """
        初始化 Gemini 顾问
        
        Args:
            api_key: Gemini API Key，如果为None则从环境变量GEMINI_API_KEY获取
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("请设置 GEMINI_API_KEY 环境变量或传入 api_key 参数")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def get_action_advice(self, game_state, available_actions):
        """
        获取行动建议
        
        Args:
            game_state: 游戏状态对象
            available_actions: 可用行动列表 ['Check', 'Bet', 'Fold'] 等
            
        Returns:
            dict: {'action': 'Bet', 'amount': 100, 'reasoning': '...'}
        """
        # 构建提示词
        prompt = self._build_prompt(game_state, available_actions)
        
        # 调用 Gemini
        response = self.model.generate_content(prompt)
        
        # 解析响应
        return self._parse_response(response.text, available_actions)
    
    def _build_prompt(self, state, available_actions):
        """构建 Gemini 提示词"""
        
        # 找到自己的玩家
        my_player = None
        for player in state.players:
            if player.cards and any(suit in card for card in player.cards for suit in ['♠', '♥', '♦', '♣']):
                my_player = player
                break
        
        if not my_player:
            return "无法识别自己的玩家"
        
        # 计算底池大小（数值）
        pot_size = self._parse_chip_value(state.pot_size)
        my_stack = self._parse_chip_value(my_player.stack)
        
        prompt = f"""你是一位专业的德州扑克玩家。请根据以下牌局信息，给出最佳行动建议。

## 当前牌局信息

**游戏类型**: {state.game_type}
**盲注**: {'/'.join(map(str, state.blinds))}
**底池大小**: {state.pot_size} ({pot_size} 筹码)

**公共牌**: {' '.join(state.community_cards) if state.community_cards else '还未发牌'}

**我的手牌**: {' '.join(my_player.cards)}
**我的筹码**: {my_player.stack} ({my_stack} 筹码)
**我的位置**: {'庄家' if state.dealer_position == my_player.name else '非庄家'}

## 其他玩家信息

"""
        
        for i, player in enumerate(state.players, 1):
            if player.name == my_player.name:
                continue
            
            status = '已弃牌' if player.status == PlayerState.FOLDED else '活跃'
            bet_info = f"下注: {player.bet_value}" if player.bet_value and player.bet_value.strip() else "未下注"
            
            prompt += f"{i}. **{player.name}** - 筹码: {player.stack}, {bet_info}, 状态: {status}\n"
        
        prompt += f"\n**当前行动玩家**: {state.current_player}\n"
        
        # 可用行动
        prompt += f"\n## 可用行动\n\n"
        
        has_check = 'Check' in available_actions
        has_call = 'Call' in available_actions
        has_raise = 'Raise' in available_actions
        
        if has_check:
            prompt += "- **Check** (过牌)\n"
            prompt += "- **Bet** (下注) - 可选金额:\n"
            prompt += f"  - 1/3 pot: {pot_size * 0.33:.0f} 筹码\n"
            prompt += f"  - 1/2 pot: {pot_size * 0.5:.0f} 筹码\n"
            prompt += f"  - 2/3 pot: {pot_size * 0.67:.0f} 筹码\n"
            prompt += f"  - pot: {pot_size:.0f} 筹码\n"
            prompt += f"  - 1.5 pot: {pot_size * 1.5:.0f} 筹码\n"
            prompt += f"  - All-in: {my_stack:.0f} 筹码\n"
        
        if has_call:
            # 计算需要跟注的金额
            max_bet = 0
            for player in state.players:
                bet_val = self._parse_chip_value(player.bet_value)
                if bet_val > max_bet:
                    max_bet = bet_val
            my_bet = self._parse_chip_value(my_player.bet_value)
            call_amount = max_bet - my_bet
            
            prompt += f"- **Call** (跟注) - 需要 {call_amount:.0f} 筹码\n"
            prompt += "- **Raise** (加注) - 可选金额:\n"
            
            # 计算最小加注
            min_raise = call_amount * 2
            prompt += f"  - Mini raise: {min_raise:.0f} 筹码\n"
            prompt += f"  - 1/2 pot: {pot_size * 0.5:.0f} 筹码\n"
            prompt += f"  - pot: {pot_size:.0f} 筹码\n"
            prompt += f"  - 1.5 pot: {pot_size * 1.5:.0f} 筹码\n"
            prompt += f"  - All-in: {my_stack:.0f} 筹码\n"
        
        prompt += "- **Fold** (弃牌)\n"
        
        prompt += """

## 请给出建议

请分析当前牌局，并给出最佳行动建议。你的回答必须严格按照以下JSON格式：

```json
{
  "action": "行动名称(Check/Call/Bet/Raise/Fold)",
  "amount": 下注金额(仅Bet/Raise需要，其他为null),
  "reasoning": "决策理由，简要说明为什么这样做"
}
```

**重要提示**：
1. 只能选择可用行动中的一个
2. 如果选择Bet/Raise，amount必须是上面列出的预设金额之一
3. 考虑位置、筹码深度、对手行为等因素
4. 回答必须是有效的JSON格式，不要包含其他文本
"""
        
        return prompt
    
    def _parse_chip_value(self, value_str):
        """解析筹码数值"""
        if not value_str or value_str == 'All In':
            return 0
        
        # 移除逗号和其他非数字字符
        import re
        match = re.search(r'[\d,]+(?:\.\d+)?', str(value_str))
        if match:
            cleaned = match.group().replace(',', '')
            try:
                return float(cleaned)
            except:
                return 0
        return 0
    
    def _parse_response(self, response_text, available_actions):
        """解析 Gemini 响应"""
        import json
        import re
        
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response_text.strip()
            
            # 解析JSON
            result = json.loads(json_str)
            
            # 验证action是否在可用列表中
            action = result.get('action', '').strip()
            
            # 映射可能的别名
            action_map = {
                'check': 'Check',
                'call': 'Call',
                'bet': 'Raise',  # Bet在系统中用Raise实现
                'raise': 'Raise',
                'fold': 'Fold'
            }
            
            action_normalized = action_map.get(action.lower(), action)
            
            if action_normalized not in available_actions:
                # 如果AI建议的action不可用，使用保守策略
                if 'Check' in available_actions:
                    return {'action': 'Check', 'amount': None, 'reasoning': 'AI建议的行动不可用，保守选择Check'}
                elif 'Fold' in available_actions:
                    return {'action': 'Fold', 'amount': None, 'reasoning': 'AI建议的行动不可用，保守选择Fold'}
            
            return {
                'action': action_normalized,
                'amount': result.get('amount'),
                'reasoning': result.get('reasoning', '无理由说明')
            }
            
        except Exception as e:
            print(f"[DEBUG] 解析AI响应失败: {e}")
            print(f"[DEBUG] 原始响应: {response_text[:200]}")
            
            # 解析失败，返回保守策略
            if 'Check' in available_actions:
                return {'action': 'Check', 'amount': None, 'reasoning': '解析AI响应失败，保守选择Check'}
            elif 'Fold' in available_actions:
                return {'action': 'Fold', 'amount': None, 'reasoning': '解析AI响应失败，保守选择Fold'}
            else:
                return {'action': available_actions[0], 'amount': None, 'reasoning': '解析失败，选择第一个可用行动'}

