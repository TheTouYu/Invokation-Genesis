#!/usr/bin/env python3
"""
Test script to verify the database contains expected tables and data
"""
import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'game.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("七圣召唤数据库测试报告")
print("=" * 30)

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"数据库中包含 {len(tables)} 个表:")
for table in tables:
    print(f"  - {table[0]}")

# Check users table
try:
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f"\n用户表 (users): {user_count} 条记录")
except sqlite3.OperationalError as e:
    print(f"\n用户表 (users) 不存在: {e}")

# Check card_data table
try:
    cursor.execute("SELECT COUNT(*) FROM card_data;")
    card_count = cursor.fetchone()[0]
    print(f"卡牌数据表 (card_data): {card_count} 条记录")
except sqlite3.OperationalError as e:
    print(f"卡牌数据表 (card_data) 不存在: {e}")

# Check decks table
try:
    cursor.execute("SELECT COUNT(*) FROM decks;")
    deck_count = cursor.fetchone()[0]
    print(f"卡组表 (decks): {deck_count} 条记录")
except sqlite3.OperationalError as e:
    print(f"卡组表 (decks) 不存在: {e}")

# Check game_histories table
try:
    cursor.execute("SELECT COUNT(*) FROM game_histories;")
    game_count = cursor.fetchone()[0]
    print(f"游戏历史表 (game_histories): {game_count} 条记录")
except sqlite3.OperationalError as e:
    print(f"游戏历史表 (game_histories) 不存在: {e}")

conn.close()

print("\n" + "=" * 30)
print("要访问 Metabase，请在浏览器中打开: http://localhost:8888")
print("在初始设置过程中，选择 SQLite 数据库，并使用路径: /app/data/db/game.db")
print("注意: 这是路径是容器内部的路径，对应于主机上的 ./instance/game.db")