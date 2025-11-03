# 德州扑克日志分析系统

一个功能强大的Poker Now德州扑克游戏日志分析工具，支持多日数据合并、自动玩家识别和全面的统计分析。

## ✨ 核心特性

### 离线分析
- 🎯 **智能日志解析**：自动解析Poker Now CSV格式日志
- 📊 **全面统计分析**：支持20+种核心扑克指标
- 🔄 **多日数据合并**：自动合并跨天数据，生成汇总和单日统计
- 👥 **智能玩家识别**：自动识别并合并相似名称玩家
- 💾 **数据持久化**：JSON格式存储，方便二次分析
- 🛠️ **自动化脚本**：一键批量处理多天日志
- ✅ **数据验证**：零和验证、筹码一致性检查
- 🤖 **AI玩家分析**：生成详细的玩家风格分析报告

### 实时监控
- 👀 **实时游戏状态**：自动获取底池、公共牌、玩家信息
- ⚡ **行动时机检测**：自动识别轮到你行动
- 🎮 **命令行操作**：支持Call/Raise/Check/Fold
- 🍪 **自动登录**：Cookie管理，无需重复登录

### AI辅助打牌
- 🤖 **Gemini AI集成**：使用Gemini 2.0 Flash提供决策建议
- 💡 **智能建议**：分析当前牌局，给出最佳行动和理由
- 🎯 **三种模式**：Manual（手动）/ Assist（辅助）/ Auto（自动）
- 📊 **底池计算**：自动计算各种下注比例
- 🎲 **位置感知**：考虑位置、筹码深度等因素

## 当前进度

### ✅ 阶段一：数据基础（已完成）

- [x] CSV日志解析器
- [x] 数据模型（Hand、Action、Player）
- [x] JSON数据持久化
- [x] 数据完整性验证
- [x] Ledger账本集成
- [x] 筹码流转追踪
- [x] 玩家买入/补码记录

### ✅ 阶段二：统计分析（已完成）

- [x] 基础指标计算（VPIP、PFR、AF）
- [x] 3-Bet率和C-Bet率
- [x] 摊牌统计（WTSD、W$SD）
- [x] BB/100收益计算
- [x] 位置统计
- [x] Fold to C-Bet
- [x] 偷盲率（Steal Rate）
- [x] 胜率和弃牌率
- [x] 多日数据合并统计
- [x] 每日统计分解

### ✅ 阶段三：实时监控（已完成）

- [x] 实时游戏状态获取
- [x] 命令行交互操作
- [x] 自动行动时机检测
- [x] Cookie自动管理
- [x] 多浏览器支持（Firefox/Chrome）

### ✅ 阶段四：AI辅助打牌（已完成）

- [x] Gemini AI集成
- [x] 实时决策建议
- [x] 三种运行模式（Manual/Assist/Auto）
- [x] 底池计算和预设金额
- [x] 决策理由说明

## 项目结构

```
poker/
├── src/                          # 源代码
│   ├── parser/                  # 日志解析模块
│   │   ├── log_parser.py        # Poker Now CSV解析器
│   │   └── ledger_parser.py     # 账本解析器
│   ├── models/                  # 数据模型
│   │   ├── hand.py              # 手牌模型
│   │   ├── action.py            # 行动模型
│   │   └── player.py            # 玩家模型
│   ├── builder/                 # 数据构建器
│   │   ├── data_builder.py      # 事件转数据模型
│   │   └── multi_day_merger.py  # 多日数据合并器
│   ├── storage/                 # 数据持久化
│   │   └── json_storage.py      # JSON存储
│   └── analyzer/                # 统计分析模块
│       ├── statistics.py        # 单日统计
│       └── multi_day_statistics.py  # 多日统计
├── pokernowclient/              # PokerNow Client库
│   └── PokerNow/               # 实时客户端底层库
├── log/                         # 原始日志目录
│   ├── log_MMDD.csv            # 游戏日志
│   └── ledger_MMDD.csv         # 账本文件
├── data/                        # 数据输出目录
│   ├── MMDD/                   # 单日数据
│   │   ├── hands.json          # 手牌数据
│   │   ├── players.json        # 玩家数据
│   │   └── summary.json        # 摘要信息
│   ├── merged/                 # 合并数据
│   └── stats/                  # 统计输出
├── parse_logs.sh               # 自动化批量解析脚本
├── main.py                     # 离线分析主程序
├── poker_live_client.py        # 实时客户端（完整版）
├── poker_live_simple.py        # 实时客户端（简化版）
├── gemini_advisor.py           # Gemini AI决策顾问
├── ai分析prompt.md             # AI分析prompt模板
├── 实时客户端说明.md            # 实时客户端文档
├── 三种模式说明.md              # AI模式详细说明
├── requirements.txt            # Python依赖包
└── README.md                   # 本文件
```

