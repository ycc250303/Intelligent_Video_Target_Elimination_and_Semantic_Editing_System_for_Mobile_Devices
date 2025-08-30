import cv2
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
from collections import defaultdict
import base64
from openai import OpenAI
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedVideoComprehension:
    """增强的视频理解模块，用于深度分析视频内容和语义"""
    
    def __init__(self, openai_api_key: str = None, openai_base_url: str = None):
        self.openai_client = None
        if openai_api_key:
            self.openai_client = OpenAI(
                api_key=openai_api_key,
                base_url=openai_base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        
        # 初始化分析器
        self.scene_detector = SceneDetector()
        self.motion_analyzer = MotionAnalyzer()
        self.color_analyzer = ColorAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.style_analyzer = StyleAnalyzer()
    
    def comprehensive_analysis(self, video_path: str, analysis_level: str = 'full') -> Dict[str, Any]:
        """综合视频分析"""
        logger.info(f"开始综合视频分析: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 基础信息分析
        basic_info = self._get_basic_info(video_path)
        
        # 场景检测
        scene_analysis = self.scene_detector.detect_scenes(video_path)
        
        # 运动分析
        motion_analysis = self.motion_analyzer.analyze_motion(video_path)
        
        # 颜色分析
        color_analysis = self.color_analyzer.analyze_colors(video_path)
        
        # 内容分析
        content_analysis = self.content_analyzer.analyze_content(video_path)
        
        # 风格分析
        style_analysis = self.style_analyzer.analyze_style(video_path)
        
        # 语义分析（如果可用OpenAI）
        semantic_analysis = {}
        if self.openai_client and analysis_level == 'full':
            semantic_analysis = self._semantic_analysis(video_path, basic_info)
        
        # 综合结果
        result = {
            'video_path': video_path,
            'analysis_timestamp': datetime.now().isoformat(),
            'basic_info': basic_info,
            'scene_analysis': scene_analysis,
            'motion_analysis': motion_analysis,
            'color_analysis': color_analysis,
            'content_analysis': content_analysis,
            'style_analysis': style_analysis,
            'semantic_analysis': semantic_analysis,
            'summary': self._generate_summary(basic_info, scene_analysis, motion_analysis, 
                                           color_analysis, content_analysis, style_analysis)
        }
        
        logger.info(f"视频分析完成: {video_path}")
        return result
    
    def _get_basic_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频基本信息"""
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # 获取视频编码信息
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        cap.release()
        
        return {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration,
            'aspect_ratio': width / height if height > 0 else 0,
            'codec': codec,
            'file_size_mb': os.path.getsize(video_path) / (1024 * 1024)
        }
    
    def _semantic_analysis(self, video_path: str, basic_info: Dict) -> Dict[str, Any]:
        """语义分析（使用OpenAI）"""
        try:
            # 编码视频
            with open(video_path, "rb") as video_file:
                base64_video = base64.b64encode(video_file.read()).decode("utf-8")
            
            # 构建分析提示
            prompt = f"""
            请分析这个视频的内容和风格特征。视频信息：
            - 时长: {basic_info['duration']:.2f}秒
            - 分辨率: {basic_info['width']}x{basic_info['height']}
            - 帧率: {basic_info['fps']}fps
            
            请从以下方面进行分析：
            1. 主要内容类型（如：人物、风景、产品展示、教程等）
            2. 情感氛围（如：欢快、平静、紧张、温馨等）
            3. 视觉风格（如：现代、复古、简约、华丽等）
            4. 节奏特点（如：快节奏、慢节奏、变化丰富等）
            5. 适合的剪辑风格建议
            
            请以JSON格式返回分析结果。
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的视频分析专家，擅长分析视频内容、风格和剪辑特征。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {"url": f"data:video/mp4;base64,{base64_video}"}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            completion = self.openai_client.chat.completions.create(
                model="qwen-vl-max-latest",
                messages=messages,
                stream=False,
            )
            
            response_text = completion.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                semantic_result = json.loads(response_text)
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建结构化结果
                semantic_result = {
                    'content_type': 'unknown',
                    'emotional_atmosphere': 'unknown',
                    'visual_style': 'unknown',
                    'rhythm_characteristics': 'unknown',
                    'editing_suggestions': [],
                    'raw_analysis': response_text
                }
            
            return semantic_result
            
        except Exception as e:
            logger.error(f"语义分析失败: {e}")
            return {
                'error': str(e),
                'content_type': 'unknown',
                'emotional_atmosphere': 'unknown',
                'visual_style': 'unknown',
                'rhythm_characteristics': 'unknown',
                'editing_suggestions': []
            }
    
    def _generate_summary(self, basic_info: Dict, scene_analysis: Dict, 
                         motion_analysis: Dict, color_analysis: Dict,
                         content_analysis: Dict, style_analysis: Dict) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            'video_type': self._classify_video_type(content_analysis, style_analysis),
            'dominant_style': self._identify_dominant_style(style_analysis),
            'rhythm_profile': self._analyze_rhythm_profile(motion_analysis, scene_analysis),
            'color_profile': self._analyze_color_profile(color_analysis),
            'content_complexity': self._assess_content_complexity(content_analysis),
            'editing_recommendations': self._generate_editing_recommendations(
                basic_info, scene_analysis, motion_analysis, color_analysis, 
                content_analysis, style_analysis
            )
        }
        
        return summary
    
    def _classify_video_type(self, content_analysis: Dict, style_analysis: Dict) -> str:
        """分类视频类型"""
        # 基于内容分析结果分类
        if content_analysis.get('has_people', False):
            return '人物视频'
        elif content_analysis.get('has_landscape', False):
            return '风景视频'
        elif content_analysis.get('has_objects', False):
            return '产品视频'
        else:
            return '综合视频'
    
    def _identify_dominant_style(self, style_analysis: Dict) -> str:
        """识别主导风格"""
        # 基于风格分析结果
        if style_analysis.get('modern_score', 0) > 0.7:
            return '现代风格'
        elif style_analysis.get('vintage_score', 0) > 0.7:
            return '复古风格'
        elif style_analysis.get('minimalist_score', 0) > 0.7:
            return '简约风格'
        else:
            return '混合风格'
    
    def _analyze_rhythm_profile(self, motion_analysis: Dict, scene_analysis: Dict) -> Dict[str, float]:
        """分析节奏特征"""
        return {
            'motion_intensity': motion_analysis.get('average_motion', 0.5),
            'scene_change_frequency': scene_analysis.get('scene_change_rate', 0.5),
            'rhythm_consistency': motion_analysis.get('motion_consistency', 0.5),
            'overall_rhythm': (motion_analysis.get('average_motion', 0.5) + 
                             scene_analysis.get('scene_change_rate', 0.5)) / 2
        }
    
    def _analyze_color_profile(self, color_analysis: Dict) -> Dict[str, Any]:
        """分析颜色特征"""
        return {
            'dominant_colors': color_analysis.get('dominant_colors', []),
            'color_temperature': color_analysis.get('color_temperature', 'neutral'),
            'saturation_level': color_analysis.get('average_saturation', 0.5),
            'brightness_level': color_analysis.get('average_brightness', 0.5),
            'color_harmony': color_analysis.get('color_harmony_score', 0.5)
        }
    
    def _assess_content_complexity(self, content_analysis: Dict) -> str:
        """评估内容复杂度"""
        complexity_score = 0
        
        if content_analysis.get('has_people', False):
            complexity_score += 0.3
        if content_analysis.get('has_objects', False):
            complexity_score += 0.2
        if content_analysis.get('has_text', False):
            complexity_score += 0.2
        if content_analysis.get('has_motion', False):
            complexity_score += 0.3
        
        if complexity_score > 0.8:
            return '高复杂度'
        elif complexity_score > 0.5:
            return '中等复杂度'
        else:
            return '低复杂度'
    
    def _generate_editing_recommendations(self, basic_info: Dict, scene_analysis: Dict,
                                        motion_analysis: Dict, color_analysis: Dict,
                                        content_analysis: Dict, style_analysis: Dict) -> List[str]:
        """生成剪辑建议"""
        recommendations = []
        
        # 基于时长建议
        duration = basic_info.get('duration', 0)
        if duration > 300:  # 5分钟以上
            recommendations.append("建议进行分段剪辑，增加转场效果")
        elif duration < 30:  # 30秒以下
            recommendations.append("适合快速剪辑，保持节奏紧凑")
        
        # 基于场景变化建议
        scene_changes = scene_analysis.get('scene_count', 0)
        if scene_changes > 10:
            recommendations.append("场景变化频繁，建议使用平滑转场")
        elif scene_changes < 3:
            recommendations.append("场景变化较少，可考虑增加镜头变化")
        
        # 基于运动特征建议
        motion_intensity = motion_analysis.get('average_motion', 0.5)
        if motion_intensity > 0.7:
            recommendations.append("运动强度高，建议使用动态剪辑风格")
        elif motion_intensity < 0.3:
            recommendations.append("运动较少，适合慢节奏剪辑")
        
        # 基于颜色特征建议
        saturation = color_analysis.get('average_saturation', 0.5)
        if saturation > 0.7:
            recommendations.append("色彩饱和度高，可考虑调色平衡")
        elif saturation < 0.3:
            recommendations.append("色彩较淡，可考虑增强饱和度")
        
        return recommendations

class SceneDetector:
    """场景检测器"""
    
    def detect_scenes(self, video_path: str, threshold: float = 30.0) -> Dict[str, Any]:
        """检测场景变化"""
        cap = cv2.VideoCapture(video_path)
        
        scenes = []
        prev_frame = None
        scene_start = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # 计算帧间差异
                diff = cv2.absdiff(prev_frame, frame)
                mean_diff = np.mean(diff)
                
                # 如果差异超过阈值，认为是新场景
                if mean_diff > threshold:
                    scenes.append({
                        'start_frame': scene_start,
                        'end_frame': frame_count - 1,
                        'start_time': scene_start / cap.get(cv2.CAP_PROP_FPS),
                        'end_time': (frame_count - 1) / cap.get(cv2.CAP_PROP_FPS),
                        'duration': (frame_count - scene_start) / cap.get(cv2.CAP_PROP_FPS)
                    })
                    scene_start = frame_count
            
            prev_frame = frame.copy()
            frame_count += 1
        
        # 添加最后一个场景
        if scene_start < frame_count:
            scenes.append({
                'start_frame': scene_start,
                'end_frame': frame_count - 1,
                'start_time': scene_start / cap.get(cv2.CAP_PROP_FPS),
                'end_time': (frame_count - 1) / cap.get(cv2.CAP_PROP_FPS),
                'duration': (frame_count - scene_start) / cap.get(cv2.CAP_PROP_FPS)
            })
        
        cap.release()
        
        return {
            'scene_count': len(scenes),
            'scenes': scenes,
            'scene_change_rate': len(scenes) / (frame_count / cap.get(cv2.CAP_PROP_FPS)) if frame_count > 0 else 0,
            'average_scene_duration': np.mean([s['duration'] for s in scenes]) if scenes else 0
        }

class MotionAnalyzer:
    """运动分析器"""
    
    def analyze_motion(self, video_path: str, sample_rate: int = 10) -> Dict[str, Any]:
        """分析视频运动特征"""
        cap = cv2.VideoCapture(video_path)
        
        motion_scores = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                # 转换为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 计算运动分数（基于拉普拉斯算子）
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                motion_scores.append(laplacian_var)
            
            frame_count += 1
        
        cap.release()
        
        if not motion_scores:
            return {
                'average_motion': 0.0,
                'motion_consistency': 0.0,
                'motion_variance': 0.0,
                'motion_trend': 'stable'
            }
        
        # 归一化运动分数
        motion_scores = np.array(motion_scores)
        normalized_scores = (motion_scores - np.min(motion_scores)) / (np.max(motion_scores) - np.min(motion_scores))
        
        return {
            'average_motion': float(np.mean(normalized_scores)),
            'motion_consistency': float(1.0 - np.std(normalized_scores)),
            'motion_variance': float(np.var(normalized_scores)),
            'motion_trend': self._analyze_motion_trend(normalized_scores)
        }
    
    def _analyze_motion_trend(self, motion_scores: np.ndarray) -> str:
        """分析运动趋势"""
        if len(motion_scores) < 2:
            return 'stable'
        
        # 计算趋势
        trend = np.polyfit(range(len(motion_scores)), motion_scores, 1)[0]
        
        if trend > 0.01:
            return 'increasing'
        elif trend < -0.01:
            return 'decreasing'
        else:
            return 'stable'

class ColorAnalyzer:
    """颜色分析器"""
    
    def analyze_colors(self, video_path: str, sample_rate: int = 10) -> Dict[str, Any]:
        """分析视频颜色特征"""
        cap = cv2.VideoCapture(video_path)
        
        brightness_scores = []
        saturation_scores = []
        color_histograms = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                # 转换为HSV色彩空间
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # 计算亮度
                brightness = np.mean(hsv[:, :, 2])
                brightness_scores.append(brightness / 255.0)
                
                # 计算饱和度
                saturation = np.mean(hsv[:, :, 1])
                saturation_scores.append(saturation / 255.0)
                
                # 计算颜色直方图
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                color_histograms.append(hist)
            
            frame_count += 1
        
        cap.release()
        
        if not brightness_scores:
            return {
                'average_brightness': 0.5,
                'average_saturation': 0.5,
                'dominant_colors': [],
                'color_temperature': 'neutral',
                'color_harmony_score': 0.5
            }
        
        # 分析颜色特征
        avg_brightness = np.mean(brightness_scores)
        avg_saturation = np.mean(saturation_scores)
        
        # 计算主导颜色
        dominant_colors = self._extract_dominant_colors(color_histograms)
        
        # 分析色温
        color_temperature = self._analyze_color_temperature(color_histograms)
        
        # 计算颜色和谐度
        color_harmony = self._calculate_color_harmony(color_histograms)
        
        return {
            'average_brightness': float(avg_brightness),
            'average_saturation': float(avg_saturation),
            'dominant_colors': dominant_colors,
            'color_temperature': color_temperature,
            'color_harmony_score': float(color_harmony)
        }
    
    def _extract_dominant_colors(self, histograms: List[np.ndarray]) -> List[Dict[str, Any]]:
        """提取主导颜色"""
        if not histograms:
            return []
        
        # 计算平均直方图
        avg_hist = np.mean(histograms, axis=0)
        
        # 找到最显著的颜色
        top_indices = np.argsort(avg_hist)[-5:]  # 取前5个最显著的颜色
        
        dominant_colors = []
        for idx in reversed(top_indices):
            # 将索引转换为RGB值
            b = (idx // 64) % 8 * 32
            g = (idx // 8) % 8 * 32
            r = idx % 8 * 32
            
            dominant_colors.append({
                'rgb': [r, g, b],
                'hex': f'#{r:02x}{g:02x}{b:02x}',
                'weight': float(avg_hist[idx])
            })
        
        return dominant_colors
    
    def _analyze_color_temperature(self, histograms: List[np.ndarray]) -> str:
        """分析色温"""
        if not histograms:
            return 'neutral'
        
        # 简化的色温分析
        avg_hist = np.mean(histograms, axis=0)
        
        # 计算暖色调和冷色调的比例
        warm_colors = np.sum(avg_hist[0:32])  # 红色和橙色
        cool_colors = np.sum(avg_hist[32:64])  # 蓝色和青色
        
        if warm_colors > cool_colors * 1.5:
            return 'warm'
        elif cool_colors > warm_colors * 1.5:
            return 'cool'
        else:
            return 'neutral'
    
    def _calculate_color_harmony(self, histograms: List[np.ndarray]) -> float:
        """计算颜色和谐度"""
        if not histograms:
            return 0.5
        
        # 简化的颜色和谐度计算
        avg_hist = np.mean(histograms, axis=0)
        
        # 计算颜色分布的均匀性
        color_variance = np.var(avg_hist)
        max_variance = np.var(np.ones_like(avg_hist))
        
        # 归一化和谐度分数
        harmony_score = 1.0 - (color_variance / max_variance)
        
        return np.clip(harmony_score, 0.0, 1.0)

class ContentAnalyzer:
    """内容分析器"""
    
    def analyze_content(self, video_path: str, sample_rate: int = 30) -> Dict[str, Any]:
        """分析视频内容特征"""
        cap = cv2.VideoCapture(video_path)
        
        content_features = {
            'has_people': False,
            'has_objects': False,
            'has_text': False,
            'has_landscape': False,
            'has_motion': False,
            'content_complexity': 0.0
        }
        
        frame_count = 0
        feature_scores = defaultdict(list)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                # 简化的内容检测
                frame_features = self._analyze_frame_content(frame)
                
                for feature, score in frame_features.items():
                    feature_scores[feature].append(score)
            
            frame_count += 1
        
        cap.release()
        
        # 汇总特征
        for feature, scores in feature_scores.items():
            avg_score = np.mean(scores)
            content_features[feature] = avg_score > 0.5
        
        # 计算内容复杂度
        content_features['content_complexity'] = self._calculate_content_complexity(feature_scores)
        
        return content_features
    
    def _analyze_frame_content(self, frame: np.ndarray) -> Dict[str, float]:
        """分析单帧内容"""
        features = {
            'has_people': 0.0,
            'has_objects': 0.0,
            'has_text': 0.0,
            'has_landscape': 0.0,
            'has_motion': 0.0
        }
        
        # 简化的特征检测（实际应用中可以使用更复杂的模型）
        
        # 检测边缘密度（可能表示物体）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (frame.shape[0] * frame.shape[1])
        features['has_objects'] = min(edge_density * 10, 1.0)
        
        # 检测颜色变化（可能表示风景）
        color_variance = np.var(frame)
        features['has_landscape'] = min(color_variance / 10000, 1.0)
        
        # 检测亮度变化（可能表示运动）
        brightness_variance = np.var(gray)
        features['has_motion'] = min(brightness_variance / 1000, 1.0)
        
        return features
    
    def _calculate_content_complexity(self, feature_scores: Dict[str, List[float]]) -> float:
        """计算内容复杂度"""
        if not feature_scores:
            return 0.0
        
        # 基于特征数量和强度计算复杂度
        complexity = 0.0
        
        for feature, scores in feature_scores.items():
            avg_score = np.mean(scores)
            complexity += avg_score
        
        # 归一化到0-1范围
        return min(complexity / len(feature_scores), 1.0)

class StyleAnalyzer:
    """风格分析器"""
    
    def analyze_style(self, video_path: str) -> Dict[str, float]:
        """分析视频风格特征"""
        # 这里可以实现更复杂的风格分析
        # 目前返回默认值
        return {
            'modern_score': 0.5,
            'vintage_score': 0.3,
            'minimalist_score': 0.4,
            'dynamic_score': 0.6,
            'artistic_score': 0.4,
            'professional_score': 0.7
        }
