## 项目需求

#### 背景
我和几位朋友在 pokernow 网站进行德州扑克对局，这是对局时的网页
https://www.pokernow.club/games/pglMy7rizRLjC3IrhYgYIgwba  

在这个网页中，左下角有个 log/ledger 按钮，点击去可以获取到每一手牌正在进行中的实时 session log，可以看到玩家筹码、自己的牌和每轮的信息。

#### 需求
1. ✅ 我想写一个程序自动拉取当前手牌的 session log
2. 🔄 调用 gemini 2.5 来帮我决策如何行动

---

## 解决方案

### 技术方案
使用 **PokerNow Client** (基于Selenium的自动化库) 实时获取游戏状态并执行操作。

### 已实现功能
✅ 实时获取游戏状态（底池、公共牌、玩家信息）  
✅ 检测轮到你行动的时机  
✅ 命令行交互式操作（Call/Raise/Check/Fold）  
✅ 自动登录和Cookie管理  
✅ 实时监控循环  

### 实现文件
- `poker_live_client.py` - 完整版客户端（支持命令行参数）
- `poker_live_simple.py` - 简化版客户端（快速启动）
- `QUICKSTART.md` - 5分钟快速启动指南
- `LIVE_CLIENT_GUIDE.md` - 完整使用文档

### 快速开始
```bash
# 1. 安装依赖
pip install selenium
brew install geckodriver

# 2. 修改游戏URL（在poker_live_simple.py中）
GAME_URL = "https://www.pokernow.club/games/你的游戏ID"

# 3. 运行
python poker_live_simple.py
```

### 下一步计划
🔄 集成 Gemini 2.5 Flash API 进行AI决策  
🔄 自动化策略引擎  
🔄 历史记录和统计分析集成