"""
SSML 增强生成器 - 让 TTS 更像真人而非捧读

解决问题：
1. 多音字正确读法（如「单于」读 chányú，「可汗」读 kèhán）
2. 自然停顿（句中停顿、段落停顿）
3. 情感表达（严肃、激动、悲伤等）
4. 语调变化（强调、疑问、感叹）
5. 语速节奏（叙事快慢、高潮慢读）
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EmotionType(Enum):
    """情感类型"""
    NEUTRAL = "neutral"        # 中性（默认）
    SERIOUS = "serious"        # 严肃
    SOLEMN = "solemn"          # 庄重
    EXCITED = "excited"        # 激动
    SAD = "sad"               # 悲伤
    HOPEFUL = "hopeful"        # 充满希望
    NOSTALGIC = "nostalgic"    # 怀旧
    DRAMATIC = "dramatic"      # 戏剧性


class PauseType(Enum):
    """停顿类型"""
    SHORT = "short"      # 短停顿（0.5秒）- 句中逗号后
    MEDIUM = "medium"    # 中停顿（1秒）- 分句之间
    LONG = "long"        # 长停顿（2秒）- 段落之间
    DRAMATIC = "dramatic"  # 戏剧性停顿（3秒）- 重要转折


@dataclass
class SSMLSegment:
    """SSML 片段"""
    text: str
    emotion: EmotionType = EmotionType.NEUTRAL
    emphasis: str = None  # "strong", "moderate", "none"
    pause_before: PauseType = None
    pause_after: PauseType = None
    rate: float = 1.0
    pitch: str = "+0%"


# 多音字词典 - 历史类常见多音字
POLYPHONE_DICT = {
    # 人名/称号
    "单于": "chán yú",       # 匈奴首领
    "可汗": "kè hán",        # 蒙古/突厥首领
    "阏氏": "yān zhī",       # 匈奴皇后
    "冒顿": "mò dú",         # 匈奴单于名
    "大月氏": "dà ròu zhī",  # 古代民族
    "龟兹": "qiū cí",        # 古西域国名
    "身毒": "yuān dú",       # 古印度别称
    "康居": "kāng jū",       # 古西域国名
    "大宛": "dà yuān",       # 古西域国名
    "吐蕃": "tǔ bō",         # 古西藏政权
    "高句丽": "gāo gōu lí",  # 古朝鲜政权
    "夫余": "fú yú",         # 古东北民族
    "先主": "xiān zhǔ",      # 刘备
    "后主": "hòu zhǔ",       # 刘禅等
    
    # 地名
    "大宛": "dà yuān",
    "高丽": "gāo lí",
    "朝歌": "zhāo gē",       # 商朝都城
    "番禺": "pān yú",        # 广州古称
    "台州": "tāi zhōu",
    "六安": "lù ān",
    "乐亭": "lào tíng",
    "洪洞": "hóng tóng",
    "蔚县": "yù xiàn",
    "枞阳": "zōng yáng",
    
    # 常见多音字（历史语境）
    "王侯": ("wáng hóu", "王侯将相"),
    "侯爵": "hóu jué",
    "万俟": "mò qí",         # 复姓
    "尉迟": "yù chí",        # 复姓
    "长孙": "zhǎng sūn",     # 复姓
    "令狐": "líng hú",       # 复姓
    "澹台": "tán tái",       # 复姓
    "郦食其": "lì yì jī",    # 人名
    "金日磾": "jīn mì dī",   # 人名
    "区寄": "ōu jì",         # 人名
    
    # 数字/量词
    "骑": ("qí", "jì"),      # 动词读qí，名词读jì（骑兵）
    "数万": "shù wàn",
    "几万": "jǐ wàn",
    
    # 文言常见
    "王天下": "wàng tiān xià",  # 动词，称王
    "朝见": "cháo jiàn",
    "朝代": "cháo dài",
    "大夫": ("dà fū", "dài fu"),  # 官职/医生
    "士大夫": "shì dà fū",
    "大王": "dài wáng",       # 戏曲中对王的称呼
    "天王": "tiān wáng",
    
    # 佛/道教
    "南无": "nā mó",
    "般若": "bō rě",
    "伽蓝": "qié lán",
    "阿房宫": "ē páng gōng",
}


class SSMLGenerator:
    """SSML 增强生成器"""
    
    def __init__(self, voice: str = "zh-CN-YunxiNeural"):
        """
        初始化
        
        Args:
            voice: 语音名称
        """
        self.voice = voice
        self.polyphone_dict = POLYPHONE_DICT
        
        # 情感到语音参数的映射
        self.emotion_params = {
            EmotionType.NEUTRAL: {"rate": "1.0", "pitch": "+0%", "style": None},
            EmotionType.SERIOUS: {"rate": "0.9", "pitch": "-5%", "style": "serious"},
            EmotionType.SOLEMN: {"rate": "0.85", "pitch": "-10%", "style": "serious"},
            EmotionType.EXCITED: {"rate": "1.1", "pitch": "+10%", "style": "cheerful"},
            EmotionType.SAD: {"rate": "0.8", "pitch": "-15%", "style": "sad"},
            EmotionType.HOPEFUL: {"rate": "0.95", "pitch": "+5%", "style": "hopeful"},
            EmotionType.NOSTALGIC: {"rate": "0.85", "pitch": "-5%", "style": "gentle"},
            EmotionType.DRAMATIC: {"rate": "0.8", "pitch": "+0%", "style": "serious"},
        }
        
        # 标点符号到停顿的映射
        self.punctuation_pauses = {
            "，": PauseType.SHORT,
            "、": PauseType.SHORT,
            "；": PauseType.MEDIUM,
            "。": PauseType.MEDIUM,
            "！": PauseType.MEDIUM,
            "？": PauseType.MEDIUM,
            "：": PauseType.SHORT,
            "——": PauseType.MEDIUM,
            "……": PauseType.MEDIUM,
        }
        
        # 停顿时长（毫秒）
        self.pause_durations = {
            PauseType.SHORT: 500,
            PauseType.MEDIUM: 1000,
            PauseType.LONG: 2000,
            PauseType.DRAMATIC: 3000,
        }
    
    def generate(
        self,
        text: str,
        emotion: EmotionType = EmotionType.NEUTRAL,
        emphasis_words: List[str] = None,
        auto_pauses: bool = True,
        fix_polyphone: bool = True,
    ) -> str:
        """
        生成增强的 SSML
        
        Args:
            text: 原始文本
            emotion: 整体情感基调
            emphasis_words: 需要强调的词语列表
            auto_pauses: 是否自动添加停顿
            fix_polyphone: 是否修正多音字
        
        Returns:
            完整的 SSML 字符串
        """
        # 1. 修正多音字
        if fix_polyphone:
            text = self._fix_polyphone(text)
        
        # 2. 添加强调标记
        if emphasis_words:
            text = self._add_emphasis(text, emphasis_words)
        
        # 3. 自动添加停顿
        if auto_pauses:
            text = self._add_auto_pauses(text)
        
        # 4. 应用情感参数
        text = self._apply_emotion(text, emotion)
        
        # 5. 包装为完整 SSML
        ssml = self._wrap_ssml(text)
        
        return ssml
    
    def generate_with_segments(
        self,
        segments: List[SSMLSegment]
    ) -> str:
        """
        根据片段生成 SSML（更精细的控制）
        
        Args:
            segments: SSML 片段列表
        
        Returns:
            完整的 SSML 字符串
        """
        parts = []
        
        for seg in segments:
            part = ""
            
            # 前置停顿
            if seg.pause_before:
                duration = self.pause_durations[seg.pause_before]
                part += f'<break time="{duration}ms"/>'
            
            # 应用情感
            params = self.emotion_params.get(seg.emotion, self.emotion_params[EmotionType.NEUTRAL])
            
            # 开始标签
            tags = []
            if params.get("style"):
                tags.append(f'<mstts:express-as style="{params["style"]}">')
            tags.append(f'<prosody rate="{seg.rate}" pitch="{seg.pitch}">')
            
            # 强调
            if seg.emphasis:
                tags.append(f'<emphasis level="{seg.emphasis}">')
            
            part += "".join(tags)
            part += seg.text
            
            # 关闭标签
            if seg.emphasis:
                part += '</emphasis>'
            part += '</prosody>'
            if params.get("style"):
                part += '</mstts:express-as>'
            
            # 后置停顿
            if seg.pause_after:
                duration = self.pause_durations[seg.pause_after]
                part += f'<break time="{duration}ms"/>'
            
            parts.append(part)
        
        return self._wrap_ssml("".join(parts))
    
    def _fix_polyphone(self, text: str) -> str:
        """修正多音字读音"""
        for word, pronunciation in self.polyphone_dict.items():
            if word in text:
                # 使用 say-as 标签标注读音
                if isinstance(pronunciation, tuple):
                    pronunciation = pronunciation[0]
                text = text.replace(word, f'<phoneme alphabet="py" ph="{pronunciation}">{word}</phoneme>')
        return text
    
    def _add_emphasis(self, text: str, words: List[str]) -> str:
        """添加强调标记"""
        for word in words:
            if word in text:
                text = text.replace(word, f'<emphasis level="strong">{word}</emphasis>')
        return text
    
    def _add_auto_pauses(self, text: str) -> str:
        """自动添加停顿"""
        # 句末停顿
        for punct, pause_type in self.punctuation_pauses.items():
            if punct in text:
                duration = self.pause_durations[pause_type]
                text = text.replace(punct, f'{punct}<break time="{duration}ms"/>')
        
        # 处理段落（双换行）
        text = text.replace("\n\n", f'<break time="{self.pause_durations[PauseType.LONG]}ms"/>')
        
        return text
    
    def _apply_emotion(self, text: str, emotion: EmotionType) -> str:
        """应用情感参数"""
        params = self.emotion_params.get(emotion, self.emotion_params[EmotionType.NEUTRAL])
        
        if params.get("style"):
            # 使用情感风格
            return f'''<mstts:express-as style="{params["style"]}">
  <prosody rate="{params["rate"]}" pitch="{params["pitch"]}">
    {text}
  </prosody>
</mstts:express-as>'''
        else:
            # 仅使用韵律
            return f'''<prosody rate="{params["rate"]}" pitch="{params["pitch"]}">
  {text}
</prosody>'''
    
    def _wrap_ssml(self, content: str) -> str:
        """包装为完整 SSML"""
        return f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="{self.voice}">
    {content}
  </voice>
</speak>'''
    
    # ==================== 便捷方法 ====================
    
    def generate_narration(self, text: str, is_dramatic: bool = False) -> str:
        """
        生成历史叙事旁白
        
        Args:
            text: 叙事文本
            is_dramatic: 是否为戏剧性高潮
        
        Returns:
            SSML
        """
        emotion = EmotionType.DRAMATIC if is_dramatic else EmotionType.SOLEMN
        return self.generate(text, emotion=emotion, auto_pauses=True)
    
    def generate_opening(self, text: str) -> str:
        """生成开场白"""
        return self.generate(text, emotion=EmotionType.HOPEFUL, auto_pauses=True)
    
    def generate_ending(self, text: str) -> str:
        """生成结尾语"""
        return self.generate(text, emotion=EmotionType.NOSTALGIC, auto_pauses=True)
    
    def generate_transition(self, text: str) -> str:
        """生成转场旁白"""
        return self.generate(text, emotion=EmotionType.NEUTRAL, auto_pauses=True)
    
    def generate_emotional(
        self,
        text: str,
        emotion: str = "solemn",
        emphasis: List[str] = None
    ) -> str:
        """
        生成带情感的旁白
        
        Args:
            text: 文本
            emotion: 情感类型 (neutral, serious, solemn, excited, sad, hopeful, nostalgic, dramatic)
            emphasis: 需要强调的词
        
        Returns:
            SSML
        """
        emotion_map = {
            "neutral": EmotionType.NEUTRAL,
            "serious": EmotionType.SERIOUS,
            "solemn": EmotionType.SOLEMN,
            "excited": EmotionType.EXCITED,
            "sad": EmotionType.SAD,
            "hopeful": EmotionType.HOPEFUL,
            "nostalgic": EmotionType.NOSTALGIC,
            "dramatic": EmotionType.DRAMATIC,
        }
        e = emotion_map.get(emotion, EmotionType.NEUTRAL)
        return self.generate(text, emotion=e, emphasis_words=emphasis, auto_pauses=True)


# ==================== 快速使用函数 ====================

def create_ssml(
    text: str,
    voice: str = "zh-CN-YunxiNeural",
    emotion: str = "solemn",
    emphasis: List[str] = None
) -> str:
    """
    快速创建 SSML
    
    Args:
        text: 文本
        voice: 语音
        emotion: 情感
        emphasis: 强调词
    
    Returns:
        SSML 字符串
    """
    gen = SSMLGenerator(voice)
    return gen.generate_emotional(text, emotion, emphasis)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("SSML 增强生成器测试")
    print("=" * 60)
    
    gen = SSMLGenerator("zh-CN-YunxiNeural")
    
    # 测试1：多音字修正
    print("\n【测试1】多音字修正")
    text1 = "公元前200年，匈奴单于冒顿率军攻打汉朝。"
    ssml1 = gen.generate(text1, fix_polyphone=True, auto_pauses=False)
    print(f"原文: {text1}")
    print(f"SSML:\n{ssml1}")
    
    # 测试2：自动停顿
    print("\n【测试2】自动停顿")
    text2 = "在人类漫长的历史长河中，某些特定的日期总会闪烁着熠熠生辉的光芒。今天，我们将穿越近2000年的时间隧道，回顾那些改变历史进程的时刻。"
    ssml2 = gen.generate(text2, emotion=EmotionType.NEUTRAL, auto_pauses=True)
    print(f"原文: {text2}")
    print(f"SSML:\n{ssml2}")
    
    # 测试3：情感表达
    print("\n【测试3】情感表达 - 庄重")
    text3 = "公元645年2月25日，唐代高僧玄奘携带657部梵文佛经回到长安。"
    ssml3 = gen.generate_narration(text3)
    print(f"原文: {text3}")
    print(f"SSML:\n{ssml3}")
    
    # 测试4：戏剧性高潮
    print("\n【测试4】戏剧性高潮")
    text4 = "这是改变历史进程的一刻！罗马帝国的命运，就此改写！"
    ssml4 = gen.generate(text4, emotion=EmotionType.DRAMATIC, auto_pauses=True)
    print(f"原文: {text4}")
    print(f"SSML:\n{ssml4}")
    
    # 测试5：强调关键词
    print("\n【测试5】强调关键词")
    text5 = "1901年2月25日，金融巨头摩根创办美国钢铁公司，资本规模高达14亿美元。"
    ssml5 = gen.generate(text5, emphasis_words=["摩根", "14亿美元"], auto_pauses=True)
    print(f"原文: {text5}")
    print(f"SSML:\n{ssml5}")
    
    # 测试6：分段精细控制
    print("\n【测试6】分段精细控制")
    segments = [
        SSMLSegment(
            text="在公元138年的这一天，",
            emotion=EmotionType.SOLEMN,
            pause_after=PauseType.SHORT
        ),
        SSMLSegment(
            text="罗马皇帝哈德良做出了一个重大决定——",
            emotion=EmotionType.SERIOUS,
            emphasis="strong",
            pause_after=PauseType.MEDIUM
        ),
        SSMLSegment(
            text="他收养并指定安敦宁·毕尤为帝国的继承人。",
            emotion=EmotionType.NEUTRAL,
            rate=0.85
        ),
    ]
    ssml6 = gen.generate_with_segments(segments)
    print(f"SSML:\n{ssml6}")
    
    print("\n✅ 测试完成")