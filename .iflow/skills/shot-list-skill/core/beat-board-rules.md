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

### 特征库查询

在生成Beat Board之前，必须查询特征库获取准确的历史特征：

**查询步骤**：
1. 根据口播稿解析时代信息（`era`）
2. 识别人物身份（`identity`）
3. 识别地点类型（`location_type`）
4. 在对应的JSON文件中查询：
   - `historical_characters.json` - 人物特征
   - `historical_costumes.json` - 服饰特征
   - `historical_architecture.json` - 建筑特征
   - `historical_locations.json` - 地点特征
5. 提取`prompt_snippet`字段（≤50字）

**参考**：`libraries/README.md`

### 使用Prompt模板

使用`templates/prompt-templates.md`中的**模板1：Beat Board Prompt模板**

**模板结构**：
```
[风格预设]，[景别]，[时代背景] [地点描述]。
[主体描述]，[服饰特征]，[表情神态]，[动作姿态]。
[光线来源]，[光影效果]。
[色调描述]，[色彩情绪]，[氛围基调]。
[画面参数：光圈、ISO、质感等]。
```

### 景别选择

| 锚点类型 | 推荐景别 | 说明 |
|---------|---------|------|
| WORLDVIEW_ESTABLISH | 远景/全景 | 建立世界观和时代背景 |
| PROTAGONIST_STATUS | 中景 | 展示主角现状和状态 |
| INCITING_EVENT | 中近景 | 展示诱发事件的细节 |
| FIRST_TURNING_POINT | 近景 | 展示第一个转折的冲突 |
| MIDPOINT_UPGRADE | 中景 | 展示中点升级的互动 |
| CRISIS_LOWPOINT | 近景/特写 | 展示危机低谷的情绪 |
| CLIMAX_ASSEMBLY | 全景 | 展示高潮集结的全貌 |
| CLIMAX_CONFRONTATION | 近景/特写 | 展示高潮对抗的细节 |
| RESOLUTION_AFTERMATH | 全景 | 展示结局的氛围 |

### 光线描述

| 光线类型 | 描述 | 适用场景 |
|---------|------|---------|
| 侧光 | 侧光从左侧射入，形成强烈明暗对比 | 冲突、戏剧性 |
| 顶光 | 顶光，眼窝下刻出深影 | 悲剧、压迫 |
| 柔光 | 柔和光线，漫射光照明 | 温馨、平和 |
| 夕阳光 | 黄金时段的柔光，夕阳光线打在主体上 | 怀旧、温暖 |
| 逆光 | 光源从背后射入，形成剪影效果 | 神秘、庄严 |

### Prompt生成流程

**参考**：`core/prompt-generation-rules.md`

**流程**：
1. 确定风格预设（历史纪录片风格/电影感风格/纪实摄影风格）
2. 根据锚点类型选择景别
3. 融入特征库的`prompt_snippet`
4. 按照模板结构生成Prompt
5. 执行一致性检查
6. 执行Prompt优化

## 一致性检查

**参考**：`core/continuity-check-rules.md`

### 检查清单

**人物一致性**：
- [ ] 同一人物的年龄/性别/脸型一致
- [ ] 同一人物的服饰类型/颜色一致
- [ ] 同一人物的姿态合理连续
- [ ] 同一人物的表情符合情绪发展

**场景一致性**：
- [ ] 同一地点的建筑风格/材料一致
- [ ] 同一场景的光线方向/时间一致
- [ ] 同一场景的天气条件一致
- [ ] 同一场景的氛围基调一致
- [ ] 同一场景的色调一致

**视觉连贯性**：
- [ ] 屏幕方向连续（180度轴线规则）
- [ ] 景别选择符合锚点类型
- [ ] 构图变化合理

**历史准确性**：
- [ ] 时代特征准确（服饰、建筑、道具）
- [ ] 文化背景准确（礼仪、习俗、称呼）
- [ ] 地理位置准确（建筑、景观、气候）

### 检查报告

生成Beat Board后，必须生成一致性检查报告：

```json
{
  "check_scope": "beat_board",
  "overall_result": "PASS",
  "score": 95,
  "details": {
    "character_consistency": {"result": "PASS", "score": 95},
    "scene_consistency": {"result": "PASS", "score": 95},
    "visual_continuity": {"result": "PASS", "score": 95},
    "historical_accuracy": {"result": "PASS", "score": 95}
  },
  "issues": [],
  "warnings": []
}
```

### Prompt优化

