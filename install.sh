#!/bin/bash
# PokerNow 实时客户端安装脚本

echo "======================================================================"
echo "PokerNow 实时客户端 - 安装脚本"
echo "======================================================================"
echo ""

# 检测操作系统
OS=$(uname -s)
echo "检测到操作系统: $OS"
echo ""

# 1. 安装Python依赖
echo "步骤 1/3: 安装Python依赖..."
pip install selenium
if [ $? -eq 0 ]; then
    echo "✓ Selenium 安装成功"
else
    echo "✗ Selenium 安装失败"
    exit 1
fi
echo ""

# 2. 安装浏览器驱动
echo "步骤 2/3: 安装浏览器驱动..."

if [ "$OS" = "Darwin" ]; then
    # macOS
    echo "检测到 macOS，使用 Homebrew 安装..."
    
    # 检查 Homebrew 是否安装
    if ! command -v brew &> /dev/null; then
        echo "✗ Homebrew 未安装"
        echo "请先安装 Homebrew: https://brew.sh/"
        exit 1
    fi
    
    # 安装 geckodriver (Firefox)
    echo "安装 geckodriver (Firefox)..."
    brew install geckodriver 2>/dev/null || echo "geckodriver 可能已安装"
    
    # 可选：安装 chromedriver (Chrome)
    read -p "是否也安装 chromedriver (Chrome)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "安装 chromedriver..."
        brew install chromedriver 2>/dev/null || echo "chromedriver 可能已安装"
    fi
    
elif [ "$OS" = "Linux" ]; then
    # Linux
    echo "检测到 Linux..."
    
    # 检测包管理器
    if command -v apt-get &> /dev/null; then
        echo "使用 apt-get 安装..."
        sudo apt-get update
        sudo apt-get install -y firefox-geckodriver
        
        read -p "是否也安装 chromedriver? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo apt-get install -y chromium-chromedriver
        fi
    elif command -v yum &> /dev/null; then
        echo "使用 yum 安装..."
        echo "请手动下载并安装 geckodriver："
        echo "https://github.com/mozilla/geckodriver/releases"
    else
        echo "未检测到支持的包管理器"
        echo "请手动下载并安装 geckodriver："
        echo "https://github.com/mozilla/geckodriver/releases"
    fi
else
    echo "不支持的操作系统: $OS"
    echo "请手动安装 geckodriver："
    echo "https://github.com/mozilla/geckodriver/releases"
fi
echo ""

# 3. 运行环境测试
echo "步骤 3/3: 验证安装..."
python test_environment.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✓ 安装完成！"
    echo "======================================================================"
    echo ""
    echo "下一步："
    echo "1. 编辑 poker_live_simple.py，修改 GAME_URL"
    echo "2. 运行: python poker_live_simple.py"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo "✗ 部分组件安装失败"
    echo "======================================================================"
    echo ""
    echo "请查看上方错误信息并手动修复"
    echo ""
fi

