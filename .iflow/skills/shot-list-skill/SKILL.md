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

[文件结构]
shot-list-skill/
├── SKILL.md                   # 本文件
├── api-spec.md                # API 规范
└── templates/
    └── shot-list-template.md  # 输出模板

## 混合方案（成本优化）

采用 **Seedance + FFmpeg** 混合方案降低成本：

| 镜头类型 | 视频工具 | 成本 | 效果 |
|---------|---------|------|------|
| title_card | ffmpeg | 免费 | Ken Burns 推进 |
| transition | ffmpeg | 免费 | Ken Burns 推进 |
| host | ffmpeg | 免费 | 缓慢推进/摇摄 |
| historical_scene | seedance | ~1元/5秒 | AI 生成动态 |
| map | ffmpeg | 免费 | 缩放/平移 |

**成本估算**：每集约 10-15 个历史场景镜头，成本 10-20 元。

[工作流程]
1. 解析口播稿 → 提取场景、时间轴、旁白
2. 场景分镜 → 按 ≤15s 拆分为镜头
3. 分配视频工具 → 根据镜头类型选择 FFmpeg/Seedance
4. 生成图像提示词 → 符合 Seedream 规范
5. 生成动态参数 → FFmpeg 效果或 Seedance 提示词
6. 生成 SSML → 符合 Azure TTS 规范
7. 输出 shot-list.json

[口播稿解析规则]

识别结构元素：
- 【开场白】→ 开场镜头（主持人/标题卡）
- 【第X部分】→ 分隔转场
- 【事件X】→ 历史场景镜头
- 【结尾语】→ 结尾镜头

提取关键信息：
- 时间标记（如：公元138年）
- 人物（如：哈德良皇帝、荆轲）
- 地点（如：咸阳宫、易水河畔）
- 旁白文本 → 用于 TTS

[分镜规则]

镜头类型与时长：
| 类型 | 时长范围 | 视频工具 | 说明 |
|------|---------|---------|------|
| title_card | 5-10秒 | ffmpeg | 节目标题卡 |
| host | 8-15秒 | ffmpeg | 主持人/口播镜头 |
| historical_scene | 5-15秒 | seedance | 历史场景重现 |
| transition | 3-8秒 | ffmpeg | 转场动画 |
| map | 5-10秒 | ffmpeg | 地图/信息图 |

视频工具选择规则：
1. **默认使用 FFmpeg**：标题卡、转场、主持人、地图
2. **使用 Seedance**：历史场景（需要人物动作、场景变化）
3. **判断依据**：
   - 需要人物动作（走动、说话、转身）→ Seedance
   - 需要场景动态（云动、水波、火光）→ Seedance
   - 静态画面 + 简单动效 → FFmpeg

时长拆分规则：
- 场景时长 > 15秒 → 拆分为多个镜头
- 每个镜头 ≤ 15秒
- 拆分点选择：动作变化、视角切换、时间跳跃

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

[输出规范]

输出文件：outputs/{episode}/shot-list.json

输出格式：参考 templates/shot-list-template.md

[FFmpeg 效果选择]

| 镜头类型 | 推荐效果 | 参数建议 |
|---------|---------|---------|
| title_card | zoom_in | zoom_end=1.15 |
| transition | zoom_in | zoom_end=1.1 |
| host | zoom_in | zoom_end=1.08 |
| map | pan_right 或 zoom_in | 根据地图方向 |

[注意事项]
- 严格按照 api-spec.md 中的规范生成提示词
- 确保每个镜头时长 ≤ 15秒
- 连续镜头必须指定 reference_image
- 旁白文本必须生成对应的 SSML
- 历史场景必须使用 Seedance（需动态效果）
- 其他类型镜头使用 FFmpeg（节省成本）
- 在 meta 中添加 cost_estimate 预估成本
