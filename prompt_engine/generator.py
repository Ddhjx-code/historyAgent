"""
历史场景提示词生成器 - 适配 skill-prompt-generator

通过 sys.path 动态引用 skill-prompt-generator 项目，
为历史故事视频生成系统提供智能提示词生成能力。
"""

import sys
import os
from typing import Dict, List, Optional

# 动态添加 skill-prompt-generator 到 Python 路径
PROMPT_GEN_PATH = "/Users/duanchao.wzj/python/workspace/skill-prompt-generator"
if PROMPT_GEN_PATH not in sys.path:
    sys.path.insert(0, PROMPT_GEN_PATH)

# 导入 skill-prompt-generator 核心模块
from core.cross_domain_generator import CrossDomainGenerator
from intelligent_generator import IntelligentGenerator


# 历史领域知识库
HISTORY_KNOWLEDGE = {
    # 朝代 -> 服饰特征
    'dynasty_costumes': {
        'qin_han': ['深衣', '冠冕', '黑色为主', '厚重庄严'],
        'tang': ['襦裙', '圆领袍', '绚丽多彩', '开放华丽'],
        'song': ['褙子', '直领对襟', '素雅淡色', '文雅含蓄'],
        'ming': ['马面裙', '立领', '红蓝为主', '端庄大气'],
        'qing': ['旗装', '马褂', '红黄蓝', '皇家气派'],
        'warring_states': ['深衣', '宽袍大袖', '古朴厚重', '青铜纹饰'],
        'roman': ['托加长袍', '橄榄冠', '白紫金', '威严'],
        'medieval': ['盔甲', '斗篷', '铁灰深红', '骑士风格'],
        'industrial': ['西装马甲', '礼帽', '深色正装', '绅士风格'],  # 新增工业时代
        'modern': ['正装', '商务西装', '深蓝灰色', '现代风格'],  # 新增现代
    },
    
    # 朝代 -> 建筑风格
    'dynasty_architecture': {
        'qin_han': ['宫殿', '城郭', '夯土台', '黑红色调', '威严雄伟'],
        'tang': ['斗拱', '飞檐', '琉璃瓦', '金碧辉煌', '大气磅礴'],
        'song': ['园林', '亭台楼阁', '白墙黑瓦', '精巧雅致'],
        'ming': ['紫禁城', '红墙黄瓦', '琉璃瓦', '皇家气派'],
        'qing': ['故宫', '皇家园林', '雕梁画栋', '富丽堂皇'],
        'warring_states': ['城墙', '烽火台', '夯土', '古朴粗犷'],
        'roman': ['大理石柱', '马赛克', '圆顶', '暖黄白色', '宏伟'],
        'medieval': ['城堡', '尖塔', '石墙', '灰暗色调', '神秘'],
        'industrial': ['工厂车间', '蒸汽机', '砖墙', '工业烟囱', '19世纪'],  # 新增
        'modern': ['现代建筑', '玻璃幕墙', '新闻发布厅', '会议室'],  # 新增
    },
    
    # 朝代 -> 色调
    'dynasty_colors': {
        'qin_han': 'black, red, gold, bronze',
        'tang': 'vibrant multicolor, gold, crimson, emerald',
        'song': 'white, black, gray, pale green, light blue',
        'ming': 'red, yellow, blue, gold',
        'qing': 'red, gold, imperial yellow, royal blue',
        'warring_states': 'black, bronze, dark red, earth tones',
        'roman': 'warm white, gold, purple, terracotta',
        'medieval': 'gray, dark red, brown, steel blue',
        'industrial': 'sepia, brown, brass, copper, dark wood',  # 新增
        'modern': 'blue, gray, white, neutral tones',  # 新增
    },
    
    # 人物类型 -> 英文提示词模板
    'character_templates': {
        'emperor': 'powerful emperor sitting on throne, commanding presence, imperial regalia',
        'general': 'armored military general, battle-hardened warrior, fierce expression',
        'scholar': 'elegant scholar in traditional robes, contemplative, holding scroll',
        'warrior': 'skilled warrior in combat stance, weapon ready, determined look',
        'monk': 'Buddhist monk in kasaya robes, peaceful expression, prayer beads',
        'concubine': 'elegant noblewoman in exquisite silk robes, graceful demeanor',
        'soldier': 'armored soldier holding spear, disciplined formation',
        'assassin': 'shadowy assassin in dark clothing, hidden blade, stealthy',
        'inventor': 'inventor in 19th century attire, working at workbench, mechanical tools',  # 新增
        'diplomat': 'diplomat in formal suit, standing at podium, professional demeanor',  # 新增
    },
    
    # 场景类型 -> 英文提示词模板  
    'scene_templates': {
        'palace_hall': 'grand imperial palace hall, ornate pillars, golden decorations',
        'battlefield': 'epic battlefield, armies clashing, dust and chaos',
        'court': 'imperial court session, officials kneeling, solemn atmosphere',
        'garden': 'traditional Chinese garden, pavilions, lotus pond, willow trees',
        'temple': 'ancient Buddhist temple, incense smoke, golden Buddha statues',
        'city_gate': 'massive city gates, soldiers guarding, imposing walls',
        'war_council': 'military command tent, strategy map, stern generals',
        'workshop': '19th century inventor workshop, tools, mechanical parts, workbench',  # 新增
        'press_hall': 'modern press conference hall, podium, flags, microphones',  # 新增
        'factory': 'industrial factory, steam engines, smoke, workers',  # 新增
    },
    
    # 视觉风格
    'visual_styles': {
        'cinematic': 'cinematic composition, dramatic lighting, film grain, 4K quality',
        'documentary': 'historical documentary style, realistic, natural lighting',
        'epic': 'epic grand scale, sweeping camera, dramatic atmosphere',
        'intimate': 'intimate close-up, emotional, shallow depth of field',
    }
}