## 安装

### 环境要求

- Python 3.8+
- 推荐使用Conda环境管理
- Firefox或Chrome浏览器（实时监控功能需要）
- Gemini API Key（AI辅助功能需要）

### 安装步骤

#### 基础安装（离线分析）

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/poker-analyzer.git
cd poker-analyzer

# 2. 创建虚拟环境（推荐）
conda create -n pokerlog python=3.10
conda activate pokerlog

# 3. 安装依赖
pip install -r requirements.txt

# 4. 添加执行权限（如果使用自动化脚本）
chmod +x parse_logs.sh
```

#### 实时监控功能（可选）

```bash
# 1. 安装Selenium
pip install selenium

# 2. 安装浏览器驱动（macOS）
brew install geckodriver  # Firefox
brew install chromedriver  # Chrome（可选）

# Linux
# sudo apt-get install firefox-geckodriver

# Windows
# 下载 geckodriver.exe 并添加到PATH
```

#### AI辅助功能（可选）

```bash
# 1. 安装Google Generative AI
pip install google-generativeai

# 2. 获取API密钥
# 访问 https://aistudio.google.com/app/apikey

# 3. 设置环境变量
export GEMINI_API_KEY="你的API密钥"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export GEMINI_API_KEY="你的API密钥"' >> ~/.zshrc
```

## 使用场景

本项目支持三种使用场景：

### 场景一：离线分析（事后复盘）

导出CSV日志文件后，进行批量解析和统计分析。

**特点**：
- 📊 全面的统计分析
- 📈 多日数据合并
- 🤖 AI玩家分析报告
- 📁 数据持久化

### 场景二：实时监控（边打边看）

通过实时客户端连接到正在进行的游戏，实时查看游戏状态。

**特点**：
- 👀 实时显示底池、公共牌、玩家信息
- ⚡ 自动检测行动时机
- 🎮 命令行交互操作
- 🍪 Cookie自动管理

### 场景三：AI辅助打牌（智能决策）

使用Gemini AI提供实时决策建议，支持三种模式。

**特点**：
- 🤖 **Manual模式**：完全手动决策
- 💡 **Assist模式**：AI给建议，玩家决定（推荐）
- 🚀 **Auto模式**：AI全自动执行

---

## 快速开始

### 场景一：离线分析

#### 方法一：使用自动化脚本（推荐）

```bash
# 解析10月12日到10月25日的所有日志并生成统计
./parse_logs.sh 1012 1025 --stats

# 只解析，不生成统计
./parse_logs.sh 1012 1025

# 指定输出目录
./parse_logs.sh 1012 1025 -o data/october --stats
```

#### 方法二：使用Python命令

#### 1. 解析单日日志

```bash
# 基本用法
python main.py parse log/log_1024.csv -l log/ledger_1024.csv -o data/1024

# 合并相似名称的玩家（如"黄笃读"和"黄笃读2"）
python main.py parse log/log_1024.csv -l log/ledger_1024.csv -o data/1024 -m