**参考**：`core/prompt-optimizer-rules.md`

**优化流程**：
1. 简洁性优化：删除冗余描述，保留核心特征
2. 流畅性优化：确保描述逻辑连贯，增强画面感
3. 专业性优化：优化摄影术语和技术参数
4. 准确性优化：修正历史错误，确保文化尊重

**优化目标**：
- Prompt长度 ≤ 200字
- 核心特征完整（人物、动作、环境、光线、氛围）
- 技术参数合理

## 验收标准

生成Beat Board后必须检查：

**叙事清晰度**：
- [ ] 九张是否能讲清故事主线与关键拐点？
- [ ] 每格的镜头目的是否明确（信息/情绪/悬念/转折）？
- [ ] 是否覆盖叙事曲线的关键拐点？

**覆盖完整性**：
- [ ] 是否缺关键转折/高潮/结果？
- [ ] 是否存在"重复信息点"的锚点（冗余）？
- [ ] 锚点类型分布是否合理？

**一致性**：
- [ ] 人物外观/服装状态是否统一？
- [ ] 场景固定物是否一致？
- [ ] 光色逻辑是否一致？
- [ ] 视觉风格是否统一？

**可用性**：
- [ ] 每格是否足够清晰，能作为Sequence Board的参考图片？
- [ ] 是否存在"画面说不清/无法复述叙事目的"的格子？
- [ ] Prompt长度是否合理（≤ 200字）？

**历史准确性**：
- [ ] 时代特征是否准确？
- [ ] 文化背景是否准确？
- [ ] 地理位置是否准确？

**质量评分**：
- [ ] 总体评分 ≥ 90分（优秀）
- [ ] 无严重问题（issues）
- [ ] 警告数量 ≤ 2个（warnings）

## 输出示例

### 格子 0

**节拍ID**: `beat_001`
**锚点类型**: `PROTAGONIST_STATUS`（主角现状）
**强度**: `LOW`
**情绪**: `NEUTRAL`

**特征库查询**：
- 人物：林江迈（`lin_jiangmai_1947`）
- 服饰：民国平民服装（`republic_of_china_1947_common`）
- 建筑：台北老街（`republic_of_china_1947_old_street`）
- 地点：天马茶房（`taipei_tianma_teahouse_1947`）

**提示词**:
```
历史纪录片风格，中景镜头，1947年台北太平町天马茶房前。
40岁的林江迈，身穿打补丁的粗布衣裳，脸上写满疲惫，蹲在路边摆摊，正在整理香烟摊位。
傍晚昏黄的街灯透过薄雾洒在粗糙路面上，形成斑驳光影。
灰褐色和旧黄色的色调，破旧木结构建筑和日式装饰，紧张混乱的氛围。
光圈 f/2.8，ISO 400，胶片质感。
```

**画面要素**:
- 景别：中景
- 主体：林江迈（40岁寡妇，蹲姿）
- 环境：台北太平町天马茶房前，傍晚
- 光线：昏黄街灯，薄雾
- 色调：灰褐色和旧黄色
- 技术参数：f/2.8，ISO 400，胶片质感

**一致性检查**：
- [x] 人物特征与特征库一致
- [x] 服饰与时代一致
- [x] 建筑风格与时代一致
- [x] 光线条件合理

## 注意事项

1. **叙事描述优先**：使用完整的叙事段落，而非关键词堆叠
2. **场景化思维**：回答"谁在哪里、做什么、环境如何、光线如何"
3. **摄影术语融入**：将景别、角度、镜头效果自然融入描述
4. **情绪具体化**：用光影、色彩、构图传达情绪，而非直接说"戏剧性"
5. **特征库优先**：优先使用特征库的`prompt_snippet`，确保历史准确性
6. **模板遵循**：严格遵循Prompt模板结构，保持一致性
7. **简洁性**：Prompt长度控制在200字以内，保留核心特征
8. **一致性**：确保同一人物/场景在9个格子中保持一致

## 参考文档

- `core/prompt-generation-rules.md` - Prompt生成流程
- `templates/prompt-templates.md` - Prompt模板库
- `core/continuity-check-rules.md` - 一致性检查规则
- `core/prompt-optimizer-rules.md` - Prompt优化规则
- `libraries/README.md` - 特征库使用指南
- `core/beat-breakdown-rules.md` - 节拍拆解规则
- `gemini-image-prompt-guide.md` - Gemini最佳实践
- `方法论补充.md` - 影视分镜方法论