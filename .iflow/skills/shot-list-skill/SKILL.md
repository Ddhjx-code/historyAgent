---
name: shot-list-skill
description: 口播稿转分镜清单技能。将口播稿转化为可执行的 JSON 分镜清单，输出符合 Seedream/Seedance/FFmpeg/Azure TTS API 规范的参数。
---

# 口播稿转分镜清单技能

[技能说明]
将口播稿转化为分镜执行清单（shot-list.json），输出符合 Seedream/Seedance/FFmpeg/Azure TTS API 规范的可执行参数。

[约束条件]
- 单个视频时长：1-15 秒（Seedance 硬性限制）
- 图像分辨率：1920x1080（16:9 横屏）
- 视频分辨率：1080p
- 输出格式：JSON
- **SSML 长度限制：≤ 1024 字符（Azure TTS 硬性限制）**
- **单镜头旁白字数：≤ 100 字（按 3.5 字/秒计算，适配 15 秒时长）**

[文件结构]
shot-list-skill/
├── SKILL.md                   # 本文件
├── api-spec.md                # API 规范（包含核心设计原则）
└── templates/
    └── shot-list-template.md  # 输出模板

## 混合方案（成本优化）

采用 **Seedance + FFmpeg** 混合方案降低成本：

| 镜头类型 | 视频工具 | 成本 | 效果 |
|---------|---------|------|------|
| title_card | ffmpeg | 免费 | Ken Burns 推进 |
| transition | ffmpeg | 免费 | Ken Burns 推进 |
| historical_scene | seedance | ~1元/5秒 | AI 生成动态 |
| map | ffmpeg | 免费 | 缩放/平移 |

**成本估算**：每集约 10-15 个历史场景镜头，成本 10-20 元。

[工作流程]
1. 解析口播稿 → 提取场景、时间轴、旁白
2. 场景分镜 → 按 ≤15s 拆分为镜头
3. 分配视频工具 → 根据镜头类型选择 FFmpeg/Seedance
4. 生成图像提示词 → 调用 prompt_engine.HistoryPromptGenerator（见下方集成说明）
5. 生成动态参数 → FFmpeg 效果或 Seedance 提示词
6. 生成 SSML → 符合 Azure TTS 规范
7. 配置全局资源 → BGM、字体、风格预设
8. 设置依赖关系 → video 依赖 image
9. 输出 shot-list.json

[提示词生成器集成]

本项目集成了 skill-prompt-generator 的智能提示词生成能力：

**使用方式**：
```python
from prompt_engine import HistoryPromptGenerator

gen = HistoryPromptGenerator()

# 方式1：自动解析场景参数
text = "战国时期，秦国大殿上，秦王赢稷与武将白起议事"
params = gen.parse_scene_from_text(text)
result = gen.generate_image_prompt(text, **params)

# 方式2：手动指定参数
result = gen.generate_image_prompt(
    scene_description="哈德良皇帝指定继承人",
    dynasty="roman",
    character_type="emperor",
    scene_type="palace_hall",
    visual_style="cinematic"
)

# 获取生成的提示词
image_prompt = result['image_prompt']
```

**支持的历史领域参数**：

| 参数 | 可选值 |
|------|--------|
| dynasty | qin_han, tang, song, ming, qing, warring_states, roman, medieval |
| character_type | emperor, general, scholar, warrior, monk, concubine, soldier, assassin |
| scene_type | palace_hall, battlefield, court, garden, temple, city_gate, war_council |
| action | duel, army_charge, court_debate, assassination, coronation |
| visual_style | cinematic, documentary, epic, intimate |

**生成动态视频提示词**：
```python
result = gen.generate_motion_prompt(
    scene_description="唐朝宫廷，皇帝坐在龙椅上",
    motion_type="subtle",  # subtle, moderate, dynamic
    dynasty="tang"
)
motion_prompt = result['motion_prompt']
```

[口播稿解析规则]

识别结构元素：
- 【开场白】→ 开场镜头（标题卡）
- 【第X部分】→ 分隔转场
- 【事件X】→ 历史场景镜头
- 【结尾语】→ 结尾镜头

提取关键信息：
- 时间标记（如：公元138年）
- 人物（如：哈德良皇帝、玄奘）
- 地点（如：罗马宫廷、长安）
- 旁白文本 → 用于 TTS