# 静默模式
python main.py parse log/log_1024.csv -l log/ledger_1024.csv -o data/1024 -m -q
```

#### 2. 合并多日数据

```bash
# 合并多天的数据
python main.py merge data/1012 data/1021 data/1022 -o data/merged

# 查看合并后的数据
python main.py load -d data/merged
```

#### 3. 分析统计指标

```bash
# 分析统计指标（自动识别单日/多日）
python main.py stats -d data/merged > data/stats/merge_stat.txt

# 查看单日统计
python main.py stats -d data/1024 > data/stats/1024_single_stat.txt
```

#### 4. AI 分析与点评

将统计数据输出到文件，然后使用 `ai分析prompt.md` 中的 prompt 在大模型 chatbot 中进行分析。

```bash
# 输出统计数据
python main.py stats -d data/merged > analysis_data.txt

# 将 analysis_data.txt 和 ai分析prompt.md 中的 prompt 一起输入 ChatGPT/Claude 等大模型
# 获得详细的玩家分析报告
```

### 场景二：实时监控

#### 1. 安装额外依赖

```bash
# 安装 Selenium
pip install selenium

# 安装浏览器驱动（macOS）
brew install geckodriver  # Firefox
brew install chromedriver  # Chrome（可选）
```

#### 2. 配置游戏URL

编辑 `poker_live_simple.py` 第10行：
```python
GAME_URL = "https://www.pokernow.club/games/你的游戏ID"
```

#### 3. 运行实时客户端

```bash
python poker_live_simple.py
```

#### 4. 首次登录

1. 浏览器自动打开
2. 手动登录PokerNow账号
3. 回到命令行按回车
4. 开始实时监控！

#### 5. 使用界面

```
======================================================================
  游戏类型: No Limit Holdem    盲注: 50/100
======================================================================

💰 底池: 350
🃏 公共牌: A♠ | K♥ | 10♦

👤 当前行动: 你的名字

──────────────────────────────────────────────────────────────────────
玩家信息:
──────────────────────────────────────────────────────────────────────

1. ➡️  你的名字
   筹码: 2500  |  下注: 100
   手牌: A♥ | K♠

2. ✓  对手1
   筹码: 3000  |  下注: 100
   手牌: 🎴🎴

======================================================================
⏰ 轮到你行动了！
======================================================================

可用行动:
  1. Call
  2. Raise
  3. Fold
  0. 跳过（不行动）

请选择行动 (输入数字): _
```

详细使用说明请查看 [实时客户端说明.md](实时客户端说明.md)

### 场景三：AI辅助打牌

#### 1. 获取Gemini API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建API密钥
3. 设置环境变量：

```bash
export GEMINI_API_KEY="你的API密钥"
```

#### 2. 配置AI模式

编辑 `poker_live_simple.py`：

```python
# 选择AI模式
AI_MODE = 'manual'  # 手动模式：完全自己决策
AI_MODE = 'assist'  # 辅助模式：AI给建议，你决定（推荐）
AI_MODE = 'auto'    # 自动模式：AI全自动执行
```

#### 3. 运行AI辅助客户端

```bash
python poker_live_simple.py
```

#### 4. AI辅助模式界面（Assist模式）

```
🤖 AI 正在分析...
💡 AI 建议: Bet 450
📝 理由: 你有顶对，位置好，值得下注获取价值

可用行动:

  Bet:
    1. 1/3 Pot (150)
    2. 1/2 Pot (225)
    3. 2/3 Pot (300)
    4. Pot (450) 👈 AI推荐
    5. 1.5 Pot (675)
    6. All-in (2500)
  7. Check
  8. Fold
  0. 跳过（不行动）
  a. 自动执行AI建议

⏱  [████████████████] 18.5秒

