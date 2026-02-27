# API 规范

本文档定义 Seedream、Seedance、FFmpeg、Azure TTS 四个工具的 API 规范。

---

## 〇、核心设计原则

### 0.1 依赖关系与执行顺序（Critical）

**问题**：视频生成依赖图片生成结果，如果盲目并行执行会导致错误。

**解决方案**：在工作流引擎中内置依赖逻辑，或在 JSON 中显式声明依赖。

**依赖规则**：
1. `video` 任务必须等待同 Shot 下的 `image` 任务成功完成
2. `audio` 任务可独立执行
3. 最终合成必须等待所有 video 和 audio 任务完成

**JSON 结构中的依赖声明**：
```json
{
  "shot_id": "shot_004",
  "tasks": {
    "image": { ... },
    "video": {
      "depends_on": ["tasks.image"],
      ...
    }
  }
}
```

### 0.2 全局资源上下文（Global Context）

**问题**：缺少背景音乐、统一风格约束、字体素材库等全局配置。

**解决方案**：在 `meta` 下增加 `global_assets` 和 `style_preset`。

**示例**：
```json
{
  "meta": {
    "project_name": "历史上的今天",
    "episode": "2026-02-25",
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
      "logo": "assets/images/logo.png",
      "watermark": "assets/images/watermark.png"
    },
    "style_preset": {
      "visual_style": "历史纪录片风格",
      "color_grading": "暖色调，电影质感",
      "transition_default": "dissolve"
    }
  }
}
```

### 0.3 音频混合逻辑（Audio Mixing）

**问题**：只有人声（TTS），没有混音策略。

**解决方案**：定义音轨结构和混音规则。

**音频轨道结构**：
```json
{
  "audio_mix": {
    "tracks": [
      {
        "type": "voice",
        "source": "tts_output",
        "volume": 1.0,
        "effects": ["normalize", "noise_reduction"]
      },
      {
        "type": "bgm",
        "source": "global_assets.bgm",
        "volume": 0.3,
        "ducking": {
          "trigger": "voice",
          "ratio": 0.2,
          "attack": 0.5,
          "release": 1.0
        }
      },
      {
        "type": "sfx",
        "events": [
          { "time": "00:05", "sound": "page_flip.mp3", "volume": 0.5 },
          { "time": "00:12", "sound": "whoosh.mp3", "volume": 0.4 }
        ]
      }
    ]
  }
}
```

### 0.4 错误处理与重试机制（Error Handling）

**问题**：AI 生成有失败率，没有定义重试策略。

**解决方案**：增加 `retry_policy` 和 `fallback_prompt`。

**重试策略**：
```json
{
  "retry_policy": {
    "max_retries": 3,
    "backoff": "exponential",
    "initial_delay": 2,
    "max_delay": 30,
    "retry_on": ["timeout", "content_filter", "rate_limit"]
  },
  "on_failure": "skip|stop|fallback",
  "fallback_prompt": "备用提示词（内容审核友好版本）"
}
```

### 0.5 文件路径管理（File Path Management）

**问题**：相对路径不明确，分布式环境无法定位资源。

**解决方案**：使用 URI 格式或由工作流引擎统一管理。

**路径规范**：
```json
{
  "storage": {
    "type": "local|s3|oss",
    "base_path": "file:///data/projects/history/outputs/2026-02-25/",
    "s3_bucket": "history-agent-output",
    "s3_prefix": "shots/"
  },
  "file_naming": {
    "image": "{shot_id}.png",
    "video": "{shot_id}.mp4",
    "audio": "{shot_id}.mp3"
  }
}
```

### 0.6 人物一致性控制（Character Consistency）

**问题**：同一人物在不同镜头中可能外观不一致。

**解决方案**：使用 Seedance 2.0 的 `reference_image` + `seed` 参数。

