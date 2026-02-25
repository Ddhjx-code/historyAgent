---
name: shot-list-template
description: 分镜执行清单 JSON 输出模板（混合方案：Seedance + FFmpeg）
---

# shot-list.json 输出模板

## 混合方案说明

本模板支持 **Seedance + FFmpeg** 混合方案：

| 镜头类型 | 视频工具 | 成本 |
|---------|---------|------|
| title_card | ffmpeg | 免费 |
| transition | ffmpeg | 免费 |
| host | ffmpeg | 免费 |
| historical_scene | seedance | ~1元/5秒 |
| map | ffmpeg | 免费 |

```json
{
  "meta": {
    "project_name": "{项目名称}",
    "episode": "{集数}",
    "total_duration": {总时长秒数},
    "shot_count": {镜头数量},
    "created_at": "{创建日期}",
    "cost_estimate": {
      "seedance_shots": {Seedance镜头数},
      "ffmpeg_shots": {FFmpeg镜头数},
      "estimated_cost_yuan": {预估成本元}
    }
  },
  
  "shots": [
    {
      "shot_id": "shot_001",
      "time_code": "00:00-00:06",
      "duration": 6,
      "type": "title_card",
      "era": null,
      "description": "节目标题卡",
      
      "tasks": {
        "image": {
          "tool": "seedream",
          "model": "doubao-seedream-4.5",
          "parameters": {
            "prompt": "{Seedream图像提示词}",
            "size": "1920x1080",
            "n": 1,
            "reference_image": null
          }
        },
        
        "video": {
          "tool": "ffmpeg",
          "effect": "zoom_in",
          "parameters": {
            "input_image": "shot_001.png",
            "duration": 6,
            "zoom_start": 1.0,
            "zoom_end": 1.15,
            "fps": 30,
            "resolution": "1920x1080"
          }
        },
        
        "audio": {
          "tool": "azure_tts",
          "voice": "zh-CN-XiaoxiaoNeural",
          "ssml": "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-XiaoxiaoNeural'><prosody rate='0.95'>{旁白文本}</prosody></voice></speak>",
          "text": "{旁白文本}"
        }
      },
      
      "reference_image": null,
      "status": "pending"
    },
    
    {
      "shot_id": "shot_002",
      "time_code": "00:06-00:16",
      "duration": 10,
      "type": "host",
      "era": null,
      "description": "主持人开场白",
      
      "tasks": {
        "image": {
          "tool": "seedream",
          "model": "doubao-seedream-4.5",
          "parameters": {
            "prompt": "{主持人画面提示词}",
            "size": "1920x1080",
            "n": 1,
            "reference_image": null
          }
        },
        
        "video": {
          "tool": "ffmpeg",
          "effect": "zoom_in",
          "parameters": {
            "input_image": "shot_002.png",
            "duration": 10,
            "zoom_start": 1.0,
            "zoom_end": 1.08,
            "fps": 30,
            "resolution": "1920x1080"
          }
        },
        
        "audio": {
          "tool": "azure_tts",
          "voice": "zh-CN-XiaoxiaoNeural",
          "ssml": "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-XiaoxiaoNeural'><prosody rate='0.95'>{旁白文本}</prosody></voice></speak>",
          "text": "{旁白文本}"
        }
      },
      
      "reference_image": null,
      "status": "pending"
    },
    
    {
      "shot_id": "shot_003",
      "time_code": "00:16-00:24",
      "duration": 8,
      "type": "transition",
      "era": null,
      "description": "章节转场",
      
      "tasks": {
        "image": {
          "tool": "seedream",
          "model": "doubao-seedream-4.5",
          "parameters": {
            "prompt": "{转场画面提示词}",
            "size": "1920x1080",
            "n": 1,
            "reference_image": null
          }
        },
        
        "video": {
          "tool": "ffmpeg",
          "effect": "zoom_in",
          "parameters": {
            "input_image": "shot_003.png",
            "duration": 8,
            "zoom_start": 1.0,
            "zoom_end": 1.1,
            "fps": 30,
            "resolution": "1920x1080"
          }
        },
        
        "audio": {
          "tool": "azure_tts",
          "voice": "zh-CN-YunxiNeural",
          "ssml": "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-YunxiNeural'><prosody rate='0.9' pitch='-5%'>{旁白文本}</prosody></voice></speak>",
          "text": "{旁白文本}"
        }
      },
      
      "reference_image": null,
      "status": "pending"
    },
    
    {
      "shot_id": "shot_004",
      "time_code": "00:24-00:36",
      "duration": 12,
      "type": "historical_scene",
      "era": "公元138年",
      "description": "古罗马哈德良皇帝",
      
      "tasks": {
        "image": {
          "tool": "seedream",
          "model": "doubao-seedream-4.5",
          "parameters": {
            "prompt": "历史纪录片风格，古罗马帝国宫廷，公元138年。哈德良皇帝身着紫色镶边托加长袍，头戴橄榄枝冠冕，面容威严而苍老，坐在大理石宝座上。宫廷内罗马柱林立，马赛克地板，墙上挂着罗马鹰旗。温暖的地中海阳光从高窗射入，形成戏剧性光影。电影质感，历史写实风格，16:9横屏，庄严肃穆。",
            "size": "1920x1080",
            "n": 1,
            "reference_image": null
          }
        },
        
        "video": {
          "tool": "seedance",
          "model": "doubao-seedance-2.0",
          "parameters": {
            "input_image": "shot_004.png",
            "motion_prompt": "镜头缓慢推进，从宫廷入口移动到皇帝身边，时长12秒。皇帝缓缓抬起头，目光深邃。阳光在宫殿内缓慢移动，照亮他的脸庞。尘埃在光柱中缓缓飘动。节奏庄重缓慢，营造历史厚重感。",
            "duration": 12,
            "resolution": "1080p",
            "aspect_ratio": "16:9"
          }
        },
        
        "audio": {
          "tool": "azure_tts",
          "voice": "zh-CN-YunxiNeural",
          "ssml": "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-YunxiNeural'><prosody rate='0.9' pitch='-5%'>我们首先把目光投向古罗马帝国。在公元138年的这一天，发生了一件关系到帝国未来的大事。</prosody></voice></speak>",
          "text": "我们首先把目光投向古罗马帝国。在公元138年的这一天，发生了一件关系到帝国未来的大事。"
        }
      },
      
      "reference_image": null,
      "status": "pending"
    }
  ]
}
```

