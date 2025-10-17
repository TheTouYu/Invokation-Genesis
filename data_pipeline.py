"""
统一的卡牌数据流水线
实现从网页抓取到数据库存储的完整流程
"""
import json
import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import uuid

from api.utis import _parse_costs
from api.characters_parse import clean_description as clean_char_description
from api.parse_equipment import clean_description as clean_equip_description
from api.parse_events import clean_description as clean_event_description
from api.parse_supports import clean_description as clean_support_description

# 配置
TARGET_JS_URL = "https://wiki.biligame.com/ys/%E5%8D%A1%E7%89%8C%E4%B8%80%E8%A7%88"
OUTPUT_DIR = "card_data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

class CardDataPipeline:
    """卡牌数据流水线：网页抓取 → 标准化JSON文件 → 数据库存储"""
    
    def __init__(self):
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
    
    def fetch_html(self) -> str:
        """从网页抓取HTML内容"""
        try:
            print(f"🌐 正在从 {TARGET_JS_URL} 抓取数据...")
            response = requests.get(TARGET_JS_URL, headers=HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = "utf-8"
            print("✅ 网页抓取成功")
            return response.text
        except Exception as e:
            logging.error(f"网页抓取失败: {e}")
            raise
    
    def parse_characters(self, html: str) -> List[Dict[str, Any]]:
        """解析角色牌数据（第1个Tab）"""
        print("🔍 正在解析角色牌数据...")
        soup = BeautifulSoup(html, "lxml")
        tab_container = soup.select_one("div.resp-tab-content:nth-child(1)")  # 第一个 Tab：角色牌
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
                        description = clean_char_description(raw_desc)

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
                        "id": str(uuid.uuid4()),  # 添加唯一ID
                        "name": name,
                        "name_url": name_url,
                        "card_type": card_type,
                        "type": card_type,  # 保持兼容性
                        "region": region,
                        "weapon": weapon,
                        "skills": skills,
                        "element_type": self._extract_element_from_skills(skills),  # 提取元素类型
                        "country": self._extract_country_from_region(region),  # 提取国家
                        "weapon_type": self._extract_weapon_type_from_region(region),  # 提取武器类型
                    }
                )
            except Exception as e:
                logging.exception(f"解析角色卡失败: {e}")
                continue  # 跳过错误卡片，继续处理

        print(f"✅ 解析完成，共 {len(characters)} 张角色牌")
        return characters

    def parse_equipments(self, html: str) -> List[Dict[str, Any]]:
        """解析装备牌数据（第2个Tab）"""
        print("🔍 正在解析装备牌数据...")
        soup = BeautifulSoup(html, "html.parser")
        tab = soup.select_one("div.resp-tab-content:nth-child(2)")
        if not tab:
            return []
        
        cards = tab.select(".kapai-data")
        results = []
        
        for card in cards:
            try:
                name_tag = card.select_one(".data-topbox a")
                name = name_tag.get_text(strip=True) if name_tag else "未知装备"

                # 修复点：安全获取并清理 src
                img_tag = card.select_one(".kapai-box img")
                name_url = img_tag.get("alt").strip() if img_tag and img_tag.get("src") else ""

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
                    desc = clean_equip_description(str(desc_divs[1])) if len(desc_divs) > 1 else ""

                    costs = _parse_costs(skill)
                    skills.append({"name": skill_name, "description": desc, "cost": costs})

                results.append(
                    {
                        "id": str(uuid.uuid4()),  # 添加唯一ID
                        "name": name,
                        "name_url": name_url,
                        "card_type": card_type,
                        "type": card_type,  # 保持兼容性
                        "category": category,
                        "detail_type": detail,
                        "skills": skills,
                        "element_type": self._extract_element_from_skills(skills),  # 提取元素类型
                    }
                )
            except Exception as e:
                logging.exception(f"解析装备卡失败: {e}")
                continue
        
        print(f"✅ 解析完成，共 {len(results)} 张装备牌")
        return results

    def parse_supports(self, html: str) -> List[Dict[str, Any]]:
        """解析支援牌数据（第3个Tab）"""
        print("🔍 正在解析支援牌数据...")
        soup = BeautifulSoup(html, "html.parser")
        tab = soup.select_one("div.resp-tab-content:nth-child(3)")
        if not tab:
            return []
        
        cards = tab.select(".kapai-data")
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
                        description = clean_support_description(str(desc_divs[1]))

                    costs = _parse_costs(skill_elem)
                    skills.append(
                        {"name": skill_name, "description": description, "cost": costs}
                    )

                results.append(
                    {
                        "id": str(uuid.uuid4()),  # 添加唯一ID
                        "name": name,
                        "name_url": name_url,
                        "card_type": card_type,
                        "type": card_type,  # 保持兼容性
                        "category": category,
                        "subtype": subtype,
                        "skills": skills,
                        "element_type": self._extract_element_from_skills(skills),  # 提取元素类型
                    }
                )
            except Exception as e:
                logging.exception(f"解析支援卡失败: {e}")
                continue

        print(f"✅ 解析完成，共 {len(results)} 张支援牌")
        return results

    def parse_events(self, html: str) -> List[Dict[str, Any]]:
        """解析事件牌数据（第4个Tab）"""
        print("🔍 正在解析事件牌数据...")
        soup = BeautifulSoup(html, "html.parser")
        tab = soup.select_one("div.resp-tab-content:nth-child(4)")
        if not tab:
            return []
        
        cards = tab.select(".kapai-data")
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
                )

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
                    description = (
                        clean_event_description(str(desc_divs[1])) if len(desc_divs) > 1 else ""
                    )

                    costs = _parse_costs(skill_elem)
                    skills.append(
                        {"name": skill_name, "description": description, "cost": costs}
                    )

                results.append(
                    {
                        "id": str(uuid.uuid4()),  # 添加唯一ID
                        "name": name,
                        "name_url": name_url,
                        "card_type": card_type,
                        "type": card_type,  # 保持兼容性
                        "category": category,
                        "subtype": subtype,
                        "skills": skills,
                        "element_type": self._extract_element_from_skills(skills),  # 提取元素类型
                    }
                )
            except Exception as e:
                logging.exception(f"解析事件卡失败: {e}")
                continue

        print(f"✅ 解析完成，共 {len(results)} 张事件牌")
        return results

    def _extract_element_from_skills(self, skills: List[Dict[str, Any]]) -> str:
        """从技能费用中提取元素信息"""
        if not skills:
            return ""
        
        first_skill = skills[0] if skills else {}
        if "cost" in first_skill:
            costs = first_skill["cost"]
            elements = ["火", "水", "雷", "草", "风", "岩", "冰", "物理", "荒性", "芒性"]
            for cost in costs:
                if isinstance(cost, dict) and "type" in cost:
                    cost_type = cost["type"]
                    if cost_type in elements:
                        return cost_type
                    if "始基力" in cost_type:
                        if "荒性" in cost_type:
                            return "荒性"
                        elif "芒性" in cost_type:
                            return "芒性"
                elif isinstance(cost, str) and cost in elements:
                    return cost
        
        return ""

    def _extract_country_from_region(self, region_str: str) -> str:
        """从region字段提取国家信息"""
        if not region_str:
            return ""
        
        countries = [
            "蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"
        ]
        
        for country in countries:
            if country in region_str:
                return country
        return ""

    def _extract_weapon_type_from_region(self, region_str: str) -> str:
        """从region字段提取武器类型"""
        if not region_str:
            return ""
        
        weapon_types = ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
        
        for weapon_type in weapon_types:
            if weapon_type in region_str:
                return weapon_type
        return ""

    def save_to_file(self, data: List[Dict[str, Any]], filename: str):
        """保存数据到JSON文件"""
        output_file = os.path.join(OUTPUT_DIR, filename)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到 {output_file}，共 {len(data)} 条记录")
    
    def run_pipeline(self):
        """执行完整的数据流水线"""
        print("🔄 开始执行卡牌数据流水线...")
        print("📊 阶段1: 网页抓取")
        
        # 阶段1: 网页抓取
        html_content = self.fetch_html()
        
        print("📊 阶段2: 数据解析")
        
        # 阶段2: 解析各种卡牌数据
        characters = self.parse_characters(html_content)
        equipments = self.parse_equipments(html_content)
        supports = self.parse_supports(html_content)
        events = self.parse_events(html_content)
        
        print("📊 阶段3: 保存到本地文件")
        
        # 阶段3: 保存到本地JSON文件
        self.save_to_file(characters, "characters.json")
        self.save_to_file(equipments, "equipments.json")
        self.save_to_file(supports, "supports.json")
        self.save_to_file(events, "events.json")
        
        print("🎉 数据流水线执行完成！")
        print(f"📋 统计: {len(characters)} 张角色牌, {len(equipments)} 张装备牌, {len(supports)} 张支援牌, {len(events)} 张事件牌")


if __name__ == "__main__":
    pipeline = CardDataPipeline()
    pipeline.run_pipeline()