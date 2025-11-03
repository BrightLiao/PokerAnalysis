# parse_logs.sh 使用指南

## 📋 功能说明

这是一个自动化批量解析德州扑克日志的Shell脚本，可以：

1. ✅ 自动解析指定日期范围内的所有日志
2. ✅ 智能跳过不存在的日期
3. ✅ 自动合并相似名称的玩家
4. ✅ 自动合并多日数据
5. ✅ 可选生成统计报告

## 🚀 快速开始

### 基本用法

```bash
# 解析10/12到10/25的所有日志
./parse_logs.sh 1012 1025

# 解析并立即生成统计
./parse_logs.sh 1012 1025 --stats

# 解析所有10月的日志
./parse_logs.sh 1001 1031 --stats
```

## 📖 详细使用

### 命令格式

```bash
./parse_logs.sh <起始日期> <结束日期> [选项]
```

### 参数说明

#### 必需参数

- **起始日期**: 格式 `MMDD`（如 `1012` 表示 10月12日）
- **结束日期**: 格式 `MMDD`（如 `1025` 表示 10月25日）

#### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--no-merge` | 不合并相似名称的玩家 | 合并 |
| `--stats` | 自动生成统计报告 | 不生成 |
| `--quiet` / `-q` | 静默模式，减少输出 | 详细输出 |
| `--output <dir>` / `-o <dir>` | 指定输出目录 | `data/merged` |
| `--help` / `-h` | 显示帮助信息 | - |

## 📚 使用示例

### 示例1：基本解析

解析10月12日到10月25日的所有日志：

```bash
./parse_logs.sh 1012 1025
```

**输出**：
- 单日数据：`data/1012/`, `data/1021/`, `data/1022/`, `data/1024/`, `data/1025/`
- 合并数据：`data/merged/`

### 示例2：解析并生成统计

```bash
./parse_logs.sh 1012 1025 --stats
```

会自动生成完整的统计报告，包括：
- 总体统计
- 每日统计
- 玩家风格分析

### 示例3：指定输出目录

```bash
./parse_logs.sh 1012 1025 -o data/october --stats
```

数据会保存到 `data/october/` 目录。

### 示例4：不合并玩家名称

如果你想保留所有原始玩家名称（如"黄笃读"和"黄笃读2"不合并）：

```bash
./parse_logs.sh 1012 1025 --no-merge
```

### 示例5：静默模式

减少输出信息，只显示关键结果：

```bash
./parse_logs.sh 1012 1025 -q --stats
```

### 示例6：解析单天

虽然设计用于多日，但也可以解析单天：

```bash
./parse_logs.sh 1024 1024 --stats
```

## 📁 文件要求

脚本期望以下文件结构：

```
poker/
├── log/
│   ├── log_1012.csv       # 日志文件
│   ├── ledger_1012.csv    # 账本文件
│   ├── log_1021.csv
│   ├── ledger_1021.csv
│   └── ...
├── data/                   # 输出目录（自动创建）
└── parse_logs.sh          # 本脚本
```

## 🎯 工作流程

脚本会按以下步骤执行：

1. **检查日志文件**
   - 扫描指定日期范围
   - 列出所有找到的日志文件
   - 跳过不存在的日期

2. **解析日志**
   - 依次解析每天的日志
   - 保存到 `data/MMDD/` 目录
   - 显示解析进度和结果

3. **合并数据**（如果有多天）
   - 自动合并所有日期的数据
   - 合并相似名称的玩家
   - 保存到指定的输出目录

4. **生成统计**（如果指定了 `--stats`）
   - 计算所有统计指标
   - 显示总体和每日统计
   - 生成玩家风格分析

## 💡 实用技巧

### 技巧1：处理跨月数据

脚本自动处理跨月情况：

```bash
# 解析9月25日到10月5日
./parse_logs.sh 0925 1005 --stats
```

### 技巧2：增量更新

如果已经解析了部分数据，可以只解析新日期：

```bash
# 先解析1012-1024
./parse_logs.sh 1012 1024

# 后来有了1025的数据，重新合并
./parse_logs.sh 1012 1025 -o data/all_merged
```

