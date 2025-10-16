import requests
from bs4 import BeautifulSoup
from .utis import _parse_costs
import re
import logging


# 配置
ROLE_TAB_SELECTOR = "div.resp-tab-content:nth-child(1)"  # 第一个 Tab：角色牌


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        raise


def clean_description(desc_html: str) -> str:
    # 替换冰元素图标为 [冰]
    desc_html = re.sub(r"卡牌UI-元素-冰\.png", "[冰]", desc_html)
    # 可扩展其他元素，如火、雷等（当前数据只有冰）
    soup = BeautifulSoup(desc_html, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    # 合并多余空格
    return re.sub(r"\s+", " ", text)


def parse_characters(html: str):
    soup = BeautifulSoup(html, "lxml")
    tab_container = soup.select_one(ROLE_TAB_SELECTOR)
    if not tab_container:
        raise ValueError("未找到角色牌 Tab 容器，请检查页面结构或选择器")

    cards = tab_container.select(".kapai-data")
    if not cards:
        logging.warning("未找到任何 .kapai-data 角色卡片")

    characters = []
    for card in cards:
        try:
            # 基础信息
            name_tag = card.select_one(".data-topbox a")
            name = name_tag.get_text(strip=True) if name_tag else "未知角色"

            info_divs = card.select(".data-topbox .flex-col > div")
            card_type = info_divs[0].get_text(strip=True) if len(info_divs) > 0 else ""
            region = info_divs[1].get_text(strip=True) if len(info_divs) > 1 else ""
            weapon = info_divs[2].get_text(strip=True) if len(info_divs) > 2 else ""

            # 修复点：安全获取并清理 src
            img_tag = card.select_one(".kapai-box img")
            name_url = img_tag.get("alt") if img_tag and img_tag.get("src") else ""
            # 技能列表
            skills = []
            for skill_box in card.select(".jiNeng"):
                title = skill_box.select_one(".jiNeng-title")
                skill_name = title.get_text(strip=True) if title else "未知技能"

                desc_divs = skill_box.select(".flex-col > div")
                skill_type = (
                    desc_divs[1].get_text(strip=True) if len(desc_divs) > 1 else ""
                )
                description = ""
                if len(desc_divs) > 2:
                    raw_desc = str(desc_divs[2])
                    description = clean_description(raw_desc)

                # 解析花费
                costs = _parse_costs(skill_box)
                skills.append(
                    {
                        "name": skill_name,
                        "type": skill_type,
                        "description": description,
                        "cost": costs,
                    }
                )

            characters.append(
                {
                    "name": name,
                    "name_url": name_url,
                    "type": card_type,
                    "region": region,
                    "weapon": weapon,
                    "skills": skills,
                }
            )
        except Exception as e:
            logging.exception(f"解析角色卡失败: {e}")
            continue  # 跳过错误卡片，继续处理

    return characters
