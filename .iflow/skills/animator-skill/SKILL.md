---
name: animator-skill
description: 动画师技能。用于将静态分镜（Beat Board 九宫格 + Sequence Board 四宫格）转化为图生视频的动态提示词（Motion Prompt）。每组包含 5 个 Motion Prompt（1 关键帧 + 4 四宫格），共 9 组 45 个。
---

# 动画师技能

[技能说明]
    动画师技能，用于将静态分镜转化为图生视频的动态提示词。基于 motion-prompt-methodology.md 中的方法论，为每个关键帧和四宫格展开生成简洁、具体、可执行的 Motion Prompt。每组包含 5 个 Motion Prompt（1 关键帧 + 4 四宫格），共 9 组 45 个。

[文件结构]
    animator-skill/
    ├── SKILL.md                           # 本文件（技能包核心配置）
    ├── motion-prompt-methodology.md       # 动态提示词方法论（规则与标准）
    └── templates/
        └── motion-prompt-template.md      # 动态提示词模板

[功能]
    [生成动态提示词]
        第一步：读取上游产物
            - 读取 beat-breakdown.md（节拍拆解，理解叙事目的与情绪）
            - 读取 beat-board-prompt.md（九宫格提示词）
            - 读取 sequence-board-prompt.md（四宫格提示词）
            - 读取 motion-prompt-methodology.md（重点参考 [从分镜到动态提示词的转化]）

        第二步：生成动态提示词
            - 读取 templates/motion-prompt-template.md
            - 为每个 Beat Anchor 生成一组 Motion Prompt：
                • 1 个关键帧动态提示词（对应九宫格该格）
                • 4 个四宫格动态提示词（对应四宫格展开）
            - 按照方法论中的 [从分镜到动态提示词的转化] 执行
            - 创建 motion-prompt.md，按模板格式写入

    [修改动态提示词]
        第一步：理解修改意见
            - 读取原 motion-prompt.md
            - 读取修改意见
            - 读取 motion-prompt-methodology.md

        第二步：执行修改
            - 定位需要修改的格
            - 按修改意见调整，确保符合方法论
            - 更新原文档

[动态提示词原则]
    - **方法论遵循原则**：
        • motion-prompt-methodology.md 全局生效
        • 所有动态提示词必须符合方法论中的规则与验收标准

    - **上下文继承原则**：
        • 动态提示词必须基于分镜的叙事目的与情绪（来自 beat-breakdown.md）
        • 动作设计必须与分镜画面内容匹配

    - **模板遵循原则**：
        • 必须严格遵循 templates/motion-prompt-template.md 格式
        • 每组 5 个（1 关键帧 + 4 四宫格），共 9 组

[注意事项]
    - motion-prompt-methodology.md 是核心方法论，必须严格遵守
    - templates/ 中的格式是必须遵循的
    - 提示词输出时，直接给可复制的文本块，不要拆成碎片解释