**一致性配置**：
```json
{
  "character_consistency": {
    "character_id": "xuanzang_645",
    "reference_images": ["shot_007.png", "shot_007_alt.png"],
    "seed": 42,
    "description": "玄奘法师，唐代僧侣，身着袈裟，手持锡杖，面容慈祥"
  }
}
```

**注意**：Seedance 2.0 的多模态 @ 引用系统可精准复制参考视频的运镜和风格。

### 0.7 转场效果定义（Inter-shot Transition）

**问题**：缺乏镜头间转场的定义。

**解决方案**：在每个镜头末尾定义转场类型，或在 `meta` 中定义默认转场。

**转场类型**：
| 类型 | 说明 | 时长 |
|------|------|------|
| dissolve | 叠化（淡入淡出） | 1-2秒 |
| fade_to_black | 黑场过渡 | 1-2秒 |
| wipe | 划像 | 0.5-1秒 |
| cut | 直接切换 | 0秒 |
| zoom | 缩放转场 | 0.5-1秒 |

**转场配置**：
```json
{
  "transition": {
    "type": "dissolve",
    "duration": 1.0,
    "params": {}
  }
}
```

---

## 一、混合方案总览

为降低成本，采用 **Seedance + FFmpeg** 混合方案：

| 镜头类型 | 视频工具 | 成本 | 说明 |
|---------|---------|------|------|
| title_card（标题卡） | ffmpeg | 0元 | Ken Burns 推拉效果 |
| transition（转场） | ffmpeg | 0元 | 简单动效足够 |
| host（主持人） | ffmpeg | 0元 | 缓慢推进/摇摄 |
| historical_scene（历史场景） | seedance | ~1元/5秒 | 需要人物/场景动态 |
| map（地图） | ffmpeg | 0元 | 缩放/平移效果 |

**成本估算**：每个节目约 10-15 个历史场景镜头，成本 10-20 元。

---

## 一、Seedream 图像生成

### 1.1 基本信息

| 项目 | 值 |
|------|-----|
| 工具 | seedream |
| 模型 | doubao-seedream-4.5 |
| 用途 | 生成关键帧图片 |

### 1.2 Prompt 规范

**结构**：
```
{视觉风格}，{主体描述}，{场景描述}，{时代背景}。
{人物描述}，{服饰描述}，{动作姿态}。
{环境细节}，{光线描述}，{氛围描述}。
{构图}，{画幅}，{色调}，{风格标签}。
```

**示例**：
```
历史纪录片风格，古罗马帝国宫廷，公元138年。哈德良皇帝身着紫色镶边托加长袍，头戴橄榄枝冠冕，面容威严而苍老，坐在大理石宝座上。宫廷内罗马柱林立，马赛克地板，墙上挂着罗马鹰旗。温暖的地中海阳光从高窗射入，形成戏剧性光影。电影质感，历史写实风格，16:9横屏，庄严肃穆。
```

### 1.3 参数规范

```json
{
  "tool": "seedream",
  "model": "doubao-seedream-4.5",
  "parameters": {
    "prompt": "string (必填，图像描述)",
    "size": "1920x1080 | 1080x1920 | 1024x1024",
    "n": 1,
    "reference_image": "string (可选，参考图片路径)",
    "needs_text": "boolean (是否需要生成文字内容)",
    "seed": "integer (可选，随机种子，确保可复现)"
  }
}
```

**参数约束**：
| 参数 | 允许值 | 默认值 |
|------|--------|--------|
| size | 1920x1080, 1080x1920, 1024x1024 | 1920x1080 |
| n | 1 | 1 |
| reference_image | 文件路径或URL | null |
| needs_text | true, false | false |
| seed | 整数 | null |

**模型选择规则**：
- `needs_text = true`：使用 `doubao-seedream-4.5`（高级模型，擅长文字生成）
- `needs_text = false`：使用 `doubao-seedream-3.0`（经济模型，成本更低）

**needs_text 判断规则**：
1. `title_card` 类型：`needs_text = true`
2. `transition` 类型：检查 prompt 是否包含文字指示词（标题、年份、标记等）
3. `historical_scene` 类型：检查 prompt 是否包含文字指示词

