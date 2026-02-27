# 集成测试与验证文档

## 测试目标

验证shot-list-skill v2.1的完整工作流程，确保：
1. 特征库查询正确性
2. Prompt生成流程完整性
3. 一致性检查有效性
4. Prompt优化质量
5. 历史准确性保障

## 测试用例

### 测试用例1：古罗马帝国权力交接

**来源**：`script/事例稿.md` - 事件一

**输入**：
```
【事件一】公元138年2月25日 - 罗马帝国的权力交接
根据维基百科的历史记载，卢基乌斯·埃利乌斯去世以后，罗马皇帝哈德良做出了一个重大的决定——他收养并指定安敦宁·毕尤为帝国的继承人。这一决定标志着罗马帝国权力的平稳过渡，关系到帝国数百万臣民的未来走向。
```

**预期输出**：

#### 阶段1：脚本解析

```json
{
  "era": "古罗马帝国（2世纪）",
  "characters": ["哈德良皇帝", "安敦宁·毕尤"],
  "locations": ["罗马帝国宫殿"],
  "events": ["权力交接", "收养继承人"],
  "emotion_overall": "SOLEMN"
}
```

#### 阶段2：特征库查询

**哈德良皇帝**：
- character_id: `hadrian_138`
- 服饰: `ancient_rome_toga_imperial`
- 建筑: `ancient_rome_imperial_palace`

**验证**：
- [ ] 人物存在且时代匹配
- [ ] 服饰存在且时代匹配
- [ ] 建筑存在且时代匹配

#### 阶段3：Beat Board生成

**格子0**：
- 锚点类型: `PROTAGONIST_STATUS`
- Prompt应包含：哈德良皇帝、紫色镶边托加长袍、大理石柱廊、穹顶
- 景别: 中景
- 光线: 高窗射入的自然光

**验证**：
- [ ] Prompt包含人物、服饰、建筑描述
- [ ] Prompt使用叙事描述式风格
- [ ] Prompt长度 ≤ 200字
- [ ] 历史准确性: 无时代错误

#### 阶段4：Sequence Board生成

**结构**: 起—承—转—合

**镜头1（起）**：
- 模板: 模板2
- 内容: 哈德良皇帝从宫殿深处走来
- 检查: 屏幕方向、动作连续性

**验证**：
- [ ] 使用正确的模板
- [ ] 动作连贯（start→middle→climax→aftermath）
- [ ] 遵守180度轴线规则
- [ ] 无跳接风险

#### 阶段5：一致性检查

```json
{
  "overall_result": "PASS",
  "score": ≥ 90,
  "details": {
    "character_consistency": {"result": "PASS", "score": ≥ 90},
    "scene_consistency": {"result": "PASS", "score": ≥ 90},
    "visual_continuity": {"result": "PASS", "score": ≥ 90},
    "historical_accuracy": {"result": "PASS", "score": ≥ 90}
  }
}
```

#### 阶段6：质量评估

```json
{
  "prompt_quality": {
    "conciseness": ≥ 90,
    "fluency": ≥ 90,
    "professionalism": ≥ 90,
    "accuracy": ≥ 90
  },
  "overall_score": ≥ 90
}
```

### 测试用例2：唐代玄奘取经归来

**来源**：`script/事例稿.md` - 事件三

**输入**：
```
【事件三】公元645年2月25日 - 玄奘西天取经归来
645年2月25日这一天，唐代著名的高僧玄奘携带着梵文佛经657部和各种珍贵的佛像，终于回到了唐帝国的首都长安。
```

**预期输出**：

#### 阶段1：脚本解析

```json
{
  "era": "唐代（7世纪）",
  "characters": ["玄奘高僧"],
  "locations": ["长安城"],
  "events": ["取经归来", "回到长安"],
  "emotion_overall": "HOPEFUL"
}
```

#### 阶段2：特征库查询

**玄奘高僧**：
- character_id: `xuanzang_645`
- 服饰: `tang_dynasty_monk_robe`
- 建筑: `tang_chang_an_city_gate`

**验证**：
- [ ] 人物存在且时代匹配
- [ ] 服饰存在且时代匹配
- [ ] 建筑存在且时代匹配

#### 阶段3：Beat Board生成

**格子0**：
- 锚点类型: `PROTAGONIST_STATUS`
- Prompt应包含：玄奘高僧、赭红色僧袍、长安城门、朱红色城墙
- 景别: 中景
- 光线: 自然阳光

**验证**：
- [ ] Prompt包含人物、服饰、建筑描述
- [ ] Prompt使用叙事描述式风格
- [ ] Prompt长度 ≤ 200字
- [ ] 历史准确性: 无时代错误

### 测试用例3：民国二二八事件

**来源**：特征库中的历史事件

**输入**：
```
1947年2月27日傍晚，台北太平町天马茶房前，专卖局查缉员查缉私烟，打伤女烟贩林江迈，引发民众愤怒，成为二二八事件的导火索。
```

**预期输出**：

#### 阶段1：脚本解析

```json
{
  "era": "民国时期（1947）",
  "characters": ["林江迈", "专卖局查缉员"],
  "locations": ["天马茶房", "专卖局门口"],
  "events": ["查缉私烟", "冲突爆发"],
  "emotion_overall": "TENSE"
}
```

