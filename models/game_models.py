"""
七圣召唤游戏核心数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.enums import ElementType, CardType, GamePhase, SkillType, CharacterStatus, DamageType
from typing import Any


@dataclass
class Card:
    """
    基础卡牌类
    """
    id: str
    name: str
    card_type: CardType
    cost: List[ElementType]  # 消耗的元素类型列表
    description: str = ""
    character_subtype: Optional[str] = None  # 如果是角色牌的装备牌，关联对应的角色名称


@dataclass
class CharacterCard(Card):
    """
    角色卡牌类，继承自 Card
    """
    health: int = 10  # 生命值
    max_health: int = 10
    energy: int = 0  # 元素能量
    max_energy: int = 3  # 最大元素能量
    skills: List[Dict[str, Any]] = field(default_factory=list)  # 技能列表
    element_type: ElementType = ElementType.NONE  # 角色元素类型
    weapon_type: str = ""  # 武器类型
    status: CharacterStatus = CharacterStatus.ALIVE  # 当前状态
    
    def __post_init__(self):
        """初始化后设置card_type为角色卡"""
        self.card_type = CardType.CHARACTER


@dataclass
class PlayerState:
    """
    玩家状态类
    """
    player_id: str
    characters: List[CharacterCard] = field(default_factory=list)  # 角色列表
    active_character_index: int = 0  # 当前出战角色索引
    hand_cards: List[Card] = field(default_factory=list)  # 手牌
    dice: List[ElementType] = field(default_factory=list)  # 当前骰子
    deck: List[Card] = field(default_factory=list)  # 牌库
    supports: List[Dict[str, Any]] = field(default_factory=list)  # 支援牌
    summons: List[Dict[str, Any]] = field(default_factory=list)  # 召唤物
    team_status: List[Dict[str, Any]] = field(default_factory=list)  # 队伍状态
    max_hand_size: int = 10  # 最大手牌数量
    max_support_size: int = 4  # 最大支援牌数量
    max_summon_size: int = 4  # 最大召唤物数量
    round_passed: bool = False  # 本回合是否已行动


@dataclass
class GameState:
    """
    游戏状态类
    """
    players: List[PlayerState] = field(default_factory=list)
    current_player_index: int = 0  # 当前行动玩家索引
    round_number: int = 1  # 回合数
    phase: GamePhase = GamePhase.ROLL_PHASE  # 当前阶段
    round_actions: int = 0  # 当前回合行动次数
    max_round_actions: int = 1  # 最大回合行动次数
    game_log: List[str] = field(default_factory=list)  # 游戏日志
    is_game_over: bool = False  # 游戏是否结束
    winner: Optional[str] = None  # 获胜玩家ID


@dataclass
class Skill:
    """
    技能类
    """
    skill_type: SkillType
    name: str
    cost: List[ElementType]
    damage: int = 0
    heal: int = 0
    damage_type: Optional[DamageType] = None
    element_application: Optional[ElementType] = None  # 附着元素
    description: str = ""