**敏感词过滤规则**：

以下词汇会导致图像生成失败，必须过滤：

| 敏感词 | 替换为 |
|--------|--------|
| 革命 | ** |
| 台湾 | ** |
| 共产党 | ** |
| 苏维埃 | ** |
| 共产主义 | ** |

**过滤策略**：
- 在生成 prompt 后立即过滤
- 将敏感词替换为 `**`
- 确保所有 prompt 都经过过滤

**说明**：
- `needs_text` 字段标识该镜头是否需要生成文字内容（如标题、字幕、年份标记等）
- 需要文字的镜头必须使用高级模型（4.5）以确保文字质量
- 不需要文字的镜头可以使用经济模型（3.0）以降低成本
- 敏感词过滤是必须的步骤，避免生成失败

### 1.4 Prompt 写法要点

1. **视觉风格优先**：开头明确风格（历史纪录片风格、电影质感、3D渲染等）
2. **时代背景明确**：标注具体年代（公元138年、战国末期等）
3. **人物描述具体**：外貌、服饰、姿态、表情
4. **环境细节丰富**：建筑、道具、光影、天气
5. **结尾固定格式**：画幅 + 色调 + 风格标签

---

## 二、Seedance 视频生成

### 2.1 基本信息

| 项目 | 值 |
|------|-----|
| 工具 | seedance |
| 模型 | doubao-seedance-2.0 |
| 用途 | 图生视频 |
| 时长限制 | **1-15 秒（硬性限制）** |

### 2.2 Motion Prompt 规范

**结构**：
```
{镜头运动}，{运动速度}，时长{X}秒。
{主体动作}，{动作细节}。
{环境变化}。
{氛围渲染}。
```

**示例**：
```
镜头缓慢推进，从宫廷入口移动到皇帝身边，时长8秒。皇帝缓缓抬起头，目光深邃，右手微微抬起。阳光在宫殿内缓慢移动，照亮他的脸庞。尘埃在光柱中缓缓飘动。节奏庄重缓慢，营造历史厚重感。
```

### 2.3 参数规范

```json
{
  "tool": "seedance",
  "model": "doubao-seedance-2.0",
  "depends_on": ["tasks.image"],
  "parameters": {
    "input_image": "string (必填，首帧图片路径)",
    "motion_prompt": "string (必填，动态描述)",
    "duration": "integer (1-15)",
    "resolution": "480p | 720p | 1080p",
    "aspect_ratio": "16:9 | 9:16 | 1:1",
    "seed": "integer (可选，一致性控制)",
    "reference_image": "string (可选，参考图片路径，用于人物一致性)",
    "negative_prompt": "string (可选，负面提示词)"
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff": "exponential"
  }
}
```

**参数约束**：
| 参数 | 允许值 | 默认值 | 说明 |
|------|--------|--------|------|
| duration | 1-15 | 5 | 视频时长（秒） |
| resolution | 480p, 720p, 1080p | 1080p | 输出分辨率 |
| aspect_ratio | 16:9, 9:16, 1:1 | 16:9 | 画面比例 |
| seed | -1 ~ 2147483647 | 随机 | 固定种子确保一致性 |
| reference_image | 文件路径或URL | null | 参考图片（人物一致性） |
| negative_prompt | 字符串 | null | 排除不需要的元素 |

**Seedance 2.0 高级功能**：
- **多模态输入**：支持文本、图片、音频、视频 4 种输入
- **多镜头叙事**：单次生成多场景连贯视频，角色和风格一致
- **原生音频生成**：自动生成与画面同步的音效和背景音乐
- **舞蹈/动作复刻**：上传参考视频，精准复制运镜和编舞动作

### 2.4 镜头运动词汇

