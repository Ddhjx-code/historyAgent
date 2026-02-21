---
name: storyboard-review-skill
description: 分镜审核技能。用于审核分镜师和动画师的产出，确保符合方法论标准和历史准确性。
---

# 分镜审核技能

[技能说明]
    分镜审核技能，用于审核分镜师和动画师的产出，确保符合方法论标准和历史准确性。基于 storyboard-methodology-playbook.md 和 motion-prompt-methodology.md 中的方法论，对所有生成的提示词进行质量审核。

[文件结构]
    storyboard-review-skill/
    ├── SKILL.md                           # 本文件（技能包核心配置）
    └── [审核方法论文件引用]

[功能]
    [审核节拍拆解表]
        第一步：读取产物
            - 读取 beat-breakdown.md
            - 读取 storyboard-methodology-playbook.md

        第二步：执行审核
            - 检查节拍识别是否准确
            - 检查叙事目的是否清晰
            - 检查历史背景是否准确
            - 检查是否符合方法论规则

        第三步：输出结果
            - PASS：简要说明通过原因
            - FAIL：明确指出问题位置、违反规则、修改方向

    [审核 Beat Board 九宫格提示词]
        第一步：读取产物
            - 读取 beat-board-prompt.md
            - 读取 beat-breakdown.md
            - 读取 storyboard-methodology-playbook.md

        第二步：执行审核
            - 检查九宫格布局是否合理
            - 检查历史细节是否准确
            - 检查视觉描述是否清晰
            - 检查是否符合方法论规则

        第三步：输出结果
            - PASS：简要说明通过原因
            - FAIL：明确指出问题位置、违反规则、修改方向

    [审核 Sequence Board 四宫格提示词]
        第一步：读取产物
            - 读取 sequence-board-prompt.md
            - 读取 beat-board-prompt.md
            - 读取 storyboard-methodology-playbook.md

        第二步：执行审核
            - 检查继承性是否保持
            - 检查连贯性是否合理
            - 检查历史细节是否准确
            - 检查是否符合方法论规则

        第三步：输出结果
            - PASS：简要说明通过原因
            - FAIL：明确指出问题位置、违反规则、修改方向

    [审核动态提示词]
        第一步：读取产物
            - 读取 motion-prompt.md
            - 读取 beat-breakdown.md
            - 读取 beat-board-prompt.md
            - 读取 sequence-board-prompt.md
            - 读取 motion-prompt-methodology.md

        第二步：执行审核
            - 检查继承性是否保持
            - 检查镜头运动是否合理
            - 检查动作描述是否真实
            - 检查是否符合方法论规则

        第三步：输出结果
            - PASS：简要说明通过原因
            - FAIL：明确指出问题位置、违反规则、修改方向

[审核原则]
    - **方法论遵循原则**：
        • storyboard-methodology-playbook.md 全局生效
        • motion-prompt-methodology.md 全局生效
        • 所有审核决策必须符合方法论中的规则与验收标准

    - **历史准确性优先原则**：
        • 服饰、建筑、道具必须符合历史时期特征
        • 人物的言行举止必须符合当时的社会礼仪
        • 场景设计必须反映真实的历史地理环境

    - **视觉叙事清晰原则**：
        • 每个镜头都应该有明确的叙事目的
        • 画面应该清晰易懂
        • 避免过于抽象或难以理解的视觉表达

    - **一致性检查原则**：
        • 人物特征必须保持一致
        • 场景特征必须保持一致
        • 光影效果必须保持连贯

    - **连贯性检查原则**：
        • 相邻镜头之间必须有合理的视觉衔接
        • 镜头运动必须符合观众的视觉预期
        • 剪辑点选择必须符合叙事节奏

[注意事项]
    - storyboard-methodology-playbook.md 和 motion-prompt-methodology.md 是核心方法论，必须严格遵守
    - 审核时要特别关注历史准确性
    - 输出时要明确指出问题所在
    - FAIL 时要提供具体的修改方向