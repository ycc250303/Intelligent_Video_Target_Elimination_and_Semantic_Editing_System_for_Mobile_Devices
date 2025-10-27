#!/usr/bin/env python3
"""
视频操作执行器
根据JSON指令调用相应的视频处理功能
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime

from config.config import OPERATIONS, QWEN_API_KEY
from VideoEditor.ffmpeg_editor import FFmpegVideoEditor
from VideoEditor.qwen_editor import QwenVideoEditor

logger = logging.getLogger(__name__)


@dataclass
class OperationResult:
    """操作结果数据类"""
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    operation_name: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VideoOperationExecutor:
    """视频操作执行器"""
    
    def __init__(self, output_dir: str = "Results"):
        """
        初始化执行器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化Qwen编辑器（不需要input_video）
        self.qwen_editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir=str(self.output_dir))
        
        # 操作历史
        self.operation_history: List[OperationResult] = []
    
    def execute_from_json(
        self, 
        json_data: Union[str, Dict[str, Any]], 
        input_video: Optional[str] = None
    ) -> OperationResult:
        """
        从JSON数据执行操作
        
        Args:
            json_data: JSON字符串或字典
            input_video: 输入视频路径（如果JSON中未指定）
            
        Returns:
            OperationResult: 操作结果
        """
        try:
            # 解析JSON
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # 提取操作信息
            operations = data.get("operations", {})
            if not operations:
                return OperationResult(
                    success=False,
                    error_message="JSON中未找到操作信息"
                )
            
            operation_name = operations.get("operation")
            params = operations.get("params", {})
            editor_type = operations.get("editor", "ffmpeg")
            
            # 验证操作是否存在
            if not operation_name or operation_name not in OPERATIONS:
                return OperationResult(
                    success=False,
                    error_message=f"未知的操作: {operation_name}"
                )
            
            # 添加输入视频路径到参数
            if input_video and "input_video" not in params:
                params["input_video"] = input_video
            
            # 执行操作
            result = self.execute_operation(
                operation_name=operation_name,
                params=params,
                editor_type=editor_type
            )
            
            # 记录历史
            self.operation_history.append(result)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return OperationResult(
                success=False,
                error_message=f"JSON解析失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"执行操作失败: {e}")
            return OperationResult(
                success=False,
                error_message=f"执行操作失败: {str(e)}"
            )
    
    def execute_operation(
        self,
        operation_name: str,
        params: Dict[str, Any],
        editor_type: str = "ffmpeg"
    ) -> OperationResult:
        """
        执行单个操作
        
        Args:
            operation_name: 操作名称
            params: 操作参数
            editor_type: 编辑器类型 (ffmpeg 用于视频编辑, qwen 用于视频生成)
            
        Returns:
            OperationResult: 操作结果
        """
        start_time = datetime.now()
        
        try:
            # 对于 Qwen 操作，input_video 不是必需的
            is_qwen_operation = editor_type.lower() == "qwen"
            
            # 生成输出文件名（如果有输入视频）
            input_video = params.get("input_video")
            if input_video:
                output_filename = self._generate_output_filename(operation_name, input_video)
                output_path = str(self.output_dir / output_filename)
                params["output_video"] = output_path
            elif not is_qwen_operation:
                # 非 Qwen 操作需要输入视频
                return OperationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message="缺少输入视频路径"
                )
            
            # 选择编辑器
            if editor_type.lower() == "ffmpeg":
                # FFmpeg 需要 input_video 参数，每次操作时创建实例
                if not input_video or not Path(input_video).exists():
                    return OperationResult(
                        success=False,
                        operation_name=operation_name,
                        error_message=f"输入视频不存在: {input_video}"
                    )
                editor = FFmpegVideoEditor(input_video)
            elif editor_type.lower() == "qwen":
                editor = self.qwen_editor
            else:
                return OperationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message=f"不支持的编辑器类型: {editor_type}，目前支持 ffmpeg 和 qwen"
                )
            
            # 执行操作
            logger.info(f"执行操作: {operation_name}, 参数: {params}")
            
            # 根据操作名称调用相应的方法
            result_path = self._call_editor_method(editor, operation_name, params)
            
            if result_path and Path(result_path).exists():
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return OperationResult(
                    success=True,
                    output_path=result_path,
                    operation_name=operation_name,
                    execution_time=execution_time,
                    metadata={
                        "editor": editor_type,
                        "params": params
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message="操作执行失败：输出文件未生成"
                )
                
        except Exception as e:
            logger.error(f"执行操作 {operation_name} 失败: {e}")
            return OperationResult(
                success=False,
                operation_name=operation_name,
                error_message=str(e)
            )
    
    def _call_editor_method(self, editor, operation_name: str, params: Dict[str, Any]) -> Optional[str]:
        """
        调用编辑器的相应方法
        
        Args:
            editor: 编辑器实例
            operation_name: 操作名称
            params: 参数
            
        Returns:
            str: 输出文件路径
        """
        # 操作名称到方法名的映射
        method_mapping = {
            # FFmpeg 视频编辑操作
            'trim': 'trim',
            'add_transition': 'add_transition',
            'concatenate': 'concatenate',
            'concatenate_multiple': 'concatenate_multiple',
            'adjust_speed': 'adjust_speed',
            'add_text': 'add_text',
            'adjust_volume': 'adjust_volume',
            'rotate': 'rotate',
            'crop': 'crop',
            'add_background_music': 'add_background_music',
            'remove_audio': 'remove_audio',
            'extract_audio': 'extract_audio',
            'resize': 'resize',
            'extract_frames': 'extract_frames',
            'create_from_images': 'create_from_images',
            'loop': 'loop',
            'reverse': 'reverse',
            'add_subtitle': 'add_subtitle',
            # Qwen 视频生成操作
            'make_video_by_text': 'make_video_by_text',
            'make_video_by_first_frame': 'make_video_by_first_frame',
            'make_video_by_first_and_last_frame': 'make_video_by_first_and_last_frame',
            'make_video_by_first_frame_and_template': 'make_video_by_first_frame_and_template',
            'extend_video': 'extend_video'
        }
        
        method_name = method_mapping.get(operation_name)
        if not method_name:
            raise ValueError(f"未实现的操作: {operation_name}")
        
        # 检查方法是否存在
        if not hasattr(editor, method_name):
            raise ValueError(f"编辑器不支持操作: {operation_name}")
        
        # 过滤掉内部参数（input_video 和 output_video 由执行器管理）
        # 这些参数不应该传递给编辑器的方法
        filtered_params = {k: v for k, v in params.items() 
                          if k not in ['input_video', 'output_video']}
        
        # 调用方法
        method = getattr(editor, method_name)
        
        # 区分 FFmpeg 和 Qwen 编辑器的处理方式
        from VideoEditor.ffmpeg_editor import FFmpegVideoEditor
        from VideoEditor.qwen_editor import QwenVideoEditor
        
        if isinstance(editor, FFmpegVideoEditor):
            # FFmpeg 编辑器：调用方法配置操作，然后调用 save()
            output_path = params.get('output_video')
            if output_path:
                editor.output_path = output_path
            
            # 调用配置方法（这些方法不返回值，只设置内部状态）
            method(**filtered_params)
            
            # 执行并保存（save() 方法没有返回值，执行后文件保存到 output_path）
            editor.save()
            
            # 返回输出文件路径
            return editor.output_path
            
        elif isinstance(editor, QwenVideoEditor):
            # Qwen 编辑器：方法直接返回输出路径
            result = method(**filtered_params)
            return result
        else:
            # 其他编辑器：直接调用
            result = method(**filtered_params)
            return result
    
    def _generate_output_filename(self, operation_name: str, input_video: str) -> str:
        """生成输出文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_name = Path(input_video).stem
        return f"{input_name}_{operation_name}_{timestamp}.mp4"
    
    def execute_batch(
        self,
        operations: List[Dict[str, Any]],
        input_video: str
    ) -> List[OperationResult]:
        """
        批量执行操作
        
        Args:
            operations: 操作列表
            input_video: 输入视频路径
            
        Returns:
            List[OperationResult]: 操作结果列表
        """
        results = []
        current_video = input_video
        
        for i, op_data in enumerate(operations):
            logger.info(f"执行批量操作 {i+1}/{len(operations)}")
            
            result = self.execute_from_json(op_data, current_video)
            results.append(result)
            
            # 如果操作成功，下一个操作使用这个输出
            if result.success and result.output_path:
                current_video = result.output_path
            else:
                logger.warning(f"操作 {i+1} 失败，中断批量执行")
                break
        
        return results
    
    def get_last_result(self) -> Optional[OperationResult]:
        """获取最后一次操作结果"""
        if self.operation_history:
            return self.operation_history[-1]
        return None
    
    def clear_history(self):
        """清空操作历史"""
        self.operation_history.clear()
    
    def save_operation_json(self, json_data: Dict[str, Any], filename: str = None) -> str:
        """
        保存操作JSON到文件
        
        Args:
            json_data: JSON数据
            filename: 文件名（可选）
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"operation_{timestamp}.json"
        
        json_dir = self.output_dir / "operations"
        json_dir.mkdir(exist_ok=True)
        
        json_path = json_dir / filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"操作JSON已保存: {json_path}")
        return str(json_path)
    
    def load_operation_json(self, json_path: str) -> Dict[str, Any]:
        """
        从文件加载操作JSON
        
        Args:
            json_path: JSON文件路径
            
        Returns:
            Dict: JSON数据
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    executor = VideoOperationExecutor(output_dir="Results/test")
    
    # 测试1: 执行单个操作 - trim
    print("=== 测试1: 剪辑操作 ===")
    test_json_1 = {
        "operations": {
            "operation": "trim",
            "params": {
                "start": 1.0,
                "end": 5.0
            },
            "editor": "ffmpeg"
        }
    }
    
    # 保存JSON
    json_path = executor.save_operation_json(test_json_1, "test_trim.json")
    print(f"JSON已保存: {json_path}")
    
    # 执行操作（需要实际的视频文件）
    # result = executor.execute_from_json(test_json_1, "test_video.mp4")
    # print(f"操作成功: {result.success}")
    # print(f"输出路径: {result.output_path}")
    
    # 测试2: 保存和加载JSON
    print("\n=== 测试2: 保存和加载JSON ===")
    test_json_2 = {
        "operations": {
            "operation": "adjust_speed",
            "params": {
                "factor": 2.0
            },
            "editor": "ffmpeg"
        }
    }
    
    json_path_2 = executor.save_operation_json(test_json_2, "test_speed.json")
    loaded_data = executor.load_operation_json(json_path_2)
    print(f"加载的JSON: {loaded_data}")
    
    print("\n测试完成！")

