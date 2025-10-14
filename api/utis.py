def _parse_costs(skill_elem):
    costs = []
    cost_box = skill_elem.select_one(".cost-box")
    if not cost_box:
        return costs

    for cost_elem in cost_box.select(".cost"):
        classes = cost_elem.get("class", [])
        val_text = cost_elem.get_text(strip=True)
        value = int(val_text) if val_text.isdigit() else 0

        if "wuse" in classes:
            costs.append({"type": "无色", "value": value})
        elif "chongneng" in classes:
            costs.append({"type": "充能", "value": value})
        elif "xiangtong" in classes:
            costs.append({"type": "象形", "value": value})
        elif "bing" in classes:
            costs.append({"type": "冰", "value": value})
        elif "yan" in classes:
            costs.append({"type": "岩", "value": value})
        elif "shui" in classes:
            costs.append({"type": "水", "value": value})
        elif "huo" in classes:
            costs.append({"type": "火", "value": value})
        elif "feng" in classes:
            costs.append({"type": "风", "value": value})
        elif "lei" in classes:
            costs.append({"type": "雷", "value": value})
        elif "cao" in classes:
            costs.append({"type": "草", "value": value})

        else:
            costs.append({"type": "其他", "value": value})

    return costs
