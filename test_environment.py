#!/usr/bin/env python3
"""
环境测试脚本
用于验证所有依赖和配置是否正确
"""

import sys
import os

def test_python_version():
    """测试Python版本"""
    print("1. 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} (符合要求)")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (需要3.8+)")
        return False

def test_selenium():
    """测试Selenium是否安装"""
    print("\n2. 检查Selenium...")
    try:
        import selenium
        print(f"   ✓ Selenium {selenium.__version__} 已安装")
        return True
    except ImportError:
        print("   ✗ Selenium 未安装")
        print("   请运行: pip install selenium")
        return False

def test_webdriver():
    """测试WebDriver"""
    print("\n3. 检查WebDriver...")
    
    drivers_found = []
    
    # 测试 geckodriver (Firefox)
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.quit()
        print("   ✓ geckodriver (Firefox) 可用")
        drivers_found.append('firefox')
    except Exception as e:
        print(f"   ✗ geckodriver (Firefox) 不可用: {str(e)[:50]}...")
        print("   安装方法: brew install geckodriver")
    
    # 测试 chromedriver (Chrome)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("   ✓ chromedriver (Chrome) 可用")
        drivers_found.append('chrome')
    except Exception as e:
        print(f"   ✗ chromedriver (Chrome) 不可用: {str(e)[:50]}...")
        print("   安装方法: brew install chromedriver")
    
    return len(drivers_found) > 0

def test_pokernow_client():
    """测试PokerNow Client库"""
    print("\n4. 检查PokerNow Client...")
    
    # 添加到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pokernowclient/PokerNow'))
    
    try:
        from PokerNow import pokernow_client
        print("   ✓ PokerNow Client 库可访问")
        return True
    except ImportError as e:
        print(f"   ✗ PokerNow Client 库未找到: {e}")
        print("   请确保 pokernowclient/PokerNow 目录存在")
        return False

def test_project_files():
    """测试项目文件"""
    print("\n5. 检查项目文件...")
    
    required_files = [
        'poker_live_client.py',
        'poker_live_simple.py',
        'QUICKSTART.md',
        'LIVE_CLIENT_GUIDE.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} 未找到")
            all_exist = False
    
    return all_exist

def print_summary(results):
    """打印测试总结"""
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ 所有测试通过！环境配置正确。")
        print("\n下一步：")
        print("1. 修改 poker_live_simple.py 中的 GAME_URL")
        print("2. 运行: python poker_live_simple.py")
    else:
        print("\n✗ 部分测试失败，请修复以下问题：")
        for name, passed in results.items():
            if not passed:
                print(f"   - {name}")
        print("\n详细信息请查看上方测试结果")
    
    print("=" * 70)

def main():
    """主函数"""
    print("=" * 70)
    print("PokerNow 实时客户端 - 环境测试")
    print("=" * 70)
    print()
    
    results = {
        'Python版本': test_python_version(),
        'Selenium': test_selenium(),
        'WebDriver': test_webdriver(),
        'PokerNow Client': test_pokernow_client(),
        '项目文件': test_project_files()
    }
    
    print_summary(results)
    
    return 0 if all(results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())

