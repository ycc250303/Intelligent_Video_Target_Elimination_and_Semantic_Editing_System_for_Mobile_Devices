#!/usr/bin/env python3
"""
FFmpegVideoEditor 功能测试脚本
说明：
- 需要安装 ffmpeg/ffprobe
- 会在当前目录创建临时输出文件
"""

import os
import sys
import uuid
import logging
import subprocess

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from VideoEditor.ffmpeg_editor import FFmpegVideoEditor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _make_dummy_video(path: str, duration: float = 3.0, size=(640, 360), color=(20, 120, 240)):
    """使用 FFmpeg 创建纯色测试视频"""
    width, height = size
    r, g, b = color
    
    # 使用 FFmpeg 创建纯色视频
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=0x{r:02x}{g:02x}{b:02x}:s={width}x{height}:d={duration}',
        '-pix_fmt', 'yuv420p',
        '-y',  # 覆盖已存在的文件
        path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"创建测试视频: {path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"创建测试视频失败: {e}")
        raise


def ensure_sample_inputs(v1_override: str = None, v2_override: str = None):
    os.makedirs('tmp', exist_ok=True)
    # 支持从参数/环境变量覆盖输入视频
    v1 = v1_override or os.environ.get('FFTEST_V1')
    v2 = v2_override or os.environ.get('FFTEST_V2')
    if v1 and os.path.exists(v1):
        v1_path = os.path.abspath(v1)
    else:
        v1_path = os.path.abspath(os.path.join('tmp', 'v1.mp4'))
        if not os.path.exists(v1_path):
            _make_dummy_video(v1_path, duration=4.0, color=(20, 120, 240))

    if v2 and os.path.exists(v2):
        v2_path = os.path.abspath(v2)
    else:
        v2_path = os.path.abspath(os.path.join('tmp', 'v2.mp4'))
        if not os.path.exists(v2_path):
            _make_dummy_video(v2_path, duration=3.0, color=(240, 120, 20))

    return v1_path, v2_path


def ensure_sample_audio(path: str = None, duration: float = 3.0):
    """生成一个示例音频（正弦波），用于 BGM/片段测试。"""
    os.makedirs('tmp', exist_ok=True)
    a1 = path or os.path.abspath(os.path.join('tmp', 'a1.wav'))
    if not os.path.exists(a1):
        import subprocess
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'sine=frequency=440:duration={duration}',
            a1
        ]
        try:
            subprocess.run(cmd, check=True)
        except Exception:
            # 回退：如果 ffmpeg 生成失败，则跳过创建，后续用例会报告缺失
            pass
    return a1


def run_case(name: str, func):
    try:
        out_path = func()
        logger.info(f'[{name}] 通过，输出: {out_path}')
    except Exception as e:
        logger.exception(f'[{name}] 失败: {e}')


def build_output_path(tag: str) -> str:
    os.makedirs('tmp', exist_ok=True)
    return os.path.abspath(os.path.join('tmp', f'ff_out_{tag}_{uuid.uuid4()}.mp4'))