**章节事件分配规则**：

根据事件编号分配到对应章节（事件编号使用中文数字：一、二、三...）：

| 章节编号 | 章节名称 | 事件编号 | 时代范围 |
|---------|---------|---------|---------|
| 第一部分 | 古代历史的见证 | 事件一、二 | 古代（罗马、波斯） |
| 第二部分 | 中国古代的文化高峰 | 事件三至七 | 中古（唐、明、西藏等） |
| 第三部分 | 工业革命与近现代的创新 | 事件八至十二 | 近现代（19-20世纪） |
| 第四部分 | 当代的国际关系 | 事件十三 | 当代（21世纪） |

**注意**：
- 事件编号与章节内容必须匹配，不要将工业革命事件放到"中国古代"章节
- 章节转场的提示词必须与后续内容主题相符

[分镜规则]

镜头类型与时长：
| 类型 | 时长范围 | 视频工具 | 说明 |
|------|---------|---------|------|
| title_card | 5-10秒 | ffmpeg | 节目标题卡 |
| historical_scene | 5-15秒 | seedance | 历史场景重现 |
| transition | 3-8秒 | ffmpeg | 转场动画 |
| map | 5-10秒 | ffmpeg | 地图/信息图 |

视频工具选择规则：
1. **默认使用 FFmpeg**：标题卡、转场、地图
2. **使用 Seedance**：历史场景（需要人物动作、场景变化）
3. **判断依据**：
   - 需要人物动作（走动、说话、转身）→ Seedance
   - 需要场景动态（云动、水波、火光）→ Seedance
   - 静态画面 + 简单动效 → FFmpeg

时长拆分规则：
- 场景时长 > 15秒 → 拆分为多个镜头
- 每个镜头 ≤ 15秒
- 拆分点选择：动作变化、视角切换、时间跳跃

**旁白时长匹配规则**：
- 中文语速：约 3-4 字/秒（建议按 3.5 字/秒计算）
- 计算公式：`旁白字数 ÷ 3.5 = 预估秒数`
- 镜头时长 = 旁白预估秒数 + 1秒缓冲
- 如果旁白过长导致 SSML 超过 1024 字符，必须精简旁白内容

**转场提示词规则**：

根据章节主题生成匹配的转场提示词：

| 章节主题 | 转场提示词背景元素 |
|---------|------------------|
| 古代历史（罗马、波斯等） | 羊皮卷轴、罗马竞技场、古代地图、历史剪影 |
| 中国古代文化 | 水墨山水画、古典亭台、远山近水、云雾缭绕 |
| 工业革命/近现代 | 蒸汽机、钢铁厂、现代都市剪影、工业烟雾 |
| 当代国际关系 | 联合国大楼、各国国旗、蓝色地球、现代科技感 |

**示例**：
- "第二部分：中国古代的文化高峰" → 背景：水墨山水画效果
- "第三部分：工业革命与近现代的创新" → 背景：蒸汽机、钢铁厂剪影

[全局资源配置]

在 meta.global_assets 中配置：

```json
{
  "global_assets": {
    "bgm": {
      "path": "assets/bgm/documentary_ambient.mp3",
      "volume": 0.3,
      "ducking": true,
      "ducking_ratio": 0.2
    },
    "fonts": {
      "title": "assets/fonts/NotoSerifSC-Bold.otf",
      "subtitle": "assets/fonts/NotoSansSC-Regular.otf"
    },
    "logo": "assets/images/logo.png"
  }
}
```

[风格预设]

在 meta.style_preset 中配置全局风格：

```json
{
  "style_preset": {
    "visual_style": "历史纪录片风格",
    "color_grading": "暖色调，电影质感",
    "transition_default": "dissolve"
  }
}
```

**注意**：visual_style 会自动添加到每个图像 prompt 开头。

[依赖关系]

每个镜头的 video 任务必须声明依赖：

```json
{
  "tasks": {
    "image": { ... },
    "video": {
      "depends_on": ["tasks.image"],
      ...
    }
  }
}
```

[转场效果]

每个镜头末尾配置转场：

```json
{
  "transition": {
    "type": "dissolve",
    "duration": 1.0
  }
}
```

