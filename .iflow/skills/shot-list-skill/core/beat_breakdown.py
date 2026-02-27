"""
节拍拆解器（Beat Breakdown）

功能：
1. 从事件文本中识别所有节拍（最小叙事单元）
2. 标注节拍强度（低/中/高）
3. 选择9个关键拐点作为Beat Board锚点
4. 生成节拍拆解表
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from . import Event, StoryBeat, BeatIntensity, AnchorType, EmotionType


class BeatBreakdown:
    """
    节拍拆解器
    """

    def __init__(self):
        # 冲突关键词（高强度）
        self.conflict_keywords = ['冲突', '殴打', '击打', '暴力', '镇压', '枪击', '死', '杀', '伤', '爆炸', '火烧', '倒塌']

        # 转折关键词（高强度）
        self.turning_point_keywords = ['但', '然而', '突然', '不料', '竟然', '谁知', '却', '反而']

        # 情绪关键词（高强度）
        self.emotion_keywords = ['愤怒', '悲伤', '震惊', '痛苦', '绝望', '恐惧', '暴怒', '悲痛欲绝']

        # 平静叙述关键词（低强度）
        self.calm_keywords = ['是', '在', '位于', '名叫', '叫做', '来自', '生活在']

        # 推进关键词（中强度）
        self.progress_keywords = ['开始', '继续', '随后', '接着', '于是', '因此', '所以', '导致']

    def identify_beats(self, event: Event) -> List[StoryBeat]:
        """
        识别事件中的所有节拍

        Args:
            event: 事件对象

        Returns:
            List[StoryBeat]: 节拍列表
        """
        beats = []

        # 按句子分割
        sentences = re.split(r'[。！？；]', event.content)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue

            # 识别节拍强度
            intensity = self._classify_intensity(sentence)

            # 识别情绪
            emotion = self._classify_emotion(sentence)

            # 分析观众收获
            audience_gains = self._analyze_audience_gains(sentence)

            # 创建节拍
            beat = StoryBeat(
                id=f'beat_{i+1:03d}',
                description=sentence,
                audience_gains=audience_gains,
                intensity=intensity,
                is_anchor=False,
                emotion=emotion,
                metadata={
                    'event_id': event.id,
                    'sentence_index': i
                }
            )

            beats.append(beat)

        return beats

    def select_anchor_beats(self, beats: List[StoryBeat]) -> List[StoryBeat]:
        """
        从所有节拍中选取9个作为Beat Board锚点

        Args:
            beats: 所有节拍列表

        Returns:
            List[StoryBeat]: 锚点节拍列表
        """
        if len(beats) <= 9:
            # 如果节拍数不足9个，全部作为锚点
            for beat in beats:
                beat.is_anchor = True
            return beats

        # 按强度排序（高强度优先）
        sorted_beats = sorted(beats, key=lambda b: self._intensity_score(b.intensity), reverse=True)

        # 选择锚点
        anchors = []
        anchor_types_assigned = set()

        # 优先分配高强度节拍
        for beat in sorted_beats:
            if beat.intensity == BeatIntensity.HIGH:
                anchor_type = self._assign_anchor_type(beat, anchor_types_assigned)
                if anchor_type:
                    beat.is_anchor = True
                    beat.anchor_type = anchor_type
                    anchors.append(beat)
                    anchor_types_assigned.add(anchor_type)

        # 如果还不足9个，从中强度节拍中选择
        if len(anchors) < 9:
            for beat in sorted_beats:
                if len(anchors) >= 9:
                    break
                if beat.intensity == BeatIntensity.MEDIUM and not beat.is_anchor:
                    anchor_type = self._assign_anchor_type(beat, anchor_types_assigned)
                    if anchor_type:
                        beat.is_anchor = True
                        beat.anchor_type = anchor_type
                        anchors.append(beat)
                        anchor_types_assigned.add(anchor_type)

        # 如果还不足9个，从低强度节拍中选择
        if len(anchors) < 9:
            for beat in sorted_beats:
                if len(anchors) >= 9:
                    break
                if beat.intensity == BeatIntensity.LOW and not beat.is_anchor:
                    anchor_type = self._assign_anchor_type(beat, anchor_types_assigned)
                    if anchor_type:
                        beat.is_anchor = True
                        beat.anchor_type = anchor_type
                        anchors.append(beat)
                        anchor_types_assigned.add(anchor_type)

        # 按原始顺序返回
        return [b for b in beats if b.is_anchor]

    def generate_beat_breakdown_table(self, event: Event, beats: List[StoryBeat]) -> str:
        """
        生成节拍拆解表（Markdown格式）

        Args:
            event: 事件对象
            beats: 节拍列表

        Returns:
            str: Markdown格式的节拍拆解表
        """
        lines = []

        # 事件信息
        lines.append(f"## 事件信息")
        lines.append("")
        lines.append(f"**事件ID**: `{event.id}`")
        lines.append(f"**事件标题**: `{event.title}`")
        if 'date' in event.metadata:
            lines.append(f"**发生时间**: `{event.metadata['date']}`")
        if 'location' in event.metadata:
            lines.append(f"**地点**: `{event.metadata['location']}`")
        if 'era' in event.metadata:
            lines.append(f"**时代**: `{event.metadata['era']}`")
        lines.append("")

        # 节拍拆解表
        lines.append(f"## 节拍拆解")
        lines.append("")
        lines.append("| 序号 | 节拍描述 | 观众收获 | 强度 | 是否锚点 | 锚点类型 | 情绪 |")
        lines.append("|------|---------|---------|------|---------|---------|------|")

        for i, beat in enumerate(beats, 1):
            anchor_mark = "✅" if beat.is_anchor else "❌"
            anchor_type = beat.anchor_type.value if beat.anchor_type else "-"
            emotion = beat.emotion.value if beat.emotion else "-"
            intensity = beat.intensity.value

            # 截断过长的描述
            description = beat.description[:30] + "..." if len(beat.description) > 30 else beat.description
            audience_gains = beat.audience_gains[:15] + "..." if len(beat.audience_gains) > 15 else beat.audience_gains

            lines.append(f"| {i} | {description} | {audience_gains} | {intensity} | {anchor_mark} | {anchor_type} | {emotion} |")

        lines.append("")

        # 锚点选择说明
        anchor_beats = [b for b in beats if b.is_anchor]
        lines.append(f"## 锚点选择说明")
        lines.append("")
        lines.append(f"**共识别节拍**: `{len(beats)}` 个")
        lines.append(f"**选取锚点**: `{len(anchor_beats)}` 个")
        lines.append("")

        lines.append(f"### 锚点列表")
        lines.append("")
        lines.append("| 序号 | 节拍ID | 锚点类型 | 选中理由 |")
        lines.append("|------|--------|---------|---------|")

        for i, anchor in enumerate(anchor_beats, 1):
            reason = f"强度:{anchor.intensity.value}, 情绪:{anchor.emotion.value if anchor.emotion else '-'}"
            lines.append(f"| {i} | {anchor.id} | {anchor.anchor_type.value if anchor.anchor_type else '-'} | {reason} |")

        lines.append("")

        # 节拍强度分布
        high_count = sum(1 for b in beats if b.intensity == BeatIntensity.HIGH)
        medium_count = sum(1 for b in beats if b.intensity == BeatIntensity.MEDIUM)
        low_count = sum(1 for b in beats if b.intensity == BeatIntensity.LOW)
        total = len(beats)

        lines.append(f"## 节拍强度分布")
        lines.append("")
        lines.append(f"- **高强度节拍**: `{high_count}` 个（占总数 `{high_count/total*100:.1f}%`）")
        lines.append(f"- **中强度节拍**: `{medium_count}` 个（占总数 `{medium_count/total*100:.1f}%`）")
        lines.append(f"- **低强度节拍**: `{low_count}` 个（占总数 `{low_count/total*100:.1f}%`）")
        lines.append("")

        # 情绪曲线
        lines.append(f"## 情绪曲线")
        lines.append("")
        lines.append("| 节拍序号 | 情绪类型 | 情绪描述 | 节拍强度 |")
        lines.append("|---------|---------|---------|---------|")

        for i, beat in enumerate(beats, 1):
            emotion = beat.emotion.value if beat.emotion else "-"
            emotion_desc = self._get_emotion_description(beat.emotion) if beat.emotion else "-"
            intensity = beat.intensity.value

            lines.append(f"| {i} | {emotion} | {emotion_desc} | {intensity} |")

        lines.append("")

        return '\n'.join(lines)

    def _classify_intensity(self, sentence: str) -> BeatIntensity:
        """
        分类节拍强度

        Args:
            sentence: 句子

        Returns:
            BeatIntensity: 强度类型
        """
        # 检查高强度关键词
        for keyword in self.conflict_keywords + self.turning_point_keywords + self.emotion_keywords:
            if keyword in sentence:
                return BeatIntensity.HIGH

        # 检查中强度关键词
        for keyword in self.progress_keywords:
            if keyword in sentence:
                return BeatIntensity.MEDIUM

        # 默认低强度
        return BeatIntensity.LOW

    def _classify_emotion(self, sentence: str) -> Optional[EmotionType]:
        """
        分类节拍情绪

        Args:
            sentence: 句子

        Returns:
            Optional[EmotionType]: 情绪类型
        """
        # 愤怒类
        if any(word in sentence for word in ['愤怒', '暴怒', '仇恨', '仇视']):
            return EmotionType.ANGRY

        # 悲伤类
        if any(word in sentence for word in ['悲伤', '悲痛', '痛苦', '绝望', '压抑']):
            return EmotionType.SOMBER

        # 紧张类
        if any(word in sentence for word in ['紧张', '恐惧', '一触即发', '压迫']):
            return EmotionType.TENSE

        # 震惊类
        if any(word in sentence for word in ['震惊', '惊愕', '意外']):
            return EmotionType.DRAMATIC

        # 希望类
        if any(word in sentence for word in ['希望', '光明', '振奋']):
            return EmotionType.HOPEFUL

        # 庄重类
        if any(word in sentence for word in ['庄严', '肃穆', '威严']):
            return EmotionType.SOLEMN

        return EmotionType.NEUTRAL

    def _analyze_audience_gains(self, sentence: str) -> str:
        """
        分析观众收获

        Args:
            sentence: 句子

        Returns:
            str: 观众收获
        """
        gains = []

        # 信息收获
        if any(word in sentence for word in ['是', '在', '发生', '叫做', '名为', '来自', '生活']):
            gains.append('信息')

        # 情绪收获
        if any(word in sentence for word in ['愤怒', '悲伤', '震惊', '痛苦', '绝望', '希望']):
            gains.append('情绪')

        # 悬念收获
        if any(word in sentence for word in ['但', '然而', '突然', '不料', '竟然']):
            gains.append('悬念')

        if not gains:
            gains.append('信息')

        return '、'.join(gains)

    def _intensity_score(self, intensity: BeatIntensity) -> int:
        """
        获取强度分数

        Args:
            intensity: 强度类型

        Returns:
            int: 分数
        """
        scores = {
            BeatIntensity.HIGH: 3,
            BeatIntensity.MEDIUM: 2,
            BeatIntensity.LOW: 1
        }
        return scores.get(intensity, 0)

    def _assign_anchor_type(self, beat: StoryBeat, assigned_types: set) -> Optional[AnchorType]:
        """
        分配锚点类型

        Args:
            beat: 节拍
            assigned_types: 已分配的类型

        Returns:
            Optional[AnchorType]: 锚点类型
        """
        # 已分配的类型
        available_types = [t for t in AnchorType if t not in assigned_types]

        if not available_types:
            return None

        # 根据节拍描述智能选择类型
        description = beat.description.lower()

        # 世界观/基调建立
        if AnchorType.WORLDVIEW_ESTABLISH in available_types and any(word in description for word in ['时代', '背景', '世界', '基调']):
            return AnchorType.WORLDVIEW_ESTABLISH

        # 主角现状与目标/缺口
        if AnchorType.PROTAGONIST_STATUS in available_types and any(word in description for word in ['主角', '人物', '现状', '生活', '困境']):
            return AnchorType.PROTAGONIST_STATUS

        # 诱因事件
        if AnchorType.INCITING_EVENT in available_types and any(word in description for word in ['出现', '到来', '发生', '开始']):
            return AnchorType.INCITING_EVENT

        # 第一次转折
        if AnchorType.FIRST_TURNING_POINT in available_types and any(word in description for word in ['但', '然而', '突然', '转折']):
            return AnchorType.FIRST_TURNING_POINT

        # 中点升级/认知反转
        if AnchorType.MIDPOINT_UPGRADE in available_types and any(word in description for word in ['升级', '反转', '认知', '发现']):
            return AnchorType.MIDPOINT_UPGRADE

        # 危机/低谷
        if AnchorType.CRISIS_LOWPOINT in available_types and any(word in description for word in ['危机', '低谷', '失败', '死亡', '重伤']):
            return AnchorType.CRISIS_LOWPOINT

        # 高潮前集结
        if AnchorType.CLIMAX_ASSEMBLY in available_types and any(word in description for word in ['集结', '准备', '汇聚']):
            return AnchorType.CLIMAX_ASSEMBLY

        # 高潮对抗/结果
        if AnchorType.CLIMAX_CONFRONTATION in available_types and any(word in description for word in ['高潮', '对抗', '结果', '结局']):
            return AnchorType.CLIMAX_CONFRONTATION

        # 结局/余韵
        if AnchorType.RESOLUTION_AFTERMATH in available_types and any(word in description for word in ['结局', '余韵', '后续', '后来']):
            return AnchorType.RESOLUTION_AFTERMATH

        # 如果没有匹配，返回第一个可用类型
        return available_types[0]

    def _get_emotion_description(self, emotion: EmotionType) -> str:
        """
        获取情绪描述

        Args:
            emotion: 情绪类型

        Returns:
            str: 情绪描述
        """
        descriptions = {
            EmotionType.SOLEMN: "庄重肃穆",
            EmotionType.TENSE: "紧张激烈",
            EmotionType.HOPEFUL: "充满希望",
            EmotionType.SOMBER: "忧郁悲凉",
            EmotionType.DRAMATIC: "戏剧性张力",
            EmotionType.NEUTRAL: "平静叙述",
            EmotionType.ANGRY: "愤怒仇恨",
            EmotionType.PEACEFUL: "宁静祥和"
        }
        return descriptions.get(emotion, "-")


# 导出
__all__ = ['BeatBreakdown']