def case_add_text(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.add_text(text='Hello', start_time=0.5, fontsize=36, duration=None)
    editor.output_path = build_output_path('add_text')
    editor.save()
    return editor.output_path


def case_black_and_white(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.make_black_and_white(start_time=1.0, duration=1.0)
    editor.output_path = build_output_path('bw')
    editor.save()
    return editor.output_path


def case_brightness(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.adjust_brightness(1.1)
    editor.output_path = build_output_path('brightness')
    editor.save()
    return editor.output_path


def case_contrast(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.adjust_contrast(1.2)
    editor.output_path = build_output_path('contrast')
    editor.save()
    return editor.output_path


def case_rotate(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.rotate(90)
    editor.output_path = build_output_path('rotate')
    editor.save()
    return editor.output_path


def case_crop(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.crop(10, 10, 630, 350)
    editor.output_path = build_output_path('crop')
    editor.save()
    return editor.output_path


def case_speed(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.adjust_speed(1.25)
    editor.output_path = build_output_path('speed')
    editor.save()
    return editor.output_path


def case_trim(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.trim(0.2, 2.8)
    editor.output_path = build_output_path('trim')
    editor.save()
    return editor.output_path


def case_concatenate(v1: str, v2: str):
    editor = FFmpegVideoEditor(v1)
    editor.concatenate(v2, transition='none')
    editor.output_path = build_output_path('concat')
    editor.save()
    return editor.output_path


def case_concatenate_fade(v1: str, v2: str):
    editor = FFmpegVideoEditor(v1)
    editor.concatenate(v2, transition='fade', transition_duration=0.6)
    editor.output_path = build_output_path('concat_fade')
    editor.save()
    return editor.output_path


def case_concatenate_multiple(v1: str, v2: str):
    # 复用已有两个视频，串行多次拼接
    editor = FFmpegVideoEditor(v1)
    editor.concatenate_multiple([v2, v1], transition='none')
    editor.output_path = build_output_path('concat_multi')
    editor.save()
    return editor.output_path


def case_set_resolution_keep_aspect(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.set_resolution(width=720, height=1280, keep_aspect=True, fill_color='black')
    editor.output_path = build_output_path('resize_keep')
    editor.save()
    return editor.output_path


def case_set_resolution_stretch(v1: str):
    editor = FFmpegVideoEditor(v1)
    editor.set_resolution(width=720, height=1280, keep_aspect=False)
    editor.output_path = build_output_path('resize_stretch')
    editor.save()
    return editor.output_path


def case_add_subtitles(v1: str):
    editor = FFmpegVideoEditor(v1)
    items = [
        ["第一句字幕", 0.3, 1.0, 32],
        ["第二句字幕", 1.4, 1.2, 36],
        ["第三句字幕", 2.8, 0.9, 32],
    ]
    editor.add_subtitles(items)
    editor.output_path = build_output_path('subtitles')
    editor.save()
    return editor.output_path


def case_add_background_music(v1: str):
    audio = ensure_sample_audio()
    editor = FFmpegVideoEditor(v1)
    # 整段作为背景音乐，混合
    editor.add_background_music(audio_file=audio, mix=True, video_start_time=0.0, video_end_time=None,
                                audio_start_time=0.0, audio_end_time=None, overwrite=False)
    editor.output_path = build_output_path('bgm_mix')
    editor.save()
    return editor.output_path


def case_add_audio_segment(v1: str):
    audio = ensure_sample_audio()
    editor = FFmpegVideoEditor(v1)
    # 截取一段，音量 0.5，从视频第 0.5s 开始覆盖 1.2s（与原音混合）
    editor.add_audio_segment(audio_file=audio, video_start_time=0.5, video_end_time=1.7,
                             audio_start_time=0.2, audio_end_time=1.4, volume=0.5, mix=True, overwrite=False)
    editor.output_path = build_output_path('audio_segment')
    editor.save()
    return editor.output_path


def case_execute_action(v1: str):
    editor = FFmpegVideoEditor(v1)
    # 动作：添加字幕 + 黑白
    editor.execute_action("action: add_text text=Hello fontsize=28 start_time=0.2 editor=ffmpeg", {})
    editor.execute_action("action: make_black_and_white start_time=0.8 duration=0.8 editor=ffmpeg", {})
    editor.output_path = build_output_path('exec_action')
    editor.save()
    return editor.output_path


def main():
    # 在此处直接配置原视频路径：
    # - 设为 None 将自动生成 tmp/v1.mp4 与 tmp/v2.mp4 演示视频
    # - 或者填入本地文件路径，例如：r"D:\\videos\\a.mp4"
    v1_override = "D:\\test1\\video001.mp4"
    v2_override = "D:\\test1\\video002.mp4"

    v1, v2 = ensure_sample_inputs(v1_override, v2_override)
    logger.info(f'测试输入: v1={v1}, v2={v2}')

    # 逐项测试：任一失败不影响其他
    # run_case('add_text', lambda: case_add_text(v1))
    # run_case('black_white', lambda: case_black_and_white(v1))
    # run_case('brightness', lambda: case_brightness(v1))
    # run_case('contrast', lambda: case_contrast(v1))
    # run_case('rotate', lambda: case_rotate(v1))
    # run_case('crop', lambda: case_crop(v1))
    # run_case('speed', lambda: case_speed(v1))
    # run_case('trim', lambda: case_trim(v1))
    # run_case('concatenate', lambda: case_concatenate(v1, v2))
    run_case('concatenate_fade', lambda: case_concatenate_fade(v1, v2))
    run_case('concatenate_multiple', lambda: case_concatenate_multiple(v1, v2))
    run_case('set_resolution_keep', lambda: case_set_resolution_keep_aspect(v1))
    run_case('set_resolution_stretch', lambda: case_set_resolution_stretch(v1))
    run_case('add_subtitles', lambda: case_add_subtitles(v1))
    run_case('add_background_music', lambda: case_add_background_music(v1))
    run_case('add_audio_segment', lambda: case_add_audio_segment(v1))
    run_case('execute_action', lambda: case_execute_action(v1))

    print('FFmpegVideoEditor 单项功能测试完成（检查 tmp 目录输出）')


if __name__ == '__main__':
    main()






