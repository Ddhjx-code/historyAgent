name: shot-list-skill
description: 口播稿转分镜清单技能。将任意口播稿转化为可执行的 JSON 分镜清单，输出符合 Seedream/Seedance/FFmpeg/Azure TTS API 规范的参数。

---

# 口播稿转分镜清单技能（通用版）

[技能说明]
将任意口播稿转化为分镜执行清单（shot-list.json），输出符合 Seedream/Seedance/FFmpeg/Azure TTS API 规范的可执行参数。

**核心特性**：
- **通用性**：不依赖特定内容模板，适用于任何类型的口播稿
- **动态提取**：从口播稿中自动提取时间、人物、地点、事件等信息
- **智能分段**：根据文本结构和长度自动生成合理镜头序列
- **一致性保障**：自动处理人物和场景的视觉连贯性

[约束条件]
- 单个视频时长：1-15 秒（Seedance 硬性限制）
- 图像分辨率：1920x1080（16:9 横屏）
- 视频分辨率：1080p
- 输出格式：JSON
- 旁白文本长度限制：≤ 1024 字符（Azure TTS text 字段硬性限制）
- 旁白文本应保留口播稿原始内容，尽量不精简
- 长旁白通过拆分为多个镜头来适配（每镜头 ≤ 15秒）

[文件结构]
shot-list-skill/
├── SKILL.md                   # 本文件
├── api-spec.md                # API 规范（包含核心设计原则）
├── core/                      # 核心模块
│   ├── script-parser-rules.md    # 口播稿解析规则
│   ├── shot-generation-rules.md  # 镜头生成规则
│   ├── prompt-generation-rules.md # Prompt生成规则
│   ├── continuity-rules.md       # 连贯性规则
│   └── data-structures.md        # 数据结构定义
└── templates/
    └── shot-list-template.md  # 输出模板

---

## 工作流程

### 整体流程图

```
口播稿输入
    ↓
[阶段1：脚本解析]
    ├─ 提取段落结构（开场、章节、结尾）
    ├─ 提取时间信息（年份、朝代、时代）
    ├─ 提取人物信息（姓名、身份、动作）
    ├─ 提取地点信息（地名、场景描述）
    └─ 提取事件信息（核心事件、描述）
    ↓
[阶段2：分段处理]
    ├─ 为每个段落确定镜头类型
    │   ├─ 开场/结尾 → title_card
    │   ├─ 章节标题 → title_card
    │   ├─ 过渡/抽象概念 → transition
    │   └─ 具体内容 → content_scene
    └─ 计算每个段落的镜头数量（基于文本长度）
    ↓
[阶段3：镜头生成]
    ├─ 为每个镜头分配时长（≤15秒）
    ├─ 生成时间码（连续无断裂）
    └─ 确定镜头类型（title_card/transition/content_scene）
    ↓
[阶段4：Prompt生成]
    ├─ title_card：标题 + 装饰元素
    ├─ transition：抽象概念的具体化描述
    └─ content_scene：具体场景的视觉描述
    ↓
[阶段5：一致性处理]
    ├─ 为同一人物分配 character_id
    ├─ 建立人物引用链（reference_image）
    ├─ 为同一场景保持视觉特征
    └─ 设置 seed 参数确保可复现
    ↓
[阶段6：参数生成]
    ├─ 生成图像参数（prompt、size、seed、reference_image）
    ├─ 生成视频参数（tool、effect、depends_on）
    ├─ 生成音频参数（voice、ssml、text）
    └─ 生成转场参数（type、duration）
    ↓
输出 shot-list.json
```

---

## 详细规则

### 阶段1：脚本解析规则

参考：`core/script-parser-rules.md`

**目标**：从口播稿中提取结构化信息

**提取内容**：
1. **段落结构**：识别开场白、章节标题、结尾语
2. **时间信息**：年份、朝代、时代描述
3. **人物信息**：姓名、身份、动作描述
4. **地点信息**：地名、场景类型、环境描述
5. **事件信息**：核心事件、事件描述

