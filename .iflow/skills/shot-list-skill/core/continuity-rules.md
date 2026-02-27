# 连贯性规则

## 概述

本文档定义了如何确保镜头序列的视觉连贯性，特别是人物和场景的一致性，使视频看起来流畅自然。

## 核心原则

1. **人物一致性**：同一人物在不同镜头中保持相同的外观特征
2. **场景一致性**：同一场景在不同镜头中保持相同的环境特征
3. **光线一致性**：同一场景的光线方向、时间、天气保持一致
4. **动作连贯性**：动作在不同镜头中自然衔接

---

## 人物一致性

### 1. 人物标识（character_id）

**目的**：为同一人物分配唯一标识符，确保跨镜头一致

**生成规则**：
```
character_id = "{人物名称}_{年份}"
```

**示例**：
- 哈德良皇帝（公元138年）→ `hadrian_138`
- 玄奘高僧（公元645年）→ `xuanzang_645`
- 毛宁发言人（2026年）→ `maoning_2026`

**应用场景**：
- 当同一个人物出现在多个镜头中时，使用相同的 character_id
- 不同的人物使用不同的 character_id

### 2. 人物引用链（reference_image）

**目的**：使用参考图片保持人物外观的一致性

**建立规则**：
1. **第一个镜头**：reference_image = null
2. **后续镜头**：reference_image = "前置镜头的图像路径"

**示例**：
```json
{
  "shot_001": {
    "shot_id": "shot_001",
    "character_id": "hadrian_138",
    "reference_image": null,
    "tasks": {
      "image": {
        "parameters": {
          "prompt": "...",
          "reference_image": null
        }
      }
    }
  },
  "shot_002": {
    "shot_id": "shot_002",
    "character_id": "hadrian_138",
    "reference_image": "shot_001.png",
    "tasks": {
      "image": {
        "parameters": {
          "prompt": "...",
          "reference_image": "shot_001.png"
        }
      }
    }
  },
  "shot_003": {
    "shot_id": "shot_003",
    "character_id": "hadrian_138",
    "reference_image": "shot_002.png",
    "tasks": {
      "image": {
        "parameters": {
          "prompt": "...",
          "reference_image": "shot_002.png"
        }
      }
    }
  }
}
```

### 3. 随机种子（seed）

**目的**：使用相同的 seed 确保人物外观的可复现性

**生成规则**：
```
seed = hash(character_id) % 2147483647
```

**应用场景**：
- 同一个人物的第一个镜头设置 seed
- 后续镜头使用 reference_image，seed 可以为空

---

## 场景一致性

### 1. 场景引用链

**目的**：保持同一场景的环境特征一致

**建立规则**：
- 同一地点出现在多个镜头中时，使用 reference_image 传递场景特征
- 首个镜头 reference_image = null
- 后续镜头 reference_image = "前置镜头的图像路径"

**示例**：
```json
{
  "shot_005": {
    "shot_id": "shot_005",
    "description": "罗马帝国宫殿外观",
    "reference_image": null
  },
  "shot_006": {
    "shot_id": "shot_006",
    "description": "罗马帝国宫殿内部",
    "reference_image": "shot_005.png"
  }
}
```

### 2. 场景元素保持

**目的**：确保同一场景的关键元素保持一致

**保持元素**：
- 建筑风格（柱式、屋顶、材质）
- 环境色调（冷色/暖色，鲜艳/素雅）
- 光线条件（光源方向、时间、天气）
- 道具和装饰

**实现方法**：
- 使用 reference_image 传递整体风格
- 在 prompt 中描述相同的环境元素
- 保持相似的光影描述

---

## 动作连贯性

### 1. 动作分解

**目的**：将复杂的动作分解为多个镜头，每个镜头展示动作的不同阶段

**分解模式**：
- 起（Start）：动作开始
- 承（Middle）：动作进行中
- 转（Climax）：动作高潮
- 合（Aftermath）：动作余势

**示例**：
```json
{
  "shot_010": {
    "description": "玄奘高僧到达长安城门",
    "action_stage": "start"
  },
  "shot_011": {
    "description": "玄奘高僧穿过城门进入城内",
    "action_stage": "middle"
  },
  "shot_012": {
    "description": "玄奘高僧到达大慈恩寺",
    "action_stage": "climax"
  }
}
```

### 2. 屏幕方向连续

**目的**：避免跳接，确保观众不迷失方向

**原则**：
- 人物的运动方向保持一致
- 视线方向保持一致
- 遵守 180 度轴线规则

