"""
七圣召唤游戏中的枚举类型定义
"""
from enum import Enum


class ElementType(Enum):
    """
    元素类型枚举
    """
    ANEMO = "风"
    GEO = "岩"
    ELECTRO = "雷"
    DENDRO = "草"
    HYDRO = "水"
    PYRO = "火"
    CRYO = "冰"
    PHYSICAL = "物理"
    OMNI = "万能"  # 万能元素骰
    NONE = "无"
    CRYSTAL = "晶体"  # 任意元素（非物理、非万能）
    SAME = "同色"  # 与当前角色相同元素


class CardType(Enum):
    """
    卡牌类型枚举
    """
    CHARACTER = "角色牌"
    WEAPON = "武器"
    ARTIFACT = "圣遗物"
    TALENT = "天赋"
    SUPPORT = "支援牌"
    EVENT = "事件牌"


class DiceType(Enum):
    """
    骰子类型枚举（与元素类型基本一致，但包含万能元素）
    """
    ANEMO = "风"
    GEO = "岩"
    ELECTRO = "雷"
    DENDRO = "草"
    HYDRO = "水"
    PYRO = "火"
    CRYO = "冰"
    OMNI = "万能"  # 万能元素骰
    PHYSICAL = "物理"


class GamePhase(Enum):
    """
    游戏阶段枚举
    """
    ROLL_PHASE = "投骰阶段"
    ACTION_PHASE = "行动阶段"
    END_PHASE = "结束阶段"


class SkillType(Enum):
    """
    技能类型枚举
    """
    NORMAL_ATTACK = "普通攻击"
    ELEMENTAL_SKILL = "元素战技"
    ELEMENTAL_BURST = "元素爆发"


class CharacterStatus(Enum):
    """
    角色状态枚举
    """
    ALIVE = "存活"
    DEAD = "死亡"


class PlayerAction(Enum):
    """
    玩家操作类型枚举
    """
    PLAY_CARD = "打出卡牌"
    USE_SKILL = "使用技能"
    SWITCH_CHARACTER = "切换角色"
    PASS = "结束回合"
    REROLL_DICE = "重投骰子"


class DamageType(Enum):
    """
    伤害类型枚举
    """
    PHYSICAL = "物理伤害"
    ELEMENTAL = "元素伤害"
    HEAL = "治疗"


class ZoneType(Enum):
    """
    区域类型枚举
    """
    CHARACTER = "角色"
    WEAPON = "武器"
    ARTIFACT = "圣遗物"
    TALENT = "天赋"
    SUPPORT = "支援"
    SUMMON = "召唤物"
    TEAM = "队伍"