**提取方法**：
- 使用正则表达式匹配时间模式（如"公元XXX年"、"XXX朝"、"XXX时代"）
- 使用上下文分析识别人物和地点
- 保留原始文本作为旁白内容

---

### 阶段2：分段处理规则

参考：`core/shot-generation-rules.md`

**目标**：将口播稿段落转换为镜头序列

**镜头类型判断**：
| 段落类型 | 镜头类型 | 说明 |
|---------|---------|------|
| 开场白 | title_card + transition | 节目标题 + 时光隧道效果 |
| 章节标题 | title_card | 章节标题卡 |
| 过渡段落 | transition | 抽象概念、时间跨越 |
| 具体事件 | content_scene | 具体历史场景、事件描述 |
| 结尾语 | title_card + transition | 感谢语 + 历史回顾 |

**镜头数量计算**：
- 基于文本长度和阅读速度（约 3-4 字/秒）
- 每个镜头时长 5-15 秒
- 长段落自动拆分为多个镜头

---

### 阶段3：镜头生成规则

**时长分配原则**：
- 标题卡：6-10 秒
- 转场镜头：8-12 秒
- 内容镜头：10-15 秒
- 结尾镜头：12-15 秒

**时间码计算**：
- 从 00:00 开始
- 累加每个镜头的 duration
- 格式：MM:SS-MM:SS

**镜头编号**：
- 格式：shot_001, shot_002, ...
- 连续无断裂
- 按时间顺序排列

---

### 阶段4：Prompt生成与优化

参考：`core/prompt-generation-rules.md`

**步骤4.1：生成 Prompt**
- title_card：标题 + 装饰元素
- transition：抽象概念的具体化描述
- content_scene：具体场景的视觉描述

**步骤4.2：判断 needs_text**
- title_card：`needs_text = true`
- transition/content_scene：检查是否包含文字指示词（标题、年份、标记等）

**步骤4.3：选择模型**
- `needs_text = true`：使用 `doubao-seedream-4.5`
- `needs_text = false`：使用 `doubao-seedream-3.0`

**步骤4.4：过滤敏感词**
- 过滤词汇：革命、台湾、共产党、苏维埃、共产主义
- 替换为：`**`
- 确保所有 prompt 都经过过滤

**步骤4.5：设置参数**
- 设置 `needs_text` 字段
- 设置 `model` 字段
- 设置其他参数（size、seed、reference_image）

**通用Prompt模板**：

#### 1. 标题卡 Prompt
```
[视觉风格]，[标题内容]。
[装饰元素描述]，[背景描述]。
电影质感，16:9横屏，[整体氛围]。
```

**示例**：
```
历史纪录片风格，标题卡片"历史上的今天"。
金色边框装饰，中央大字标题，下方副标题"2026年2月25日"。
背景是历史时光隧道效果，展现从古代到现代的时间流动。
电影质感，16:9横屏，庄重大气。
```

#### 2. 转场镜头 Prompt
```
[视觉风格]，[抽象概念的具体化描述]。
[具体元素列举]，[视觉细节]。
电影质感，16:9横屏，[整体氛围]。
```

**关键原则**：
- 将抽象概念转化为**具体的视觉元素**
- 列举关键的时间点、事件、场景
- 使用连接词建立视觉联系

**示例**：
```
历史纪录片风格，横向时间轴画面。
背景是深邃的宇宙星空。时间轴从左到右延伸，标记了公元138年（罗马帝国）、628年（波斯萨珊）、645年（玄奘取经）、1836年（左轮手枪）、1901年（美国钢铁）、1921年（苏联扩张）、1961年（科威特独立）、1980年（苏里南**）、2026年（中国外交部）。每个年份用金色光点标记，金色光芒连接各个光点。
电影质感，16:9横屏，宏大史诗感。
```

#### 3. 内容场景 Prompt
```
[视觉风格]，[时代描述]。
[人物描述]，[人物动作]，[场景环境]。
[光影氛围]，[色调描述]。
电影质感，16:9横屏，[整体氛围]。
```