请选择行动 (输入数字或 a): _
```

#### 5. 三种AI模式对比

| 特性 | Manual | Assist | Auto |
|------|--------|--------|------|
| AI分析 | ❌ | ✅ | ✅ |
| AI建议 | ❌ | ✅ | ✅ |
| AI标记 | ❌ | ✅ | ✅ |
| 用户输入 | ✅ | ✅ | ❌ |
| 快捷键 'a' | ❌ | ✅ | ❌ |
| 适合场景 | 学习/练习 | 日常对局 | 测试/观察 |

详细模式说明请查看 [三种模式说明.md](三种模式说明.md)

## 数据模型说明

### Hand（手牌）
- `hand_id`: 手牌唯一标识
- `hand_number`: 手牌序号
- `timestamp`: 时间戳
- `dealer`: 庄家信息
- `players`: 参与玩家及筹码
- `small_blind`, `big_blind`: 盲注
- `flop`, `turn`, `river`: 公共牌
- `actions`: 各街行动序列
- `showdowns`: 摊牌信息
- `pot_size`: 底池大小
- `winners`: 赢家和金额

### Action（行动）
- `action_type`: 行动类型（fold/check/call/bet/raise/all_in）
- `player_name`, `player_id`: 玩家信息
- `amount`: 金额
- `street`: 所在街道（preflop/flop/turn/river）
- `timestamp`: 时间戳

### Player（玩家）
- `name`, `player_id`: 玩家标识
- `hands_played`: 参与手牌数
- `total_profit`: 总盈亏
- `hand_ids`: 手牌历史
- `starting_stacks`: 每手牌初始筹码

## 统计指标说明

### 基础指标
- **VPIP** (Voluntarily Put in Pot): 主动入池率，反映玩家松紧程度
- **PFR** (Pre-Flop Raise): 翻牌前加注率，反映玩家激进程度
- **AF** (Aggression Factor): 激进因子 = (下注+加注) / 跟注
- **3-Bet**: 面对加注后再加注的比例
- **C-Bet** (Continuation Bet): 翻牌前加注后在flop继续下注的比例

### 摊牌指标
- **WTSD** (Went To Showdown): 摊牌率，看到flop后到摊牌的比例
- **W$SD** (Won $ at Showdown): 摊牌胜率

### 高级指标
- **Fold to C-Bet**: 面对持续下注的弃牌率
- **Steal Rate**: 偷盲率（后位加注偷盲的比例）
- **Win Rate**: 胜率（赢得手牌的比例）
- **Fold Rate**: 总体弃牌率
- **Position Stats**: 不同位置的VPIP和PFR统计

### 收益指标
- **BB/100**: 每100手牌的大盲收益
- **总盈亏**: 玩家总盈亏金额（基于ledger账本）
- **每日盈亏**: 多日数据的每日盈亏分解

### 风格分类
- **紧凶** (TAG): VPIP 20-30%, PFR 15-25%, AF > 1.5
- **松凶** (LAG): VPIP > 30%, PFR > 20%, AF > 1.5  
- **紧弱** (Rock): VPIP < 25%, AF < 1.0
- **松弱** (Calling Station): VPIP > 35%, AF < 1.0

### 多日统计特性
- **总体统计**: 所有日期的汇总数据和指标
- **单日统计**: 每一天的独立统计和指标
- **盈亏追踪**: 跨天盈亏趋势和每日表现
- **数据验证**: 零和验证确保数据准确性

## 测试

项目包含多个测试脚本：

```bash
# 测试解析器
python test_parser.py

# 测试数据构建
python test_builder.py

# 测试存储功能
python test_storage.py

# 测试统计分析
python test_statistics.py
```

## 输出示例

### 单日解析输出

```
================================================================================
德州扑克日志分析系统 - 数据解析
================================================================================

步骤 1/3: 解析日志文件...
  文件: log/log_1024.csv
  ✓ 成功解析 1910 条事件

步骤 2/3: 构建数据模型...
✓ 零和规则验证通过（总盈亏: 0.00）

