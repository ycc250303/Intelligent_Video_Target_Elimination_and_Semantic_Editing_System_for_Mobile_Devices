#!/usr/bin/env python3
"""
MoviePy 视频编辑器实现
基于 MoviePy 库的视频编辑功能
"""

import os
import gc
import uuid
import logging
import psutil
import numpy as np
import retrying
from typing import Optional
from abc import ABC, abstractmethod
from moviepy.editor import (
    VideoFileClip, 
    concatenate_videoclips, 
    vfx, 
    TextClip, 
    CompositeVideoClip, 
    AudioFileClip, 
    CompositeAudioClip
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AbstractVideoEditor(ABC):
    """视频编辑器的抽象基类，定义所有视频编辑器必须实现的接口"""
    
    @abstractmethod
    def __init__(self, input_video: str):
        """初始化视频编辑器"""
        pass
        
    @abstractmethod
    def trim(self, start: float = 0.0, end: Optional[float] = None):
        """裁剪视频"""
        pass
        
    @abstractmethod
    def add_transition(self, type: str = "fade", duration: float = 1.0, start_time: float = 0.0):
        """添加转场效果"""
        pass
        
    @abstractmethod
    def adjust_speed(self, factor: float = 1.0):
        """调整视频播放速度"""
        pass
        
    @abstractmethod
    def add_text(self, text: str, fontsize: int = 24, duration: float = 5.0, position: str = "center"):
        """添加字幕（抽象接口）"""
        pass
        
    @abstractmethod
    def concatenate(self, second_video: str):
        """合并另一个视频"""
        pass
        
    @abstractmethod
    def adjust_volume(self, factor: float = 1.0):
        """调整视频音量"""
        pass
        
    @abstractmethod
    def rotate(self, angle: float = 90.0):
        """旋转视频"""
        pass
        
    @abstractmethod
    def crop(self, x1: float = 0.0, y1: float = 0.0, x2: float = None, y2: float = None):
        """裁剪画面"""
        pass
        
    @abstractmethod
    def add_background_music(self, audio_file: str, mix: bool = False):
        """添加背景音乐"""
        pass
        
    @abstractmethod
    def adjust_brightness(self, factor: float = 1.0):
        """调整亮度"""
        pass

    @abstractmethod
    def adjust_contrast(self, factor: float = 1.0):
        """调整对比度"""
        pass
        
    @abstractmethod
    def save(self):
        """保存编辑后的视频"""
        pass
        
    @abstractmethod
    def close(self):
        """关闭视频剪辑，释放资源"""
        pass

class MoviePyVideoEditor(AbstractVideoEditor):
    """基于 MoviePy 的视频编辑器实现"""
    
    def __init__(self, input_video: str):
        """
        初始化视频编辑器。

        Args:
            input_video: 输入视频文件路径。
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件 {input_video} 不存在")
        self.video_clip = VideoFileClip(input_video)
        self.output_path = f"output_video_{uuid.uuid4()}.mp4"
        # 持有子剪辑引用，避免在渲染前被关闭
        self._child_clips = []
        logger.info(f"已加载视频: {input_video}, 时长: {self.video_clip.duration}秒")

    def _parse_duration_expression(self, expression: str) -> float:
        """
        解析包含"总时长"的表达式，计算具体的时间值。
        
        Args:
            expression: 包含"总时长"的表达式字符串，如"总时长/2"、"总时长*3/4"等
            
        Returns:
            float: 计算后的具体时间值
        """
        if not isinstance(expression, str):
            return float(expression)
            
        # 如果表达式不包含"总时长"，直接转换
        if "总时长" not in expression:
            try:
                return float(expression)
            except ValueError:
                raise ValueError(f"无法解析时间表达式: {expression}")
        
        # 获取视频总时长
        total_duration = self.video_clip.duration
        logger.info(f"视频总时长: {total_duration}秒")
        
        # 替换"总时长"为实际数值
        expression = expression.replace("总时长", str(total_duration))
        logger.info(f"替换后的表达式: {expression}")
        
        try:
            # 安全地计算表达式
            # 只允许基本的数学运算：+、-、*、/、()
            allowed_chars = set("0123456789.+-*/() ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError(f"表达式包含不允许的字符: {expression}")
            
            # 使用eval计算表达式（在受控环境下）
            result = eval(expression)
            return float(result)
        except Exception as e:
            raise ValueError(f"无法计算时间表达式 '{expression}': {e}")

    def trim(self, start: float = 0.0, end: Optional[float] = None):
        """裁剪视频。"""
        end = end if end is not None else self.video_clip.duration
        if start >= self.video_clip.duration:
            raise ValueError("起始时间超出视频时长")
        if end is not None and end <= start:
            raise ValueError("结束时间必须大于起始时间")
        # 只裁剪时间，不做任何分辨率修改
        original_size = (self.video_clip.w, self.video_clip.h)
        self.video_clip = self.video_clip.subclip(start, end)
        logger.info(f"已裁剪视频: start={start}, end={end}")

    def add_transition(self, type: str = "fade", duration: float = 1.0, start_time: float = 0.0):
        """添加转场效果（目前支持淡入淡出）。"""
        # 将 crossfade 映射到 fade，因为 MoviePy 不支持 crossfade
        if type == "crossfade":
            type = "fade"
            logger.info("将 crossfade 转场类型映射为 fade")
            
        if type == "fade":
            # 检查开始时间是否有效
            if start_time < 0:
                raise ValueError("开始时间不能为负数")
            if start_time >= self.video_clip.duration:
                raise ValueError("开始时间超出视频时长")
            
            # 添加淡入淡出效果，从指定时间开始
            if start_time == 0.0:
                # 从开头开始，添加淡入效果
                self.video_clip = self.video_clip.fadein(duration)
                logger.info(f"已添加淡入效果，持续时间={duration}秒")
            else:
                # 从指定时间开始，添加淡出效果
                # 创建两个片段：开始到指定时间，指定时间到结束
                before_clip = self.video_clip.subclip(0, start_time)
                after_clip = self.video_clip.subclip(start_time).fadein(duration)
                
                # 合并两个片段
                self.video_clip = concatenate_videoclips([before_clip, after_clip])
                logger.info(f"已在第 {start_time} 秒添加淡入转场效果，持续时间={duration}秒")
        else:
            logger.warning(f"不支持的转场类型: {type}")

    def adjust_speed(self, factor: float = 1.0):
        """调整视频播放速度。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if factor <= 0:
            raise ValueError("速度倍数必须大于 0")
        self.video_clip = self.video_clip.fx(vfx.speedx, factor)
        logger.info(f"已调整视频速度为 {factor} 倍")

    def add_text(self, text: str, fontsize: int = 24, duration: float = 5.0, position: str = "center"):
        """MoviePy 版本不再支持字幕，请改用 FFmpeg 编辑器。"""
        raise NotImplementedError("MoviePyVideoEditor 不支持 add_text，请使用 editor=ffmpeg")

    def _ensure_audio_track(self, clip):
        """若 clip 无音轨，则填充同等时长的静音音轨。"""
        if clip.audio is None:
            silent = self._silent_audio(clip.duration)
            return clip.set_audio(silent)
        return clip

    def _silent_audio(self, duration: float, fps: int = 44100, channels: int = 2):
        """构造指定时长的静音音轨。"""
        from moviepy.audio.AudioClip import AudioClip
        def make_frame(t):
            # 确保返回正确的音频帧格式：对于立体声，返回 (2,) 数组
            # 对于单声道，返回 (1,) 数组
            return np.zeros((channels,), dtype=np.float32)
        
        # 创建静音音频剪辑
        silent_clip = AudioClip(make_frame, duration=duration)
        # 设置正确的采样率
        silent_clip = silent_clip.set_fps(fps)
        # 确保音频格式正确
        return silent_clip

    def concatenate(self, second_video: str, transition: str = "none", transition_duration: float = 1.0):
        """
        合并另一个视频，支持转场效果。
        
        Args:
            second_video: 第二个视频文件路径
            transition: 转场效果类型 ("none", "fade")
            transition_duration: 转场持续时间（秒）
        """
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if not os.path.exists(second_video):
            raise FileNotFoundError(f"第二个视频文件 {second_video} 不存在")
        
        # 加载并规范化音轨
        second_clip = VideoFileClip(second_video)
        try:
            # 确保两个视频都有音频轨道
            clip1 = self._ensure_audio_track(self.video_clip)
            clip2 = self._ensure_audio_track(second_clip)
            # 保持对子剪辑的引用，防止提前回收
            self._child_clips.extend([second_clip, clip1, clip2])

            # 应用转场效果
            if transition == "fade":
                # 应用淡出和淡入效果
                clip1_fadeout = clip1.fadeout(transition_duration)
                clip2_fadein = clip2.fadein(transition_duration)
                self._child_clips.extend([clip1_fadeout, clip2_fadein])
                
                # 合并视频，确保音频轨道完整
                result = concatenate_videoclips([clip1_fadeout, clip2_fadein], method="compose")
                
                # 验证合并后的音频轨道
                if result.audio is None:
                    logger.warning("合并后音频轨道丢失，重新添加静音轨道")
                    result = result.set_audio(self._silent_audio(result.duration))
                    
            elif transition == "crossfade":
                # 交叉淡化：第二段做交叉淡入，并在拼接时使用负 padding 对齐重叠区间
                clip2_cf = clip2.crossfadein(transition_duration)
                self._child_clips.append(clip2_cf)
                result = concatenate_videoclips([clip1, clip2_cf], method="compose", padding=-transition_duration)
                
                # 验证合并后的音频轨道
                if result.audio is None:
                    logger.warning("交叉淡化后音频轨道丢失，重新添加静音轨道")
                    result = result.set_audio(self._silent_audio(result.duration))
            else:
                # 无转场效果，直接合并
                result = concatenate_videoclips([clip1, clip2], method="compose")
                
                # 验证合并后的音频轨道
                if result.audio is None:
                    logger.warning("合并后音频轨道丢失，重新添加静音轨道")
                    result = result.set_audio(self._silent_audio(result.duration))

            # 最终验证：确保结果有有效的音频轨道
            if result.audio is None:
                logger.warning("最终音频轨道验证失败，强制添加静音轨道")
                result = result.set_audio(self._silent_audio(result.duration))
            
            # 替换当前视频
            self.video_clip = result
            logger.info(f"已合并视频: {second_video}")
            logger.info(f"转场效果: {transition}, 持续时间: {transition_duration}s")
            
        except Exception as e:
            logger.error(f"视频合并失败: {e}")
            # 如果转场效果失败，尝试无转场合并
            try:
                logger.info("尝试无转场合并...")
                clip1 = self._ensure_audio_track(self.video_clip)
                clip2 = self._ensure_audio_track(second_clip)
                self._child_clips.extend([second_clip, clip1, clip2])
                result = concatenate_videoclips([clip1, clip2], method="compose")
                
                if result.audio is None:
                    result = result.set_audio(self._silent_audio(result.duration))
                
                self.video_clip = result
                logger.info(f"无转场合并成功: {second_video}")
            except Exception as fallback_e:
                logger.error(f"无转场合并也失败: {fallback_e}")
                raise fallback_e
        finally:
            # 不在此处关闭 second_clip，由 close() 统一管理
            pass

    def concatenate_multiple(self, video_files: list, transition: str = "none", transition_duration: float = 1.0):
        """
        合并多个视频文件。
        
        Args:
            video_files: 视频文件路径列表
            transition: 转场效果类型 ("none", "fade")
            transition_duration: 转场持续时间（秒）
        """
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if not video_files:
            logger.warning("没有提供要合并的视频文件")
            return
        
        # 收集并规范化片段
        loaded = []
        for path in video_files:
            if not os.path.exists(path):
                logger.warning(f"视频文件不存在，跳过: {path}")
                continue
            c = VideoFileClip(path)
            loaded.append(c)

        try:
            clips = [self._ensure_audio_track(self.video_clip)] + [self._ensure_audio_track(c) for c in loaded]
            # 保持对子剪辑的引用
            self._child_clips.extend(loaded)
            self._child_clips.extend(clips)

            if transition == "none":
                result = concatenate_videoclips(clips, method="compose")
            elif transition == "fade":
                proc = []
                for i, c in enumerate(clips):
                    if i > 0:
                        c = c.fadein(transition_duration)
                    if i < len(clips) - 1:
                        c = c.fadeout(transition_duration)
                    proc.append(c)
                self._child_clips.extend(proc)
                result = concatenate_videoclips(proc, method="compose")
            elif transition == "crossfade":
                proc = [clips[0]]
                for i in range(1, len(clips)):
                    proc.append(clips[i].crossfadein(transition_duration))
                self._child_clips.extend(proc)
                result = concatenate_videoclips(proc, method="compose", padding=-transition_duration)
            else:
                result = concatenate_videoclips(clips, method="compose")

            # 验证合并后的音频轨道
            if result.audio is None:
                logger.warning("多视频合并后音频轨道丢失，重新添加静音轨道")
                result = result.set_audio(self._silent_audio(result.duration))
            
            # 最终验证
            if result.audio is None:
                logger.warning("最终音频轨道验证失败，强制添加静音轨道")
                result = result.set_audio(self._silent_audio(result.duration))
                
            self.video_clip = result
            logger.info(f"已合并 {1 + len(loaded)} 段视频，转场={transition}, 时长={transition_duration}s")
        except Exception as e:
            logger.error(f"多视频合并失败: {e}")
            # 如果转场效果失败，尝试无转场合并
            try:
                logger.info("尝试无转场多视频合并...")
                clips = [self._ensure_audio_track(self.video_clip)] + [self._ensure_audio_track(c) for c in loaded]
                self._child_clips.extend(loaded)
                self._child_clips.extend(clips)
                result = concatenate_videoclips(clips, method="compose")
                
                if result.audio is None:
                    result = result.set_audio(self._silent_audio(result.duration))
                
                self.video_clip = result
                logger.info(f"无转场多视频合并成功，共 {1 + len(loaded)} 段")
            except Exception as fallback_e:
                logger.error(f"无转场多视频合并也失败: {fallback_e}")
                raise fallback_e
        finally:
            # 不在此处关闭 loaded，由 close() 统一管理
            pass

    def adjust_volume(self, factor: float = 1.0):
        """调整视频音量。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if factor < 0:
            raise ValueError("音量倍数必须非负")
        self.video_clip = self.video_clip.volumex(factor)
        logger.info(f"已调整音量为 {factor} 倍")

    def rotate(self, angle: float = 90.0):
        """旋转视频。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        self.video_clip = self.video_clip.rotate(angle)
        logger.info(f"已旋转视频: 角度={angle}度")

    def crop(self, x1: float = 0.0, y1: float = 0.0, x2: float = None, y2: float = None):
        """裁剪画面。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if x2 is None or y2 is None:
            raise ValueError("x2 和 y2 必须指定")
        if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
            raise ValueError("裁剪坐标无效")
        if x2 > self.video_clip.w or y2 > self.video_clip.h:
            raise ValueError("裁剪坐标超出视频尺寸")
        self.video_clip = self.video_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
        logger.info(f"已裁剪画面: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    def add_background_music(
        self, 
        audio_file: str, 
        video_start_time: float = 0.0,
        video_end_time: float = None,
        audio_start_time: float = 0.0,
        audio_end_time: float = None,
        mix: bool = False,
        overwrite: bool = False,
    ):
        """
        添加背景音乐，支持精确的时间控制。
        
        Args:
            audio_file: 音频文件路径
            video_start_time: 在视频中添加音频的起始时间（秒）
            video_end_time: 在视频中添加音频的结束时间（秒），None表示到视频结尾
            audio_start_time: 音频文件的起始时间（秒）
            audio_end_time: 音频文件的结束时间（秒），None表示到音频结尾
            mix: 是否与原音频混合（向后兼容，若提供 overwrite 则以 overwrite 为准）
            overwrite: 是否覆盖选中视频时间段的原音频（True=覆盖，仅保留新音频；False=共存）
        """
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 {audio_file} 不存在")
        
        # 设置默认值
        if video_end_time is None:
            video_end_time = self.video_clip.duration
        if audio_end_time is None:
            audio_probe = AudioFileClip(audio_file)
            audio_end_time = audio_probe.duration
            audio_probe.close()
        
        # 验证时间参数
        if video_start_time < 0 or video_start_time >= self.video_clip.duration:
            raise ValueError(f"视频起始时间 {video_start_time} 无效，应在 0 到 {self.video_clip.duration} 之间")
        if video_end_time <= video_start_time:
            raise ValueError(f"视频结束时间 {video_end_time} 必须大于起始时间 {video_start_time}")
        if video_end_time > self.video_clip.duration:
            raise ValueError(f"视频结束时间 {video_end_time} 超出视频总时长 {self.video_clip.duration}")
        
        # 计算音频持续时间（必须与视频区间时长一致）
        audio_duration = audio_end_time - audio_start_time
        video_audio_duration = video_end_time - video_start_time
        if abs(audio_duration - video_audio_duration) > 0.1:
            raise ValueError(f"音频持续时间 {audio_duration}s 与视频音频持续时间 {video_audio_duration}s 不匹配")
        
        # 加载并裁剪音频片段
        segment_clip = AudioFileClip(audio_file).subclip(audio_start_time, audio_end_time)
        
        # 基础音频（原音频或静音）
        base_audio = self.video_clip.audio if self.video_clip.audio is not None else self._silent_audio(self.video_clip.duration)
        
        if overwrite:
            # 覆盖模式：区间内仅保留新音频，区间外保留原音频
            def combined_frame(t):
                if t < 0 or t > self.video_clip.duration:
                    return np.zeros((2,), dtype=np.float32)  # 返回立体声静音帧
                if video_start_time <= t <= video_end_time:
                    nt = t - video_start_time
                    if nt < segment_clip.duration:
                        try:
                            frame = segment_clip.get_frame(nt)
                            # 确保返回正确的音频帧格式
                            if frame is None:
                                return np.zeros((2,), dtype=np.float32)
                            # 如果是单声道，转换为立体声
                            if len(frame.shape) == 1 or frame.shape[0] == 1:
                                return np.tile(frame, (2,))
                            return frame
                        except Exception as e:
                            logger.warning(f"获取音频片段帧失败: {e}")
                            return np.zeros((2,), dtype=np.float32)
                    else:
                        return np.zeros((2,), dtype=np.float32)
                # 区间外：保留原音频
                try:
                    if base_audio is not None and t < base_audio.duration:
                        frame = base_audio.get_frame(t)
                        if frame is None:
                            return np.zeros((2,), dtype=np.float32)
                        # 如果是单声道，转换为立体声
                        if len(frame.shape) == 1 or frame.shape[0] == 1:
                            return np.tile(frame, (2,))
                        return frame
                    else:
                        return np.zeros((2,), dtype=np.float32)
                except Exception as e:
                    logger.warning(f"获取原音频帧失败: {e}")
                    return np.zeros((2,), dtype=np.float32)
            
            from moviepy.audio.AudioClip import AudioClip
            combined = AudioClip(combined_frame, duration=self.video_clip.duration).set_fps(44100)
            final_audio = combined
        else:
            # 共存模式：在区间内叠加新音频与原音频（使用 set_start 进行对齐）
            segment_started = segment_clip.set_start(video_start_time)
            final_audio = CompositeAudioClip([base_audio, segment_started])
        
        self.video_clip = self.video_clip.set_audio(final_audio)
        logger.info(f"已添加背景音乐: {audio_file}")
        logger.info(f"视频时间: {video_start_time}s - {video_end_time}s")
        logger.info(f"音频时间: {audio_start_time}s - {audio_end_time}s")
        logger.info(f"覆盖原音频: {overwrite}")

    def add_audio_segment(
        self,
        audio_file: str,
        video_start_time: float,
        video_end_time: float,
        audio_start_time: float = 0.0,
        audio_end_time: float = None,
        volume: float = 1.0,
        mix: bool = True,
        overwrite: bool = False,
    ):
        """
        在视频的特定时间段添加音频片段。
        
        Args:
            audio_file: 音频文件路径
            video_start_time: 在视频中添加音频的起始时间（秒）
            video_end_time: 在视频中添加音频的结束时间（秒）
            audio_start_time: 音频文件的起始时间（秒）
            audio_end_time: 音频文件的结束时间（秒），None表示到音频结尾
            volume: 音频音量倍数
            mix: 是否与原音频混合（向后兼容，若提供 overwrite 则以 overwrite 为准）
            overwrite: 是否覆盖选中视频时间段的原音频（True=覆盖，仅保留新音频；False=共存）
        """
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 {audio_file} 不存在")
        
        # 设置默认值
        if audio_end_time is None:
            temp_audio = AudioFileClip(audio_file)
            audio_end_time = temp_audio.duration
            temp_audio.close()
        
        # 验证时间参数
        if video_start_time < 0 or video_start_time >= self.video_clip.duration:
            raise ValueError(f"视频起始时间 {video_start_time} 无效，应在 0 到 {self.video_clip.duration} 之间")
        if video_end_time <= video_start_time:
            raise ValueError(f"视频结束时间 {video_end_time} 必须大于起始时间 {video_start_time}")
        if video_end_time > self.video_clip.duration:
            raise ValueError(f"视频结束时间 {video_end_time} 超出视频总时长 {self.video_clip.duration}")
        
        # 计算音频持续时间（必须与视频区间时长一致）
        audio_duration = audio_end_time - audio_start_time
        video_audio_duration = video_end_time - video_start_time
        if abs(audio_duration - video_audio_duration) > 0.1:
            raise ValueError(f"音频持续时间 {audio_duration}s 与视频音频持续时间 {video_audio_duration}s 不匹配")
        
        # 加载并裁剪音频
        segment_clip = AudioFileClip(audio_file).subclip(audio_start_time, audio_end_time)
        
        # 调整音量
        if volume != 1.0:
            segment_clip = segment_clip.volumex(volume)
        
        # 基础音频（原音频或静音）
        base_audio = self.video_clip.audio if self.video_clip.audio is not None else self._silent_audio(self.video_clip.duration)
        
        if overwrite:
            # 覆盖模式：区间内仅保留新音频，区间外保留原音频
            def combined_frame(t):
                if t < 0 or t > self.video_clip.duration:
                    return np.zeros((2,), dtype=np.float32)  # 返回立体声静音帧
                if video_start_time <= t <= video_end_time:
                    nt = t - video_start_time
                    if nt < segment_clip.duration:
                        try:
                            frame = segment_clip.get_frame(nt)
                            # 确保返回正确的音频帧格式
                            if frame is None:
                                return np.zeros((2,), dtype=np.float32)
                            # 如果是单声道，转换为立体声
                            if len(frame.shape) == 1 or frame.shape[0] == 1:
                                return np.tile(frame, (2,))
                            return frame
                        except Exception as e:
                            logger.warning(f"获取音频片段帧失败: {e}")
                            return np.zeros((2,), dtype=np.float32)
                    else:
                        return np.zeros((2,), dtype=np.float32)
                # 区间外：保留原音频
                try:
                    if base_audio is not None and t < base_audio.duration:
                        frame = base_audio.get_frame(t)
                        if frame is None:
                            return np.zeros((2,), dtype=np.float32)
                        # 如果是单声道，转换为立体声
                        if len(frame.shape) == 1 or frame.shape[0] == 1:
                            return np.tile(frame, (2,))
                        return frame
                    else:
                        return np.zeros((2,), dtype=np.float32)
                except Exception as e:
                    logger.warning(f"获取原音频帧失败: {e}")
                    return np.zeros((2,), dtype=np.float32)
            
            from moviepy.audio.AudioClip import AudioClip
            combined = AudioClip(combined_frame, duration=self.video_clip.duration).set_fps(44100)
            final_audio = combined
        else:
            # 共存模式：叠加新音频（对齐起点）
            segment_started = segment_clip.set_start(video_start_time)
            final_audio = CompositeAudioClip([base_audio, segment_started])
        
        self.video_clip = self.video_clip.set_audio(final_audio)
        logger.info(f"已在视频时间段 {video_start_time}s - {video_end_time}s 添加音频: {audio_file}")
        logger.info(f"音频时间段: {audio_start_time}s - {audio_end_time}s")
        logger.info(f"音量倍数: {volume}, 覆盖原音频: {overwrite}")

    def adjust_brightness(self, factor: float = 1.0):
        """调整亮度。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if factor <= 0:
            raise ValueError("亮度倍数必须大于 0")
        self.video_clip = self.video_clip.fx(vfx.colorx, factor)
        logger.info(f"已调整亮度为 {factor} 倍")

    def adjust_contrast(self, factor: float = 1.0):
        """调整对比度。"""
        if self.video_clip is None:
            raise ValueError("视频剪辑未初始化或已被关闭")
        if factor <= 0:
            raise ValueError("对比度倍数必须大于 0")
        # 使用 moviepy 的 lum_contrast 实现对比度调整
        self.video_clip = self.video_clip.fx(vfx.lum_contrast, contrast=factor)
        logger.info(f"已调整对比度为 {factor} 倍")
        
    def save(self):
        """保存编辑后的视频。"""
        if not hasattr(self, 'output_path') or not self.output_path:
            raise ValueError("未设置输出路径")
        # 使用原始分辨率保存，不做任何压缩或修改
        self.video_clip.write_videofile(
            self.output_path,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            ffmpeg_params=["-pix_fmt", "yuv420p"]
        )
        logger.info(f"视频已保存至: {self.output_path}")

    def close(self):
        """关闭视频剪辑，释放资源。"""
        if hasattr(self, 'video_clip') and self.video_clip:
            if hasattr(self.video_clip, 'audio') and self.video_clip.audio:
                self.video_clip.audio.close()
            self.video_clip.close()
            self.video_clip = None
        # 关闭并清空子剪辑
        if hasattr(self, '_child_clips') and self._child_clips:
            for c in self._child_clips:
                try:
                    if hasattr(c, 'audio') and c.audio:
                        c.audio.close()
                    c.close()
                except Exception:
                    pass
            self._child_clips = []
        gc.collect()
        logger.info("视频剪辑已关闭")

    @retrying.retry(stop_max_attempt_number=3, wait_fixed=200)
    def _remove_temp_file(self, temp_output: str):
        """尝试删除临时文件，重试 3 次，每次间隔 200ms。"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in ['ffmpeg.exe', 'ffmpeg']:
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except psutil.Error as e:
                    logger.warning(f"终止 ffmpeg 进程失败: {e}")
        os.remove(temp_output)
        logger.info(f"临时文件 {temp_output} 已删除")

    def execute_action(self, action_str: str, operations: dict) -> bool:
        """
        根据解析的操作指令执行视频编辑。

        Args:
            action_str: LLM 返回的操作指令，例如 'action: trim start=10 end=20'.
            operations: 支持的操作字典
            
        Returns:
            bool: 操作是否成功执行
        """
        # 检查编辑器状态
        if not hasattr(self, 'video_clip') or self.video_clip is None:
            error_msg = "视频剪辑未初始化或已被关闭"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not action_str:
            error_msg = "未收到有效的操作指令"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        try:
            logger.info(f"执行操作: {action_str}")
            action_parts = action_str.strip().split()
            if not action_parts or action_parts[0] != 'action:':
                error_msg = "无效的 action 格式"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            action = action_parts[1]
            if action not in operations:
                error_msg = f"不支持的操作: {action}"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            params = {}
            for param in action_parts[2:]:
                key, value = param.split('=')
                params[key] = value

            operation = operations[action]
            parsed_params = {}
            for param_name, param_info in operation['params'].items():
                if param_name in params:
                    try:
                        if param_info['type'] is bool:
                            parsed_params[param_name] = params[param_name].lower() == 'true'
                        elif param_info['type'] is float and isinstance(params[param_name], str) and "总时长" in params[param_name]:
                            # 处理包含"总时长"的表达式
                            logger.info(f"解析总时长表达式: {params[param_name]}");
                            parsed_params[param_name] = self._parse_duration_expression(params[param_name])
                            logger.info(f"解析结果: {parsed_params[param_name]}");
                        elif param_info['type'] is float:
                            # 处理普通的浮点数参数
                            parsed_params[param_name] = float(params[param_name])
                        else:
                            parsed_params[param_name] = param_info['type'](params[param_name])
                    except ValueError:
                        error_msg = f"参数 {param_name} 格式错误: {params[param_name]}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                elif param_info['required']:
                    error_msg = f"缺少必需参数: {param_name}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                else:
                    parsed_params[param_name] = param_info['default']

            if action == 'trim':
                self.trim(**parsed_params)
            elif action == 'add_transition':
                self.add_transition(**parsed_params)
            elif action == 'speed':
                self.adjust_speed(**parsed_params)
            elif action == 'add_text':
                # 明确拒绝 MoviePy 的字幕能力
                raise NotImplementedError("MoviePy 不支持 add_text，请使用 editor=ffmpeg")
            elif action == 'concatenate':
                self.concatenate(**parsed_params)
            elif action == 'concatenate_multiple':
                self.concatenate_multiple(**parsed_params)
            elif action == 'adjust_volume':
                self.adjust_volume(**parsed_params)
            elif action == 'rotate':
                self.rotate(**parsed_params)
            elif action == 'crop':
                self.crop(**parsed_params)
            elif action == 'add_background_music':
                self.add_background_music(**parsed_params)
            elif action == 'adjust_brightness':
                self.adjust_brightness(**parsed_params)
            elif action == 'adjust_contrast':
                self.adjust_contrast(**parsed_params)
            elif action == 'add_audio_segment':
                self.add_audio_segment(**parsed_params)
            else:
                error_msg = f"未知操作: {action}"
                logger.warning(error_msg)
                raise ValueError(error_msg)
                
            return True

        except Exception as e:
            logger.error(f"编辑操作失败: {e}")
            raise  # 重新抛出异常，让调用方知道操作失败

if __name__ == "__main__":
    # 测试代码
    print("MoviePy 视频编辑器模块")
    print("这个模块提供了基于 MoviePy 的视频编辑功能")
