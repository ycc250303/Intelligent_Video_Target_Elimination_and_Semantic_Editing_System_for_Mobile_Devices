#!/usr/bin/env python3
"""
多模态视频编辑工具
支持通过本地图片/视频 + 文本进行视频生成和编辑
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import DialogueManager
from persona.executor import PersonaAwareVideoOperationExecutor


class MultimodalVideoTool:
    """多模态视频编辑工具"""
    
    def __init__(self, output_dir: str = "Results"):
        """
        初始化工具
        
        Args:
            output_dir: 输出目录
        """
        self.manager = DialogueManager()
        self.executor = PersonaAwareVideoOperationExecutor(output_dir=output_dir)
        self.output_dir = output_dir
        
        print(f"✅ 工具初始化完成")
        print(f"📁 输出目录: {output_dir}")
    
    def process(
        self,
        text: str,
        video_path: Optional[str] = None,
        image_path: Optional[str] = None,
        auto_execute: bool = True,
        verbose: bool = False
    ):
        """
        处理多模态输入并执行操作
        
        Args:
            text: 文本指令或描述
            video_path: 视频文件路径（可选）
            image_path: 图片文件路径（可选）
            auto_execute: 是否自动执行操作
            verbose: 是否显示详细信息
            
        Returns:
            dict: 执行结果
        """
        print("\n" + "="*60)
        print("🎬 开始处理多模态输入")
        print("="*60)
        
        # 1. 验证输入
        print("\n📋 输入信息:")
        print(f"  文本: {text}")
        
        video_paths = []
        image_paths = []
        
        if video_path:
            if not Path(video_path).exists():
                print(f"❌ 错误: 视频文件不存在 - {video_path}")
                return {"success": False, "error": "视频文件不存在"}
            video_paths = [video_path]
            print(f"  视频: {video_path}")
        
        if image_path:
            if not Path(image_path).exists():
                print(f"❌ 错误: 图片文件不存在 - {image_path}")
                return {"success": False, "error": "图片文件不存在"}
            image_paths = [image_path]
            print(f"  图片: {image_path}")
        
        # 确定输入模态
        modal_type = self._get_modal_type(text, video_path, image_path)
        print(f"  模态类型: {modal_type}")
        
        # 2. NLP 解析
        print("\n🤖 AI 正在理解你的指令...")
        
        try:
            if video_paths or image_paths:
                result = self.manager.process_multimodal_input(
                    text=text,
                    video_paths=video_paths,
                    image_paths=image_paths
                )
            else:
                result = self.manager.process_user_input(text)
            
            if verbose:
                print(f"\n[调试] 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if not result.get('success'):
                print(f"❌ 解析失败: {result.get('response', '未知错误')}")
                return result
            
            # 3. 显示操作 JSON
            action = result.get('action', '')
            if action:
                print(f"\n✅ AI 理解成功")
                print(f"\n📝 生成的操作:")
                action_clean = action.replace("action:", "").strip()
                action_json = json.loads(action_clean)
                print(json.dumps(action_json, indent=2, ensure_ascii=False))
            else:
                # 没有 action，可能是对话响应
                response_text = result.get('response', '')
                print(f"\n💬 AI 回复: {response_text}")
                print("⚠️  未生成可执行的操作 JSON")
                return result
            
            # 4. 执行操作
            if auto_execute:
                print("\n⚙️ 执行操作中...")
                exec_result = self._execute_operation(
                    action_json, 
                    video_path,
                    verbose
                )
                
                if exec_result.success:
                    print(f"\n✅ 操作完成!")
                    print(f"📁 输出文件: {exec_result.output_path}")
                    print(f"⏱️  耗时: {exec_result.execution_time:.2f} 秒")
                    
                    return {
                        "success": True,
                        "output_path": exec_result.output_path,
                        "execution_time": exec_result.execution_time,
                        "operation": exec_result.operation_name
                    }
                else:
                    print(f"\n❌ 操作失败: {exec_result.error_message}")
                    return {
                        "success": False,
                        "error": exec_result.error_message
                    }
            else:
                print("\n⏸️  已生成操作 JSON，但未执行（auto_execute=False）")
                return {
                    "success": True,
                    "action_json": action_json,
                    "executed": False
                }
                
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _get_modal_type(self, text: str, video: Optional[str], image: Optional[str]) -> str:
        """确定输入模态类型"""
        if video and image:
            return "视频+图片+文本"
        elif video:
            return "视频+文本 (FFmpeg编辑)"
        elif image:
            return "图片+文本 (Qwen生成)"
        else:
            return "纯文本 (Qwen生成)"
    
    def _execute_operation(self, action_json: dict, input_video: Optional[str], verbose: bool):
        """执行操作"""
        try:
            if input_video:
                # 有输入视频的情况
                result = self.executor.execute_from_json(
                    action_json,
                    input_video=input_video
                )
            else:
                # 纯生成的情况
                result = self.executor.execute_from_json(action_json)
            
            if verbose:
                print(f"\n[调试] 执行结果: success={result.success}")
                if not result.success:
                    print(f"[调试] 错误信息: {result.error_message}")
            
            return result
            
        except Exception as e:
            print(f"执行出错: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            raise
    
    def batch_process(self, tasks: List[dict], verbose: bool = False):
        """
        批量处理多个任务
        
        Args:
            tasks: 任务列表，每个任务包含 text, video_path, image_path
            verbose: 是否显示详细信息
            
        Returns:
            list: 结果列表
        """
        print(f"\n📦 批量处理 {len(tasks)} 个任务")
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- 任务 {i}/{len(tasks)} ---")
            result = self.process(
                text=task.get('text', ''),
                video_path=task.get('video_path'),
                image_path=task.get('image_path'),
                auto_execute=task.get('auto_execute', True),
                verbose=verbose
            )
            results.append(result)
        
        # 统计
        success_count = sum(1 for r in results if r.get('success'))
        print(f"\n📊 批量处理完成: {success_count}/{len(tasks)} 成功")
        
        return results


def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("🎬 多模态视频编辑工具 - 交互模式")
    print("="*60)
    
    # 初始化
    output_dir = input("\n输出目录 [默认: Results]: ").strip() or "Results"
    tool = MultimodalVideoTool(output_dir=output_dir)
    
    while True:
        print("\n" + "-"*60)
        print("请选择操作模式:")
        print("1. 编辑现有视频 (视频 + 文本)")
        print("2. 文本生成视频 (纯文本)")
        print("3. 图片生成视频 (图片 + 文本)")
        print("4. 退出")
        print("-"*60)
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "4":
            print("👋 再见!")
            break
        
        if choice == "1":
            # 编辑视频
            video_path = input("视频文件路径: ").strip()
            text = input("编辑指令 (如'剪掉前3秒'): ").strip()
            
            if not video_path or not text:
                print("❌ 视频路径和指令不能为空")
                continue
            
            tool.process(text=text, video_path=video_path)
            
        elif choice == "2":
            # 文本生成视频
            text = input("描述你想要的视频: ").strip()
            
            if not text:
                print("❌ 描述不能为空")
                continue
            
            tool.process(text=text)
            
        elif choice == "3":
            # 图片生成视频
            image_path = input("图片文件路径: ").strip()
            text = input("描述动态效果: ").strip()
            
            if not image_path or not text:
                print("❌ 图片路径和描述不能为空")
                continue
            
            tool.process(text=text, image_path=image_path)
        
        else:
            print("❌ 无效选择")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="多模态视频编辑工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 交互模式
  python multimodal_video_tool.py

  # 编辑视频
  python multimodal_video_tool.py --text "剪掉前3秒" --video input.mp4

  # 文本生成视频
  python multimodal_video_tool.py --text "一只猫在草地上奔跑"

  # 图片生成视频
  python multimodal_video_tool.py --text "让这张图片动起来" --image photo.jpg

  # 批量处理（从配置文件）
  python multimodal_video_tool.py --batch tasks.json
        """
    )
    
    parser.add_argument(
        '--text', '-t',
        type=str,
        help='文本指令或描述'
    )
    
    parser.add_argument(
        '--video', '-v',
        type=str,
        help='输入视频路径'
    )
    
    parser.add_argument(
        '--image', '-i',
        type=str,
        help='输入图片路径'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='Results',
        help='输出目录 (默认: Results)'
    )
    
    parser.add_argument(
        '--no-execute',
        action='store_true',
        help='只生成 JSON，不执行操作'
    )
    
    parser.add_argument(
        '--batch', '-b',
        type=str,
        help='批量处理的任务配置文件 (JSON)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细信息'
    )
    
    args = parser.parse_args()
    
    # 如果没有参数，进入交互模式
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # 批量处理模式
    if args.batch:
        if not Path(args.batch).exists():
            print(f"❌ 配置文件不存在: {args.batch}")
            return
        
        with open(args.batch, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        tool = MultimodalVideoTool(output_dir=args.output)
        tool.batch_process(tasks, verbose=args.verbose)
        return
    
    # 单任务处理模式
    if not args.text:
        print("❌ 错误: 必须提供 --text 参数")
        parser.print_help()
        return
    
    tool = MultimodalVideoTool(output_dir=args.output)
    
    result = tool.process(
        text=args.text,
        video_path=args.video,
        image_path=args.image,
        auto_execute=not args.no_execute,
        verbose=args.verbose
    )
    
    # 返回状态码
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
