#!/usr/bin/env python3
"""
FFmpeg 视频编辑器实现
仅实现与 ffmpeg 流水线相关的能力，当前提供 add_text（硬字幕）能力：
- 位置默认底部居中
- 支持控制开始出现的时间与持续时长

使用方式：
- 通过累积滤镜（filters）在 save() 时一次性应用，避免多次有损转码
"""

import os
import uuid
import shlex
import logging
import subprocess
from typing import Optional, List, Tuple, Union

from moviepy_editor import AbstractVideoEditor  # 复用抽象接口，便于在现有流程中替换


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FFmpegVideoEditor(AbstractVideoEditor):
    """基于 FFmpeg 的视频编辑器实现（最小可用：add_text/save/close）。"""

    def __init__(self, input_video: str):
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件 {input_video} 不存在")
        self.input_video: str = os.path.abspath(input_video)
        self.filters: List[str] = []  # 累积 -vf 的过滤器，如 drawtext
        self.output_path: str = f"ffmpeg_output_{uuid.uuid4()}.mp4"
        self._duration: Optional[float] = None
        self._has_scale: bool = False

    def _get_video_duration(self) -> float:
        """使用 ffprobe 获取视频总时长（秒），结果缓存。"""
        if self._duration is not None:
            return self._duration
        input_ff = self.input_video.replace("\\", "/")
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_ff}"'
        try:
            result = subprocess.run(shlex.split(cmd), check=True, capture_output=True, text=True)
            self._duration = float(result.stdout.strip())
        except Exception as e:
            logger.error(f"获取视频时长失败: {e}")
            raise ValueError("无法获取视频总时长，请确认已安装 ffprobe 并视频文件可用")
        return self._duration

    # ---------- 未实现的接口：如需扩展可逐步补齐 ----------
    def trim(self, start: float = 0.0, end: Optional[float] = None):
        raise NotImplementedError("FFmpegVideoEditor.trim 尚未实现")

    def add_transition(self, type: str = "fade", duration: float = 1.0, start_time: float = 0.0):
        """
        添加转场效果，使用FFmpeg的fade过滤器实现淡入淡出。

        Args:
            type: 转场类型，目前支持 'fade'
            duration: 转场持续时间（秒）
            start_time: 转场开始时间（秒）
        """
        if type != "fade":
            raise ValueError(f"FFmpeg编辑器目前只支持 'fade' 类型的转场，收到: {type}")
        
        if duration <= 0:
            raise ValueError("转场持续时间必须大于 0")
        if start_time < 0:
            raise ValueError("转场开始时间不能为负")

        total = self._get_video_duration()
        if start_time >= total:
            raise ValueError(f"转场开始时间 {start_time}s 不能超过或等于视频总时长 {total:.3f}s")
        if start_time + duration > total:
            raise ValueError(
                f"转场结束时间 {start_time + duration:.3f}s 超过视频总时长 {total:.3f}s，请缩短持续时间或调整开始时间"
            )

        # 使用fade过滤器实现淡入淡出效果
        # 淡入：从start_time开始，持续duration秒
        fade_in = f"fade=t=in:st={start_time}:d={duration}"
        
        # 淡出：从start_time开始，持续duration秒
        fade_out = f"fade=t=out:st={start_time}:d={duration}"
        
        # 添加淡入淡出效果
        self.filters.append(fade_in)
        self.filters.append(fade_out)
        
        logger.info(
            f"已添加转场效果（ffmpeg）：type={type}, start={start_time}s, duration={duration}s"
        )

    def adjust_speed(self, factor: float = 1.0):
        raise NotImplementedError("FFmpegVideoEditor.adjust_speed 尚未实现")

    def make_black_and_white(self, start_time: float = 0.0, duration: float = 3.0):
        """
        将视频变为黑白效果。

        Args:
            start_time: 开始时间（秒），默认为0
            duration: 持续时间（秒），默认为1秒
        """
        if duration <= 0:
            raise ValueError("持续时间必须大于 0")
        if start_time < 0:
            raise ValueError("开始时间不能为负")

        total = self._get_video_duration()
        if start_time >= total:
            raise ValueError(f"开始时间 {start_time}s 不能超过或等于视频总时长 {total:.3f}s")
        if start_time + duration > total:
            raise ValueError(
                f"结束时间 {start_time + duration:.3f}s 超过视频总时长 {total:.3f}s，请缩短持续时间或调整开始时间"
            )

        # 使用hue过滤器将饱和度设为0，实现黑白效果
        # enable参数控制应用效果的时间段
        enable = f"between(t,{start_time},{start_time + duration})"
        
        # 创建hue过滤器，将饱和度设为0
        hue_filter = f"hue=s=0:enable='{enable}'"
        
        self.filters.append(hue_filter)
        logger.info(
            f"已添加黑白效果（ffmpeg）：start={start_time}s, duration={duration}s"
        )

    def add_text(self, text: str, fontsize: int = 72, duration: float = 5.0, position: str = "center", start_time: float = 0.0):
        """
        添加硬字幕（烧录），使用 drawtext 过滤器。

        Args:
            text: 字幕内容
            fontsize: 字号
            duration: 持续时间（秒）
            position: 位置标识（当前忽略，统一按底部居中渲染）
            start_time: 开始出现的时间（秒）
        """
        if not text:
            raise ValueError("字幕文本不能为空")
        if duration <= 0:
            raise ValueError("字幕持续时间必须大于 0")
        if start_time < 0:
            raise ValueError("开始时间不能为负")

        total = self._get_video_duration()
        if start_time >= total:
            raise ValueError(f"字幕开始时间 {start_time}s 不能超过或等于视频总时长 {total:.3f}s")
        if start_time + duration > total:
            raise ValueError(
                f"字幕结束时间 {start_time + duration:.3f}s 超过视频总时长 {total:.3f}s，请缩短持续时间或调整开始时间"
            )

        # 跨平台字体检测，优先使用电脑端最兼容的字体
        font_candidates = []
        
        # Windows 字体路径（电脑端优先）
        if os.name == 'nt':  # Windows 系统
            font_candidates.extend([
                r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑（最兼容）
                r"C:\Windows\Fonts\msyhbd.ttc",    # 微软雅黑粗体
                r"C:\Windows\Fonts\simhei.ttf",    # 黑体
                r"C:\Windows\Fonts\simsun.ttc",    # 宋体
                r"C:\Windows\Fonts\simkai.ttf",    # 楷体
                r"C:\Windows\Fonts\simfang.ttf",   # 仿宋
            ])
        else:  # Linux/Android/iOS 系统
            font_candidates.extend([
                "/system/fonts/DroidSansFallback.ttf",      # Android 系统字体
                "/system/fonts/NotoSansCJK-Regular.ttc",    # Android Noto 字体
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux 字体
                "/System/Library/Fonts/PingFang.ttc",       # iOS 字体
                "/System/Library/Fonts/STHeiti Light.ttc",  # iOS 字体
            ])
        
        # 添加通用字体路径（作为备选）
        font_candidates.extend([
            "arial.ttf",      # 通用字体
            "helvetica.ttf",  # 通用字体
            "sans-serif",     # 系统默认字体
        ])
        
        fontfile = None
        for font_path in font_candidates:
            if os.path.exists(font_path):
                fontfile = font_path
                logger.info(f"找到可用字体: {font_path}")
                break
        
        if not fontfile:
            logger.warning("未找到可用的字体文件，将使用系统默认字体")
            # 尝试使用系统默认字体，不指定具体路径
            fontfile = None

        # 统一用正斜杠，避免 ffmpeg 在 Windows 下解析反斜杠转义问题
        if fontfile:
            fontfile_ff = fontfile.replace("\\", "/")
            logger.info(f"使用字体文件: {fontfile_ff}，确保在电脑端生成兼容的视频")
        else:
            fontfile_ff = None
            logger.info("使用系统默认字体，可能在不同设备上显示效果不同")

        # 转义文本中的特殊字符（: ' \ 等）。用 \: 与 \' 规避解析问题
        safe_text = (
            text.replace("\\", "\\\\")  # 先转义反斜杠
                .replace(":", r"\:")
                .replace("'", r"\'")
        )

        # 底部居中：x=(w-text_w)/2, y=h-text_h-40（略上移避免贴边）
        x_expr = "(w-text_w)/2"
        y_expr = "h-text_h-40"

        enable = f"between(t,{start_time},{start_time + duration})"

        # 简化参数组合，避免复杂的参数导致FFmpeg解析失败
        drawtext_parts = []
        
        # 添加字体文件设置（如果可用）
        if fontfile_ff:
            drawtext_parts.insert(0, f"fontfile='{fontfile_ff}'")
            logger.info(f"使用指定字体: {fontfile_ff}")
        else:
            # 不指定字体文件，让系统使用默认字体
            logger.info("使用系统默认字体")
        
        # 基本参数
        drawtext_parts.extend([
            f"text='{safe_text}'",
            f"fontsize={fontsize}",
            "fontcolor=white",
            f"x={x_expr}",
            f"y={y_expr}",
            f"enable='{enable}'"
        ])
        
        # 添加边框和背景，提高可读性
        drawtext_parts.extend([
            "borderw=2",
            "bordercolor=black@0.8",
            "box=1",
            "boxcolor=black@0.5",
            "boxborderw=2"
        ])

        drawtext = "drawtext=" + ":".join(drawtext_parts)
        self.filters.append(drawtext)
        
        # 记录详细的字体信息
        font_info = f"字体={fontfile_ff if fontfile_ff else '系统默认'}"
        logger.info(
            f"已添加字幕（ffmpeg，电脑端处理）：text='{text}', start={start_time}s, duration={duration}s, fontsize={fontsize}, {font_info}"
        )
        logger.info("字幕在电脑端生成，使用电脑端字体，确保在手机上播放时字体显示正常")

    def set_resolution(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        keep_aspect: bool = True,
        fill_color: str = 'black',
        resolution: Optional[Union[str, Tuple[int, int], List[int]]] = None,
    ):
        """
        设置输出分辨率。默认保持原纵横比：先按比例缩放（不放大填满），再居中补边。

        Args:
            width: 目标宽度
            height: 目标高度
            keep_aspect: 是否保持纵横比（True 时 scale+pad；False 时直接 scale 拉伸）
            fill_color: 留白颜色（keep_aspect=True 时使用）
        """
        # 解析 resolution 参数（优先）
        if resolution is not None:
            w, h = self._parse_resolution(resolution)
        else:
            if width is None or height is None:
                raise ValueError("请提供 width 与 height，或提供 resolution 预设/字符串/元组")
            w, h = int(width), int(height)

        if w <= 0 or h <= 0:
            raise ValueError("width 和 height 必须为正整数")

        # 清除已存在的 scale/pad，避免重复叠加
        def _is_scale_or_pad(f: str) -> bool:
            head = f.split('=')[0].strip()
            return head in ("scale", "pad")

        if self._has_scale:
            self.filters = [f for f in self.filters if not _is_scale_or_pad(f)]
            self._has_scale = False

        if keep_aspect:
            scale = f"scale={w}:{h}:force_original_aspect_ratio=decrease"
            pad = f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={fill_color}"
            # 将几何处理放在最前，后续滤镜（如字幕）使用目标画布坐标
            self.filters.insert(0, pad)
            self.filters.insert(0, scale)
        else:
            scale = f"scale={w}:{h}"
            self.filters.insert(0, scale)

        self._has_scale = True
        logger.info(f"已设置输出分辨率为 {w}x{h}，keep_aspect={keep_aspect}, fill_color={fill_color}")

    def _parse_resolution(self, value: Union[str, Tuple[int, int], List[int]]) -> Tuple[int, int]:
        """解析 resolution 预设/字符串/元组为 (width, height)。
        支持：
        - 预设字符串：'1080p','720p','480p','360p'
        - 形如 '1920x1080' / '1920X1080' / '1920*1080'
        - (1920,1080) 或 [1920,1080]
        """
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return int(value[0]), int(value[1])

        if isinstance(value, str):
            preset_map = {
                '1080p': (1920, 1080),
                '720p': (1280, 720),
                '480p': (854, 480),
                '360p': (640, 360),
            }
            key = value.strip().lower()
            if key in preset_map:
                return preset_map[key]

            # 尝试解析 'WxH'
            for sep in ('x', 'X', '*'):
                if sep in key:
                    parts = key.split(sep)
                    if len(parts) == 2:
                        return int(parts[0]), int(parts[1])

        raise ValueError(f"无法解析 resolution: {value}，支持示例：'1080p'、'1280x720'、(1920,1080)")

    def add_subtitles(self, items: List[List], default_fontsize: int = 36):
        """
        批量添加连贯字幕。每个条目格式：
        [text, start_time, duration] 或 [text, start_time, duration, fontsize]

        Args:
            items: 字幕条目列表
            default_fontsize: 未提供字体大小时的默认值
        """
        if not isinstance(items, list) or not items:
            raise ValueError("items 必须为非空列表")

        # 先解析并收集区间，做一致性校验（开始时间 < 结束时间、区间不重叠、不得越界）
        total = self._get_video_duration()
        parsed: List[dict] = []
        for idx, it in enumerate(items):
            if not isinstance(it, (list, tuple)) or len(it) < 3:
                raise ValueError(f"第 {idx} 个字幕项格式错误，应为 [text, start, duration, (fontsize)]")
            text = str(it[0])
            try:
                start_time = float(it[1])
                duration = float(it[2])
            except Exception:
                raise ValueError(f"第 {idx} 个字幕项的时间参数无法转换为数字: {it[1]}, {it[2]}")

            if start_time < 0:
                raise ValueError(f"第 {idx} 个字幕项开始时间不能为负: start={start_time}")
            if duration <= 0:
                raise ValueError(f"第 {idx} 个字幕项持续时间必须大于 0: duration={duration}")

            end_time = start_time + duration
            if start_time >= end_time:
                raise ValueError(f"第 {idx} 个字幕项开始时间必须小于结束时间: start={start_time}, end={end_time}")
            if start_time >= total:
                raise ValueError(
                    f"第 {idx} 个字幕项开始时间 {start_time}s 不能超过或等于视频总时长 {total:.3f}s"
                )
            if end_time > total:
                raise ValueError(
                    f"第 {idx} 个字幕项结束时间 {end_time:.3f}s 超过视频总时长 {total:.3f}s"
                )

            fontsize = int(it[3]) if len(it) >= 4 else int(default_fontsize)
            parsed.append({
                "text": text,
                "start": start_time,
                "end": end_time,
                "duration": duration,
                "fontsize": fontsize,
                "index": idx,
            })

        # 按开始时间排序并校验重叠（允许首尾相接，不允许交叠）
        parsed.sort(key=lambda x: x["start"])
        for i in range(1, len(parsed)):
            prev = parsed[i-1]
            curr = parsed[i]
            if curr["start"] < prev["end"]:
                raise ValueError(
                    f"字幕时间区间不可重叠: 第 {prev['index']} 项 [{prev['start']},{prev['end']}) 与 第 {curr['index']} 项 [{curr['start']},{curr['end']}) 重叠"
                )

        # 校验通过后再逐条添加
        for item in parsed:
            self.add_text(
                text=item["text"],
                fontsize=item["fontsize"],
                duration=item["duration"],
                start_time=item["start"],
            )

    def concatenate(self, second_video: str):
        raise NotImplementedError("FFmpegVideoEditor.concatenate 尚未实现")

    def adjust_volume(self, factor: float = 1.0):
        raise NotImplementedError("FFmpegVideoEditor.adjust_volume 尚未实现")

    def rotate(self, angle: float = 90.0):
        raise NotImplementedError("FFmpegVideoEditor.rotate 尚未实现")

    def crop(self, x1: float = 0.0, y1: float = 0.0, x2: float = None, y2: float = None):
        raise NotImplementedError("FFmpegVideoEditor.crop 尚未实现")

    def add_background_music(self, audio_file: str, mix: bool = False):
        raise NotImplementedError("FFmpegVideoEditor.add_background_music 尚未实现")

    def adjust_brightness(self, factor: float = 1.0):
        raise NotImplementedError("FFmpegVideoEditor.adjust_brightness 尚未实现")

    def adjust_contrast(self, factor: float = 1.0):
        raise NotImplementedError("FFmpegVideoEditor.adjust_contrast 尚未实现")

    def save(self):
        """根据累积的 filters，调用 ffmpeg 生成输出文件。"""
        if not hasattr(self, 'output_path') or not self.output_path:
            raise ValueError("未设置输出路径")

        logger.info(f"[DEBUG] 当前 filters: {self.filters}")
        vf = ",".join(self.filters) if self.filters else "null"
        input_ff = self.input_video.replace("\\", "/")
        output_ff = os.path.abspath(self.output_path).replace("\\", "/")

        cmd = f'ffmpeg -y -i "{input_ff}" -vf "{vf}" -c:a copy "{output_ff}"'
        logger.info(f"运行 ffmpeg 命令: {cmd}")
        try:
            subprocess.run(shlex.split(cmd), check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg 执行失败: {e}")
            raise

        logger.info(f"[DEBUG] 输出已保存，filters: {self.filters}")
        logger.info(f"视频已保存至: {self.output_path}")

    def close(self):
        """释放资源（无保持状态资源，清空过滤器即可）。"""
        self.filters.clear()
        logger.info("FFmpeg 编辑器已清理状态")

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
        total_duration = self._get_video_duration()
        
        # 替换"总时长"为实际数值
        expression = expression.replace("总时长", str(total_duration))
        
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

    # 可选：提供一个仅支持 add_text 的 execute_action，保持与 MoviePyVideoEditor 接口相似
    def execute_action(self, action_str: str, operations: dict) -> bool:
        if not action_str:
            raise ValueError("未收到有效的操作指令")

        logger.info(f"执行操作(FFmpeg): {action_str}")
        parts = action_str.strip().split()
        if not parts or parts[0] != 'action:':
            raise ValueError("无效的 action 格式")

        action = parts[1]
        params = {}
        for p in parts[2:]:
            if '=' in p:
                k, v = p.split('=', 1)
                if k != 'editor':
                    params[k] = v

        if action == 'add_text':
            # 解析参数，支持"总时长"表达式
            text = params.get('text', '')
            fontsize = int(params.get('fontsize', 24))
            duration = self._parse_duration_expression(params.get('duration', 5.0)) if 'duration' in params else 5.0
            position = params.get('position', 'center')  # 目前忽略，统一底部居中
            start_time = self._parse_duration_expression(params.get('start_time', 0.0)) if 'start_time' in params else 0.0

            self.add_text(text=text, fontsize=fontsize, duration=duration, position=position, start_time=start_time)
            return True
        elif action == 'make_black_and_white':
            # 解析参数，支持"总时长"表达式
            start_time = self._parse_duration_expression(params.get('start_time', 0.0)) if 'start_time' in params else 0.0
            duration = self._parse_duration_expression(params.get('duration', 1.0)) if 'duration' in params else 1.0

            self.make_black_and_white(start_time=start_time, duration=duration)
            return True
        elif action == 'add_transition':
            # 解析参数，支持"总时长"表达式
            type_param = params.get('type', 'fade')
            duration = self._parse_duration_expression(params.get('duration', 1.0)) if 'duration' in params else 1.0
            start_time = self._parse_duration_expression(params.get('start_time', 0.0)) if 'start_time' in params else 0.0

            self.add_transition(type=type_param, duration=duration, start_time=start_time)
            return True
        else:
            raise ValueError(f"FFmpegVideoEditor 目前仅支持 add_text、make_black_and_white 和 add_transition，收到: {action}")


if __name__ == "__main__":
    print("FFmpeg 视频编辑器模块（仅实现 add_text）")

