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




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FFmpegVideoEditor:
    """基于 FFmpeg 的视频编辑器实现（最小可用：add_text/save/close）。"""

    def __init__(self, input_video: str):
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件 {input_video} 不存在")
        self.input_video: str = os.path.abspath(input_video)
        self.filters: List[str] = []  # 累积 -vf 的过滤器，如 drawtext
        self.output_path: str = f"ffmpeg_output_{uuid.uuid4()}.mp4"
        self._duration: Optional[float] = None
        self._has_scale: bool = False
        # 额外的处理状态
        self._trim_start: Optional[float] = None
        self._trim_end: Optional[float] = None
        self._speed_factor: float = 1.0
        self.audio_filters: List[str] = []  # 累积 -af 的过滤器
        self._needs_audio_encode: bool = False
        self._concat_queue: List[str] = []  # 需要拼接的视频（顺序追加）
        self._audio_overlays: List[dict] = []  # 背景音乐或音效叠加描述

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
        if start < 0:
            raise ValueError("开始时间不能为负")
        total = self._get_video_duration()
        end_time = end if end is not None else total
        if start >= total:
            raise ValueError("起始时间超出视频时长")
        if end_time <= start:
            raise ValueError("结束时间必须大于起始时间")
        self._trim_start = float(start)
        self._trim_end = float(end_time)
        logger.info(f"设置裁剪: start={self._trim_start}, end={self._trim_end}")

    def add_transition(self, type: str = "fade", duration: float = 1.0, start_time: float = 0.0):
        """
        添加转场效果，使用FFmpeg的fade过滤器实现淡入淡出。
        
        注意：此函数会智能判断应该使用淡入还是淡出：
        - 在视频开头（start_time < 2秒）：使用淡入效果（从黑色渐显）
        - 在视频结尾（距结尾 < 2秒）：使用淡出效果（渐变到黑色）
        - 其他位置：默认使用淡入效果

        Args:
            type: 转场类型，目前支持 'fade' 或 'fade_in'（淡入）、'fade_out'（淡出）
            duration: 转场持续时间（秒）
            start_time: 转场开始时间（秒）
        """
        if type not in ("fade", "fade_in", "fade_out"):
            raise ValueError(f"FFmpeg编辑器目前只支持 'fade'、'fade_in'、'fade_out' 类型的转场，收到: {type}")
        
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

        # 智能判断应该使用淡入还是淡出
        if type == "fade":
            # 自动判断：开头用淡入，结尾用淡出
            if start_time < 2.0:
                # 在视频开头，使用淡入
                fade_filter = f"fade=t=in:st={start_time}:d={duration}"
                effect_type = "淡入"
            elif start_time > total - 2.0:
                # 在视频结尾，使用淡出
                fade_filter = f"fade=t=out:st={start_time}:d={duration}"
                effect_type = "淡出"
            else:
                # 中间位置，默认使用淡入
                fade_filter = f"fade=t=in:st={start_time}:d={duration}"
                effect_type = "淡入"
                logger.warning(
                    f"转场位于视频中间位置（{start_time}s），默认使用淡入效果。"
                    f"如需淡出，请明确指定 type='fade_out'"
                )
        elif type == "fade_in":
            # 明确指定淡入
            fade_filter = f"fade=t=in:st={start_time}:d={duration}"
            effect_type = "淡入"
        else:  # fade_out
            # 明确指定淡出
            fade_filter = f"fade=t=out:st={start_time}:d={duration}"
            effect_type = "淡出"
        
        self.filters.append(fade_filter)
        
        logger.info(
            f"已添加转场效果（ffmpeg）：{effect_type}, start={start_time}s, duration={duration}s"
        )

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

    def adjust_speed(self, factor: float = 1.0):
        """
        调整视频速度（含音频）。
        注意：音频 atempo 限制在 0.5~2.0 区间，超出范围用多次链式相乘。
        """
        if factor <= 0:
            raise ValueError("速度倍数必须大于 0")
        self._speed_factor = float(factor)
        # 视频速度：setpts=PTS/factor
        self.filters.append(f"setpts=PTS/{self._speed_factor}")
        # 音频速度：atempo 链
        atempo_chain: List[str] = []
        remaining = self._speed_factor
        # 将 factor 分解为多个 0.5~2.0 范围内的片段
        while remaining > 2.0:
            atempo_chain.append("atempo=2.0")
            remaining /= 2.0
        while remaining < 0.5:
            atempo_chain.append("atempo=0.5")
            remaining *= 2.0
        atempo_chain.append(f"atempo={remaining}")
        self.audio_filters.extend(atempo_chain)
        self._needs_audio_encode = True
        logger.info(f"已设置速度: factor={factor}, atempo_chain={atempo_chain}")

    def adjust_volume(self, factor: float = 1.0):
        if factor < 0:
            raise ValueError("音量倍数必须非负")
        self.audio_filters.append(f"volume={factor}")
        self._needs_audio_encode = True
        logger.info(f"已设置音量: factor={factor}")

    def rotate(self, angle: float = 90.0):
        """
        旋转视频。
        仅支持 90/180/270 三种常见角度，更复杂角度可使用 rotate 过滤器（此处不建议）。
        """
        a = int(angle) % 360
        if a == 90:
            self.filters.append("transpose=1")  # 顺时针90
        elif a == 180:
            self.filters.append("transpose=1,transpose=1")
        elif a == 270:
            self.filters.append("transpose=2")  # 逆时针90
        elif a == 0:
            return
        else:
            # 对任意角度使用 rotate（弧度），此处转换度到弧度
            rad = angle * 3.141592653589793 / 180.0
            self.filters.append(f"rotate={rad}")
        logger.info(f"已添加旋转: angle={angle}")

    def crop(self, x1: float = 0.0, y1: float = 0.0, x2: float = None, y2: float = None):
        if x2 is None or y2 is None:
            raise ValueError("x2 和 y2 必须指定")
        if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
            raise ValueError("裁剪坐标无效")
        w = x2 - x1
        h = y2 - y1
        self.filters.append(f"crop={int(w)}:{int(h)}:{int(x1)}:{int(y1)}")
        logger.info(f"已添加裁剪: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    def add_background_music(self, audio_file: str, mix: bool = False, video_start_time: float = 0.0, video_end_time: Optional[float] = None, audio_start_time: float = 0.0, audio_end_time: Optional[float] = None, overwrite: bool = False):
        """
        添加背景音乐。为统一处理，保存时使用 filter_complex 进行混音。
        若 overwrite=True，则视频该时间段仅保留新音频；否则为混合。
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 {audio_file} 不存在")
        self._audio_overlays.append({
            "type": "bgm",
            "path": os.path.abspath(audio_file),
            "video_start": float(video_start_time),
            "video_end": float(video_end_time) if video_end_time is not None else None,
            "audio_start": float(audio_start_time),
            "audio_end": float(audio_end_time) if audio_end_time is not None else None,
            "mix": bool(mix),
            "overwrite": bool(overwrite),
        })
        self._needs_audio_encode = True
        logger.info(f"计划添加背景音乐: {audio_file}, mix={mix}, overwrite={overwrite}")

    def add_audio_segment(self, audio_file: str, video_start_time: float, video_end_time: float, audio_start_time: float = 0.0, audio_end_time: Optional[float] = None, volume: float = 1.0, mix: bool = True, overwrite: bool = False):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 {audio_file} 不存在")
        if video_end_time <= video_start_time:
            raise ValueError("视频结束时间必须大于起始时间")
        self._audio_overlays.append({
            "type": "segment",
            "path": os.path.abspath(audio_file),
            "video_start": float(video_start_time),
            "video_end": float(video_end_time),
            "audio_start": float(audio_start_time),
            "audio_end": float(audio_end_time) if audio_end_time is not None else None,
            "volume": float(volume),
            "mix": bool(mix),
            "overwrite": bool(overwrite),
        })
        self._needs_audio_encode = True
        logger.info(f"计划添加音频片段: {audio_file}, {video_start_time}-{video_end_time}s, volume={volume}")

    def adjust_brightness(self, factor: float = 1.0):
        if factor <= 0:
            raise ValueError("亮度倍数必须大于 0")
        # 亮度：eq=brightness=delta。以 1.0 为基准，>1 变亮，<1 变暗。
        delta = factor - 1.0
        self.filters.append(f"eq=brightness={delta}")
        logger.info(f"已设置亮度: factor={factor}")

    def adjust_contrast(self, factor: float = 1.0):
        if factor <= 0:
            raise ValueError("对比度倍数必须大于 0")
        self.filters.append(f"eq=contrast={factor}")
        logger.info(f"已设置对比度: factor={factor}")

    def concatenate(self, second_video: str, transition: str = "none", transition_duration: float = 1.0):
        """
        简化实现：立即调用 ffmpeg 将当前输入与 second_video 合并为一个临时文件，
        然后将该输出作为新的 input_video，保留已累积的 filters（在合并后继续应用）。
        仅支持无转场或淡入淡出（使用 fadeout/fadein 简化）。
        """
        if not os.path.exists(second_video):
            raise FileNotFoundError(f"第二个视频文件 {second_video} 不存在")
        # 生成中间输出
        temp_output = f"concat_tmp_{uuid.uuid4()}.mp4"
        input_ff1 = self.input_video.replace("\\", "/")
        input_ff2 = os.path.abspath(second_video).replace("\\", "/")
        temp_ff = os.path.abspath(temp_output).replace("\\", "/")

        try:
            if transition == "none":
                # 使用 concat demuxer 创建文件列表
                list_path = f"concat_list_{uuid.uuid4()}.txt"
                with open(list_path, 'w', encoding='utf-8') as f:
                    f.write(f"file '{input_ff1}'\n")
                    f.write(f"file '{input_ff2}'\n")
                cmd = f"ffmpeg -y -f concat -safe 0 -i {list_path} -c copy {temp_ff}"
                subprocess.run(shlex.split(cmd), check=True)
                os.remove(list_path)
            elif transition == "fade":
                # 简化：对第一段结尾做淡出，对第二段开头做淡入，并重新拼接
                # 使用 filter_complex
                cmd = (
                    f"ffmpeg -y -i '{input_ff1}' -i '{input_ff2}' "
                    f"-filter_complex "
                    f"[0:v]format=yuv420p,fade=t=out:st=0:d={transition_duration}:alpha=1[v0];"
                    f"[1:v]format=yuv420p,fade=t=in:st=0:d={transition_duration}:alpha=1[v1];"
                    f"[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a] "
                    f"-map [v] -map [a] {temp_ff}"
                )
                subprocess.run(shlex.split(cmd), check=True)
            else:
                # 其他转场暂不支持，退回无转场
                list_path = f"concat_list_{uuid.uuid4()}.txt"
                with open(list_path, 'w', encoding='utf-8') as f:
                    f.write(f"file '{input_ff1}'\n")
                    f.write(f"file '{input_ff2}'\n")
                cmd = f"ffmpeg -y -f concat -safe 0 -i {list_path} -c copy {temp_ff}"
                subprocess.run(shlex.split(cmd), check=True)
                os.remove(list_path)

            # 替换输入
            self.input_video = temp_ff
            # 重新计算时长缓存
            self._duration = None
            logger.info(f"已拼接视频，新的输入: {self.input_video}")
        except subprocess.CalledProcessError as e:
            logger.error(f"拼接失败: {e}")
            raise

    def concatenate_multiple(self, video_files: list, transition: str = "none", transition_duration: float = 1.0):
        if not video_files:
            logger.warning("没有提供要合并的视频文件")
            return
        current_input = self.input_video
        for vf in video_files:
            self.concatenate(vf, transition=transition, transition_duration=transition_duration)

    def add_text(self, text: str, start_time: float, fontsize: int = 72, duration: Optional[float] = None):
        """
        添加硬字幕（烧录），使用 drawtext 过滤器。

        Args:
            text: 字幕内容
            start_time: 开始出现的时间（秒）（必填）
            fontsize: 字号
            duration: 持续时间（秒）；未提供时按文本长度自动计算
        """
        if not text:
            raise ValueError("字幕文本不能为空")
        if start_time < 0:
            raise ValueError("开始时间不能为负")

        # 若未显式给出 duration，则按文本长度成比例计算。
        # 经验值：每字符 0.2s，至少 1.0s，最多不超过剩余时长。
        total = self._get_video_duration()
        if duration is None:
            auto_duration = max(1.0, len(str(text)) * 0.2)
            # 不超过视频剩余时长
            duration = min(auto_duration, max(0.0, total - float(start_time)))
        else:
            duration = float(duration)
        if duration <= 0:
            raise ValueError("字幕持续时间必须大于 0")

        if start_time >= total:
            raise ValueError(f"字幕开始时间 {start_time}s 不能超过或等于视频总时长 {total:.3f}s")
        if start_time + duration > total:
            raise ValueError(
                f"字幕结束时间 {start_time + duration:.3f}s 超过视频总时长 {total:.3f}s，请缩短持续时间或调整开始时间"
            )

        # 字体设置：仅在 Windows 下尝试特定字体，其它系统不指定字体文件
        font_candidates = []
        if os.name == 'nt':  # Windows 系统
            font_candidates.extend([
                r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
                r"C:\Windows\Fonts\msyhbd.ttc",    # 微软雅黑粗体
                r"C:\Windows\Fonts\simhei.ttf",    # 黑体
                r"C:\Windows\Fonts\simsun.ttc",    # 宋体
                r"C:\Windows\Fonts\simkai.ttf",    # 楷体
                r"C:\Windows\Fonts\simfang.ttf",   # 仿宋
            ])
        
        fontfile = None
        for font_path in font_candidates:
            if os.path.exists(font_path):
                fontfile = font_path
                logger.info(f"找到可用字体: {font_path}")
                break
        
        if not fontfile:
            logger.info("未在 Windows 字体列表中找到可用字体，将使用系统默认字体")
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
        
        # 添加字体文件设置（如果是 Windows 且找到字体）
        if fontfile_ff:
            drawtext_parts.insert(0, f"fontfile='{fontfile_ff}'")
            logger.info(f"使用指定字体: {fontfile_ff}")
        
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
            f"已添加字幕（ffmpeg，固定底部居中）：text='{text}', start={start_time}s, duration={duration}s, fontsize={fontsize}, {font_info}"
        )
        logger.info("字幕固定在画面下方居中渲染，跨端显示一致")

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

    

    def save(self):
        """根据累积的 filters，调用 ffmpeg 生成输出文件。"""
        if not hasattr(self, 'output_path') or not self.output_path:
            raise ValueError("未设置输出路径")

        logger.info(f"[DEBUG] 当前 filters: {self.filters}")
        vf = ",".join(self.filters) if self.filters else None
        af = ",".join(self.audio_filters) if self.audio_filters else None
        input_ff = self.input_video.replace("\\", "/")
        output_ff = os.path.abspath(self.output_path).replace("\\", "/")

        # 构建命令
        cmd_parts = ["ffmpeg", "-y"]

        # 精准裁剪：在输入后使用 -ss/-to 提高精度
        cmd_parts.extend(["-i", input_ff])
        if self._trim_start is not None:
            cmd_parts.extend(["-ss", str(self._trim_start)])
        if self._trim_end is not None:
            cmd_parts.extend(["-to", str(self._trim_end)])

        if vf:
            cmd_parts.extend(["-vf", vf])

        # 处理音频叠加（背景音乐/片段）
        # 简化策略：无叠加 → 使用 -af；有叠加 → 构建 filter_complex
        filter_complex = None
        map_audio = None
        extra_inputs: List[str] = []
        if self._audio_overlays:
            # 输入流标记：主音频 0:a，附加音频 1:a,2:a,...
            # 构建各自的裁剪与延迟，再与主音频混合
            complex_parts = []
            input_index = 1
            mix_inputs = []

            # 主音频预处理（速度、音量）
            a_main = "0:a"
            if af:
                complex_parts.append(f"[{a_main}]{af}[a0]")
                a_main = "a0"
            mix_inputs.append(f"[{a_main}]")

            for ov in self._audio_overlays:
                extra_inputs.extend(["-i", ov["path"]])
                a_in = f"{input_index}:a"
                input_index += 1

                # 计算区间
                v_start = float(ov.get("video_start", 0.0))
                v_end = ov.get("video_end", None)
                a_start = float(ov.get("audio_start", 0.0))
                a_end = ov.get("audio_end", None)
                vol = float(ov.get("volume", 1.0))

                # 截取音频
                trims = []
                if a_start and a_start > 0:
                    trims.append(f"atrim=start={a_start}")
                if a_end is not None:
                    trims.append(f"atrim=end={a_end}")
                label_in = f"a{input_index}in"
                if trims:
                    complex_parts.append(f"[{a_in}]{','.join(trims)}[{label_in}]")
                else:
                    label_in = a_in

                # 音量
                if vol != 1.0:
                    label_vol = f"a{input_index}vol"
                    complex_parts.append(f"[{label_in}]volume={vol}[{label_vol}]")
                    label_in = label_vol

                # 对齐到视频时间：毫秒延迟
                delay_ms = max(0, int(v_start * 1000))
                label_delay = f"a{input_index}d"
                complex_parts.append(f"[{label_in}]adelay={delay_ms}|{delay_ms}[{label_delay}]")

                # 如果 v_end 指定，裁到该区间长度
                if v_end is not None:
                    duration = max(0.0, float(v_end) - float(v_start))
                    label_dur = f"a{input_index}dur"
                    complex_parts.append(f"[{label_delay}]atrim=end={duration}[{label_dur}]")
                    label_delay = label_dur

                mix_inputs.append(f"[{label_delay}]")

            # 混合
            amix_inputs = ''.join(mix_inputs)
            complex_parts.append(f"{amix_inputs}amix=inputs={len(mix_inputs)}:normalize=0[aout]")
            filter_complex = ';'.join(complex_parts)
            map_audio = "[aout]"

        # 追加额外输入（若有）
        if extra_inputs:
            cmd_parts = ["ffmpeg", "-y", "-i", input_ff] + extra_inputs
            if self._trim_start is not None:
                cmd_parts.extend(["-ss", str(self._trim_start)])
            if self._trim_end is not None:
                cmd_parts.extend(["-to", str(self._trim_end)])
            if vf:
                cmd_parts.extend(["-vf", vf])

        if filter_complex:
            cmd_parts.extend(["-filter_complex", filter_complex, "-map", "0:v"])
            cmd_parts.extend(["-map", map_audio])
            # 有复杂音频处理时，强制编码音频
            cmd_parts.extend(["-c:a", "aac"]) 
        else:
            # 无叠加：若仅视频滤镜且不需要音频编码，复制音频；否则使用 -af
            if af:
                cmd_parts.extend(["-af", af, "-c:a", "aac"])  # 有音频滤镜时需要编码
            else:
                cmd_parts.extend(["-c:a", "copy"])  # 不处理音频则直接复制

        # 编码视频（统一使用 libx264，像素格式兼容）
        cmd_parts.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", output_ff])

        # 以列表形式直接调用，避免 Windows 下引号转义问题
        logger.info(f"运行 ffmpeg 命令: {' '.join(cmd_parts)}")
        try:
            subprocess.run(cmd_parts, check=True)
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

    # 提供 execute_action，支持与 MoviePyVideoEditor 相似的操作解析
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
            # 未提供 duration 时传递 None 以启用按文本长度自动计算
            duration = self._parse_duration_expression(params['duration']) if 'duration' in params else None
            if 'start_time' not in params:
                raise ValueError("add_text 需要提供 start_time")
            start_time = self._parse_duration_expression(params.get('start_time'))

            self.add_text(text=text, start_time=start_time, fontsize=fontsize, duration=duration)
            return True
        elif action == 'make_black_and_white':
            # 解析参数，支持"总时长"表达式
            start_time = self._parse_duration_expression(params.get('start_time', 0.0)) if 'start_time' in params else 0.0
            duration = self._parse_duration_expression(params.get('duration', 1.0)) if 'duration' in params else 1.0

            self.make_black_and_white(start_time=start_time, duration=duration)
            return True
        elif action == 'add_transition':
            # 解析参数，支持"总时长"表达式
            # 支持 type 为 'fade', 'fade_in', 'fade_out'
            type_param = params.get('type', 'fade')
            duration = self._parse_duration_expression(params.get('duration', 1.0)) if 'duration' in params else 1.0
            start_time = self._parse_duration_expression(params.get('start_time', 0.0)) if 'start_time' in params else 0.0

            self.add_transition(type=type_param, duration=duration, start_time=start_time)
            return True
        elif action == 'trim':
            start = float(params.get('start', 0.0))
            end = float(params['end']) if 'end' in params and params['end'] not in ('None', '') else None
            self.trim(start=start, end=end)
            return True
        elif action in ('speed', 'adjust_speed'):
            factor = float(params.get('factor', 1.0))
            self.adjust_speed(factor=factor)
            return True
        elif action == 'adjust_volume':
            factor = float(params.get('factor', 1.0))
            self.adjust_volume(factor=factor)
            return True
        elif action == 'rotate':
            angle = float(params.get('angle', 90.0))
            self.rotate(angle=angle)
            return True
        elif action == 'crop':
            x1 = float(params.get('x1', 0.0))
            y1 = float(params.get('y1', 0.0))
            x2 = float(params['x2']) if 'x2' in params and params['x2'] not in ('None', '') else None
            y2 = float(params['y2']) if 'y2' in params and params['y2'] not in ('None', '') else None
            self.crop(x1=x1, y1=y1, x2=x2, y2=y2)
            return True
        elif action == 'add_background_music':
            audio_file = params.get('audio_file', '')
            video_start_time = float(params.get('video_start_time', 0.0)) if 'video_start_time' in params else 0.0
            video_end_time = float(params['video_end_time']) if 'video_end_time' in params and params['video_end_time'] not in ('None', '') else None
            audio_start_time = float(params.get('audio_start_time', 0.0)) if 'audio_start_time' in params else 0.0
            audio_end_time = float(params['audio_end_time']) if 'audio_end_time' in params and params['audio_end_time'] not in ('None', '') else None
            mix = params.get('mix', 'false').lower() == 'true'
            overwrite = params.get('overwrite', 'false').lower() == 'true'
            self.add_background_music(audio_file=audio_file, mix=mix, video_start_time=video_start_time, video_end_time=video_end_time, audio_start_time=audio_start_time, audio_end_time=audio_end_time, overwrite=overwrite)
            return True
        elif action == 'add_audio_segment':
            audio_file = params.get('audio_file', '')
            video_start_time = float(params.get('video_start_time'))
            video_end_time = float(params.get('video_end_time'))
            audio_start_time = float(params.get('audio_start_time', 0.0)) if 'audio_start_time' in params else 0.0
            audio_end_time = float(params['audio_end_time']) if 'audio_end_time' in params and params['audio_end_time'] not in ('None', '') else None
            volume = float(params.get('volume', 1.0))
            mix = params.get('mix', 'true').lower() == 'true'
            overwrite = params.get('overwrite', 'false').lower() == 'true'
            self.add_audio_segment(audio_file=audio_file, video_start_time=video_start_time, video_end_time=video_end_time, audio_start_time=audio_start_time, audio_end_time=audio_end_time, volume=volume, mix=mix, overwrite=overwrite)
            return True
        elif action == 'concatenate':
            second_video = params.get('second_video', '')
            transition = params.get('transition', 'none')
            transition_duration = float(params.get('transition_duration', 1.0))
            self.concatenate(second_video=second_video, transition=transition, transition_duration=transition_duration)
            return True
        elif action == 'concatenate_multiple':
            # 约定：video_files 以逗号分隔，或 JSON 数组（前端可转换）
            raw = params.get('video_files', '')
            files = []
            if raw.startswith('[') and raw.endswith(']'):
                try:
                    import json
                    files = json.loads(raw)
                except Exception:
                    files = []
            else:
                files = [s for s in raw.split(',') if s]
            transition = params.get('transition', 'none')
            transition_duration = float(params.get('transition_duration', 1.0))
            self.concatenate_multiple(files, transition=transition, transition_duration=transition_duration)
            return True
        else:
            raise ValueError(f"FFmpegVideoEditor 目前仅支持 add_text、make_black_and_white 和 add_transition，收到: {action}")


if __name__ == "__main__":
    print("FFmpeg 视频编辑器模块（仅实现 add_text）")

