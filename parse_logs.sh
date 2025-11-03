#!/bin/bash

################################################################################
# 德州扑克日志批量解析脚本
# 
# 功能：
# 1. 解析指定日期范围内的所有日志文件
# 2. 自动跳过不存在的日期
# 3. 合并所有数据并生成统计
#
# 使用方法：
#   ./parse_logs.sh <起始日期> <结束日期> [选项]
#
# 示例：
#   ./parse_logs.sh 1012 1025              # 解析10/12到10/25的所有日志
#   ./parse_logs.sh 1012 1025 --no-merge   # 只解析，不合并玩家
#   ./parse_logs.sh 1021 1022 --stats      # 解析后自动生成统计
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
MERGE_PLAYERS=true
GENERATE_STATS=false
LOG_DIR="log"
DATA_DIR="data"
OUTPUT_DIR="data/merged_"+$1+"_"+$2
QUIET_MODE=false

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 显示使用帮助
show_help() {
    cat << EOF
德州扑克日志批量解析脚本

使用方法:
  ./parse_logs.sh <起始日期> <结束日期> [选项]

参数:
  起始日期        格式：MMDD（如 1012 表示 10月12日）
  结束日期        格式：MMDD（如 1025 表示 10月25日）

选项:
  --no-merge      不合并相似名称的玩家（默认：合并）
  --stats         解析后自动生成统计报告（默认：不生成）
  --quiet, -q     静默模式，减少输出信息
  --output, -o    指定合并后的输出目录（默认：data/merged）
  --help, -h      显示此帮助信息

示例:
  # 解析10/12到10/25的所有日志
  ./parse_logs.sh 1012 1025

  # 解析并自动生成统计
  ./parse_logs.sh 1012 1025 --stats

  # 不合并玩家名称
  ./parse_logs.sh 1012 1025 --no-merge

  # 指定输出目录
  ./parse_logs.sh 1012 1025 -o data/october

  # 静默模式
  ./parse_logs.sh 1012 1025 -q --stats

注意:
  - 脚本会自动跳过不存在的日期
  - 日志文件需要存在于 log/ 目录
  - 格式：log/log_MMDD.csv 和 log/ledger_MMDD.csv

EOF
}

# 检查日期是否有对应的日志文件
check_log_exists() {
    local date=$1
    local log_file="${LOG_DIR}/log_${date}.csv"
    local ledger_file="${LOG_DIR}/ledger_${date}.csv"
    
    if [[ -f "$log_file" && -f "$ledger_file" ]]; then
        return 0
    else
        return 1
    fi
}

