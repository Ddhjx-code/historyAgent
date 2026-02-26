"""
Prompt Engine - 历史场景提示词生成引擎

适配 skill-prompt-generator 为历史故事视频生成系统提供智能提示词生成能力。
包含 SSML 增强生成器，让 TTS 更像真人而非捧读。
"""

from .generator import (
    HistoryPromptGenerator,
    HISTORY_KNOWLEDGE,
    generate_history_prompt,
)

from .ssml_generator import (
    SSMLGenerator,
    SSMLSegment,
    EmotionType,
    PauseType,
    POLYPHONE_DICT,
    create_ssml,
)

__all__ = [
    # 图像/视频提示词生成
    'HistoryPromptGenerator',
    'HISTORY_KNOWLEDGE',
    'generate_history_prompt',
    # SSML 生成
    'SSMLGenerator',
    'SSMLSegment',
    'EmotionType',
    'PauseType',
    'POLYPHONE_DICT',
    'create_ssml',
]

__version__ = '1.1.0'
