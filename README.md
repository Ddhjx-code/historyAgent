# History Agent - 历史故事视频生成系统

## 项目简介

History Agent 是一个专门用于将口播稿和历史故事转化为视频分镜的 AI 系统。支持 **Seedance + FFmpeg 混合方案**，大幅降低视频生成成本。

## 核心功能

### 口播稿转分镜（shot-list-skill）

将口播稿转化为可执行的 JSON 分镜清单，输出符合 API 规范的参数：

- **Seedream**：生成关键帧图片
- **Seedance**：历史场景视频生成（~1元/5秒）
- **FFmpeg**：标题卡/转场/主持人镜头（免费）
- **Azure TTS**：旁白音频生成

### 混合方案成本优势

| 镜头类型 | 视频工具 | 成本 |
|---------|---------|------|
| title_card（标题卡） | FFmpeg | 免费 |
| transition（转场） | FFmpeg | 免费 |
| host（主持人） | FFmpeg | 免费 |
| historical_scene（历史场景） | Seedance | ~1元/5秒 |
| map（地图） | FFmpeg | 免费 |

**单集成本估算**：约 10-20 元（10-15 个历史场景镜头）

## 项目结构

```
history/
├── .iflow/                              # 核心配置目录
│   ├── CLAUDE.md                        # 主 Agent 配置（制片人）
│   ├── agents/                          # Agent 配置
│   │   ├── storyboard-artist.md         # 分镜师 Agent
│   │   └── director.md                  # 导演 Agent
│   └── skills/                          # 技能包
│       ├── shot-list-skill/             # 口播稿转分镜技能
│       │   ├── SKILL.md                 # 技能说明
│       │   ├── api-spec.md              # API 规范
│       │   └── templates/
│       │       └── shot-list-template.md
│       ├── history-storyboard-skill/    # 历史故事分镜技能
│       └── storyboard-review-skill/     # 分镜审核技能
├── script/                              # 口播稿/剧本目录
│   └── 事例稿.md                        # 示例口播稿
├── outputs/                             # 生成产物目录
│   └── {episode}/
│       └── shot-list.json               # 分镜执行清单
└── README.md
```

## 使用方法

### 1. 准备口播稿

将口播稿放入 `script/` 目录，使用以下结构：

```markdown
【开场白】
开场内容...

【第一部分】
【事件一】
事件内容...

【结尾语】
结尾内容...
```

### 2. 生成分镜清单

使用命令：

```
/shotlist {集数}
```

流程：
1. 读取口播稿
2. 分镜师生成分镜清单
3. 导演审核质量
4. 输出 shot-list.json

### 3. 执行分镜清单

读取 `shot-list.json`，依次调用 API：

1. **Seedream** - 生成关键帧图片
2. **Seedance/FFmpeg** - 生成视频片段
3. **Azure TTS** - 生成旁白音频

### 4. 视频合成

使用 FFmpeg 或剪辑软件合成最终视频。

## Agent 协作系统

| Agent | 角色 | 职责 |
|-------|------|------|
| 制片人（主 Agent） | 统筹协调 | 调度分镜师和导演，把控整体流程 |
| 分镜师 | storyboard-artist | 解析口播稿，生成分镜清单 |
| 导演 | director | 审核分镜质量，确保符合规范 |

## API 规范

### Seedream 图像生成

```json
{
  "tool": "seedream",
  "model": "doubao-seedream-4.5",
  "parameters": {
    "prompt": "历史纪录片风格，...",
    "size": "1920x1080",
    "n": 1
  }
}
```

### Seedance 视频生成（历史场景）

```json
{
  "tool": "seedance",
  "model": "doubao-seedance-2.0",
  "parameters": {
    "input_image": "shot_001.png",
    "motion_prompt": "镜头缓慢推进...",
    "duration": 10,
    "resolution": "1080p"
  }
}
```

### FFmpeg Ken Burns（免费镜头）

```json
{
  "tool": "ffmpeg",
  "effect": "zoom_in",
  "parameters": {
    "input_image": "shot_001.png",
    "duration": 8,
    "zoom_start": 1.0,
    "zoom_end": 1.15
  }
}
```

### Azure TTS 音频生成

```json
{
  "tool": "azure_tts",
  "voice": "zh-CN-XiaoxiaoNeural",
  "ssml": "<speak>...</speak>",
  "text": "旁白文本"
}
```

## 即梦会员积分

推荐使用即梦会员降低成本：

| 平台 | 每日赠送 | 视频消耗 |
|------|---------|---------|
| 即梦网页版 | 每日登录积分 | 6积分/秒 |
| 小云雀网页版 | 120积分/天 | 10积分/秒 |
| 豆包App | 10次/天 | 免费 |

## 技术栈

- **Agent 框架**：iFlow CLI
- **图像生成**：Seedream (doubao-seedream-4.5)
- **视频生成**：Seedance (doubao-seedance-2.0) / FFmpeg
- **音频生成**：Azure TTS
- **历史考据**：基于权威史料

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/Ddhjx-code/historyAgent
- Issues: https://github.com/Ddhjx-code/historyAgent/issues
