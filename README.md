# History Agent - 历史故事视频生成系统

## 项目简介

History Agent 是一个专门用于将历史故事转化为视频的 AI 系统。它通过生成详细的视觉和动态提示词，帮助用户制作历史题材的短视频。

## 项目结构

```
history/
├── .iflow/                          # 核心配置目录
│   ├── CLAUDE.md                    # 主 Agent 配置（制片人）
│   ├── settings.local.json          # 权限配置
│   ├── agents/                      # Agent 配置
│   │   ├── storyboard-artist.md     # 分镜师 Agent
│   │   ├── director.md              # 导演 Agent
│   │   └── animator.md              # 动画师 Agent
│   └── skills/                      # 技能包
│       ├── history-storyboard-skill/   # 历史故事分镜生成技能
│       ├── animator-skill/             # 动画师技能
│       └── storyboard-review-skill/    # 分镜审核技能
├── script/                          # 剧本目录
│   └── 第一章-荆轲刺秦王.md
├── outputs/                         # 生成产物目录
│   ├── beat-breakdown-ep01.md       # 节拍拆解表
│   ├── beat-board-prompt-ep01.md    # 九宫格提示词
│   ├── sequence-board-prompt-ep01.md # 四宫格提示词
│   └── motion-prompt-ep01.md        # 动态提示词
└── README.md                        # 项目说明文档
```

## 功能特点

### 1. 历史准确性优先
- 服饰、建筑、道具符合历史时期特征
- 人物的言行举止符合当时的社会礼仪
- 场景设计反映真实的历史地理环境

### 2. 完整的工作流程
- **节拍拆解**：识别叙事曲线的关键拐点
- **九宫格提示词**：生成 9 个关键画面
- **四宫格提示词**：每个关键画面展开为 4 个序列帧
- **动态提示词**：生成 30 个详细的动态场景描述

### 3. Agent 协作系统
- **制片人**：协调工作流程，把控质量
- **分镜师**：生成静态分镜提示词
- **导演**：审核所有产出，确保质量
- **动画师**：生成动态提示词

## 使用方法

### 准备工作

1. 将历史故事文本放入 `script/` 目录
2. 文件命名建议带集数标识，如 `ep01-故事名.md`

### 生成提示词

按照以下顺序执行：

```
1. 节拍拆解 → 生成 outputs/beat-breakdown-ep01.md
2. 九宫格提示词 → 生成 outputs/beat-board-prompt-ep01.md
3. 四宫格提示词 → 生成 outputs/sequence-board-prompt-ep01.md
4. 动态提示词 → 生成 outputs/motion-prompt-ep01.md
```

### 使用提示词生成视频

#### 推荐的 AI 视频生成工具：
- **Runway Gen-2/Gen-3**（runwayml.com）
- **Pika Labs**（pika.art）
- **Kling AI**（可灵）
- **Luma Dream Machine**

#### 完整制作流程：

1. **生成关键帧图片**
   - 使用 Midjourney、DALL-E、Stable Diffusion
   - 根据 `beat-board-prompt-ep01.md` 生成 9 个关键画面
   - 作为视频生成的参考（垫图）

2. **生成视频片段**
   - 使用 AI 视频生成工具
   - 根据 `motion-prompt-ep01.md` 生成 30 个场景
   - 使用关键帧图片作为参考，确保一致性

3. **视频剪辑**
   - 使用 Premiere、Final Cut、剪映等工具
   - 拼接 30 个场景
   - 添加转场效果
   - 同步音频

4. **音频制作**
   - 使用 TTS 工具（Azure TTS、ElevenLabs）生成旁白
   - 根据 `sequence-board-prompt-ep01.md` 中的字幕内容
   - 添加背景音乐

5. **最终导出**
   - 导出为 MP4 格式
   - 确保音视频同步

## 示例：荆轲刺秦王

项目包含完整的示例故事《荆轲刺秦王》：

- **脚本**：`script/第一章-荆轲刺秦王.md`
- **时长**：约 3 分钟
- **场景数**：30 个动态场景
- **特点**：注重历史准确性，从易水送别到刺秦失败的完整叙事

## 项目优势

1. **历史专业性**：专门针对历史故事设计，注重历史准确性
2. **系统性**：完整的从故事到视频的工作流程
3. **可扩展**：支持多集故事，模块化设计
4. **AI 驱动**：充分利用 AI 视频生成技术

## 技术栈

- **核心系统**：Agent 协作系统
- **提示词生成**：分层渐进式方法论
- **视频生成**：兼容主流 AI 视频生成工具
- **历史考证**：基于《史记》等权威史料

## 贡献指南

欢迎提交历史故事脚本和改进建议！

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/Ddhjx-code/historyAgent
- Issues: https://github.com/Ddhjx-code/historyAgent/issues

---

**让历史故事通过 AI 视频生动呈现！**