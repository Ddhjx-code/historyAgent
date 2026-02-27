"""
shot-list-skill 核心模块
分层渐进式历史分镜系统

模块结构：
- script_parser: 口播稿解析器
- beat_breakdown: 节拍拆解器
- beat_board_generator: Beat Board生成器（九宫格）
- sequence_board_generator: Sequence Board生成器（四宫格）
- prompt_integrator: Prompt集成器
- prompt_optimizer: Prompt优化器
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class EmotionType(Enum):
    """情绪类型"""
    SOLEMN = "solemn"  # 庄重
    TENSE = "tense"  # 紧张
    HOPEFUL = "hopeful"  # 充满希望
    SOMBER = "somber"  # 忧郁
    DRAMATIC = "dramatic"  # 戏剧性
    NEUTRAL = "neutral"  # 中性
    ANGRY = "angry"  # 愤怒
    PEACEFUL = "peaceful"  # 宁静


class BeatIntensity(Enum):
    """节拍强度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnchorType(Enum):
    """锚点类型"""
    WORLDVIEW_ESTABLISH = "worldview_establish"  # 世界观/基调建立
    PROTAGONIST_STATUS = "protagonist_status"  # 主角现状与目标/缺口
    INCITING_EVENT = "inciting_event"  # 诱因事件
    FIRST_TURNING_POINT = "first_turning_point"  # 第一次转折
    MIDPOINT_UPGRADE = "midpoint_upgrade"  # 中点升级/认知反转
    CRISIS_LOWPOINT = "crisis_lowpoint"  # 危机/低谷
    CLIMAX_ASSEMBLY = "climax_assembly"  # 高潮前集结
    CLIMAX_CONFRONTATION = "climax_confrontation"  # 高潮对抗/结果
    RESOLUTION_AFTERMATH = "resolution_aftermath"  # 结局/余韵


class ShotType(Enum):
    """镜头类型"""
    TITLE_CARD = "title_card"  # 标题卡
    HISTORICAL_SCENE = "historical_scene"  # 历史场景
    TRANSITION = "transition"  # 转场
    MAP = "map"  # 地图/信息图


class VideoTool(Enum):
    """视频工具"""
    SEEDANCE = "seedance"
    FFMPEG = "ffmpeg"


@dataclass
class StoryBeat:
    """节拍 - 最小叙事单元"""
    id: str
    description: str
    audience_gains: str  # 观众获得的信息/情绪/悬念
    intensity: BeatIntensity
    is_anchor: bool = False
    anchor_type: Optional[AnchorType] = None
    emotion: Optional[EmotionType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """事件"""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    beats: List[StoryBeat] = field(default_factory=list)


@dataclass
class ParsedSection:
    """解析后的章节"""
    type: str  # opening, transition, event, ending
    content: str
    title: Optional[str] = None
    emotion: Optional[EmotionType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedScript:
    """解析后的口播稿"""
    sections: List[ParsedSection]
    events: List[Event]
    global_emotion: Optional[EmotionType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StylePreset:
    """风格预设"""
    visual_style: str  # 视觉风格
    color_grading: str  # 色彩调色
    lighting_type: Optional[str] = None  # 光照类型
    mood: Optional[str] = None  # 情绪氛围


@dataclass
class Character:
    """人物特征"""
    character_id: str
    name: str
    description: str
    visual_features: Dict[str, str] = field(default_factory=dict)
    clothing: Dict[str, str] = field(default_factory=dict)
    pose: Dict[str, str] = field(default_factory=dict)
    era: Optional[str] = None


@dataclass
class BeatBoardGridCell:
    """Beat Board格子"""
    position: int  # 0-8
    beat_id: str
    prompt: str
    image_path: Optional[str] = None
    is_reference_for: List[str] = field(default_factory=list)


@dataclass
class BeatBoard:
    """Beat Board（九宫格）"""
    event_id: str
    grid_size: str = "3x3"
    style_preset: StylePreset = field(default_factory=lambda: StylePreset(
        visual_style="历史纪录片风格",
        color_grading="低饱和棕黄暖色调",
        lighting_type="dramatic"
    ))
    characters: Dict[str, Character] = field(default_factory=dict)
    grid: List[BeatBoardGridCell] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SequenceShot:
    """Sequence镜头"""
    position: int
    type: str  # 起/承/转/合
    prompt: str
    reference_image: Optional[str] = None
    continuity_check: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SequenceGroup:
    """Sequence Board组（四宫格/可变格）"""
    group_id: str
    anchor_beat_id: str
    reference_beat_image: Optional[str] = None
    structure: str = "起—承—转—合"
    grid_size: int = 4
    inheritance: Dict[str, str] = field(default_factory=dict)
    shots: List[SequenceShot] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityIssue:
    """连贯性问题"""
    shot_id: str
    issue_type: str  # screen_direction, action_continuity, axis_management, jump_cut
    description: str
    severity: str  # low, medium, high


@dataclass
class ContinuityReport:
    """连贯性检查报告"""
    group_id: str
    issues: List[ContinuityIssue] = field(default_factory=list)
    status: str = "passed"  # passed, warning, failed


@dataclass
class PromptScore:
    """提示词评分"""
    clarity: float  # 清晰度（0-10）
    detail_richness: float  # 细节丰富度（0-10）
    reusability: float  # 复用性（0-10）
    overall: float  # 总分（0-10）


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: str  # lighting, character, composition, emotion
    description: str
    priority: str  # low, medium, high


@dataclass
class OptimizationResult:
    """优化结果"""
    original_prompt: str
    optimized_prompt: str
    consistency_check: Dict[str, Any] = field(default_factory=dict)
    score: PromptScore = field(default_factory=lambda: PromptScore(0, 0, 0, 0))
    suggestions: List[OptimizationSuggestion] = field(default_factory=list)


@dataclass
class HistoricalFeature:
    """历史特征"""
    id: str
    name: str
    description: str
    era: Optional[str] = None
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HistoricalLocation:
    """历史地点"""
    location_id: str
    name: str
    description: str
    era: str
    atmosphere: str
    lighting: str
    background: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# 导出所有类
__all__ = [
    'EmotionType',
    'BeatIntensity',
    'AnchorType',
    'ShotType',
    'VideoTool',
    'StoryBeat',
    'Event',
    'ParsedSection',
    'ParsedScript',
    'StylePreset',
    'Character',
    'BeatBoardGridCell',
    'BeatBoard',
    'SequenceShot',
    'SequenceGroup',
    'ContinuityIssue',
    'ContinuityReport',
    'PromptScore',
    'OptimizationSuggestion',
    'OptimizationResult',
    'HistoricalFeature',
    'HistoricalLocation',
]