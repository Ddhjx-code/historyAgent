# .iflow 设计方案

## 一、.iflow 目录结构

```
.iflow/
├── CLAUDE.md                          # 主 Agent（制片人）
├── settings.local.json                # 权限配置
│
├── agents/
│   ├── storyboard-artist.md           # 分镜师：生成 shot-list.json
│   └── director.md                    # 导演：审核 shot-list.json
│
└── skills/
    ├── shot-list-skill/               # 口播稿转分镜清单技能
    │   ├── SKILL.md                   # 技能配置
    │   ├── api-spec.md                # API 规范
    │   └── templates/
    │       └── shot-list-template.md  # 输出模板
    │
    ├── storyboard-review-skill/       # 分镜审核技能（现有）
    └── history-storyboard-skill/      # 历史故事分镜技能（现有）
```

---

## 二、Agents

### 2.1 storyboard-artist.md（分镜师）

**职责**：将口播稿转化为分镜执行清单

**输入**：口播稿文本（script/*.md）

**输出**：shot-list.json

**技能**：shot-list-skill

**核心能力**：
- 解析口播稿结构（开场、事件、转场、结尾）
- 按 15 秒上限拆分镜头
- 生成 Seedream 图像提示词
- 生成 Seedance 动态提示词
- 生成 Azure TTS 的 SSML

### 2.2 director.md（导演）

**职责**：审核分镜执行清单的质量

**输入**：shot-list.json

**输出**：PASS / FAIL + 修改意见

**技能**：storyboard-review-skill

**审核项**：
- 镜头时长是否 ≤ 15 秒
- 提示词是否符合 API 规范
- 场景是否有历史考据
- 首尾帧衔接是否合理
- 音视频时长是否匹配

---

## 三、Skills

### 3.1 shot-list-skill/（口播稿转分镜清单）

**用途**：将口播稿转化为可执行的 JSON 分镜清单

**文件结构**：
```
shot-list-skill/
├── SKILL.md                   # 技能配置
├── api-spec.md                # API 规范（Seed + Azure TTS）
└── templates/
    └── shot-list-template.md  # JSON 输出模板
```

**SKILL.md 内容**：
- 技能说明
- 约束条件（时长、分辨率、格式）
- 工作流程
- 分镜规则
- 首尾帧衔接规则

**api-spec.md 内容**：
- Seedream prompt 规范
- Seedance motion_prompt 规范
- Azure TTS SSML 规范
- 参数约束表

**shot-list-template.md 内容**：
- JSON 输出结构模板
- 字段说明

---

## 四、Outputs 输出

### 4.1 输出目录结构

```
outputs/
└── {episode}/
    └── shot-list.json          # 分镜执行清单
```

### 4.2 shot-list.json 结构

```json
{
  "meta": {
    "project_name": "历史上的今天 - 2026年2月25日",
    "episode": "ep01",
    "total_duration": 480,
    "shot_count": 32,
    "created_at": "2026-02-25"
  },
  
  "shots": [
    {
      "shot_id": "shot_001",
      "time_code": "00:00-00:08",
      "duration": 8,
      "type": "title_card",
      "era": null,
      "description": "节目标题卡",
      
      "tasks": {
        "image": {
          "tool": "seedream",
          "model": "doubao-seedream-4.5",
          "parameters": {
            "prompt": "历史纪录片风格...",
            "size": "1920x1080"
          }
        },
        
        "video": {
          "tool": "seedance",
          "model": "doubao-seedance-2.0",
          "input_image": "shot_001.png",
          "parameters": {
            "motion_prompt": "镜头固定...",
            "duration": 8,
            "resolution": "1080p"
          }
        },
        
        "audio": {
          "tool": "azure_tts",
          "voice": "zh-CN-XiaoxiaoNeural",
          "ssml": "<speak>...</speak>",
          "text": "历史上的今天..."
        }
      },
      
      "reference_image": null,
      "status": "pending"
    }
  ]
}
```

### 4.3 字段说明

| 字段 | 说明 |
|------|------|
| `meta` | 项目元信息 |
| `shots[]` | 镜头列表 |
| `shot_id` | 镜头编号 |
| `time_code` | 时间码 |
| `duration` | 时长（秒），≤15 |
| `type` | 镜头类型：title_card / host / historical_scene / transition / map |
| `era` | 历史时期（历史场景必填） |
| `tasks.image` | Seedream 图像生成参数 |
| `tasks.video` | Seedance 视频生成参数 |
| `tasks.audio` | Azure TTS 音频生成参数 |
| `reference_image` | 首帧参考图片（用于一致性控制） |

---

## 五、执行流程

```
用户输入口播稿
       ↓
  /shotlist 命令
       ↓
 storyboard-artist
  (shot-list-skill)
       ↓
 shot-list.json
       ↓
    director 审核
       ↓
   PASS → 交付
   FAIL → 修改 → 重审
```

---

## 六、文件修改清单

| 操作 | 文件 | 内容 |
|------|------|------|
| 新增 | `.iflow/skills/shot-list-skill/SKILL.md` | 技能配置 |
| 新增 | `.iflow/skills/shot-list-skill/api-spec.md` | API 规范 |
| 新增 | `.iflow/skills/shot-list-skill/templates/shot-list-template.md` | 输出模板 |
| 修改 | `.iflow/agents/storyboard-artist.md` | 新增 shot-list-skill，支持 JSON 输出 |
| 修改 | `.iflow/agents/director.md` | 新增 shot-list 审核项 |
| 修改 | `.iflow/CLAUDE.md` | 新增 /shotlist 命令流程 |
| 删除 | `.iflow/agents/animator.md` | 功能合并到 storyboard-artist |
| 删除 | `.iflow/skills/animator-skill/` | 功能合并到 shot-list-skill |
