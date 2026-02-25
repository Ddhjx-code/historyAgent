# API 规范

本文档定义 Seedream、Seedance、FFmpeg、Azure TTS 四个工具的 API 规范。

---

## 〇、混合方案总览

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
    "reference_image": "string (可选，参考图片路径)"
  }
}
```

**参数约束**：
| 参数 | 允许值 | 默认值 |
|------|--------|--------|
| size | 1920x1080, 1080x1920, 1024x1024 | 1920x1080 |
| n | 1 | 1 |
| reference_image | 文件路径或URL | null |

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
  "parameters": {
    "input_image": "string (必填，首帧图片路径)",
    "motion_prompt": "string (必填，动态描述)",
    "duration": "integer (1-15)",
    "resolution": "480p | 720p | 1080p",
    "aspect_ratio": "16:9 | 9:16 | 1:1"
  }
}
```

**参数约束**：
| 参数 | 允许值 | 默认值 |
|------|--------|--------|
| duration | 1-15 | 5 |
| resolution | 480p, 720p, 1080p | 1080p |
| aspect_ratio | 16:9, 9:16, 1:1 | 16:9 |

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