#### 阶段2：特征库查询

**林江迈**：
- character_id: `lin_jiangmai_1947`
- 服饰: `republic_of_china_1947_common`
- 建筑: `republic_of_china_1947_old_street`
- 地点: `taipei_tianma_teahouse_1947`

**验证**：
- [ ] 人物存在且时代匹配
- [ ] 服饰存在且时代匹配
- [ ] 建筑存在且时代匹配
- [ ] 地点存在且时代匹配

#### 阶段3：Beat Board生成

**格子1**：
- 锚点类型: `INCITING_EVENT`
- Prompt应包含：林江迈、打补丁的粗布衣裳、天马茶房、傍晚昏黄灯光
- 景别: 中近景
- 光线: 傍晚昏黄的街灯

**验证**：
- [ ] Prompt包含人物、服饰、建筑描述
- [ ] Prompt使用叙事描述式风格
- [ ] Prompt长度 ≤ 200字
- [ ] 历史准确性: 无时代错误

## 测试检查清单

### 特征库测试

- [ ] 所有10个人物可以正确查询
- [ ] 所有10类服饰可以正确查询
- [ ] 所有7类建筑可以正确查询
- [ ] 所有10个地点可以正确查询
- [ ] `prompt_snippet`字段存在且 ≤ 50字
- [ ] 历史背景信息完整

### Prompt生成测试

- [ ] 脚本解析正确提取时代、人物、地点
- [ ] 节拍拆解正确识别强度和锚点类型
- [ ] Beat Board使用模板1生成
- [ ] Sequence Board使用模板2-5生成
- [ ] Prompt使用叙事描述式风格
- [ ] Prompt长度控制在200字以内

### 一致性检查测试

- [ ] 人物一致性检查生效
- [ ] 场景一致性检查生效
- [ ] 视觉连贯性检查生效
- [ ] 历史准确性检查生效
- [ ] 检查报告格式正确
- [ ] 评分机制正常

### Prompt优化测试

- [ ] 简洁性优化生效（删除冗余）
- [ ] 流畅性优化生效（逻辑连贯）
- [ ] 专业性优化生效（术语准确）
- [ ] 准确性优化生效（历史准确）
- [ ] 优化后的Prompt质量 ≥ 90分

### 历史准确性测试

- [ ] 古罗马（2世纪）: 无时代错误
- [ ] 唐代（7世纪）: 无时代错误
- [ ] 明代（15世纪）: 无时代错误
- [ ] 民国（1947）: 无时代错误
- [ ] 现代（2010）: 无时代错误

## 测试执行步骤

1. **准备测试数据**
   - 读取 `script/事例稿.md`
   - 选择3个不同时代的事件作为测试用例

2. **执行脚本解析**
   - 提取时代、人物、地点、事件
   - 识别整体情绪

3. **执行特征库查询**
   - 查询人物特征
   - 查询服饰特征
   - 查询建筑特征
   - 查询地点特征

4. **执行节拍拆解**
   - 拆解为StoryBeat
   - 识别强度和锚点类型

5. **生成Beat Board**
   - 使用模板1生成Prompt
   - 执行一致性检查
   - 执行Prompt优化

6. **生成Sequence Board**
   - 使用模板2-5生成Prompt
   - 执行连贯性检查
   - 执行Prompt优化

7. **质量评估**
   - 评估Prompt质量（4维度）
   - 评估一致性（4维度）
   - 生成测试报告

## 预期结果

### 成功标准

- [ ] 所有测试用例通过
- [ ] Prompt质量 ≥ 90分
- [ ] 一致性评分 ≥ 90分
- [ ] 无历史错误
- [ ] 无严重问题（issues）
- [ ] 警告数量 ≤ 2个

### 失败标准

- 任何测试用例未通过
- Prompt质量 < 70分
- 一致性评分 < 70分
- 存在历史错误
- 存在严重问题（issues）

## 测试报告格式

```json
{
  "test_timestamp": "2026-02-27T10:30:00Z",
  "test_cases": [
    {
      "case_id": "test_001",
      "name": "古罗马帝国权力交接",
      "status": "PASS",
      "score": 93,
      "results": {
        "script_parsing": {"status": "PASS", "score": 95},
        "feature_query": {"status": "PASS", "score": 95},
        "beat_board": {"status": "PASS", "score": 90},
        "sequence_board": {"status": "PASS", "score": 92},
        "continuity_check": {"status": "PASS", "score": 92},
        "prompt_quality": {"status": "PASS", "score": 93}
      },
      "issues": [],
      "warnings": ["Shot 3-2的光线强度略有变化"]
    }
  ],
  "overall_result": "PASS",
  "overall_score": 92,
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0
}
```

## 测试完成后

- [ ] 生成测试报告
- [ ] 提交测试结果
- [ ] 更新文档
- [ ] 标记todo为completed

## 参考文档

- `core/prompt-generation-rules.md` - Prompt生成流程
- `templates/prompt-templates.md` - Prompt模板库
- `core/continuity-check-rules.md` - 一致性检查规则
- `core/prompt-optimizer-rules.md` - Prompt优化规则
- `libraries/README.md` - 特征库使用指南
- `docs/prompt-generation-example.md` - Prompt生成示例