| 运动类型 | 描述词汇 |
|---------|---------|
| 推进 | 镜头推进、缓慢推进、快速推进 |
| 拉远 | 镜头拉远、缓慢拉远、快速拉远 |
| 环绕 | 镜头环绕、围绕主体旋转 |
| 跟随 | 镜头跟随、跟随人物移动 |
| 固定 | 镜头固定、静止镜头 |
| 升降 | 镜头上升、镜头下降 |
| 摇摄 | 镜头左右摇、镜头上下摇 |

### 2.5 时长拆分规则

**规则**：场景时长 > 15秒 必须拆分

**拆分方法**：
1. 按动作节点拆分（人物进入、转身、坐下等）
2. 按视角切换拆分（全景→中景→特写）
3. 按时间跳跃拆分（日→夜、春→秋）

**示例**：
- 原场景：皇帝从入口走到宝座坐下（20秒）
- 拆分：
  - 镜头1：皇帝从入口走向宝座（8秒）
  - 镜头2：皇帝转身坐下（7秒）
  - 镜头3：皇帝抬起头看向远方（5秒）

---

## 二-B、FFmpeg Ken Burns 视频生成（免费）

### 2B.1 基本信息

| 项目 | 值 |
|------|-----|
| 工具 | ffmpeg |
| 用途 | 图片转视频（Ken Burns 效果） |
| 成本 | **免费** |
| 适用场景 | 标题卡、转场、主持人、地图 |

### 2B.2 Ken Burns 效果类型

| 效果类型 | 描述 | 适用场景 |
|---------|------|---------|
| zoom_in | 缓慢推进 | 标题卡、主持人、开场 |
| zoom_out | 缓慢拉远 | 结尾、全景展示 |
| pan_left | 左摇 | 地图、横向展示 |
| pan_right | 右摇 | 地图、横向展示 |
| pan_up | 上摇 | 建筑、人物全身 |
| pan_down | 下摇 | 建筑、从天空到地面 |
| static | 静止（微呼吸） | 聚焦主体 |

### 2B.3 参数规范

```json
{
  "tool": "ffmpeg",
  "effect": "zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down | static",
  "parameters": {
    "input_image": "string (必填，图片路径)",
    "duration": "integer (必填，时长秒数)",
    "zoom_start": "float (可选，起始缩放，默认1.0)",
    "zoom_end": "float (可选，结束缩放，默认1.2)",
    "pan_x_start": "float (可选，起始X位置，默认0.5)",
    "pan_x_end": "float (可选，结束X位置，默认0.5)",
    "pan_y_start": "float (可选，起始Y位置，默认0.5)",
    "pan_y_end": "float (可选，结束Y位置，默认0.5)",
    "fps": "integer (可选，帧率，默认30)",
    "resolution": "1920x1080 (固定)"
  }
}
```

### 2B.4 FFmpeg 命令模板

**推进效果（zoom_in）**：
```bash
ffmpeg -loop 1 -i {input_image} \
  -vf "zoompan=z='min(zoom+0.0005,{zoom_end})':d={duration}*30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080" \
  -t {duration} -c:v libx264 -pix_fmt yuv420p {output_video}
```

**左摇效果（pan_left）**：
```bash
ffmpeg -loop 1 -i {input_image} \
  -vf "zoompan=z='1.2':d={duration}*30:x='iw*(1-{pan_x_end})':y='ih/2-(ih/zoom/2)':s=1920x1080" \
  -t {duration} -c:v libx264 -pix_fmt yuv420p {output_video}
```

**静止微呼吸（static）**：
```bash
ffmpeg -loop 1 -i {input_image} \
  -vf "zoompan=z='1+0.01*sin(on/25)':d={duration}*30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080" \
  -t {duration} -c:v libx264 -pix_fmt yuv420p {output_video}
```

### 2B.5 效果选择指南

| 镜头类型 | 推荐效果 | 参数建议 |
|---------|---------|---------|
| title_card | zoom_in | zoom_end=1.15, duration=6-10 |
| transition | zoom_in 或 static | zoom_end=1.1, duration=5-8 |
| host | zoom_in | zoom_end=1.1, duration=10-15 |
| map | pan_right 或 zoom_in | 根据地图方向选择 |
| historical_scene | **使用 Seedance** | - |

