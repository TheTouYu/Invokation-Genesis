"""
七圣召唤游戏核心数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.enums import ElementType, CardType, GamePhase, SkillType, CharacterStatus, DamageType, PlayerAction
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
    # 角色状态和效果相关
    element_attached: Optional[ElementType] = None  # 附着的元素
    weapon: Optional[Card] = None  # 装备的武器
    artifact: Optional[Card] = None  # 装备的圣遗物
    talent: Optional[Card] = None  # 装备的天赋
    character_statuses: List[Dict[str, Any]] = field(default_factory=list)  # 角色状态
    is_alive: bool = True  # 是否存活
    shield: int = 0  # 护盾值
    survive_at_hp: bool = False  # 免于被击倒机制
    
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
    # 新增属性
    has_used_elemental_tuning: bool = False  # 本回合是否已使用元素调和
    can_change_active_character: bool = True  # 是否可以切换角色
    dice_count_limit: int = 16  # 骰子数量上限
    # 游戏阶段状态
    has_reroll_option_used: bool = False  # 是否已使用重投选项
    has_card_replace_option_used: bool = False  # 是否已使用手牌替换选项
    # 特殊状态
    is_quick_action: bool = True  # 是否为快速行动
    plunge_attack_available: bool = False  # 下落攻击是否可用


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
    # 新增属性
    first_player_index: int = 0  # 先手玩家索引
    last_action_type: Optional[PlayerAction] = None  # 上一个行动类型
    quick_action_available: bool = True  # 是否可以继续快速行动
    action_queue: List[Dict[str, Any]] = field(default_factory=list)  # 行动队列
    # 元素反应相关
    damage_queue: List[Dict[str, Any]] = field(default_factory=list)  # 伤害队列
    # 特殊阶段状态
    has_players_drawn_initial_cards: bool = False  # 是否已抽取初始手牌
    can_replace_initial_cards: bool = True  # 是否可以替换初始手牌
    # 其他特殊机制
    dice_omni_count: int = 0  # 万能元素骰数量


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