转场类型：
| 类型 | 说明 | 适用场景 |
|------|------|---------|
| dissolve | 叠化 | 默认转场 |
| fade_to_black | 黑场 | 章节/年代跨度大 |
| wipe | 划像 | 时间线推进 |
| cut | 直接切换 | 快节奏叙事 |

[人物一致性]

跨镜头人物一致性控制：

```json
{
  "shot_id": "shot_004",
  "character_id": "xuanzang_645",
  "tasks": {
    "image": {
      "parameters": {
        "reference_image": "shot_003.png",
        "seed": 42
      }
    },
    "video": {
      "parameters": {
        "seed": 42,
        "reference_image": "shot_003.png"
      }
    }
  }
}
```

**一致性规则**：
1. 同一人物在不同镜头中使用相同的 character_id
2. 后续镜头的 reference_image 指向前一个镜头
3. 使用相同的 seed 值保持风格一致

[首尾帧衔接规则]

连续镜头需要指定 reference_image：
```json
{
  "reference_image": "shot_004.png"
}
```

衔接原则：
- 同一场景的连续镜头使用前一个镜头的图片作为参考
- 保持人物外貌一致
- 保持场景光色一致
- 变化时显式说明原因

[历史考据规则]

识别时代后自动补充：
| 时代 | 服饰特征 | 建筑风格 | 色调 |
|------|---------|---------|------|
| 古罗马 | 托加长袍、橄榄冠 | 大理石柱、马赛克 | 暖黄、白 |
| 战国秦汉 | 深衣、冠冕 | 宫殿、城郭 | 黑红、金 |
| 唐代 | 襦裙、圆领袍 | 斗拱、飞檐 | 绚丽多彩 |
| 明清 | 马褂、旗装 | 琉璃瓦、红墙 | 红黄、蓝 |
| 工业时代（19世纪） | 西装马甲、礼帽 | 工厂车间、蒸汽机 | 褐色、铜色 |
| 现代（20-21世纪） | 正装、商务西装 | 现代建筑、会议室 | 蓝灰、中性色 |

**时代关键词识别**：

| 时代标识 | 关键词（优先级从高到低） |
|---------|------------------------|
| roman | 罗马、哈德良、安敦宁、罗马帝国 |
| persian | 波斯、萨珊、霍斯劳、喀瓦德 |
| tang | 玄奘、长安、唐代（注意：单独"唐"不匹配） |
| ming | 明代、明朝、朱瞻基、宣德（注意：单独"明"不匹配，避免匹配"发明"） |
| medieval | 中世纪、骑士、瑞典国王、埃里克 |
| tibetan | 西藏、达赖、仓央嘉措、布达拉宫 |
| industrial | 柯尔特、左轮手枪、钢铁公司、摩根、发明家、工业 |
| modern | 外交部、发言人、科威特、独立、苏维埃 |

**注意**：
- 识别时要避免误匹配，如"发明"中的"明"不应匹配为明朝
- 使用完整词汇匹配优先于单字匹配

[重试策略]

每个任务配置重试策略：

```json
{
  "retry_policy": {
    "max_retries": 3,
    "backoff": "exponential"
  }
}
```

[输出规范]

输出文件：outputs/{episode}/shot-list.json

输出格式：参考 templates/shot-list-template.md

[FFmpeg 效果选择]

| 镜头类型 | 推荐效果 | 参数建议 |
|---------|---------|---------|
| title_card | zoom_in | zoom_end=1.15 |
| transition | zoom_in | zoom_end=1.1 |
| map | pan_right 或 zoom_in | 根据地图方向 |

[注意事项]
- 严格按照 api-spec.md 中的规范生成提示词
- 确保每个镜头时长 ≤ 15秒
- **确保每个 SSML 长度 ≤ 1024 字符**
- **确保旁白字数与镜头时长匹配（3.5 字/秒）**
- **确保章节与事件分配正确**
- **确保转场提示词与章节主题匹配**
- 连续镜头必须指定 reference_image
- 旁白文本必须生成对应的 SSML（使用 SSMLGenerator，见下方说明）
- 历史场景必须使用 Seedance（需动态效果）
- 其他类型镜头使用 FFmpeg（节省成本）
- 在 meta 中添加 cost_estimate 预估成本
- 配置 global_assets（BGM、字体）
- 配置 style_preset（全局风格）
- 设置 depends_on（依赖关系）
- 设置 transition（转场效果）
- 设置 character_id（人物一致性）
- 设置 retry_policy（重试策略）