---

## 三、Azure TTS 音频生成

### 3.1 基本信息

| 项目 | 值 |
|------|-----|
| 工具 | azure_tts |
| 用途 | 生成旁白音频 |
| 格式 | SSML |

### 3.2 SSML 规范

**模板**：
```xml
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
  <voice name='{voice_name}'>
    <prosody rate='{rate}' pitch='{pitch}'>
      {text}
    </prosody>
  </voice>
</speak>
```

**示例**：
```xml
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
  <voice name='zh-CN-XiaoxiaoNeural'>
    <prosody rate='0.9' pitch='+0%'>
      大家好！欢迎收听《历史上的今天》节目。今天是2026年2月25日，星期三。
    </prosody>
  </voice>
</speak>
```

### 3.3 参数规范

```json
{
  "tool": "azure_tts",
  "voice": "string",
  "ssml": "string",
  "text": "string"
}
```

**参数约束**：
| 参数 | 允许值 | 说明 |
|------|--------|------|
| voice | zh-CN-XiaoxiaoNeural (女声) | 温柔自然 |
| voice | zh-CN-YunxiNeural (男声) | 沉稳大气 |
| rate | 0.8 - 1.2 | 语速，默认1.0 |
| pitch | -10% ~ +10% | 音调，默认+0% |

### 3.4 语音选择指南

| 场景类型 | 推荐语音 | 语速 | 音调 |
|---------|---------|------|------|
| 开场白 | zh-CN-XiaoxiaoNeural | 0.95 | +0% |
| 历史叙事 | zh-CN-YunxiNeural | 0.9 | -5% |
| 情感高潮 | zh-CN-XiaoxiaoNeural | 0.85 | +5% |
| 结尾语 | zh-CN-XiaoxiaoNeural | 0.9 | +0% |

---

## 四、时长匹配规则

**原则**：音频时长 ≈ 视频时长

**计算方式**：
- 中文语速：约 3-4 字/秒
- 音频时长 = 旁白字数 / 3.5 秒

**示例**：
- 旁白：大家好！欢迎收听《历史上的今天》节目。（17字）
- 预估时长：17 / 3.5 ≈ 5秒
- 视频时长设置：5秒

**匹配策略**：
1. 先计算音频预估时长
2. 视频时长 = 音频预估时长 + 1秒（缓冲）
3. 如果视频时长 > 15秒，拆分镜头

---

## 五、参数校验清单

生成 shot-list.json 后必须校验：

- [ ] 每个镜头 duration ≤ 15
- [ ] 所有 image.parameters.size 为 1920x1080
- [ ] video.tool 为 seedance 或 ffmpeg
- [ ] Seedance: resolution 为 1080p
- [ ] FFmpeg: effect 为有效值
- [ ] 所有 audio.ssml 格式正确
- [ ] 连续镜头有 reference_image
- [ ] 音视频时长匹配

## 六、成本优化建议

### 6.1 镜头类型分配

| 镜头类型 | 视频工具 | 单集数量 | 单集成本 |
|---------|---------|---------|---------|
| title_card | ffmpeg | 2 | 0元 |
| transition | ffmpeg | 4 | 0元 |
| host | ffmpeg | 3 | 0元 |
| historical_scene | seedance | 10-15 | 10-20元 |
| map | ffmpeg | 0-2 | 0元 |
| **合计** | - | 20-25 | **10-20元** |

### 6.2 日更成本控制

对于日更项目（如"历史上的今天"）：

1. **精简历史场景**：选择 3-5 个重点事件，而非全部罗列
2. **复用模板**：标题卡、转场可批量生成复用
3. **会员积分**：即梦会员每日送积分，可大幅降低成本
4. **批量处理**：FFmpeg 镜头可脚本批量生成
