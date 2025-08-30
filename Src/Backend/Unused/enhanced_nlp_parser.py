#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版智能语言指令解析器
提供更智能的自然语言理解和视频编辑操作转换
"""

import re
import logging
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from auth_util_tools import gen_sign_headers
from config import APP_ID, APP_KEY, URI, DOMAIN, METHOD, SYSTEM_PROMPT

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartInstructionParser:
    """智能指令解析器，支持多种自然语言表达方式"""
    
    def __init__(self):
        self.operation_patterns = self._init_operation_patterns()
        self.context_analyzer = ContextAnalyzer()
        self.intent_classifier = IntentClassifier()
        
    def _init_operation_patterns(self) -> Dict[str, List[Dict]]:
        """初始化操作模式匹配规则"""
        return {
            'trim': [
                {
                    'patterns': [
                        r'剪掉?开头?(\d+(?:\.\d+)?)\s*秒?',
                        r'去掉?开头?(\d+(?:\.\d+)?)\s*秒?',
                        r'砍掉?开头?(\d+(?:\.\d+)?)\s*秒?',
                        r'前(\d+(?:\.\d+)?)\s*秒?不要了?',
                        r'删除?前(\d+(?:\.\d+)?)\s*秒?',
                        r'开头?(\d+(?:\.\d+)?)\s*秒?删掉?'
                    ],
                    'action_template': 'action: trim start={start_time} editor=moviepy',
                    'param_extractor': lambda m: {'start_time': float(m.group(1))}
                },
                {
                    'patterns': [
                        r'剪掉?(\d+(?:\.\d+)?)\s*秒?到(\d+(?:\.\d+)?)\s*秒?',
                        r'保留?(\d+(?:\.\d+)?)\s*秒?到(\d+(?:\.\d+)?)\s*秒?',
                        r'只留?(\d+(?:\.\d+)?)\s*秒?到(\d+(?:\.\d+)?)\s*秒?'
                    ],
                    'action_template': 'action: trim start={start_time} end={end_time} editor=moviepy',
                    'param_extractor': lambda m: {'start_time': float(m.group(1)), 'end_time': float(m.group(2))}
                }
            ],
            'speed': [
                {
                    'patterns': [
                        r'快一点?',
                        r'加速',
                        r'速度快点?',
                        r'播放快点?'
                    ],
                    'action_template': 'action: speed factor=1.25 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 1.25}
                },
                {
                    'patterns': [
                        r'慢一点?',
                        r'减速',
                        r'速度慢点?',
                        r'播放慢点?'
                    ],
                    'action_template': 'action: speed factor=0.75 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 0.75}
                },
                {
                    'patterns': [
                        r'(\d+(?:\.\d+)?)\s*倍速',
                        r'速度调到?(\d+(?:\.\d+)?)\s*倍',
                        r'(\d+(?:\.\d+)?)\s*倍播放'
                    ],
                    'action_template': 'action: speed factor={factor} editor=moviepy',
                    'param_extractor': lambda m: {'factor': float(m.group(1))}
                }
            ],
            'brightness': [
                {
                    'patterns': [
                        r'亮一点?',
                        r'变亮',
                        r'亮度提高',
                        r'调亮'
                    ],
                    'action_template': 'action: adjust_brightness factor=1.2 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 1.2}
                },
                {
                    'patterns': [
                        r'暗一点?',
                        r'变暗',
                        r'亮度降低',
                        r'调暗'
                    ],
                    'action_template': 'action: adjust_brightness factor=0.8 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 0.8}
                },
                {
                    'patterns': [
                        r'亮度(\d+(?:\.\d+)?)\s*倍',
                        r'亮度调到?(\d+(?:\.\d+)?)\s*倍'
                    ],
                    'action_template': 'action: adjust_brightness factor={factor} editor=moviepy',
                    'param_extractor': lambda m: {'factor': float(m.group(1))}
                }
            ],
            'contrast': [
                {
                    'patterns': [
                        r'对比度增强',
                        r'对比度提高',
                        r'对比度调高',
                        r'增大对比度',
                        r'增强对比度'
                    ],
                    'action_template': 'action: adjust_contrast factor=1.3 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 1.3}
                },
                {
                    'patterns': [
                        r'对比度降低',
                        r'对比度调低',
                        r'对比度减弱'
                    ],
                    'action_template': 'action: adjust_contrast factor=0.8 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 0.8}
                }
            ],
            'volume': [
                {
                    'patterns': [
                        r'静音',
                        r'关掉?声音',
                        r'不要声音'
                    ],
                    'action_template': 'action: adjust_volume factor=0.0 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 0.0}
                },
                {
                    'patterns': [
                        r'声音小一点?',
                        r'音量降低',
                        r'调小声音'
                    ],
                    'action_template': 'action: adjust_volume factor=0.7 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 0.7}
                },
                {
                    'patterns': [
                        r'声音大一点?',
                        r'音量提高',
                        r'调大声音'
                    ],
                    'action_template': 'action: adjust_volume factor=1.3 editor=moviepy',
                    'param_extractor': lambda m: {'factor': 1.3}
                }
            ],
            'text': [
                {
                    'patterns': [
                        r'加字幕\s*([^，。！？\s]+)',
                        r'打字幕\s*([^，。！？\s]+)',
                        r'添加文字\s*([^，。！？\s]+)',
                        r'智能字幕\s*([^，。！？\s]+)'
                    ],
                    'action_template': 'action: add_text text={text} duration=3.0 start_time=0.0 editor=ffmpeg',
                    'param_extractor': lambda m: {'text': m.group(1)}
                },
                {
                    'patterns': [
                        r'在(\d+(?:\.\d+)?)\s*秒加字幕\s*([^，。！？\s]+)',
                        r'(\d+(?:\.\d+)?)\s*秒打字幕\s*([^，。！？\s]+)',
                        r'第(\d+(?:\.\d+)?)\s*秒开始添加智能字幕\s*([^，。！？\s]+)'
                    ],
                    'action_template': 'action: add_text text={text} duration=3.0 start_time={start_time} editor=ffmpeg',
                    'param_extractor': lambda m: {'text': m.group(2), 'start_time': float(m.group(1))}
                }
            ],
            'transition': [
                {
                    'patterns': [
                        r'加转场',
                        r'添加转场',
                        r'淡入淡出',
                        r'过渡效果'
                    ],
                    'action_template': 'action: add_transition type=fade duration=1.0 start_time=0.0 editor=ffmpeg',
                    'param_extractor': lambda m: {}
                },
                {
                    'patterns': [
                        r'在(\d+(?:\.\d+)?)\s*秒加转场',
                        r'(\d+(?:\.\d+)?)\s*秒添加转场',
                        r'第(\d+(?:\.\d+)?)\s*秒添加转场效果'
                    ],
                    'action_template': 'action: add_transition type=fade duration=1.0 start_time={start_time} editor=ffmpeg',
                    'param_extractor': lambda m: {'start_time': float(m.group(1))}
                }
            ],
            'black_and_white': [
                {
                    'patterns': [
                        r'变成黑白',
                        r'黑白效果',
                        r'黑白化',
                        r'去色'
                    ],
                    'action_template': 'action: make_black_and_white start_time=0.0 duration=1.0 editor=ffmpeg',
                    'param_extractor': lambda m: {}
                },
                {
                    'patterns': [
                        r'前(\d+(?:\.\d+)?)\s*秒变黑白',
                        r'开头(\d+(?:\.\d+)?)\s*秒黑白',
                        r'(\d+(?:\.\d+)?)\s*秒黑白效果',
                        r'第一秒变成黑白'
                    ],
                    'action_template': 'action: make_black_and_white start_time=0.0 duration={duration} editor=ffmpeg',
                    'param_extractor': lambda m: {'duration': float(m.group(1))}
                }
            ],
            'rotate': [
                {
                    'patterns': [
                        r'顺时针转(\d+)\s*度',
                        r'向右转(\d+)\s*度'
                    ],
                    'action_template': 'action: rotate angle={angle} editor=moviepy',
                    'param_extractor': lambda m: {'angle': float(m.group(1))}
                },
                {
                    'patterns': [
                        r'逆时针转(\d+)\s*度',
                        r'向左转(\d+)\s*度'
                    ],
                    'action_template': 'action: rotate angle={-float(m.group(1))} editor=moviepy',
                    'param_extractor': lambda m: {'angle': -float(m.group(1))}
                }
            ],
            'persona': [
                {
                    'patterns': [
                        r'应用persona',
                        r'使用persona',
                        r'应用风格',
                        r'使用风格',
                        r'应用预设',
                        r'使用预设'
                    ],
                    'action_template': 'COMPOSITE:apply_persona',
                    'param_extractor': lambda m: {},
                    'is_composite': True
                }
            ]
        }
    
    def parse_instruction(self, user_input: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        解析用户指令，返回对应的操作指令
        
        Args:
            user_input: 用户输入的自然语言指令
            context: 上下文信息（当前视频状态等）
            
        Returns:
            str: 解析后的操作指令，如果无法解析则返回None
        """
        try:
            # 预处理用户输入
            processed_input = self._preprocess_input(user_input)
            
            # 分析意图
            intent = self.intent_classifier.classify(processed_input)
            
            # 根据意图选择最佳匹配模式
            for operation, patterns in self.operation_patterns.items():
                for pattern_info in patterns:
                    for pattern in pattern_info['patterns']:
                        match = re.search(pattern, processed_input)
                        if match:
                            # 提取参数
                            params = pattern_info['param_extractor'](match)
                            
                            # 应用上下文优化
                            if context:
                                params = self.context_analyzer.optimize_params(operation, params, context)
                            
                            # 生成操作指令
                            action = pattern_info['action_template'].format(**params)
                            logger.info(f"匹配到操作: {operation}, 参数: {params}")
                            return action
            
            # 如果没有匹配到具体模式，尝试模糊匹配
            return self._fuzzy_match(processed_input, context)
            
        except Exception as e:
            logger.error(f"解析指令时出错: {e}")
            return None
    
    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入"""
        # 标准化数字表达
        user_input = re.sub(r'(\d+)秒', r'\1.0秒', user_input)
        user_input = re.sub(r'(\d+)倍', r'\1.0倍', user_input)
        
        # 标准化时间表达
        user_input = re.sub(r'(\d+)分(\d+)秒', lambda m: str(float(m.group(1)) * 60 + float(m.group(2))), user_input)
        
        return user_input
    
    def _fuzzy_match(self, user_input: str, context: Dict[str, Any] = None) -> Optional[str]:
        """模糊匹配，处理一些常见的表达方式"""
        user_input_lower = user_input.lower()
        
        # 处理一些常见的模糊表达
        if any(word in user_input_lower for word in ['美化', '优化', '改善']):
            return 'action: adjust_brightness factor=1.1 editor=moviepy'
        
        if any(word in user_input_lower for word in ['专业', '电影感', '高级']):
            return 'action: adjust_contrast factor=1.2 editor=moviepy'
        
        if any(word in user_input_lower for word in ['复古', '怀旧', '老电影']):
            return 'action: make_black_and_white start_time=0.0 duration=1.0 editor=ffmpeg'
        
        return None


class ContextAnalyzer:
    """上下文分析器，用于优化操作参数"""
    
    def __init__(self):
        self.video_context = {}
    
    def update_context(self, video_info: Dict[str, Any]):
        """更新视频上下文信息"""
        self.video_context.update(video_info)
    
    def optimize_params(self, operation: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """根据上下文优化操作参数"""
        optimized_params = params.copy()
        
        # 根据视频时长优化参数
        if 'duration' in self.video_context:
            video_duration = self.video_context['duration']
            
            # 优化转场时间
            if operation == 'transition' and 'start_time' in optimized_params:
                if optimized_params['start_time'] >= video_duration:
                    optimized_params['start_time'] = max(0, video_duration - 2.0)
            
            # 优化裁剪时间
            if operation == 'trim' and 'end_time' in optimized_params:
                if optimized_params['end_time'] > video_duration:
                    optimized_params['end_time'] = video_duration
        
        # 根据视频分辨率优化参数
        if 'resolution' in self.video_context:
            width, height = self.video_context['resolution']
            
            # 优化文字大小
            if operation == 'text' and 'fontsize' not in optimized_params:
                base_fontsize = min(width, height) // 20
                optimized_params['fontsize'] = max(24, base_fontsize)
        
        return optimized_params


class IntentClassifier:
    """意图分类器，用于理解用户指令的意图"""
    
    def __init__(self):
        self.intent_keywords = {
            'edit': ['编辑', '修改', '调整', '改变', '优化'],
            'create': ['创建', '制作', '生成', '新建'],
            'delete': ['删除', '去掉', '移除', '清除'],
            'view': ['查看', '显示', '预览', '播放'],
            'export': ['导出', '保存', '下载', '分享']
        }
    
    def classify(self, user_input: str) -> str:
        """分类用户意图"""
        user_input_lower = user_input.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return intent
        
        return 'edit'  # 默认为编辑意图


class SmartVideoEditor:
    """智能视频编辑器，整合所有智能功能"""
    
    def __init__(self):
        self.parser = SmartInstructionParser()
        self.context_analyzer = ContextAnalyzer()
        self.history = []
        
    def process_instruction(self, user_input: str, video_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户指令，返回编辑操作和响应
        
        Args:
            user_input: 用户输入的自然语言指令
            video_context: 视频上下文信息
            
        Returns:
            Dict: {
                'action': 操作指令,
                'confidence': 置信度,
                'explanation': 操作说明,
                'suggestions': 建议的其他操作,
                'is_composite': 是否是复合指令,
                'composite_actions': 复合指令包含的所有操作
            }
        """
        try:
            # 更新上下文
            if video_context:
                self.context_analyzer.update_context(video_context)
            
            # 解析指令
            action = self.parser.parse_instruction(user_input, video_context)
            
            if action:
                # 检查是否是复合指令
                if action.startswith('COMPOSITE:'):
                    operation_type = action.split(':', 1)[1]
                    composite_actions = self._get_composite_actions(operation_type)
                    
                    # 添加到历史记录
                    self.history.append({
                        'input': user_input,
                        'action': f"复合指令: {operation_type}",
                        'timestamp': time.time(),
                        'composite_actions': composite_actions
                    })
                    
                    return {
                        'action': action,
                        'confidence': 0.95,
                        'explanation': f"我将应用{operation_type}风格，执行多个编辑操作",
                        'suggestions': self._generate_composite_suggestions(operation_type),
                        'is_composite': True,
                        'composite_actions': composite_actions,
                        'success': True
                    }
                
                # 添加到历史记录
                self.history.append({
                    'input': user_input,
                    'action': action,
                    'timestamp': time.time(),
                })
                
                # 生成操作说明
                explanation = self._generate_explanation(action)
                
                # 生成建议
                suggestions = self._generate_suggestions(action, video_context)
                
                return {
                    'action': action,
                    'confidence': 0.9,
                    'explanation': explanation,
                    'suggestions': suggestions,
                    'is_composite': False,
                    'composite_actions': [],
                    'success': True
                }
            else:
                # 无法解析的指令
                return {
                    'action': None,
                    'confidence': 0.0,
                    'explanation': '抱歉，我没有理解您的指令。请尝试更清晰的表达。',
                    'suggestions': self._get_common_instructions(),
                    'is_composite': False,
                    'composite_actions': [],
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"处理指令时出错: {e}")
            return {
                'action': None,
                'confidence': 0.0,
                'explanation': f'处理指令时出现错误: {str(e)}',
                'suggestions': [],
                'is_composite': False,
                'composite_actions': [],
                'success': False
            }
    
    def _generate_explanation(self, action: str) -> str:
        """生成操作说明"""
        if 'trim' in action:
            return "我将帮您裁剪视频，去掉不需要的部分"
        elif 'speed' in action:
            return "我将调整视频播放速度"
        elif 'brightness' in action:
            return "我将调整视频亮度"
        elif 'contrast' in action:
            return "我将调整视频对比度"
        elif 'text' in action:
            return "我将为视频添加文字字幕"
        elif 'transition' in action:
            return "我将为视频添加转场效果"
        elif 'black_and_white' in action:
            return "我将为视频添加黑白效果"
        else:
            return "我将执行您要求的视频编辑操作"
    
    def _generate_suggestions(self, action: str, context: Dict[str, Any] = None) -> List[str]:
        """生成操作建议"""
        suggestions = []
        
        if 'trim' in action:
            suggestions.extend([
                "调整视频亮度",
                "添加转场效果",
                "调整播放速度"
            ])
        elif 'brightness' in action:
            suggestions.extend([
                "调整对比度",
                "添加黑白效果",
                "调整饱和度"
            ])
        elif 'text' in action:
            suggestions.extend([
                "调整文字位置",
                "添加背景音乐",
                "调整视频速度"
            ])
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _get_composite_actions(self, operation_type: str) -> List[str]:
        """获取复合指令包含的所有操作"""
        if operation_type == 'apply_persona':
            return [
                'action: adjust_contrast factor=1.3 editor=moviepy',
                'action: make_black_and_white start_time=0.0 duration=1.0 editor=ffmpeg',
                'action: add_transition type=fade duration=1.0 start_time=0.0 editor=ffmpeg',
                'action: add_text text=智能字幕 duration=3.0 start_time=1.0 editor=ffmpeg'
            ]
        return []
    
    def _generate_composite_suggestions(self, operation_type: str) -> List[str]:
        """为复合指令生成建议"""
        if operation_type == 'apply_persona':
            return [
                "调整对比度强度",
                "修改黑白效果时长",
                "自定义转场类型",
                "编辑字幕内容"
            ]
        return []
    
    def _get_common_instructions(self) -> List[str]:
        """获取常用指令示例"""
        return [
            "剪掉开头5秒",
            "调整亮度",
            "添加字幕",
            "调整播放速度",
            "添加转场效果"
        ]
    
    def get_history(self) -> List[Dict]:
        """获取操作历史"""
        return self.history.copy()
    
    def clear_history(self):
        """清除操作历史"""
        self.history.clear()


# 兼容性函数，保持与现有代码的兼容
def smart_process_instruction(user_input: str, video_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """智能处理用户指令的兼容性函数"""
    editor = SmartVideoEditor()
    return editor.process_instruction(user_input, video_context)


if __name__ == "__main__":
    # 测试智能指令解析器
    editor = SmartVideoEditor()
    
    test_instructions = [
        "剪掉开头3秒",
        "视频快一点",
        "亮度调高",
        "添加字幕Hello",
        "在5秒加转场",
        "前2秒变黑白"
    ]
    
    for instruction in test_instructions:
        print(f"\n输入: {instruction}")
        result = editor.process_instruction(instruction)
        print(f"结果: {result}")
