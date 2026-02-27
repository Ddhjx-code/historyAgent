---
name: data-structures
description: shot-list-skill 数据结构参考 - 用于大模型理解输出格式
---

# 数据结构参考

本文档定义shot-list-skill使用的数据结构，供大模型生成输出时参考。

## 枚举类型

### EmotionType（情绪类型）
```yaml
SOLEMN: "solemn"      # 庄重
TENSE: "tense"        # 紧张
HOPEFUL: "hopeful"    # 充满希望
SOMBER: "somber"      # 忧郁
DRAMATIC: "dramatic"  # 戏剧性
NEUTRAL: "neutral"    # 中性
ANGRY: "angry"        # 愤怒
PEACEFUL: "peaceful"  # 宁静
```

### BeatIntensity（节拍强度）
```yaml
LOW: "low"
MEDIUM: "medium"
HIGH: "high"
```

### AnchorType（锚点类型）
```yaml
WORLDVIEW_ESTABLISH: "worldview_establish"      # 世界观/基调建立
PROTAGONIST_STATUS: "protagonist_status"        # 主角现状与目标/缺口
INCITING_EVENT: "inciting_event"                # 诱因事件
FIRST_TURNING_POINT: "first_turning_point"      # 第一次转折
MIDPOINT_UPGRADE: "midpoint_upgrade"            # 中点升级/认知反转
CRISIS_LOWPOINT: "crisis_lowpoint"              # 危机/低谷
CLIMAX_ASSEMBLY: "climax_assembly"              # 高潮前集结
CLIMAX_CONFRONTATION: "climax_confrontation"    # 高潮对抗/结果
RESOLUTION_AFTERMATH: "resolution_aftermath"    # 结局/余韵
```

### ShotType（镜头类型）
```yaml
TITLE_CARD: "title_card"
HISTORICAL_SCENE: "historical_scene"
TRANSITION: "transition"
MAP: "map"
```

### VideoTool（视频工具）
```yaml
SEEDANCE: "seedance"
FFMPEG: "ffmpeg"
```

## 数据结构

### StoryBeat（节拍）
```yaml
id: str                      # 节拍ID（如 beat_001）
description: str              # 节拍描述
audience_gains: str           # 观众收获（信息/情绪/悬念）
intensity: BeatIntensity      # 强度（low/medium/high）
is_anchor: bool               # 是否为锚点
anchor_type: AnchorType       # 锚点类型（可选）
emotion: EmotionType          # 情绪类型（可选）
metadata: dict                # 元数据
```

### Event（事件）
```yaml
id: str                      # 事件ID（如 event_001）
title: str                   # 事件标题
content: str                 # 事件内容
metadata: dict               # 元数据（时间、地点、时代等）
beats: list[StoryBeat]       # 节拍列表
```

### ParsedSection（解析后的章节）
```yaml
type: str                    # 类型（opening/transition/event/ending）
content: str                 # 内容
title: str                   # 标题（可选）
emotion: EmotionType         # 情绪（可选）
metadata: dict               # 元数据
```

### ParsedScript（解析后的口播稿）
```yaml
sections: list[ParsedSection]  # 章节列表
events: list[Event]             # 事件列表
global_emotion: EmotionType     # 全局情绪（可选）
metadata: dict                   # 元数据
```

### StylePreset（风格预设）
```yaml
visual_style: str          # 视觉风格（如"历史纪录片风格"）
color_grading: str         # 色彩调色（如"低饱和棕黄暖色调"）
lighting_type: str         # 光照类型（可选）
mood: str                  # 情绪氛围（可选）
```

### Character（人物特征）
```yaml
character_id: str          # 人物ID
name: str                  # 姓名
description: str           # 描述
visual_features: dict      # 视觉特征（年龄、性别、脸型、表情等）
clothing: dict             # 服装（类型、描述、颜色、状态）
pose: dict                 # 姿态（默认、备选）
era: str                   # 时代（可选）
```

### BeatBoardGridCell（Beat Board格子）
```yaml
position: int              # 位置（0-8）
beat_id: str               # 节拍ID
prompt: str                # 提示词
image_path: str            # 图像路径（可选）
is_reference_for: list[str] # 作为参考图片的Sequence Board组ID列表
```

### BeatBoard（Beat Board）
```yaml
event_id: str              # 事件ID
grid_size: str             # 网格大小（如"3x3"）
style_preset: StylePreset # 风格预设
characters: dict           # 人物字典
grid: list[BeatBoardGridCell]  # 九宫格列表
metadata: dict             # 元数据
```

### SequenceShot（Sequence镜头）
```yaml
position: int              # 位置
type: str                  # 类型（起/承/转/合）
prompt: str                # 提示词
reference_image: str       # 参考图片（可选）
continuity_check: dict     # 连贯性检查
metadata: dict             # 元数据
```

### SequenceGroup（Sequence Board组）
```yaml
group_id: str              # 组ID
anchor_beat_id: str        # 锚点节拍ID
reference_beat_image: str  # 参考图片（可选）
structure: str             # 结构（如"起—承—转—合"）
grid_size: int             # 格数
inheritance: dict          # 继承性
shots: list[SequenceShot]  # 镜头列表
metadata: dict             # 元数据
```

### ContinuityIssue（连贯性问题）
```yaml
shot_id: str               # 镜头ID
issue_type: str            # 问题类型
description: str           # 描述
severity: str              # 严重程度（low/medium/high）
```

### ContinuityReport（连贯性检查报告）
```yaml
group_id: str              # 组ID
issues: list[ContinuityIssue]  # 问题列表
status: str                # 状态（passed/warning/failed）
```

## 使用说明

这些数据结构用于：

1. **节拍拆解表**：使用 StoryBeat、Event
2. **Beat Board**：使用 BeatBoard、BeatBoardGridCell、Character、StylePreset
3. **Sequence Board**：使用 SequenceGroup、SequenceShot
4. **连贯性检查**：使用 ContinuityReport、ContinuityIssue

大模型在生成输出时，应确保数据符合这些结构的定义。