筹码验证:
--------------------------------------------------------------------------------
✓ yx          : 逐手=  +480.0, ledger=  +480.0, 差值=   0.0 (1次进场)
✓ vzzz        : 逐手=  +465.0, ledger=  +465.0, 差值=   0.0 (1次进场)
✓ ldl         : 逐手=   +78.0, ledger=   +78.0, 差值=   0.0 (1次进场)
--------------------------------------------------------------------------------
✓ 所有玩家筹码验证通过

玩家名称合并:
--------------------------------------------------------------------------------
合并玩家: 黄笃读, 黄笃读2 -> 黄笃读
✓ 成功合并 1 组玩家
--------------------------------------------------------------------------------
  ✓ 构建了 91 手牌
  ✓ 识别了 6 位玩家

步骤 3/3: 保存数据...
  ✓ 数据已保存到 data/1024/
      - hands.json (384.2 KB)
      - players.json (21.4 KB)
      - summary.json (0.2 KB)
```

### 多日统计输出

```
========================================================================================================================
多日统计汇总
========================================================================================================================

【总体统计】
========================================================================================================================
玩家            手牌   VPIP    PFR     AF  3-Bet  C-Bet  Steal   Fold     胜率         盈亏
------------------------------------------------------------------------------------------------------------------------
vzzz           488    32.4    20.1     1.3    6.7   36.8   29.1    85.9    10.7      +1453.0
gf             389    89.2    18.8     0.5    7.4   52.3   14.3    56.3    29.8       +852.0
xx             646    74.0    14.2     0.5    8.1   50.6   27.3    74.9    18.1       +509.0
...

【20251024 单日统计】
玩家            手牌   VPIP    PFR     AF  3-Bet  C-Bet  Steal   Fold     胜率         盈亏
------------------------------------------------------------------------------------------------------------------------
yx              50    78.0    22.0     0.6   14.3   70.0   10.0    70.0    22.0       +480.0
vzzz            86    39.5    30.2     1.5    0.0   30.0   30.0    79.1    19.8       +465.0
...
```

## 支持的日志格式

本系统支持 [Poker Now](https://www.pokernow.club/) 导出的CSV格式日志，包含以下信息：

### 游戏日志 (log_MMDD.csv)
- 手牌开始/结束
- 玩家行动（下注/跟注/加注/弃牌/过牌/all-in）
- 公共牌（Flop/Turn/River）
- 摊牌信息
- 底池收集
- 玩家筹码变动
- 玩家进场/离场/补码记录

### 账本文件 (ledger_MMDD.csv)
- 玩家买入记录
- 玩家离场金额
- 最终筹码余额
- 进场次数统计

## 核心功能详解

### 1. 智能玩家识别

自动识别并合并以下情况的玩家：
- 同一玩家的不同账号（如"黄笃读"和"黄笃读2"）
- 跨天游戏中的同一玩家
- 基于玩家ID的准确匹配

### 2. 数据验证

- **零和验证**: 确保所有玩家盈亏之和为0
- **筹码一致性**: 验证筹码流转的准确性
- **逐手验证**: 每手牌的盈亏计算和验证
- **买入追踪**: 准确记录初始买入、补码、离场

### 3. 多日数据处理

- 自动为手牌添加日期前缀（如`20251024_#1`）
- 合并跨天玩家的所有数据
- 生成总体统计和每日统计
- 盈亏趋势分析

### 4. 自动化脚本

`parse_logs.sh` 提供以下功能：
- 批量解析指定日期范围的日志
- 自动跳过不存在的日期
- 一键生成统计报告
- 灵活的参数配置

详细使用方法见 [PARSE_LOGS_GUIDE.md](PARSE_LOGS_GUIDE.md)

## 下一步计划

- [x] 阶段一：数据基础（已完成）
  - [x] CSV日志解析
  - [x] 数据模型设计
  - [x] JSON持久化
  - [x] Ledger集成
  - [x] 数据验证
  
- [x] 阶段二：统计分析（已完成）
  - [x] 核心指标计算
  - [x] 高级指标
  - [x] 多日数据合并
  - [x] 自动化脚本
  
