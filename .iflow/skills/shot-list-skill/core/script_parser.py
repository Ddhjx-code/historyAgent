"""
口播稿解析器（Script Parser）

功能：
1. 识别结构元素（开场、章节、事件、结尾）
2. 提取事件元数据（时间、人物、地点、动作）
3. 识别情绪关键词
4. 提取场景描述（环境、氛围、光线）
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from . import ParsedScript, ParsedSection, Event, EmotionType


class ScriptParser:
    """
    口播稿解析器
    """

    def __init__(self):
        # 情绪关键词映射
        self.emotion_keywords = {
            EmotionType.SOLEMN: ['庄严', '肃穆', '沉重', '悲痛', '威严', '庄重'],
            EmotionType.TENSE: ['紧张', '冲突', '暴力', '愤怒', '压迫', '一触即发'],
            EmotionType.HOPEFUL: ['希望', '振奋', '成功', '胜利', '光明', '充满希望'],
            EmotionType.SOMBER: ['忧郁', '悲凉', '压抑', '悲伤', '沉重', '苦难'],
            EmotionType.DRAMATIC: ['戏剧性', '转折', '高潮', '冲突', '爆发', '震撼'],
            EmotionType.NEUTRAL: ['平静', '普通', '正常', '日常'],
            EmotionType.ANGRY: ['愤怒', '仇恨', '仇视', '暴怒'],
            EmotionType.PEACEFUL: ['宁静', '祥和', '和平', '安宁']
        }

        # 场景关键词映射
        self.scene_keywords = {
            'street': ['街道', '街头', '路边', '市集', '巷口'],
            'court': ['宫廷', '宫殿', '宝座', '罗马柱', '大殿'],
            'disaster': ['地震', '火灾', '废墟', '倒塌', '灾难'],
            'protest': ['抗议', '罢工', '罢课', '罢市', '示威'],
            'battle': ['战争', '战斗', '对抗', '冲突', '战争']
        }

        # 时间标记正则表达式
        self.date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 1947年2月27日
            r'公元(\d+)年',  # 公元138年
            r'(\d+)世纪',  # 19世纪
        ]

        # 人物识别正则表达式
        self.person_patterns = [
            r'([一-龥]{2,10})(皇帝|国王|女王|皇帝|高僧|寡妇|将军|大臣)',  # 职位
            r'([一-龥]{2,10})，([0-9]+)岁',  # 年龄
        ]

        # 地点识别正则表达式
        self.location_patterns = [
            r'([一-龥]{2,10})(市|城|国|岛|省|州|县|镇|村)',  # 行政区划
            r'([一-龥]{2,10})(宫|殿|寺|庙|堂|馆|楼|阁)',  # 建筑
        ]

    def parse(self, script_text: str) -> ParsedScript:
        """
        解析口播稿，返回结构化数据

        Args:
            script_text: 口播稿文本

        Returns:
            ParsedScript: 解析后的口播稿
        """
        lines = script_text.split('\n')

        sections: List[ParsedSection] = []
        events: List[Event] = []

        current_section = None
        current_event = None
        section_counter = 0
        event_counter = 0

        for line in lines:
            # 识别开场白
            if '【开场' in line or '【开场白】' in line:
                if current_section:
                    sections.append(current_section)
                current_section = ParsedSection(
                    type='opening',
                    content='',
                    title=line.strip('【】'),
                    emotion=EmotionType.NEUTRAL
                )
                section_counter += 1

            # 识别章节
            elif re.match(r'【第[一二三四五六七八九十]+部分】', line):
                if current_section:
                    sections.append(current_section)
                current_section = ParsedSection(
                    type='transition',
                    content=line,
                    title=line.strip('【】'),
                    emotion=self._classify_emotion(line)
                )
                section_counter += 1

            # 识别事件
            elif re.match(r'【第[一二三四五六七八九十]+个事件】|【事件[一二三四五六七八九十]+】', line):
                # 保存当前事件
                if current_event:
                    events.append(current_event)

                # 创建新事件
                event_title = line.strip('【】')
                event_counter += 1
                current_event = Event(
                    id=f'event_{event_counter:03d}',
                    title=event_title,
                    content='',
                    metadata=self._extract_event_metadata(event_title)
                )

            # 识别结尾
            elif '【结尾' in line:
                if current_section:
                    sections.append(current_section)
                current_section = ParsedSection(
                    type='ending',
                    content='',
                    title=line.strip('【】'),
                    emotion=EmotionType.NEUTRAL
                )

            # 累积内容
            elif line.strip():
                if current_event:
                    current_event.content += line + '\n'
                elif current_section:
                    current_section.content += line + '\n'

        # 保存最后一个事件和章节
        if current_event:
            events.append(current_event)
        if current_section:
            sections.append(current_section)

        # 计算全局情绪
        global_emotion = self._calculate_global_emotion(sections + events)

        return ParsedScript(
            sections=sections,
            events=events,
            global_emotion=global_emotion,
            metadata={
                'total_sections': len(sections),
                'total_events': len(events),
                'parsed_at': self._get_timestamp()
            }
        )

    def _extract_event_metadata(self, event_title: str) -> Dict[str, str]:
        """
        从事件标题中提取元数据

        Args:
            event_title: 事件标题

        Returns:
            Dict: 元数据字典
        """
        metadata = {}

        # 提取日期
        for pattern in self.date_patterns:
            match = re.search(pattern, event_title)
            if match:
                if len(match.groups()) == 3:
                    metadata['date'] = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                elif len(match.groups()) == 1:
                    metadata['year'] = match.group(1)
                break

        # 提取地点
        for pattern in self.location_patterns:
            match = re.search(pattern, event_title)
            if match:
                metadata['location'] = match.group(1) + match.group(2)
                break

        # 提取时代/朝代
        if '台湾' in event_title and '民国' in event_title:
            metadata['era'] = 'republic_of_china_1947'
        elif '罗马' in event_title:
            metadata['era'] = 'ancient_rome'
        elif '唐朝' in event_title or '唐代' in event_title:
            metadata['era'] = 'tang_dynasty'
        elif '智利' in event_title:
            metadata['era'] = 'modern_chile'

        return metadata

    def _classify_emotion(self, text: str) -> EmotionType:
        """
        识别文本中的情绪类型

        Args:
            text: 文本

        Returns:
            EmotionType: 情绪类型
        """
        emotion_scores = {}

        for emotion_type, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                emotion_scores[emotion_type] = score

        if emotion_scores:
            # 返回得分最高的情绪
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        else:
            return EmotionType.NEUTRAL

    def _calculate_global_emotion(self, items: List) -> EmotionType:
        """
        计算全局情绪

        Args:
            items: 章节或事件列表

        Returns:
            EmotionType: 全局情绪
        """
        emotion_counts = {}

        for item in items:
            emotion = getattr(item, 'emotion', None)
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if emotion_counts:
            # 返回出现次数最多的情绪
            return max(emotion_counts.items(), key=lambda x: x[1])[0]
        else:
            return EmotionType.NEUTRAL

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            str: 时间戳
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def extract_beats(self, event_text: str) -> List[Tuple[str, str]]:
        """
        从事件文本中提取节拍（最小叙事单元）

        Args:
            event_text: 事件文本

        Returns:
            List[Tuple]: 节拍列表，每个元素为 (描述, 观众收获)
        """
        beats = []

        # 按句子分割
        sentences = re.split(r'[。！？；]', event_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 跳过过短的句子
            if len(sentence) < 10:
                continue

            # 分析观众收获
            audience_gains = self._analyze_audience_gains(sentence)

            beats.append((sentence, audience_gains))

        return beats

    def _analyze_audience_gains(self, sentence: str) -> str:
        """
        分析观众从这句话中获得了什么

        Args:
            sentence: 句子

        Returns:
            str: 观众收获（信息/情绪/悬念）
        """
        gains = []

        # 信息收获
        if any(word in sentence for word in ['是', '在', '发生', '叫做', '名为', '来自']):
            gains.append('信息')

        # 情绪收获
        if any(word in sentence for word in ['愤怒', '悲伤', '震惊', '痛苦', '绝望', '希望', '快乐']):
            gains.append('情绪')

        # 悬念收获
        if any(word in sentence for word in ['但', '然而', '突然', '不料', '竟然']):
            gains.append('悬念')

        if not gains:
            gains.append('信息')

        return '、'.join(gains)


# 导出
__all__ = ['ScriptParser']
"""