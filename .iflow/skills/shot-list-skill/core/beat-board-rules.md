---
name: beat-board-rules
description: Beat Board生成规则 - 指导大模型如何生成九宫格视觉锚点
---

# Beat Board生成规则

本文档定义大模型生成Beat Board（九宫格）时应遵循的规则。

## Beat Board目的

Beat Board（九宫格总览板）用于：
1. **确立视觉锚点**：为后续Sequence Board提供视觉参考
2. **确保风格统一**：统一人物、场景、光色基调
3. **叙事总览清晰**：用9张关键帧覆盖叙事曲线的关键拐点

## 九宫格布局

```
┌─────────┬─────────┬─────────┐
│   0     │   1     │   2     │
│ (0,0)   │ (0,1)   │ (0,2)   │
├─────────┼─────────┼─────────┤
│   3     │   4     │   5     │
│ (1,0)   │ (1,1)   │ (1,2)   │
├─────────┼─────────┼─────────┤
│   6     │   7     │   8     │
│ (2,0)   │ (2,1)   │ (2,2)   │
└─────────┴─────────┴─────────┘
```

## 风格预设规则

### 基础风格

```yaml
visual_style: "历史纪录片风格"
```

### 时代特征映射

| 时代 | 服饰 | 建筑 | 色调 | 氛围 |
|------|------|------|------|------|
| 古罗马 | 托加长袍、橄榄冠 | 大理石柱、马赛克 | 暖黄白金 | 威严庄重 |
| 台湾民国 | 中山装、旗袍 | 台北老街 | 棕暖黄 | 压抑悲凉 |
| 唐代 | 襦裙、圆领袍 | 斗拱、飞檐 | 绚丽多彩 | 神圣庄严 |
| 智利现代 | 现代服装 | 现代建筑 | 蓝白暖橙 | 紧张震撼 |

### 光照类型

| 类型 | 描述 | 适用场景 |
|------|------|---------|
| dramatic | 戏剧性光影，强烈明暗对比 | 冲突、高潮 |
| soft | 柔光，漫射光照明 | 温馨、平和 |
| golden_hour | 黄金时段的柔光 | 怀旧、希望 |
| hard | 硬光，轮廓分明 | 悲剧、冲突 |

## 人物识别规则

### 林江迈（1947年台湾）

```yaml
character_id: "lin_jiangmai_1947"
name: "林江迈"
description: "40岁台湾寡妇，烟纸摊贩"
visual_features:
  age: "40_years_old"
  gender: "female"
  face_shape: "weathered_face"
  expression: "exhausted_worried"
clothing:
  primary: "patched_cotton_clothing_1947_taiwan"
  description: "打补丁的粗布衣裳，民国时期台湾平民风格"
  color: "gray_brown"
  condition: "worn_tattered"
pose:
  default: "squatting_vendor_posture"
  alternative: "crouching_defensive"
era: "republic_of_china_1947"
```

### 哈德良皇帝（古罗马）

```yaml
character_id: "hadrian_138"
name: "哈德良皇帝"
description: "古罗马帝国皇帝（117-138年）"
visual_features:
  age: "60_years_old"
  gender: "male"
  face_shape: "roman_imperial_profile"
  expression: "wise_authoritative"
clothing:
  primary: "purple_border_toga"
  description: "紫色镶边托加长袍，罗马皇帝专用"
  color: "purple_white_gold"
  accessories: ["olive_wreath_crown", "imperial_ring"]
pose:
  default: "seated_on_throne"
  alternative: "standing_ancient_pose"
era: "ancient_rome"
```

### 玄奘高僧（唐代）

```yaml
character_id: "xuanzang_645"
name: "玄奘高僧"
description: "唐代高僧，西行取经"
visual_features:
  age: "45_years_old"
  gender: "male"
  face_shape: "serene_monk"
  expression: "peaceful_determined"
clothing:
  primary: "monk_robe_tang"
  description: "唐代僧袍，朴素庄严"
  color: "saffron_brown"
  accessories: ["buddhist_sutra", "monk_staff"]
pose:
  default: "standing_with_sutra"
  alternative: "walking_pilgrimage"
era: "tang_dynasty"
```