- [x] 阶段三：实时监控（已完成）
  - [x] 实时游戏状态获取
  - [x] 命令行交互操作
  - [x] Cookie自动管理
  - [x] 多浏览器支持
  
- [x] 阶段四：AI辅助打牌（已完成）
  - [x] Gemini AI集成
  - [x] 三种运行模式
  - [x] 实时决策建议
  - [x] AI玩家分析（通过prompt）
  
- [ ] 阶段五：功能优化（计划中）
  - [ ] 实时统计集成（边打边统计）
  - [ ] AI决策质量评估
  - [ ] 运行时模式切换
  - [ ] GUI图形界面
  
- [ ] 阶段六：精彩手牌筛选（计划中）
  - [ ] 大底池手牌识别
  - [ ] 特殊牌型检测
  - [ ] 文字回放生成
  - [ ] 关键决策点分析
  
- [ ] 阶段七：HTML页面展示（计划中）
  - [ ] 数据可视化
  - [ ] 交互式图表
  - [ ] 报告生成
  - [ ] 玩家对比分析

## 技术栈

### 核心技术
- **语言**: Python 3.8+
- **数据处理**: 标准库（csv, json, datetime, pathlib, re等）
- **环境管理**: Conda

### 实时监控
- **浏览器自动化**: Selenium WebDriver
- **浏览器**: Firefox (geckodriver) / Chrome (chromedriver)
- **底层库**: PokerNow Client

### AI功能
- **大语言模型**: Google Gemini 2.0 Flash
- **API**: google-generativeai

### 未来计划
- **数据分析**: pandas, numpy
- **可视化**: ECharts, Plotly
- **Web框架**: Flask / FastAPI

## 常见问题

### 离线分析

#### Q: 如何处理玩家名称重复？

使用 `-m` 参数自动合并相似名称：
```bash
python main.py parse log.csv -l ledger.csv -m
```

#### Q: 支持哪些日期格式？

目前支持 `MMDD` 格式（如 `1024` 表示10月24日）。

#### Q: 数据不一致怎么办？

检查以下几点：
1. ledger文件是否完整
2. 是否有玩家中途退出又重新进入
3. 查看验证输出中的具体差异

#### Q: 如何批量处理多天数据？

使用自动化脚本：
```bash
./parse_logs.sh 1012 1025 --stats
```

### 实时监控

#### Q: 浏览器启动失败怎么办？

检查驱动是否安装：
```bash
geckodriver --version  # Firefox
chromedriver --version  # Chrome
```

重新安装：
```bash
brew reinstall geckodriver
```

#### Q: Cookie失效了怎么办？

删除并重新登录：
```bash
rm poker_cookies.pkl
python poker_live_simple.py
```

#### Q: 可以后台运行吗？

可以启用无头模式，编辑 `poker_live_client.py`：
```python
options.add_argument('--headless')  # 取消注释
```

### AI辅助

#### Q: 如何获取Gemini API Key？

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建API密钥
3. 设置环境变量：`export GEMINI_API_KEY="你的密钥"`

#### Q: AI的建议准确吗？

AI建议基于统计概率和位置策略，不保证100%正确。建议：
- 在Assist模式下学习AI的思路
- 结合自己的判断做决策
- 记录并复盘AI建议的效果

#### Q: 三种AI模式如何选择？

- **Manual**: 想完全自己决策
- **Assist**: 想要AI帮助但自己决定（推荐）
- **Auto**: 测试AI性能或观察学习

#### Q: Auto模式安全吗？

Auto模式会自动执行AI决策，有风险。建议：
- 仅用于测试和学习
- 使用小筹码账号
- 有人监督

#### Q: API调用频率限制？

Gemini API有免费额度和速率限制：
- 免费版：15次/分钟
- 每手牌消耗1次调用
- 建议合理使用

## 贡献

欢迎提交Issue和Pull Request！

## 许可

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue。

---

**注意**: 本项目仅用于学习和娱乐目的，请遵守当地法律法规。

