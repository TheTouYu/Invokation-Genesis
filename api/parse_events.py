# api/parse_events.py
from bs4 import BeautifulSoup
import re
from .utis import _parse_costs


def clean_description(desc_html: str) -> str:
    """
    清理技能描述，替换常见图标为文本标记
    """
    # 替换图标
    desc_html = re.sub(r"卡牌UI-图标-武器\.png", "[武器]", desc_html)
    desc_html = re.sub(r"卡牌UI-图标-圣遗物\.png", "[圣遗物]", desc_html)
    desc_html = re.sub(r"卡牌UI-cost-万能\.png", "[万能]", desc_html)
    # 可继续扩展其他图标

    soup = BeautifulSoup(desc_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)


def parse_events(html: str):
    """
    解析事件牌（第4个 Tab）
    """
    soup = BeautifulSoup(html, "html.parser")
    tab = soup.select_one("div.resp-tab-content:nth-child(4)")
    if not tab:
        return []
    return _parse_cards(tab)


def _parse_cards(container):
    cards = container.select(".kapai-data")
    results = []

    for card in cards:
        try:
            name_tag = card.select_one(".data-topbox a")
            name = name_tag.get_text(strip=True) if name_tag else "未知事件"

            info_divs = card.select(".data-topbox .flex-col > div")
            card_type = info_divs[0].get_text(strip=True) if len(info_divs) > 0 else ""
            category = info_divs[1].get_text(strip=True) if len(info_divs) > 1 else ""
            subtype = (
                info_divs[2].get_text(strip=True) if len(info_divs) > 2 else ""
            )  # 可能为空

            skills = []
            for skill_elem in card.select(".jiNeng"):
                title_elem = skill_elem.select_one(".jiNeng-title")
                skill_name = (
                    title_elem.get_text(strip=True).rstrip("：")
                    if title_elem
                    else "技能说明"
                )

                desc_divs = skill_elem.select(".flex-col > div")
                description = (
                    clean_description(str(desc_divs[1])) if len(desc_divs) > 1 else ""
                )

                costs = _parse_costs(skill_elem)
                skills.append(
                    {"name": skill_name, "description": description, "cost": costs}
                )

            results.append(
                {
                    "name": name,
                    "type": card_type,  # "事件牌"
                    "category": category,  # "行动牌"
                    "subtype": subtype,  # 可能为空字符串
                    "skills": skills,
                }
            )
        except Exception:
            # 可选：记录日志
            continue

    return results