## 提示词生成规则

### 基础结构

```
[风格]，[景别]，[环境]。
[主体描述]，[动作/状态]。
[光线描述]，[光影效果]。
[色调描述]，[氛围]。
[画面参数]。
```

### 景别选择

| 景别 | 使用场景 | 关键词 |
|------|---------|--------|
| 特写 | 情绪细节、关键瞬间 | 眼睛、脸、表情、手、特写 |
| 近景 | 人物互动、对话 | 人、身、头、近景 |
| 中景 | 常规叙述、动作 | - |
| 全景 | 环境全貌、人物关系 | 全景、全身、整个 |
| 极远景 | 世界观建立 | 极远景、全景 |

### 光线描述

| 光线类型 | 描述 | 适用场景 |
|---------|------|---------|
| 侧光 | 侧光从左侧射入，形成强烈明暗对比 | 冲突、戏剧性 |
| 顶光 | 顶光，眼窝下刻出深影 | 悲剧、压迫 |
| 柔光 | 柔和光线，漫射光照明 | 温馨、平和 |
| 夕阳光 | 黄金时段的柔光，夕阳光线打在主体上 | 怀旧、温暖 |

## 一致性检查

### 人物一致性

| 人物 | 格子 | 外观一致性 | 服装一致性 | 姿态一致性 |
|------|------|-----------|-----------|-----------|
| 林江迈 | 0,1,2 | ✅ 通过 | ✅ 通过 | ✅ 通过 |

### 场景一致性

| 场景 | 格子 | 建筑风格 | 光色逻辑 | 氛围 |
|------|------|---------|---------|------|
| 台北街头 | 0,1,2 | ✅ 统一 | ✅ 统一 | ✅ 统一 |

### 风格一致性

- 视觉风格：✅ 全部为"历史纪录片风格"
- 色彩调色：✅ 全部为"{color_grading}"
- 光照类型：✅ 全部为"{lighting_type}"

## 验收标准

生成Beat Board后必须检查：

- [ ] **清晰**：九张是否能讲清故事主线与关键拐点？
- [ ] **清晰**：每格的镜头目的是否明确（信息/情绪/悬念/转折）？
- [ ] **覆盖**：是否缺关键转折/高潮/结果？
- [ ] **覆盖**：是否存在"重复信息点"的锚点（冗余）？
- [ ] **一致性**：人物外观/服装状态是否统一？
- [ ] **一致性**：场景固定物是否一致？
- [ ] **一致性**：光色逻辑是否一致？
- [ ] **一致性**：视觉风格是否统一？
- [ ] **可用性**：每格是否足够清晰，能作为Sequence Board的参考图片？
- [ ] **可用性**：是否存在"画面说不清/无法复述叙事目的"的格子？

## 输出示例

### 格子 0

**节拍ID**: `beat_001`
**锚点类型**: `主角现状与目标/缺口`

**提示词**:
```
历史纪录片风格。中景，1947年台北市太平町的黄昏街头。
一位40岁的寡妇林江迈，身穿打补丁的粗布衣裳，蹲在路边摆起烟纸摊。
她的脸上写满疲惫，眼神中有对明天的担忧。街道上行人匆匆，
远处是模糊的日本殖民时期建筑。柔和的夕阳光线打在她身上，
投下长长的影子。低饱和度的棕黄暖色调，传递出那个时代的压抑与艰辛。
电影质感，16:9横屏。
```

**画面要素**:
- 景别：中景
- 主体：林江迈（40岁寡妇，蹲姿）
- 环境：台北老街，黄昏
- 光线：夕阳柔光
- 色调：棕黄暖色，低饱和

## 注意事项

1. **叙事描述优先**：使用完整的叙事段落，而非关键词堆叠
2. **场景化思维**：回答"谁在哪里、做什么、环境如何、光线如何"
3. **摄影术语融入**：将景别、角度、镜头效果自然融入描述
4. **情绪具体化**：用光影、色彩、构图传达情绪，而非直接说"戏剧性"