### 技巧3：查看已解析的数据

解析完成后，可以随时查看统计：

```bash
python main.py stats -d data/merged
```

### 技巧4：批量处理

可以创建一个包装脚本来定期处理：

```bash
#!/bin/bash
# daily_parse.sh - 每日自动解析

TODAY=$(date +%m%d)
MONTH_START="${TODAY:0:2}01"

./parse_logs.sh $MONTH_START $TODAY --stats -o data/current_month
```

## 🐛 常见问题

### Q1: 脚本提示"未找到任何日志文件"

**原因**：指定日期范围内没有匹配的日志文件。

**解决**：
- 检查 `log/` 目录下的文件
- 确认文件命名格式：`log_MMDD.csv` 和 `ledger_MMDD.csv`
- 验证日期范围是否正确

### Q2: 某些日期解析失败

**原因**：日志文件格式错误或数据不完整。

**解决**：
- 查看错误信息
- 手动运行该日期的解析命令进行调试：
  ```bash
  python main.py parse log/log_1024.csv -l log/ledger_1024.csv -o data/1024 -m
  ```

### Q3: 合并后玩家数据异常

**原因**：可能是玩家名称合并逻辑导致。

**解决**：
- 使用 `--no-merge` 选项禁用自动合并
- 检查合并后的数据：
  ```bash
  python main.py load -d data/merged
  ```

### Q4: 脚本没有执行权限

**解决**：
```bash
chmod +x parse_logs.sh
```

## 📊 输出说明

### 单日数据结构

每天的数据会保存在独立目录：

```
data/1024/
├── hands.json        # 手牌数据
├── players.json      # 玩家数据
└── summary.json      # 摘要信息
```

### 合并数据结构

合并后的数据包含所有天的信息：

```
data/merged/
├── hands.json        # 所有手牌（带日期前缀）
├── players.json      # 合并后的玩家数据
└── summary.json      # 总体摘要
```

### 手牌ID格式

- 单日：`#1`, `#2`, `#3`, ...
- 多日：`20251024_#1`, `20251025_#2`, ...

## 🔄 与现有命令的对比

| 任务 | 传统方式 | 使用脚本 |
|------|---------|---------|
| 解析5天数据 | 运行5次parse命令 + 1次merge | `./parse_logs.sh 1012 1025` |
| 生成统计 | parse → merge → stats | `./parse_logs.sh 1012 1025 --stats` |
| 处理新数据 | 手动检查哪些日期有数据 | 自动扫描和跳过 |

## 🎓 高级用法

### 组合使用多个脚本

```bash
# 1. 先批量替换玩家名称
find log -name "*.csv" -exec sed -i '' 's/旧名称/新名称/g' {} \;

# 2. 然后批量解析
./parse_logs.sh 1001 1031 --stats -o data/october

# 3. 查看特定玩家的统计
python -c "from src.storage.json_storage import JSONStorage; \
  hands, players = JSONStorage.load_data('data/october'); \
  print({k:v.total_profit for k,v in players.items()})"
```

### 定时任务

添加到 crontab：

```cron
# 每天凌晨3点自动解析本月所有数据
0 3 * * * cd /path/to/poker && ./parse_logs.sh 0101 1231 --stats -q
```

## 📝 注意事项

1. ⚠️ 确保在 `poker` 项目根目录下运行脚本
2. ⚠️ 日期范围不要太大（建议不超过31天）
3. ⚠️ 合并数据时会覆盖输出目录中的现有数据
4. ⚠️ 使用 `--no-merge` 后，统计数据中可能会出现重复玩家

## 🎉 总结

`parse_logs.sh` 大大简化了多日日志的处理流程，从原来的多步骤手动操作变成了一行命令。特别适合：

- 📅 月度数据汇总
- 🔄 定期数据更新
- 📊 快速生成报告
- 🚀 批量处理历史数据

---

**更多信息**：查看项目主 README.md 或运行 `./parse_logs.sh --help`