# 生成日期范围内的所有日期
generate_date_list() {
    local start=$1
    local end=$2
    local dates=()
    
    # 提取月份和日期
    local start_month=${start:0:2}
    local start_day=${start:2:2}
    local end_month=${end:0:2}
    local end_day=${end:2:2}
    
    # 去除前导零
    start_month=$((10#$start_month))
    start_day=$((10#$start_day))
    end_month=$((10#$end_month))
    end_day=$((10#$end_day))
    
    # 生成日期列表
    for month in $(seq $start_month $end_month); do
        if [ $month -eq $start_month ]; then
            start_d=$start_day
        else
            start_d=1
        fi
        
        if [ $month -eq $end_month ]; then
            end_d=$end_day
        else
            # 获取该月的最后一天
            if [ $month -eq 2 ]; then
                end_d=29
            elif [ $month -eq 4 ] || [ $month -eq 6 ] || [ $month -eq 9 ] || [ $month -eq 11 ]; then
                end_d=30
            else
                end_d=31
            fi
        fi
        
        for day in $(seq $start_d $end_d); do
            # 格式化为MMDD
            printf -v date_str "%02d%02d" $month $day
            dates+=("$date_str")
        done
    done
    
    echo "${dates[@]}"
}

# 解析参数
START_DATE=""
END_DATE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-merge)
            MERGE_PLAYERS=false
            shift
            ;;
        --stats)
            GENERATE_STATS=true
            shift
            ;;
        --quiet|-q)
            QUIET_MODE=true
            shift
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$START_DATE" ]]; then
                START_DATE="$1"
            elif [[ -z "$END_DATE" ]]; then
                END_DATE="$1"
            else
                print_error "未知参数: $1"
                echo "使用 --help 查看帮助信息"
                exit 1
            fi
            shift
            ;;
    esac
done

# 检查必需参数
if [[ -z "$START_DATE" || -z "$END_DATE" ]]; then
    print_error "缺少必需参数: 起始日期和结束日期"
    echo ""
    show_help
    exit 1
fi

# 验证日期格式
if [[ ! "$START_DATE" =~ ^[0-9]{4}$ ]] || [[ ! "$END_DATE" =~ ^[0-9]{4}$ ]]; then
    print_error "日期格式错误，应为MMDD格式（如：1012）"
    exit 1
fi

# 显示配置信息
echo ""
echo "========================================================================"
echo "               德州扑克日志批量解析"
echo "========================================================================"
echo ""
print_info "配置信息:"
echo "  日期范围: $START_DATE - $END_DATE"
echo "  合并玩家: $MERGE_PLAYERS"
echo "  生成统计: $GENERATE_STATS"
echo "  输出目录: $OUTPUT_DIR"
echo ""

# 生成日期列表
all_dates=($(generate_date_list $START_DATE $END_DATE))
existing_dates=()

# 检查哪些日期有日志文件
print_info "检查日志文件..."
for date in "${all_dates[@]}"; do
    if check_log_exists "$date"; then
        existing_dates+=("$date")
        echo "  ✓ $date"
    fi
done

if [[ ${#existing_dates[@]} -eq 0 ]]; then
    print_error "未找到任何日志文件"
    exit 1
fi

echo ""
print_success "找到 ${#existing_dates[@]} 天的日志文件"
echo ""

# 步骤1: 解析所有日期的日志
echo "========================================================================"
echo "步骤 1: 解析日志文件"
echo "========================================================================"
echo ""

PARSE_OPTIONS=""
if [[ "$MERGE_PLAYERS" == true ]]; then
    PARSE_OPTIONS="$PARSE_OPTIONS -m"
fi
if [[ "$QUIET_MODE" == true ]]; then
    PARSE_OPTIONS="$PARSE_OPTIONS -q"
fi

for date in "${existing_dates[@]}"; do
    print_info "解析 $date 的日志..."
    
    if python main.py parse \
        "${LOG_DIR}/log_${date}.csv" \
        -l "${LOG_DIR}/ledger_${date}.csv" \
        -o "${DATA_DIR}/${date}" \
        $PARSE_OPTIONS; then
        print_success "$date 解析完成"
    else
        print_error "$date 解析失败"
        exit 1
    fi
    echo ""
done

# 步骤2: 合并所有数据
if [[ ${#existing_dates[@]} -gt 1 ]]; then
    echo ""
    echo "========================================================================"
    echo "步骤 2: 合并多日数据"
    echo "========================================================================"
    echo ""
    
    # 构建数据目录列表
    data_dirs=()
    for date in "${existing_dates[@]}"; do
        data_dirs+=("${DATA_DIR}/${date}")
    done
    
    print_info "合并 ${#existing_dates[@]} 天的数据..."
    
    if python main.py merge "${data_dirs[@]}" -o "$OUTPUT_DIR"; then
        print_success "数据合并完成"
    else
        print_error "数据合并失败"
        exit 1
    fi
else
    print_warning "只有一天的数据，跳过合并步骤"
    OUTPUT_DIR="${DATA_DIR}/${existing_dates[0]}"
fi

# 步骤3: 生成统计报告（可选）
if [[ "$GENERATE_STATS" == true ]]; then
    echo ""
    echo "========================================================================"
    echo "步骤 3: 生成统计报告"
    echo "========================================================================"
    echo ""
    
    print_info "计算统计指标..."
    
    if python main.py stats -d "$OUTPUT_DIR"; then
        print_success "统计报告生成完成"
    else
        print_error "统计报告生成失败"
        exit 1
    fi
fi

# 完成
echo ""
echo "========================================================================"
print_success "所有任务完成!"
echo "========================================================================"
echo ""
print_info "数据摘要:"
echo "  解析日期: ${existing_dates[@]}"
echo "  总天数: ${#existing_dates[@]} 天"
echo "  数据位置: $OUTPUT_DIR"
echo ""

if [[ "$GENERATE_STATS" == false ]]; then
    print_info "提示: 使用以下命令查看统计报告"
    echo "  python main.py stats -d $OUTPUT_DIR"
    echo ""
fi

exit 0