---

## 字段说明

### meta 元信息

| 字段 | 类型 | 说明 |
|------|------|------|
| project_name | string | 项目名称 |
| episode | string | 集数标识（ep01） |
| total_duration | integer | 总时长（秒） |
| shot_count | integer | 镜头数量 |
| created_at | string | 创建日期 |
| cost_estimate | object | 成本预估 |

### shots 镜头列表

| 字段 | 类型 | 说明 |
|------|------|------|
| shot_id | string | 镜头编号（shot_001） |
| time_code | string | 时间码（00:00-00:08） |
| duration | integer | 时长（秒），**必须 ≤ 15** |
| type | string | 镜头类型 |
| era | string/null | 历史时期（历史场景必填） |
| description | string | 镜头描述 |
| tasks | object | 执行任务 |
| reference_image | string/null | 参考图片路径 |
| status | string | 状态：pending / completed / failed |

### type 镜头类型与视频工具映射

| 类型 | 说明 | 视频工具 | 典型时长 |
|------|------|---------|---------|
| title_card | 标题卡 | **ffmpeg** | 5-10秒 |
| host | 主持人/口播 | **ffmpeg** | 8-15秒 |
| historical_scene | 历史场景 | **seedance** | 5-15秒 |
| transition | 转场动画 | **ffmpeg** | 3-8秒 |
| map | 地图/信息图 | **ffmpeg** | 5-10秒 |

### tasks 执行任务

#### tasks.image

| 字段 | 类型 | 说明 |
|------|------|------|
| tool | string | 固定值：seedream |
| model | string | 模型：doubao-seedream-4.5 |
| parameters.prompt | string | 图像提示词 |
| parameters.size | string | 分辨率：1920x1080 |
| parameters.n | integer | 固定值：1 |
| parameters.reference_image | string/null | 参考图片 |

#### tasks.video (FFmpeg)

| 字段 | 类型 | 说明 |
|------|------|------|
| tool | string | 固定值：ffmpeg |
| effect | string | 效果：zoom_in / zoom_out / pan_left / pan_right / static |
| parameters.input_image | string | 图片路径 |
| parameters.duration | integer | 时长（秒） |
| parameters.zoom_start | float | 起始缩放（默认1.0） |
| parameters.zoom_end | float | 结束缩放（默认1.2） |
| parameters.fps | integer | 帧率（默认30） |
| parameters.resolution | string | 分辨率：1920x1080 |

#### tasks.video (Seedance)

| 字段 | 类型 | 说明 |
|------|------|------|
| tool | string | 固定值：seedance |
| model | string | 模型：doubao-seedance-2.0 |
| parameters.input_image | string | 首帧图片 |
| parameters.motion_prompt | string | 动态提示词 |
| parameters.duration | integer | 时长（1-15） |
| parameters.resolution | string | 1080p |
| parameters.aspect_ratio | string | 16:9 |

#### tasks.audio

| 字段 | 类型 | 说明 |
|------|------|------|
| tool | string | 固定值：azure_tts |
| voice | string | 语音：zh-CN-XiaoxiaoNeural / zh-CN-YunxiNeural |
| ssml | string | SSML 格式文本 |
| text | string | 纯文本旁白 |