"""
Beat Board生成器（Beat Board Generator）

功能：
1. 为9个锚点节拍生成九宫格提示词
2. 确保九格风格统一、角色统一、光色逻辑统一
3. 九宫格作为Sequence Board的垫图（一致性保障）
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from . import Event, StoryBeat, BeatBoard, BeatBoardGridCell, StylePreset, Character


class BeatBoardGenerator:
    """
    Beat Board生成器
    """

    def __init__(self):
        # 时代特征映射
        self.era_features = {
            'republic_of_china_1947': {
                'clothing': '中山装旗袍',
                'architecture': '台北老街建筑',
                'color': '棕暖黄色调',
                'atmosphere': '压抑悲凉'
            },
            'ancient_rome': {
                'clothing': '托加长袍、橄榄冠',
                'architecture': '大理石柱、马赛克',
                'color': '暖黄白金色调',
                'atmosphere': '威严庄重'
            },
            'tang_dynasty': {
                'clothing': '襦裙、圆领袍',
                'architecture': '斗拱、飞檐',
                'color': '绚丽多彩色调',
                'atmosphere': '神圣庄严'
            },
            'modern_chile': {
                'clothing': '现代服装',
                'architecture': '现代建筑',
                'color': '蓝白暖橙色调',
                'atmosphere': '紧张震撼'
            }
        }

        # 默认风格预设
        self.default_style = StylePreset(
            visual_style="历史纪录片风格",
            color_grading="低饱和棕黄暖色调",
            lighting_type="dramatic",
            mood="压抑悲凉"
        )

    def generate_beat_board(self, event: Event, anchor_beats: List[StoryBeat]) -> BeatBoard:
        """
        生成Beat Board（九宫格）

        Args:
            event: 事件对象
            anchor_beats: 锚点节拍列表

        Returns:
            BeatBoard: Beat Board对象
        """
        # 确定风格预设
        style_preset = self._determine_style_preset(event)

        # 识别人物
        characters = self._identify_characters(event, anchor_beats)

        # 生成九宫格
        grid = self._generate_grid(anchor_beats, event, style_preset)

        beat_board = BeatBoard(
            event_id=event.id,
            grid_size="3x3",
            style_preset=style_preset,
            characters=characters,
            grid=grid,
            metadata={
                'total_anchor_beats': len(anchor_beats),
                'generated_at': self._get_timestamp()
            }
        )

        return beat_board

    def generate_prompt_for_beat(self, beat: StoryBeat, style_preset: StylePreset, era: Optional[str] = None) -> str:
        """
        为单个节拍生成提示词

        Args:
            beat: 节拍对象
            style_preset: 风格预设
            era: 时代

        Returns:
            str: 提示词
        """
        # 获取时代特征
        era_info = self.era_features.get(era, {}) if era else {}

        # 确定景别
        shot_size = self._determine_shot_size(beat)

        # 确定角度
        camera_angle = self._determine_camera_angle(beat)

        # 生成提示词
        prompt_parts = []

        # 1. 风格和景别
        prompt_parts.append(f"{style_preset.visual_style}。{shot_size}，")

        # 2. 环境描述
        environment = self._generate_environment_description(beat, era_info)
        prompt_parts.append(f"{environment}。")

        # 3. 主体描述
        subject = self._generate_subject_description(beat)
        prompt_parts.append(f"{subject}。")

        # 4. 光线描述
        lighting = self._generate_lighting_description(style_preset)
        prompt_parts.append(f"{lighting}。")

        # 5. 色调描述
        color = self._generate_color_description(style_preset, era_info)
        prompt_parts.append(f"{color}。")

        # 6. 画面参数
        prompt_parts.append("电影质感，16:9横屏。")

        return ''.join(prompt_parts)

    def _determine_style_preset(self, event: Event) -> StylePreset:
        """
        确定风格预设

        Args:
            event: 事件对象

        Returns:
            StylePreset: 风格预设
        """
        era = event.metadata.get('era', None)

        if era and era in self.era_features:
            era_info = self.era_features[era]
            return StylePreset(
                visual_style="历史纪录片风格",
                color_grading=era_info['color'],
                lighting_type="dramatic",
                mood=era_info['atmosphere']
            )

        return self.default_style

    def _identify_characters(self, event: Event, anchor_beats: List[StoryBeat]) -> Dict[str, Character]:
        """
        识别人物

        Args:
            event: 事件对象
            anchor_beats: 锚点节拍列表

        Returns:
            Dict[str, Character]: 人物字典
        """
        characters = {}

        # 从事件标题中提取人物
        title = event.title
        era = event.metadata.get('era', None)

        # 林江迈（1947年台湾）
        if '林江迈' in title or '寡妇' in title:
            characters['lin_jiangmai_1947'] = Character(
                character_id='lin_jiangmai_1947',
                name='林江迈',
                description='40岁台湾寡妇，烟纸摊贩',
                visual_features={
                    'age': '40_years_old',
                    'gender': 'female',
                    'face_shape': 'weathered_face',
                    'expression': 'exhausted_worried'
                },
                clothing={
                    'primary': 'patched_cotton_clothing_1947_taiwan',
                    'description': '打补丁的粗布衣裳，民国时期台湾平民风格',
                    'color': 'gray_brown',
                    'condition': 'worn_tattered'
                },
                pose={
                    'default': 'squatting_vendor_posture',
                    'alternative': 'crouching_defensive'
                },
                era=era
            )

        # 哈德良皇帝（古罗马）
        if '哈德良' in title or '罗马' in title:
            characters['hadrian_138'] = Character(
                character_id='hadrian_138',
                name='哈德良皇帝',
                description='古罗马帝国皇帝（117-138年）',
                visual_features={
                    'age': '60_years_old',
                    'gender': 'male',
                    'face_shape': 'roman_imperial_profile',
                    'expression': 'wise_authoritative'
                },
                clothing={
                    'primary': 'purple_border_toga',
                    'description': '紫色镶边托加长袍，罗马皇帝专用',
                    'color': 'purple_white_gold',
                    'accessories': ['olive_wreath_crown', 'imperial_ring']
                },
                pose={
                    'default': 'seated_on_throne',
                    'alternative': 'standing_ancient_pose'
                },
                era=era
            )

        # 玄奘高僧（唐代）
        if '玄奘' in title or '唐朝' in title or '唐代' in title:
            characters['xuanzang_645'] = Character(
                character_id='xuanzang_645',
                name='玄奘高僧',
                description='唐代高僧，西行取经',
                visual_features={
                    'age': '45_years_old',
                    'gender': 'male',
                    'face_shape': 'serene_monk',
                    'expression': 'peaceful_determined'
                },
                clothing={
                    'primary': 'monk_robe_tang',
                    'description': '唐代僧袍，朴素庄严',
                    'color': 'saffron_brown',
                    'accessories': ['buddhist_sutra', 'monk_staff']
                },
                pose={
                    'default': 'standing_with_sutra',
                    'alternative': 'walking_pilgrimage'
                },
                era=era
            )

        return characters

    def _generate_grid(self, anchor_beats: List[StoryBeat], event: Event, style_preset: StylePreset) -> List[BeatBoardGridCell]:
        """
        生成九宫格

        Args:
            anchor_beats: 锚点节拍列表
            event: 事件对象
            style_preset: 风格预设

        Returns:
            List[BeatBoardGridCell]: 九宫格列表
        """
        grid = []
        era = event.metadata.get('era', None)

        for i, beat in enumerate(anchor_beats):
            # 生成提示词
            prompt = self.generate_prompt_for_beat(beat, style_preset, era)

            # 创建格子
            cell = BeatBoardGridCell(
                position=i,
                beat_id=beat.id,
                prompt=prompt,
                image_path=f"beat_board_{i:02d}.png",
                is_reference_for=[f"sequence_group_{i+1:02d}"]
            )

            grid.append(cell)

        return grid

    def _determine_shot_size(self, beat: StoryBeat) -> str:
        """
        确定景别

        Args:
            beat: 节拍对象

        Returns:
            str: 景别描述
        """
        description = beat.description.lower()

        # 特写
        if any(word in description for word in ['眼睛', '脸', '表情', '手', '特写']):
            return '特写'

        # 近景
        if any(word in description for word in ['人', '身', '头', '近景']):
            return '近景'

        # 全景
        if any(word in description for word in ['全景', '全身', '整个']):
            return '全景'

        # 中景（默认）
        return '中景'

    def _determine_camera_angle(self, beat: StoryBeat) -> str:
        """
        确定角度

        Args:
            beat: 节拍对象

        Returns:
            str: 角度描述
        """
        description = beat.description.lower()

        # 俯拍
        if any(word in description for word in ['渺小', '脆弱', '俯视']):
            return '俯拍'

        # 仰拍
        if any(word in description for word in ['威严', '高大', '仰视']):
            return '仰拍'

        # 平视（默认）
        return '平视'

    def _generate_environment_description(self, beat: StoryBeat, era_info: Dict) -> str:
        """
        生成环境描述

        Args:
            beat: 节拍对象
            era_info: 时代信息

        Returns:
            str: 环境描述
        """
        description = beat.description

        # 基础环境
        environment = ""

        # 使用时代特征
        if 'architecture' in era_info:
            environment += era_info['architecture'] + "，"

        # 从描述中提取环境
        if '街头' in description or '街边' in description:
            environment += "黄昏街头"
        elif '宫廷' in description or '宝座' in description:
            environment += "庄严宫殿"
        elif '城门' in description:
            environment += "城门广场"
        elif '地震' in description:
            environment += "震后街道"
        else:
            environment += "历史场景"

        return environment

    def _generate_subject_description(self, beat: StoryBeat) -> str:
        """
        生成主体描述

        Args:
            beat: 节拍对象

        Returns:
            str: 主体描述
        """
        return beat.description

    def _generate_lighting_description(self, style_preset: StylePreset) -> str:
        """
        生成光线描述

        Args:
            style_preset: 风格预设

        Returns:
            str: 光线描述
        """
        lighting = ""

        if style_preset.lighting_type == "dramatic":
            lighting = "戏剧性光影，侧光从左侧射入，形成强烈明暗对比"
        elif style_preset.lighting_type == "soft":
            lighting = "柔和光线，漫射光照明"
        elif style_preset.lighting_type == "golden_hour":
            lighting = "黄金时段的柔光，夕阳光线打在主体上"
        else:
            lighting = "自然光线"

        return lighting

    def _generate_color_description(self, style_preset: StylePreset, era_info: Dict) -> str:
        """
        生成色调描述

        Args:
            style_preset: 风格预设
            era_info: 时代信息

        Returns:
            str: 色调描述
        """
        color = style_preset.color_grading

        if 'atmosphere' in era_info:
            color += f"，传递出{era_info['atmosphere']}的氛围"

        return color

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            str: 时间戳
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 导出
__all__ = ['BeatBoardGenerator']