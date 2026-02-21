---
name: history-storyboard-skill
description: 历史故事分镜生成技能。当用户需要将历史剧本、故事梗概或分场大纲转化为可用于 AI 出图的分镜时使用。采用分层渐进式流程：节拍拆解 → Beat Board（九宫格叙事总览）→ Sequence Board（四宫格段落展开），确保人物与环境稳定一致、镜头叙事清晰可读、画面连贯可剪辑，同时注重历史准确性。
---

# 历史故事分镜生成 Skill

[技能说明]
    历史故事分镜生成技能，将历史剧本、故事梗概或分场大纲转化为可用于 AI 出图的分镜提示词。采用分层渐进式流程：先进行节拍拆解识别叙事锚点，再生成 Beat Board 九宫格提示词，最后为每个锚点生成 Sequence Board 四宫格提示词展开段落动作。四宫格生成时以九宫格对应格作为参考图片（垫图），确保人物与场景一致性。特别注重历史准确性，包括服饰、建筑、道具、礼仪等细节。

[文件结构]
    history-storyboard-skill/
    ├── SKILL.md                               # 本文件（技能包核心配置）
    ├── storyboard-methodology-playbook.md     # 分镜方法论（规则与标准）
    └── templates/                             # 模板
        ├── beat-breakdown-template.md         # 节拍拆解表模板
        ├── beat-board-template.md             # 九宫格提示词模板
        └── sequence-board-template.md         # 四宫格提示词模板

[功能]
    [生成节拍拆解表]
        第一步：理解输入
            - 读取用户提供的历史剧本/梗概/分场文本
            - 读取 storyboard-methodology-playbook.md
            - 确认视觉风格（默认：历史写实风格，可被用户覆盖）

        第二步：节拍拆解
            - 识别叙事曲线的关键拐点
            - 读取 templates/beat-breakdown-template.md
            - 创建 beat-breakdown.md，将节拍拆解表写入

    [生成 Beat Board 九宫格提示词]
        第一步：读取上游产物
            - 读取 beat-breakdown.md
            - 读取 storyboard-methodology-playbook.md

        第二步：生成 Beat Board 提示词
            - 读取 templates/beat-board-template.md
            - 将 Beat Anchor 转化为九宫格提示词
            - 提示词采用叙事描述式
            - 特别注重历史准确性描述（服饰、建筑、道具等）
            - 创建 beat-board-prompt.md，将九宫格提示词写入

    [生成 Sequence Board 四宫格提示词]
        第一步：读取上游产物
            - 读取 beat-board-prompt.md
            - 读取 storyboard-methodology-playbook.md

        第二步：生成 Sequence Board 提示词
            - 读取 templates/sequence-board-template.md
            - 为每个 Beat Anchor 生成一组四宫格提示词
            - 必须继承九宫格对应格的人物/场景/光色描述
            - 提示词采用叙事描述式
            - 创建 sequence-board-prompt.md，将四宫格提示词写入

    [修改提示词]
        第一步：理解修改意见
            - 读取原文档（beat-breakdown.md / beat-board-prompt.md / sequence-board-prompt.md）
            - 读取修改意见
            - 读取 storyboard-methodology-playbook.md

        第二步：执行修改
            - 定位需要修改的内容
            - 按修改意见调整，确保符合方法论
            - 更新原文档

[分镜原则]
    - **方法论遵循原则**：
        • storyboard-methodology-playbook.md 全局生效
        • 所有分镜决策必须符合方法论中的规则与验收标准

    - **历史准确性优先原则**：
        • 服饰、建筑、道具必须符合历史时期特征
        • 人物的言行举止必须符合当时的社会礼仪
        • 场景设计必须反映真实的历史地理环境

    - **一致性优先原则**：
        • 四宫格提示词必须继承九宫格对应格的人物/场景/光色描述
        • 发生变化必须显式说明原因

    - **连贯性检查原则**：
        • 参考 storyboard-methodology-playbook 连贯性与剪接相关规则

    - **模板遵循原则**：
        • 提示词必须严格遵循 templates/ 中定义的格式
        • 不能遗漏模板中的必要字段

    - **工程约束原则**：
        • 九宫格用于"选点与定锚"，生成后作为四宫格的参考图片（垫图）
        • 四宫格生成时，使用九宫格对应格作为参考图片输入

[注意事项]
    - storyboard-methodology-playbook.md 是核心方法论，必须严格遵守
    - 历史准确性是本技能的核心特色，必须在提示词中体现
    - 提示词采用叙事描述式（完整段落），而非关键词堆叠式（逗号分隔）
    - templates/ 中的格式是必须遵循的
    - 提示词输出时，直接给可复制的文本块，不要拆成碎片解释
    - 默认视觉风格为历史写实风格，用户可覆盖
    - 四宫格生成时需配合九宫格对应格作为参考图片（垫图）使用