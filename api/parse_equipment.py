# api/parse_equipments.py
from bs4 import BeautifulSoup
import re
from .utis import _parse_costs

def clean_description(desc_html: str) -> str:
    # 替换常见图标
    desc_html = re.sub(r"卡牌UI-图标-单手剑\.png", "[单手剑]", desc_html)
    desc_html = re.sub(r"卡牌UI-图标-武器\.png", "[武器]", desc_html)
    desc_html = re.sub(r"卡牌UI-元素-冰\.png", "[冰]", desc_html)
    soup = BeautifulSoup(desc_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)


def parse_equipments(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tab = soup.select_one("div.resp-tab-content:nth-child(2)")
    if not tab:
        return []
    return _parse_cards(tab)


def _parse_cards(container):
    cards = container.select(".kapai-data")
    results = []
    for card in cards:
        name_tag = card.select_one(".data-topbox a")
        name = name_tag.get_text(strip=True) if name_tag else "未知装备"

        info_divs = card.select(".data-topbox .flex-col > div")
        card_type = info_divs[0].get_text(strip=True) if len(info_divs) > 0 else ""
        category = info_divs[1].get_text(strip=True) if len(info_divs) > 1 else ""
        detail = info_divs[2].get_text(strip=True) if len(info_divs) > 2 else ""

        skills = []
        for skill in card.select(".jiNeng"):
            title_elem = skill.select_one(".jiNeng-title")
            skill_name = (
                title_elem.get_text(strip=True).rstrip("：")
                if title_elem
                else "技能说明"
            )
            desc_divs = skill.select(".flex-col > div")
            desc = clean_description(str(desc_divs[1])) if len(desc_divs) > 1 else ""

            costs = _parse_costs(skill)
            skills.append({"name": skill_name, "description": desc, "cost": costs})

        results.append(
            {
                "name": name,
                "type": card_type,  # "装备牌"
                "category": category,  # "行动牌"
                "detail_type": detail,  # "武器 单手剑"
                "skills": skills,
            }
        )
    return results



