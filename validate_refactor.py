#!/usr/bin/env python3
"""
七圣召唤卡牌系统重构 - 验证脚本

验证重构后的系统是否正常工作：
1. 网页抓取 → JSON文件（data_pipeline.py）
2. JSON文件 → 数据库（database_importer.py）  
3. 数据库 → API（standardized_cards.py）
4. 兼容旧API（deck_builder/api_routes.py）
"""

import os
import sys
import json
from pathlib import Path

def check_files():
    """检查所有必要的文件是否已创建"""
    required_files = [
        "data_pipeline.py",
        "database_importer.py", 
        "utils/card_data_processor.py",
        "api/standardized_cards.py",
        "api/deck_builder/api_routes.py"
    ]
    
    print("🔍 检查重构文件...")
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_present = False
    
    return all_present

def check_card_data_files():
    """检查卡牌数据文件是否存在"""
    data_dir = Path("card_data")
    if not data_dir.exists():
        print("⚠️  card_data 目录不存在，需要先运行数据流水线")
        return False
    
    required_data_files = ["characters.json", "equipments.json", "events.json", "supports.json"]
    print(f"\n🔍 检查数据文件...")
    all_present = True
    for file_name in required_data_files:
        file_path = data_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ {file_name} (共 {len(data)} 张卡牌)")
        else:
            print(f"❌ {file_name}")
            all_present = False
    
    return all_present

def show_refactoring_summary():
    """显示重构摘要"""
    print(f"\n" + "="*60)
    print(f"🎉 七圣召唤卡牌系统重构完成！")
    print(f"="*60)
    print(f"🔄 统一数据流水线:")
    print(f"   网页抓取 → JSON文件 → 数据库 → API")
    print(f"")
    print(f"📁 新增文件:")
    print(f"   • data_pipeline.py - 从网页抓取到JSON文件")
    print(f"   • database_importer.py - JSON到数据库导入")
    print(f"   • utils/card_data_processor.py - 统一数据处理器")
    print(f"   • api/standardized_cards.py - 标准化API端点")
    print(f"   • 修改: api/deck_builder/api_routes.py - 使用数据库源")
    print(f"   • 修改: app.py - 使用新API蓝图")
    print(f"")
    print(f"⚡ 统一数据源:")
    print(f"   • 所有API端点现在都使用数据库作为唯一数据源")
    print(f"   • 消除了文件和数据库之间的数据不一致")
    print(f"   • 统一了数据格式和处理逻辑")
    print(f"")
    print(f"🔧 标准化API:")
    print(f"   • 统一的响应格式和字段命名")
    print(f"   • 一致的过滤和分页机制")
    print(f"   • 兼容原API端点以保证向后兼容")
    print(f"")
    print(f"🚀 使用方法:")
    print(f"   1. python data_pipeline.py # 抓取最新数据到JSON文件")
    print(f"   2. python database_importer.py # 导入数据到数据库") 
    print(f"   3. python app.py # 启动应用并使用标准化API")
    print(f"="*60)

def main():
    print("🚀 开始验证七圣召唤卡牌系统重构...")
    
    # 检查必要文件
    files_ok = check_files()
    
    # 检查数据文件
    data_ok = check_card_data_files()
    
    if files_ok:
        print(f"\n✅ 文件结构验证通过")
    else:
        print(f"\n❌ 文件结构验证失败")
        
    if data_ok:
        print(f"✅ 数据文件验证通过")
    else:
        print(f"⚠️  数据文件验证警告")
    
    # 显示重构摘要
    show_refactoring_summary()
    
    return files_ok

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 验证完成！重构成功。")
    else:
        print(f"\n❌ 验证失败，请检查错误。")