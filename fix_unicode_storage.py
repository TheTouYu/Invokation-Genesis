#!/usr/bin/env python3
"""
修复数据库中的Unicode转义字符，转换为直接的中文字符
"""

import sqlite3
import json
import os


def fix_unicode_in_database():
    """修复数据库中的Unicode转义字符"""
    # 获取数据库路径
    db_path = os.path.join('instance', 'game.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    print(f"开始修复数据库中的Unicode转义字符: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有卡牌数据
        cursor.execute("SELECT id, skills, tags FROM card_data")
        rows = cursor.fetchall()
        
        updated_count = 0
        
        for row in rows:
            card_id, skills_str, tags_str = row
            
            # 处理skills字段
            if skills_str:
                try:
                    skills_obj = json.loads(skills_str)
                    fixed_skills = json.dumps(skills_obj, ensure_ascii=False)
                    
                    # 只有在修复后字符串发生变化时才更新
                    if fixed_skills != skills_str:
                        cursor.execute(
                            "UPDATE card_data SET skills = ? WHERE id = ?",
                            (fixed_skills, card_id)
                        )
                        updated_count += 1
                except (json.JSONDecodeError, TypeError):
                    pass  # 如果解析失败，跳过
            
            # 处理tags字段
            if tags_str:
                try:
                    tags_obj = json.loads(tags_str)
                    fixed_tags = json.dumps(tags_obj, ensure_ascii=False)
                    
                    # 只有在修复后字符串发生变化时才更新
                    if fixed_tags != tags_str:
                        cursor.execute(
                            "UPDATE card_data SET tags = ? WHERE id = ?",
                            (fixed_tags, card_id)
                        )
                        # 不增加updated_count，因为上面已经增加过了
                except (json.JSONDecodeError, TypeError):
                    pass  # 如果解析失败，跳过
        
        conn.commit()
        print(f"修复完成！更新了 {updated_count} 张卡牌的Unicode转义字符")
        return True
        
    except sqlite3.Error as e:
        print(f"数据库操作错误: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def verify_fix():
    """验证修复结果"""
    db_path = os.path.join('instance', 'game.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查一张卡牌
        cursor.execute("SELECT name, skills, tags FROM card_data WHERE name='茜特菈莉' LIMIT 1")
        row = cursor.fetchone()
        if row:
            name, skills, tags = row
            print(f"\n验证卡牌: {name}")
            print(f"技能字段前100字符: {skills[:100]}...")
            print(f"标签字段: {tags}")
            
            # 检查是否还有Unicode转义
            has_unicode = '\\\\u' in skills or '\\\\u' in tags
            print(f"是否包含Unicode转义: {has_unicode}")
            
            # 解析并显示实际内容
            skills_obj = json.loads(skills)
            if skills_obj:
                first_skill = skills_obj[0]
                print(f"第一个技能名称: {first_skill['name']}")
                print(f"第一个技能描述: {first_skill['description']}")
                
            tags_obj = json.loads(tags)
            print(f"标签: {tags_obj}")
            
        return True
    except Exception as e:
        print(f"验证错误: {e}")
        return False
    finally:
        conn.close()


def main():
    print("开始修复数据库中的Unicode转义字符...")
    success = fix_unicode_in_database()
    
    if success:
        print("\n验证修复结果...")
        verify_fix()
        print("\n✓ Unicode转义字符修复完成！")
    else:
        print("\n✗ Unicode转义字符修复失败！")


if __name__ == "__main__":
    main()