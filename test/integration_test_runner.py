"""
集成测试文件
运行所有后端API和功能的测试
"""
import pytest
import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """运行所有测试"""
    print("开始运行所有后端测试...")
    
    # 获取test目录路径
    test_dir = Path(__file__).parent / "test"
    
    # 运行所有测试文件
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        print(f"在 {test_dir} 中未找到测试文件")
        return False
    
    all_tests_passed = True
    
    for test_file in test_files:
        print(f"\n运行测试文件: {test_file.name}")
        try:
            # 使用pytest运行单个测试文件
            result = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-v"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"测试文件 {test_file.name} 失败:")
                print(result.stdout)
                print(result.stderr)
                all_tests_passed = False
            else:
                print(f"测试文件 {test_file.name} 通过")
        except Exception as e:
            print(f"运行测试文件 {test_file.name} 时出错: {e}")
            all_tests_passed = False
    
    return all_tests_passed


def run_pytest_directly():
    """直接使用pytest运行所有测试"""
    print("\n使用pytest直接运行所有测试...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "test/", "-v", "--tb=short"], 
                              capture_output=True, text=True)
        
        print("测试输出:")
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"运行pytest时出错: {e}")
        return False


if __name__ == "__main__":
    print("七圣召唤后端集成测试")
    print("=" * 50)
    
    # 方法1: 逐个运行测试文件
    method1_result = run_tests()
    
    print("\n" + "=" * 50)
    
    # 方法2: 使用pytest运行所有测试
    method2_result = run_pytest_directly()
    
    print("\n" + "=" * 50)
    print("集成测试完成")
    
    if method1_result and method2_result:
        print("所有测试通过！ ✓")
        sys.exit(0)
    else:
        print("部分测试失败！ ✗")
        sys.exit(1)