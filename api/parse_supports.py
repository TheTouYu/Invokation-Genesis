# api/parse_supports.py
from bs4 import BeautifulSoup
import re

from .utis import _parse_costs


def clean_description(desc_html: str) -> str:
    # 可按需扩展图标替换，当前无特殊图标
    soup = BeautifulSoup(desc_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)


def parse_supports(html: str):
    """
    解析支援牌（第3个 Tab）
    """
    soup = BeautifulSoup(html, "html.parser")
    tab = soup.select_one("div.resp-tab-content:nth-child(3)")
    if not tab:
        return []
    return _parse_cards(tab)


def _parse_cards(container):
    cards = container.select(".kapai-data")
    results = []

    for card in cards:
        try:
            name_tag = card.select_one(".data-topbox a")
            name = name_tag.get_text(strip=True) if name_tag else "未知支援"

            info_divs = card.select(".data-topbox .flex-col > div")
            card_type = info_divs[0].get_text(strip=True) if len(info_divs) > 0 else ""
            category = info_divs[1].get_text(strip=True) if len(info_divs) > 1 else ""
            subtype = info_divs[2].get_text(strip=True) if len(info_divs) > 2 else ""

            # 修复点：安全获取并清理 src
            img_tag = card.select_one(".kapai-box img")
            name_url = img_tag.get("alt") if img_tag and img_tag.get("src") else ""
            skills = []
            for skill_elem in card.select(".jiNeng"):
                title_elem = skill_elem.select_one(".jiNeng-title")
                skill_name = (
                    title_elem.get_text(strip=True).rstrip("：")
                    if title_elem
                    else "技能说明"
                )

                desc_divs = skill_elem.select(".flex-col > div")
                description = ""
                if len(desc_divs) > 1:
                    description = clean_description(str(desc_divs[1]))

                costs = _parse_costs(skill_elem)
                skills.append(
                    {"name": skill_name, "description": description, "cost": costs}
                )

            results.append(
                {
                    "name": name,
                    "name_url": name_url,
                    "type": card_type,  # "支援牌"
                    "category": category,  # "行动牌"
                    "subtype": subtype,  # "伙伴"
                    "skills": skills,
                }
            )
        except Exception as e:
            # 可选：记录日志（需导入 logging）
            continue

    return results