**示例**：
```
shot_010: 人物从左向右移动
shot_011: 人物继续从左向右移动 ✓
shot_012: 人物从右向左移动 ✗（违反方向连续性）
```

---

## 连贯性处理流程

### 输入
```json
{
  "shots": [
    {
      "shot_id": "shot_001",
      "type": "content_scene",
      "content": "哈德良皇帝坐在宝座上...",
      "time_info": {"era": "公元138年"},
      "character": {"name": "哈德良", "identity": "皇帝"}
    },
    {
      "shot_id": "shot_002",
      "type": "content_scene",
      "content": "哈德良皇帝做出决定...",
      "time_info": {"era": "公元138年"},
      "character": {"name": "哈德良", "identity": "皇帝"}
    }
  ]
}
```

### 处理步骤

1. **识别同一人物**：
   - 比较人物名称和年份
   - 如果相同，分配相同的 character_id

2. **建立引用链**：
   - 第一个镜头：reference_image = null
   - 后续镜头：reference_image = "前置镜头.png"

3. **设置 seed**：
   - 第一个镜头：seed = hash(character_id)
   - 后续镜头：seed = null（使用 reference_image）

4. **保持场景一致**：
   - 识别同一地点的镜头
   - 使用 reference_image 传递场景特征

### 输出
```json
{
  "shots": [
    {
      "shot_id": "shot_001",
      "character_id": "hadrian_138",
      "reference_image": null,
      "tasks": {
        "image": {
          "parameters": {
            "seed": 1380225,
            "reference_image": null
          }
        }
      }
    },
    {
      "shot_id": "shot_002",
      "character_id": "hadrian_138",
      "reference_image": "shot_001.png",
      "tasks": {
        "image": {
          "parameters": {
            "seed": null,
            "reference_image": "shot_001.png"
          }
        }
      }
    }
  ]
}
```

---

## 连贯性检查清单

生成 shot-list.json 后，进行以下检查：

### 人物一致性
- [ ] 同一人物使用相同的 character_id
- [ ] 连续镜头有 reference_image 引用
- [ ] 人物的 seed 设置正确

### 场景一致性
- [ ] 同一场景的镜头有 reference_image 引用
- [ ] 场景的环境描述保持一致
- [ ] 光线、色调描述保持一致

### 动作连贯性
- [ ] 动作分解合理（起-承-转-合）
- [ ] 屏幕方向连续
- [ ] 无跳接风险

---

## 常见问题

### Q1：如何处理跨时代的人物？

A：使用不同的 character_id，因为不同时代的人物外观可能不同。

**示例**：
- 唐太宗（公元626年）→ `taizong_626`
- 唐太宗（公元645年）→ `taizong_645`（如果年龄变化明显）

### Q2：如何处理群像场景？

A：选择主要人物作为 character_id，其他人物在 prompt 中描述。

### Q3：reference_image 不起作用怎么办？

A：确保：
1. reference_image 的路径正确
2. 前置镜头已经生成
3. reference_image 指向的是同一场景或同一人物

### Q4：如何处理镜头序列不连续的情况？

A：如果中间插入了转场镜头，reference_image 可以跳过转场镜头，直接引用同一人物的最后一个内容镜头。

---

## 示例

### 场景：玄奘取经

**镜头序列**：
1. shot_010: 玄奘到达长安城门（start）
2. shot_011: 玄奘穿过城门（middle）
3. shot_012: 玄奘到达大慈恩寺（climax）
4. shot_013: 玄奘在寺内讲经（aftermath）

**连贯性处理**：
```json
{
  "shot_010": {
    "shot_id": "shot_010",
    "character_id": "xuanzang_645",
    "reference_image": null,
    "seed": 6450225,
    "action_stage": "start"
  },
  "shot_011": {
    "shot_id": "shot_011",
    "character_id": "xuanzang_645",
    "reference_image": "shot_010.png",
    "action_stage": "middle"
  },
  "shot_012": {
    "shot_id": "shot_012",
    "character_id": "xuanzang_645",
    "reference_image": "shot_011.png",
    "action_stage": "climax"
  },
  "shot_013": {
    "shot_id": "shot_013",
    "character_id": "xuanzang_645",
    "reference_image": "shot_012.png",
    "action_stage": "aftermath"
  }
}
```

---

## 后续处理

连贯性处理结果将用于：
- 阶段6：参数生成（作为图像任务的 reference_image 和 seed 参数）
- 视频生成：确保生成的视频人物和场景连贯