**示例**：
```
历史纪录片风格，古罗马帝国时代。
哈德良皇帝身着紫色镶边托加长袍，头戴橄榄枝冠冕，坐在大理石宝座上。宫廷内罗马柱林立，马赛克地板，墙上挂着罗马鹰旗。温暖的地中海阳光从高窗射入，形成戏剧性光影。
电影质感，16:9横屏，庄严肃穆。
```

---

### 阶段5：一致性处理规则

参考：`core/continuity-rules.md`

**人物一致性**：
1. 为同一人物分配相同的 `character_id`
2. 后续镜头使用 `reference_image` 指向前一个镜头
3. 使用 `seed` 参数确保人物外观可复现

**场景一致性**：
1. 同一地点保持相似的视觉描述
2. 使用 `reference_image` 传递场景特征
3. 保持光线、色调、氛围的一致性

**引用链建立**：
```
shot_001: character_id = "person_a", reference_image = null
shot_002: character_id = "person_a", reference_image = "shot_001.png"
shot_003: character_id = "person_a", reference_image = "shot_002.png"
```

---

### 阶段6：参数生成规则

**图像参数**：
- `tool`: "seedream"
- `model`: "doubao-seedream-4.5"
- `prompt`: [阶段4生成的prompt]
- `size`: "1920x1080"
- `n`: 1
- `seed`: [人物ID的哈希值，确保可复现]
- `reference_image`: [前置镜头的图像路径]

**视频参数**：
- `tool`: "seedance" 或 "ffmpeg"
  - 核心场景使用 "seedance"
  - 标题卡和转场使用 "ffmpeg"
- `effect`: "zoom_in", "pan_left", "dissolve" 等
- `depends_on`: ["tasks.image"]
- `parameters`:
  - Seedance: `resolution: "1080p"`, `motion_prompt`
  - FFmpeg: `input_image`, `duration`, `zoom_start`, `zoom_end`, `fps`

**音频参数**：
- `tool`: "azure_tts"
- `voice`: "zh-CN-XiaoxiaoNeural" 或 "zh-CN-YunxiNeural"
- `ssml`: [SSML格式的旁白文本]
- `text`: [原始旁白文本]

**转场参数**：
- `type`: "dissolve", "fade", "wipe" 等
- `duration`: 0.5-1.5 秒

---

## 成本优化策略

采用 **Seedance + FFmpeg** 混合方案降低成本：

| 镜头类型 | 视频工具 | 成本 | 适用场景 |
|---------|---------|------|---------|
| title_card | ffmpeg | 免费 | 标题卡、章节标题 |
| transition | ffmpeg | 免费 | 转场、抽象概念 |
| content_scene | seedance | ~1元/5秒 | 核心历史场景 |

**成本估算**：
- 假设 10 分钟口播稿
- 标题卡：约 5 个（免费）
- 转场镜头：约 10 个（免费）
- 内容场景：约 15-20 个（15-25元）
- **总成本：约 15-25 元**

---

## API 规范

详细的 API 参数规范请参考 `api-spec.md`。

---

## 模板参考

shot-list.json 的模板请参考 `templates/shot-list-template.md`。

---

## 常见问题

### Q1：如何处理口播稿中没有明确描述的场景？

A：使用通用的视觉描述，例如"历史场景"、"抽象概念"等，结合口播稿中的时间信息构建合理的画面。

### Q2：如何确保历史准确性？

A：从口播稿中提取准确的时间、人物、地点信息，在 prompt 中直接使用这些信息，不添加未经证实的细节。

### Q3：如何处理非常长的口播稿？

A：自动拆分为多个镜头，每个镜头时长控制在 15 秒以内，确保流畅观看体验。

### Q4：如何处理不同类型的口播稿？

A：本技能采用通用化设计，适用于历史、科普、故事、新闻等各类口播稿，不依赖特定模板。

---

## 更新日志

**v3.0** (2026-02-27) - 全面重构
- 移除 Beat Board/Sequence Board 分层流程
- 建立通用化脚本解析和镜头生成规则
- 移除静态历史特征库，改为动态提取
- 简化工作流程，提升通用性

**v2.1** - 添加历史特征库和智能Prompt生成
**v2.0** - 分层渐进式分镜系统（Beat Board + Sequence Board）
**v1.0** - 初始版本