class HistoryPromptGenerator:
    """
    历史场景提示词生成器
    
    适配 skill-prompt-generator 为历史故事视频生成系统提供：
    1. 历史场景图像提示词（Seedream）
    2. 动态视频提示词（Seedance）
    3. 历史领域知识增强
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            db_path: 元素数据库路径，默认使用 skill-prompt-generator 的数据库
        """
        if db_path is None:
            db_path = os.path.join(PROMPT_GEN_PATH, "extracted_results/elements.db")
        
        self.db_path = db_path
        self.generator = CrossDomainGenerator(db_path)
        self.knowledge = HISTORY_KNOWLEDGE
    
    def generate_image_prompt(
        self, 
        scene_description: str,
        dynasty: Optional[str] = None,
        character_type: Optional[str] = None,
        scene_type: Optional[str] = None,
        action: Optional[str] = None,
        visual_style: str = 'cinematic'
    ) -> Dict:
        """
        生成历史场景图像提示词
        
        策略：
        1. 使用历史领域知识模板生成主体内容（服饰、建筑、人物、场景）
        2. 只从 skill-prompt-generator 获取通用技术参数（光影、构图、画质）
        
        Args:
            scene_description: 场景描述（中文自然语言）
            dynasty: 朝代（qin_han, tang, song, ming, qing, roman 等）
            character_type: 人物类型（emperor, general, scholar 等）
            scene_type: 场景类型（palace_hall, battlefield, court 等）
            action: 动作类型（duel, army_charge 等）
            visual_style: 视觉风格（cinematic, documentary, epic, intimate）
        
        Returns:
            {
                'image_prompt': 'Seedream 图像提示词',
                'style_preset': {...},
                'metadata': {...}
            }
        """
        # 1. 使用历史领域知识构建主体内容
        main_parts = []
        main_parts.append("historical documentary style")
        
        # 添加朝代风格
        if dynasty and dynasty in self.knowledge['dynasty_costumes']:
            costumes = self.knowledge['dynasty_costumes'][dynasty]
            architecture = self.knowledge['dynasty_architecture'][dynasty]
            colors = self.knowledge['dynasty_colors'][dynasty]
            
            main_parts.append(f"{dynasty.replace('_', ' ')} period setting")
            main_parts.append(f"traditional {costumes[0]}")
            main_parts.append(f"{architecture[0]} architecture")
            main_parts.append(f"{colors} color palette")
        
        # 添加人物模板
        if character_type and character_type in self.knowledge['character_templates']:
            main_parts.append(self.knowledge['character_templates'][character_type])
        
        # 添加场景模板
        if scene_type and scene_type in self.knowledge['scene_templates']:
            main_parts.append(self.knowledge['scene_templates'][scene_type])
        
        # 添加动作模板
        if action and action in self.knowledge['action_templates']:
            main_parts.append(self.knowledge['action_templates'][action])
        
        # 添加场景描述
        main_parts.append(scene_description)
        
        # 2. 从 skill-prompt-generator 获取技术参数（仅光影和构图）
        # 注意：只获取通用技术参数，不获取人像相关元素
        tech_params = self._get_technical_params(visual_style)
        
        # 3. 组合最终提示词：历史主体 + 技术参数
        main_content = ', '.join(main_parts)
        final_prompt = f"{main_content}, {tech_params}"
        
        return {
            'image_prompt': final_prompt,
            'style_preset': {
                'dynasty': dynasty,
                'character_type': character_type,
                'scene_type': scene_type,
                'visual_style': visual_style,
            },
            'metadata': {
                'source': 'history_knowledge_template',
                'dynasty': dynasty,
                'enhanced': True,
            }
        }
    
    def _get_technical_params(self, visual_style: str = 'cinematic') -> str:
        """
        从 skill-prompt-generator 的 art/video/common 域获取技术参数
        
        使用 Cross-Domain 模式，只查询非人像领域的元素：
        - art: 艺术风格
        - video: 场景类型、镜头运动
        - common: 光影技术、摄影技术
        """
        try:
            from core.cross_domain_query import CrossDomainQueryEngine
            
            query_engine = CrossDomainQueryEngine(self.db_path)
            
            tech_parts = []
            
            # 使用 get_all_elements_by_category 获取元素
            # art domain - 光影技术
            art_lighting = query_engine.get_all_elements_by_category('art', 'lighting_techniques')
            if art_lighting:
                for elem in art_lighting[:2]:
                    template = elem.get('ai_prompt_template', '')
                    if template and len(template) < 100 and 'cute' not in template.lower():
                        tech_parts.append(template)
            
            # common domain - 光影技术
            common_lighting = query_engine.get_all_elements_by_category('common', 'lighting_techniques')
            if common_lighting:
                for elem in common_lighting[:2]:
                    template = elem.get('ai_prompt_template', '')
                    if template and len(template) < 100:
                        tech_parts.append(template)
            
            # common domain - 摄影技术
            common_photo = query_engine.get_all_elements_by_category('common', 'photography_techniques')
            if common_photo:
                for elem in common_photo[:2]:
                    template = elem.get('ai_prompt_template', '')
                    if template and len(template) < 80:
                        tech_parts.append(template)
            
            query_engine.close()
            
            if tech_parts:
                # 去重并限制数量
                unique_parts = list(dict.fromkeys(tech_parts))[:4]
                return ', '.join(unique_parts)
            
        except Exception as e:
            print(f"⚠️ 跨域查询失败: {e}")
        
        # 回退到预定义参数
        tech_params = {
            'cinematic': 'cinematic composition, dramatic lighting, film grain, 4K quality, 16:9 aspect ratio',
            'documentary': 'natural lighting, realistic style, documentary photography, high detail, 16:9',
            'epic': 'grand scale composition, dramatic atmosphere, sweeping view, epic cinematography, 4K',
            'intimate': 'shallow depth of field, soft lighting, emotional close-up, intimate atmosphere',
        }
        
        return tech_params.get(visual_style, tech_params['cinematic'])
    
    def generate_motion_prompt(
        self,
        scene_description: str,
        motion_type: str = 'subtle',
        dynasty: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        生成动态视频提示词（Seedance）
        
        Args:
            scene_description: 场景描述
            motion_type: 动态类型（subtle, moderate, dynamic）
            dynasty: 朝代
            **kwargs: 其他参数传递给 generate_image_prompt
        
        Returns:
            {
                'image_prompt': '静态图像提示词',
                'motion_prompt': 'Seedance 动态提示词',
                'motion_params': {...}
            }
        """
        # 生成静态图像提示词
        image_result = self.generate_image_prompt(
            scene_description, 
            dynasty=dynasty, 
            **kwargs
        )
        
        # 构建动态增强
        motion_enhancements = {
            'subtle': 'gentle camera movement, slight swaying, natural breathing motion',
            'moderate': 'smooth camera pan, walking motion, fabric flowing',
            'dynamic': 'fast camera movement, action sequence, dynamic lighting changes',
        }
        
        motion_suffix = motion_enhancements.get(motion_type, motion_enhancements['subtle'])
        motion_prompt = f"{image_result['image_prompt']}, {motion_suffix}"
        
        return {
            'image_prompt': image_result['image_prompt'],
            'motion_prompt': motion_prompt,
            'motion_params': {
                'motion_type': motion_type,
                'duration': 5 if motion_type == 'subtle' else 4,
            },
            'style_preset': image_result['style_preset'],
            'metadata': image_result['metadata'],
        }
    
    def parse_scene_from_text(self, text: str) -> Dict:
        """
        从中文文本解析场景参数
        
        自动识别：
        - 朝代（秦汉、唐、宋、明清等）
        - 人物类型（皇帝、将军、武将等）
        - 场景类型（宫殿、战场、朝堂等）
        - 动作（比武、战争、登基等）
        
        Args:
            text: 中文场景描述文本
        
        Returns:
            解析后的场景参数字典
        """
        result = {
            'dynasty': None,
            'character_type': None,
            'scene_type': None,
            'action': None,
            'visual_style': 'cinematic',
        }
        
        # 朝代识别
        dynasty_keywords = {
            'qin_han': ['秦', '汉', '秦汉', '秦朝', '汉朝'],
            'tang': ['唐', '唐朝', '大唐'],
            'song': ['宋', '宋朝', '大宋'],
            'ming': ['明', '明朝', '大明'],
            'qing': ['清', '清朝', '大清'],
            'warring_states': ['战国', '春秋'],
            'roman': ['罗马', '古罗马', 'Roman'],
            'medieval': ['中世纪', '骑士', '城堡'],
        }
        
        for dynasty, keywords in dynasty_keywords.items():
            if any(kw in text for kw in keywords):
                result['dynasty'] = dynasty
                break
        
        # 人物类型识别
        character_keywords = {
            'emperor': ['皇帝', '帝王', '君王', '天子'],
            'general': ['将军', '武将', '将领', '大将'],
            'scholar': ['文人', '书生', '士大夫', '学者'],
            'warrior': ['武士', '剑客', '侠客', '战士'],
            'monk': ['僧人', '和尚', '高僧', '禅师'],
            'concubine': ['妃子', '贵妃', '公主', '宫女'],
            'soldier': ['士兵', '士卒', '军士'],
            'assassin': ['刺客', '杀手', '刺客'],
        }
        
        for char_type, keywords in character_keywords.items():
            if any(kw in text for kw in keywords):
                result['character_type'] = char_type
                break
        
        # 场景类型识别
        scene_keywords = {
            'palace_hall': ['宫殿', '大殿', '皇宫', '朝堂'],
            'battlefield': ['战场', '战争', '交战', '厮杀'],
            'court': ['朝堂', '朝会', '议事', '殿堂'],
            'garden': ['花园', '园林', '亭台', '御花园'],
            'temple': ['寺庙', '佛寺', '寺院', '禅院'],
            'city_gate': ['城门', '城楼', '城墙', '关隘'],
            'war_council': ['军帐', '帅帐', '营帐', '军营'],
        }
        
        for scene_type, keywords in scene_keywords.items():
            if any(kw in text for kw in keywords):
                result['scene_type'] = scene_type
                break
        
        # 动作识别
        action_keywords = {
            'duel': ['比武', '对决', '单挑', '决斗'],
            'army_charge': ['冲锋', '进攻', '突袭', '大军'],
            'court_debate': ['争论', '辩论', '议事', '廷争'],
            'assassination': ['刺杀', '行刺', '暗杀'],
            'coronation': ['登基', '即位', '加冕', '继位'],
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in text for kw in keywords):
                result['action'] = action
                break
        
        # 视觉风格识别
        if any(kw in text for kw in ['史诗', '壮观', '宏大']):
            result['visual_style'] = 'epic'
        elif any(kw in text for kw in ['纪录片', '写实', '真实']):
            result['visual_style'] = 'documentary'
        elif any(kw in text for kw in ['特写', '情感', '细腻']):
            result['visual_style'] = 'intimate'
        
        return result
    
    def close(self):
        """关闭资源"""
        self.generator.close()


# 便捷函数
def generate_history_prompt(
    scene_description: str,
    dynasty: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    便捷函数：快速生成历史场景提示词
    
    Args:
        scene_description: 场景描述
        dynasty: 朝代
        **kwargs: 其他参数
    
    Returns:
        生成结果
    """
    generator = HistoryPromptGenerator()
    try:
        return generator.generate_image_prompt(scene_description, dynasty=dynasty, **kwargs)
    finally:
        generator.close()


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("历史场景提示词生成器测试")
    print("=" * 60)
    
    gen = HistoryPromptGenerator()
    
    # 测试1：自动解析
    text = "战国时期，秦国大殿上，秦王赢稷与武将白起议事"
    print(f"\n输入: {text}")
    params = gen.parse_scene_from_text(text)
    print(f"解析结果: {params}")
    
    result = gen.generate_image_prompt(text, **params)
    print(f"\n生成的提示词:\n{result['image_prompt'][:300]}...")
    
    # 测试2：动态视频
    print("\n" + "=" * 60)
    text2 = "唐朝宫廷，皇帝坐在龙椅上"
    print(f"输入: {text2}")
    result2 = gen.generate_motion_prompt(text2, motion_type='subtle', dynasty='tang')
    print(f"动态提示词:\n{result2['motion_prompt'][:300]}...")
    
    gen.close()
    print("\n✅ 测试完成")