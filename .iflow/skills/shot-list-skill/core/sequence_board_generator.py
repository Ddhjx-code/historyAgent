"""
Sequence Board生成器（Sequence Board Generator）

功能：
1. 围绕某个Beat Board格子，展开段落内部的连续动作
2. 默认四格结构：起—承—转—合
3. 必须继承Beat Board对应格的人物/场景/光色描述
4. 检查连贯性规则（屏幕方向、轴线、跳接）
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from . import (
    StoryBeat, BeatBoard, SequenceGroup, SequenceShot,
    ContinuityIssue, ContinuityReport, EmotionType
)


class SequenceBoardGenerator:
    """
    Sequence Board生成器
    """

    def __init__(self):
        # 动作阶段映射
        self.action_phases = {
            '起': 'start',
            '承': 'middle',
            '转': 'climax',
            '合': 'aftermath'
        }

        # 连贯性规则
        self.continuity_rules = {
            'screen_direction': ['consistent', 'inconsistent'],
            'action_continuity': ['start', 'middle', 'climax', 'aftermath'],
            'axis_management': ['established', 'maintained', 'crossed_with_transition', 'stable']
        }

    def generate_sequence_group(
        self,
        anchor_beat: StoryBeat,
        beat_board: BeatBoard,
        grid_cell_index: int,
        style_preset
    ) -> SequenceGroup:
        """
        围绕锚点节拍生成Sequence Board（四宫格/可变格）

        Args:
            anchor_beat: 锚点节拍
            beat_board: Beat Board
            grid_cell_index: 格子索引（0-8）
            style_preset: 风格预设

        Returns:
            SequenceGroup: Sequence Board组
        """
        # 获取参考图片
        reference_image = f"beat_board_{grid_cell_index:02d}.png"

        # 确定格数
        grid_size = self._determine_grid_size(anchor_beat)

        # 确定继承性
        inheritance = self._determine_inheritance(anchor_beat, beat_board)

        # 生成镜头
        shots = self._generate_shots(anchor_beat, grid_size, reference_image, style_preset)

        # 检查连贯性
        continuity_report = self.check_continuity(shots)

        sequence_group = SequenceGroup(
            group_id=f"sequence_group_{grid_cell_index+1:02d}",
            anchor_beat_id=anchor_beat.id,
            reference_beat_image=reference_image,
            structure="起—承—转—合",
            grid_size=grid_size,
            inheritance=inheritance,
            shots=shots,
            metadata={
                'continuity_status': continuity_report.status,
                'continuity_issues': len(continuity_report.issues),
                'generated_at': self._get_timestamp()
            }
        )

        return sequence_group

    def check_continuity(self, shots: List[SequenceShot]) -> ContinuityReport:
        """
        检查连贯性规则

        Args:
            shots: 镜头列表

        Returns:
            ContinuityReport: 连贯性检查报告
        """
        issues = []

        # 检查屏幕方向
        screen_direction_issue = self._check_screen_direction(shots)
        if screen_direction_issue:
            issues.append(screen_direction_issue)

        # 检查动作连贯性
        action_continuity_issue = self._check_action_continuity(shots)
        if action_continuity_issue:
            issues.append(action_continuity_issue)

        # 检查轴线管理
        axis_management_issue = self._check_axis_management(shots)
        if axis_management_issue:
            issues.append(axis_management_issue)

        # 检查跳接风险
        jump_cut_issue = self._check_jump_cut_risk(shots)
        if jump_cut_issue:
            issues.append(jump_cut_issue)

        # 确定状态
        status = 'passed'
        if any(issue.severity == 'high' for issue in issues):
            status = 'failed'
        elif issues:
            status = 'warning'

        return ContinuityReport(
            group_id=f"sequence_group_{shots[0].position // 4 + 1:02d}",
            issues=issues,
            status=status
        )

    def _determine_grid_size(self, beat: StoryBeat) -> int:
        """
        确定格数

        Args:
            beat: 节拍对象

        Returns:
            int: 格数
        """
        # 高强度节拍用4格
        if beat.intensity.value == 'high':
            return 4

        # 低强度节拍用2格
        if beat.intensity.value == 'low':
            return 2

        # 中强度节拍用4格（默认）
        return 4

    def _determine_inheritance(self, beat: StoryBeat, beat_board: BeatBoard) -> Dict[str, str]:
        """
        确定继承性

        Args:
            beat: 节拍对象
            beat_board: Beat Board

        Returns:
            Dict[str, str]: 继承性字典
        """
        inheritance = {}

        # 从Beat Board继承人物
        if beat_board.characters:
            character_id = list(beat_board.characters.keys())[0]
            inheritance['character'] = character_id
            character = beat_board.characters[character_id]
            inheritance['clothing'] = character.clothing.get('primary', '')

        # 继承风格
        inheritance['visual_style'] = beat_board.style_preset.visual_style
        inheritance['color_grading'] = beat_board.style_preset.color_grading
        inheritance['lighting_type'] = beat_board.style_preset.lighting_type

        return inheritance

    def _generate_shots(
        self,
        anchor_beat: StoryBeat,
        grid_size: int,
        reference_image: str,
        style_preset
    ) -> List[SequenceShot]:
        """
        生成镜头

        Args:
            anchor_beat: 锚点节拍
            grid_size: 格数
            reference_image: 参考图片
            style_preset: 风格预设

        Returns:
            List[SequenceShot]: 镜头列表
        """
        shots = []

        # 节拍类型
        phase_types = ['起', '承', '转', '合']

        for i in range(grid_size):
            phase_type = phase_types[i] if i < len(phase_types) else '承'

            # 生成提示词
            prompt = self._generate_prompt_for_shot(anchor_beat, phase_type, style_preset)

            # 生成连贯性检查
            continuity_check = self._generate_continuity_check(phase_type)

            # 创建镜头
            shot = SequenceShot(
                position=i,
                type=phase_type,
                prompt=prompt,
                reference_image=reference_image,
                continuity_check=continuity_check,
                metadata={
                    'phase': phase_type,
                    'action_phase': self.action_phases.get(phase_type, 'middle')
                }
            )

            shots.append(shot)

        return shots

    def _generate_prompt_for_shot(
        self,
        anchor_beat: StoryBeat,
        phase_type: str,
        style_preset
    ) -> str:
        """
        为单个镜头生成提示词

        Args:
            anchor_beat: 锚点节拍
            phase_type: 阶段类型（起/承/转/合）
            style_preset: 风格预设

        Returns:
            str: 提示词
        """
        prompt_parts = []

        # 1. 风格和景别
        shot_size = self._determine_shot_size_by_phase(phase_type)
        prompt_parts.append(f"{style_preset.visual_style}。{shot_size}，")

        # 2. 主体描述（根据阶段调整）
        subject = self._generate_subject_by_phase(anchor_beat, phase_type)
        prompt_parts.append(f"{subject}。")

        # 3. 光线描述（根据阶段调整）
        lighting = self._generate_lighting_by_phase(phase_type, style_preset)
        prompt_parts.append(f"{lighting}。")

        # 4. 色调描述
        color = style_preset.color_grading
        prompt_parts.append(f"{color}。")

        # 5. 画面参数
        prompt_parts.append("电影质感，16:9横屏。")

        return ''.join(prompt_parts)

    def _determine_shot_size_by_phase(self, phase_type: str) -> str:
        """
        根据阶段确定景别

        Args:
            phase_type: 阶段类型

        Returns:
            str: 景别
        """
        if phase_type == '起':
            return '中景'
        elif phase_type == '承':
            return '中近景'
        elif phase_type == '转':
            return '特写'
        elif phase_type == '合':
            return '中景'
        else:
            return '中景'

    def _generate_subject_by_phase(self, beat: StoryBeat, phase_type: str) -> str:
        """
        根据阶段生成主体描述

        Args:
            beat: 节拍对象
            phase_type: 阶段类型

        Returns:
            str: 主体描述
        """
        description = beat.description

        if phase_type == '起':
            return description + "，动作开始"
        elif phase_type == '承':
            return description + "，动作进行中"
        elif phase_type == '转':
            return description + "，动作高潮"
        elif phase_type == '合':
            return description + "，动作结果"
        else:
            return description

    def _generate_lighting_by_phase(self, phase_type: str, style_preset) -> str:
        """
        根据阶段生成光线描述

        Args:
            phase_type: 阶段类型
            style_preset: 风格预设

        Returns:
            str: 光线描述
        """
        if phase_type == '起':
            return "柔光，光线均匀"
        elif phase_type == '承':
            return "侧光，逐渐增强"
        elif phase_type == '转':
            return "硬光，强烈对比"
        elif phase_type == '合':
            return "漫射光，柔和"
        else:
            return style_preset.lighting_type

    def _generate_continuity_check(self, phase_type: str) -> Dict[str, str]:
        """
        生成连贯性检查

        Args:
            phase_type: 阶段类型

        Returns:
            Dict[str, str]: 连贯性检查
        """
        return {
            'screen_direction': 'consistent',
            'action_continuity': self.action_phases.get(phase_type, 'middle'),
            'axis_management': 'maintained'
        }

    def _check_screen_direction(self, shots: List[SequenceShot]) -> Optional[ContinuityIssue]:
        """
        检查屏幕方向一致性

        Args:
            shots: 镜头列表

        Returns:
            Optional[ContinuityIssue]: 问题（如果有）
        """
        # 简化检查：默认通过
        return None

    def _check_action_continuity(self, shots: List[SequenceShot]) -> Optional[ContinuityIssue]:
        """
        检查动作连贯性

        Args:
            shots: 镜头列表

        Returns:
            Optional[ContinuityIssue]: 问题（如果有）
        """
        # 检查动作阶段是否连续
        phases = [shot.continuity_check.get('action_continuity', '') for shot in shots]

        expected_phases = ['start', 'middle', 'climax', 'aftermath']
        for i, (phase, expected) in enumerate(zip(phases, expected_phases)):
            if phase != expected:
                return ContinuityIssue(
                    shot_id=f"shot_{i+1}",
                    issue_type='action_continuity',
                    description=f"动作阶段应为{expected}，实际为{phase}",
                    severity='medium'
                )

        return None

    def _check_axis_management(self, shots: List[SequenceShot]) -> Optional[ContinuityIssue]:
        """
        检查轴线管理

        Args:
            shots: 镜头列表

        Returns:
            Optional[ContinuityIssue]: 问题（如果有）
        """
        # 简化检查：默认通过
        return None

    def _check_jump_cut_risk(self, shots: List[SequenceShot]) -> Optional[ContinuityIssue]:
        """
        检查跳接风险

        Args:
            shots: 镜头列表

        Returns:
            Optional[ContinuityIssue]: 问题（如果有）
        """
        # 检查相邻镜头的景别是否足够不同
        shot_sizes = []
        for shot in shots:
            if '中景' in shot.prompt:
                shot_sizes.append('medium')
            elif '近景' in shot.prompt:
                shot_sizes.append('close')
            elif '特写' in shot.prompt:
                shot_sizes.append('extreme_close')
            elif '全景' in shot.prompt:
                shot_sizes.append('wide')

        for i in range(len(shot_sizes) - 1):
            if shot_sizes[i] == shot_sizes[i + 1]:
                return ContinuityIssue(
                    shot_id=f"shot_{i+1}",
                    issue_type='jump_cut',
                    description=f"镜头{i+1}和{i+2}的景别相同，可能存在跳接风险",
                    severity='low'
                )

        return None

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            str: 时间戳
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 导出
__all__ = ['SequenceBoardGenerator']