[输出校验清单]

生成 shot-list.json 后必须校验：

- [ ] 每个镜头 duration ≤ 15
- [ ] 每个 SSML 长度 ≤ 1024 字符
- [ ] 每个镜头旁白字数 ≤ 时长 × 4（留有余量）
- [ ] 章节转场位置正确（在各章节第一个事件之前）
- [ ] 章节转场提示词与后续内容主题匹配
- [ ] 历史场景的朝代/时代识别正确
- [ ] 所有 image.parameters.size 为 1920x1080
- [ ] video.tool 为 seedance 或 ffmpeg
- [ ] 所有 video 任务有 depends_on
- [ ] 连续镜头有 reference_image（人物一致性）
- [ ] meta 中包含 cost_estimate、global_assets、style_preset

[SSML 增强生成器]

使用 SSMLGenerator 生成自然的语音旁白，解决多音字、停顿、情感等问题：

**使用方式**：
```python
from prompt_engine import SSMLGenerator, EmotionType

gen = SSMLGenerator("zh-CN-YunxiNeural")

# 方式1：快速生成
ssml = gen.generate_emotional(
    text="公元645年2月25日，唐代高僧玄奘携带657部梵文佛经回到长安。",
    emotion="solemn",  # solemn, serious, dramatic, hopeful, nostalgic
    emphasis=["玄奘", "657部"]
)

# 方式2：便捷方法
ssml = gen.generate_narration(text, is_dramatic=False)  # 历史叙事
ssml = gen.generate_opening(text)   # 开场白
ssml = gen.generate_ending(text)    # 结尾语

# 方式3：精细控制（分段）
from prompt_engine import SSMLSegment, PauseType

segments = [
    SSMLSegment(text="在公元138年的这一天，", emotion=EmotionType.SOLEMN, pause_after=PauseType.SHORT),
    SSMLSegment(text="罗马皇帝哈德良做出了一个重大决定——", emotion=EmotionType.SERIOUS, emphasis="strong", pause_after=PauseType.MEDIUM),
    SSMLSegment(text="他收养并指定安敦宁·毕尤为帝国的继承人。", emotion=EmotionType.NEUTRAL, rate=0.85),
]
ssml = gen.generate_with_segments(segments)
```

**功能说明**：

| 功能 | 说明 | 示例 |
|------|------|------|
| 多音字修正 | 自动修正历史类常见多音字 | 单于→chán yú，冒顿→mò dú |
| 自动停顿 | 根据标点自动添加停顿 | ，→500ms，。→1000ms |
| 情感表达 | 8种情感风格 | solemn(庄重), dramatic(戏剧性), hopeful(充满希望) |
| 强调标记 | 强调关键词语 | 摩根、14亿美元 |
| 语速控制 | 不同情感自动调整语速 | 庄重0.85，激动1.1 |

**情感类型**：
| 情感 | 适用场景 | 语速 | 音调 |
|------|---------|------|------|
| neutral | 中性叙述 | 1.0 | +0% |
| serious | 严肃内容 | 0.9 | -5% |
| solemn | 庄重历史 | 0.85 | -10% |
| dramatic | 戏剧高潮 | 0.8 | +0% |
| hopeful | 充满希望 | 0.95 | +5% |
| nostalgic | 怀旧结尾 | 0.85 | -5% |
| excited | 激动兴奋 | 1.1 | +10% |
| sad | 悲伤内容 | 0.8 | -15% |

**多音字词典**（已内置）：
- 人名/称号：单于(chán yú)、可汗(kè hán)、冒顿(mò dú)、阏氏(yān zhī)
- 地名：大宛(dà yuān)、龟兹(qiū cí)、吐蕃(tǔ bō)
- 复姓：万俟(mò qí)、尉迟(yù chí)、长孙(zhǎng sūn)
- 其他：大月氏(dà ròu zhī)、般若(bō rě)、南无(nā mó)
