# fetch_and_save_cards.py
import requests
import json
import os
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000/api"
OUTPUT_DIR = "card_data"

ENDPOINTS = {
    "characters": "/characters",
    "equipments": "/equipments",
    "supports": "/supports",
    "events": "/events",
}


def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def fetch_and_save(endpoint_name, path):
    url = BASE_URL + path
    output_file = os.path.join(OUTPUT_DIR, f"{endpoint_name}.json")

    try:
        print(f"📥 正在获取 {endpoint_name} 数据: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()

        # 保存到文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        count = len(data) if isinstance(data, list) else 0
        print(f"✅ 成功保存 {count} 条 {endpoint_name} 数据到 {output_file}")

    except Exception as e:
        print(f"❌ 获取 {endpoint_name} 失败: {e}")
        # 可选：保存错误占位文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {"error": str(e), "timestamp": datetime.now().isoformat()},
                f,
                ensure_ascii=False,
                indent=2,
            )


def main():
    ensure_dir()
    print("🚀 开始抓取卡牌数据...\n")

    for name, path in ENDPOINTS.items():
        fetch_and_save(name, path)
        print()  # 空行分隔

    print("🎉 所有数据抓取完成！文件保存在 ./card_data/ 目录下。")


if __name__ == "__main__":
    main()
