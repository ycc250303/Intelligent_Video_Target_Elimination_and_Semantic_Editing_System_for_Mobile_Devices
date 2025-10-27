import base64
import os
import sys
import requests
import glob
import re
from http import HTTPStatus
from dashscope import VideoSynthesis
import mimetypes
import dashscope

# 添加父目录到路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import QWEN_API_KEY, QWEN_BASE_GENERATE_VIDEO_URL

# 导入视频上传工具函数
from VideoEditor.get_template_video_url import upload_file_and_get_url


class QwenVideoEditor:
    def __init__(self, api_key, base_dir="Results"):
        self.api_key = QWEN_API_KEY
        self.base_dir = base_dir
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = QWEN_BASE_GENERATE_VIDEO_URL
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    @staticmethod
    def encode_file(file_path):
        """
        将文件编码为base64
        Args:
            file_path: 文件路径
        Returns:
            str: base64编码的文件
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError("不支持或无法识别的图像格式")
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"

    @staticmethod
    def ensure_base64_image(img_input):
        """
        统一处理图片输入:
        - 如果是 data:base64 格式，直接返回
        - 如果是文件路径，则调用 encode_file 转成 data:base64
        - 如果是 http(s) URL，直接返回
        Args:
            img_input: 图片输入
        Returns:
            str: base64编码的图片
        """
        if isinstance(img_input, str):
            if img_input.startswith("data:"):
                return img_input
            elif img_input.startswith("http://") or img_input.startswith("https://"):
                return img_input
            elif os.path.exists(img_input):
                return QwenVideoEditor.encode_file(img_input)
            else:
                raise ValueError(f"无法识别的输入: {img_input}")
        else:
            raise TypeError("图片输入必须是字符串类型（文件路径 / data:base64 / URL）")


    @staticmethod
    def run_async_video_task(rsp):
        """
        统一处理异步视频生成任务，返回最终 video_url 或 None
        Args:
            rsp: 异步视频生成任务响应
        Returns:
            str: 生成的视频URL，如果失败返回None
        """
        if rsp.status_code != HTTPStatus.OK:
            print(f"Failed, status_code: {rsp.status_code}, code: {rsp.code}, message: {rsp.message}")
            return None
        
        print("task_id:", rsp.output.task_id)

        # 获取异步任务状态
        status = VideoSynthesis.fetch(rsp)
        if status.status_code == HTTPStatus.OK:
            print("task_status:", status.output.task_status)
        else:
            print(f"Fetch failed, status_code: {status.status_code}, code: {status.code}, message: {status.message}")
            return None

        # 等待异步任务结束
        final_rsp = VideoSynthesis.wait(rsp)
        print(final_rsp)

        if final_rsp.status_code == HTTPStatus.OK:
            print("video_url:", final_rsp.output.video_url)
            return final_rsp.output.video_url
        else:
            print(f"Wait failed, status_code: {final_rsp.status_code}, code: {final_rsp.code}, message: {final_rsp.message}")
            return None

    def download_video(self,video_url, save_dir, filename=None):
        """
        下载视频到本地
        Args:
            video_url: 视频下载链接
            save_dir: 存放的文件夹路径（由你定义）
            filename: 文件名，默认为URL中的文件名
        Returns:
            str: 本地保存的视频路径
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if filename is None:
            filename = os.path.basename(video_url.split("?")[0])  # 去掉url里的参数

        save_path = os.path.join(save_dir, filename)

        print(f"正在下载视频: {video_url}")
        rsp = requests.get(video_url, stream=True)
        if rsp.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in rsp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"下载完成: {save_path}")
            return save_path
        else:
            print(f"下载失败，状态码: {rsp.status_code}")
            return None

    def upload_video_to_oss(self, file_path, model_name="qwen-vl-plus"):
        """
        上传本地视频到阿里云OSS临时存储，获取公网可访问的URL
        （复用 get_template_video_url.py 中的函数）
        Args:
            file_path: 本地视频文件路径
            model_name: 模型名称，默认'qwen-vl-plus'
        Returns:
            str: OSS临时URL (oss://开头)，有效期48小时
        """
        # 直接调用已有的上传函数
        return upload_file_and_get_url(self.api_key, model_name, file_path)


    def make_video_by_first_frame(self,img_url, prompt,model='wan2.2-i2v-flash',resolution="1080P"):
        """
        从图片生成视频
        Args:
            img_url: 图片文件路径或Base64编码的图片数据
            prompt: 视频生成提示词
            model: 使用的模型，默认'wan2.2-i2v-flash'
        Returns:
            str: 生成的视频URL，如果失败返回None
        """
    
        if img_url is None:
            return None
        
        print('please wait...')  
        # 兼容 data:base64 或 本地文件路径
        img_url = self.ensure_base64_image(img_url)

        # 异步调用，返回task_id
        rsp = VideoSynthesis.async_call(api_key=self.api_key,
                                        model=model,
                                        prompt=prompt,
                                        resolution=resolution,
                                        img_url=img_url)
        video_url = self.run_async_video_task(rsp)
        if video_url:
            return self.download_video(video_url, self.base_dir)
        return None

    def make_video_by_first_and_last_frame(self,first_img_url, last_img_url,prompt,model='wanx2.2-kf2v-flash',resolution="720P"):
        """
        从首尾两张图片生成视频
        Args:
            first_img_url: 第一张图片文件路径或Base64编码
            last_img_url: 最后一张图片文件路径或Base64编码
            prompt: 视频生成提示词
            model: 使用的模型，默认'wanx2.2-kf2v-flash'
        Returns:
            str: 生成的视频URL，如果失败返回None
        """
        if first_img_url is None or last_img_url is None:
            return None
    
        first_img_url = self.ensure_base64_image(first_img_url)
        last_img_url = self.ensure_base64_image(last_img_url)
            
        rsp = VideoSynthesis.async_call(api_key=self.api_key,
                                model=model,
                                prompt=prompt,
                                first_frame_url=first_img_url,
                                last_frame_url=last_img_url,
                                resolution=resolution,
                                prompt_extend=True)
        video_url = self.run_async_video_task(rsp)
        if video_url:
            return self.download_video(video_url, self.base_dir)
        return None


    def make_video_by_text(self,prompt, model='wan2.2-t2v-plus',size="832*480"):
        """
        从文本生成视频
        Args:
            prompt: 文本描述
            model: 使用的模型，默认'wan2.2-t2v-plus'
            size: 视频尺寸，默认'832*480'
        Returns:
            str: 生成的视频本地路径，如果失败返回None
        """
        if prompt is None or prompt == "":
            return None
        print('please wait...')
        rsp = VideoSynthesis.async_call(api_key=self.api_key,
                                        model=model,
                                        prompt=prompt,
                                        prompt_extend=True,
                                        size=size,
                                        negative_prompt="",
                                        watermark=False,
                                        seed=12345)

        video_url = self.run_async_video_task(rsp)
        if video_url:
            return self.download_video(video_url, self.base_dir)
        return None

    def make_video_by_first_frame_and_template(self,img_url,template,model='wanx2.1-i2v-plus',resolution="720P"):
        """
        从图片和模板生成视频
        Args:
            img_url: 图片文件路径或Base64编码
            template: 模板
            resolution: 分辨率
            model: 使用的模型，默认'wanx2.1-i2v-plus'
        Returns:
            str: 生成的视频URL，如果失败返回None
        """
        if img_url is None or template is None:
            return None

        img_url = self.ensure_base64_image(img_url)

        if(template == "hanfu-1" or template == "solaron" or template == "magazine" or
        template == "mech1" or template == "mech2"):
            model = "wanx2.1-kf2v-plus"
        rsp = VideoSynthesis.async_call(api_key=self.api_key,
                                        model=model,
                                        img_url=img_url,
                                        template=template,
                                        resolution=resolution,
                                    )

        video_url = self.run_async_video_task(rsp)
        if video_url:
            return self.download_video(video_url, self.base_dir)
        return None

    def extend_video(self, prompt, first_clip_url, prompt_extend=False):
        """
        视频延展功能 - 延长视频时间到5秒
        
        Args:
            prompt: 提示词，描述生成视频中期望包含的元素和视觉特点（必选）
            first_clip_url: 首段视频的URL地址或本地文件路径（必选）
                           - 支持本地文件路径（会自动上传到OSS临时存储）
                           - 支持 HTTP/HTTPS/OSS URL
                           - 视频格式：MP4，帧率≥16FPS，大小≤50MB，长度≤3秒
            prompt_extend: 是否开启prompt智能改写（可选，默认False）
                          False: 关闭智能改写（推荐）
                          True: 开启智能改写（会增加耗时）
        
        Returns:
            str: 生成的视频本地路径，如果失败返回None
            
        注意:
            - 延长后的视频总时长固定为 5 秒（这是最终输出视频的完整时长）
            - 本地文件会自动上传到阿里云OSS临时存储（有效期48小时）
        """
        if prompt is None or prompt == "":
            print("错误: prompt 参数不能为空")
            return None
        
        if first_clip_url is None or first_clip_url == "":
            print("错误: first_clip_url 参数不能为空")
            return None
        
        # 处理本地文件路径：自动上传到OSS
        if os.path.exists(first_clip_url):
            print(f"检测到本地文件: {first_clip_url}")
            print(f"文件大小: {os.path.getsize(first_clip_url) / 1024 / 1024:.2f} MB")
            print("开始上传到OSS临时存储...")
            try:
                oss_url = self.upload_video_to_oss(first_clip_url)
                print(f"✓ 上传成功！OSS URL: {oss_url}")
                first_clip_url = oss_url
            except Exception as e:
                print(f"✗ 上传视频失败: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # 检查是否为有效的 URL
        if not (first_clip_url.startswith("http://") or 
                first_clip_url.startswith("https://") or 
                first_clip_url.startswith("oss://")):
            print(f"错误: first_clip_url 必须是有效的 URL，当前值: {first_clip_url}")
            return None
        
        print()
        print(f"使用视频URL: {first_clip_url}")
        print('视频延展中，请稍候...')
        
        try:
            # 调用视频延展 API
            # 尝试方案：将所有视频延展参数放在extra_input中
            print("调试信息 - 调用参数:")
            print(f"  model: wanx2.1-vace-plus")
            print(f"  prompt: {prompt}")
            print(f"  first_clip_url: {first_clip_url}")
            print(f"  duration: 5")
            print(f"  prompt_extend: {prompt_extend}")
            print()
            
            rsp = VideoSynthesis.async_call(
                api_key=self.api_key,
                model='wanx2.1-vace-plus',
                prompt=prompt,
                extra_input={
                    'function': 'video_extension',
                    'first_clip_url': first_clip_url,
                    'duration': 5,
                    'prompt_extend': prompt_extend,
                    'watermark': False
                }
            )
            
            video_url = self.run_async_video_task(rsp)
            if video_url:
                return self.download_video(video_url, self.base_dir)
            return None
            
        except Exception as e:
            print(f"视频延展失败: {e}")
            import traceback
            traceback.print_exc()
            return None

        


op_json = {
  "operations": [
    {
      "operation": "make_video_by_first_frame",
      "params": {
        "img_url": "../Images/wanx-demo-1.png",
        "prompt": "小猫在草地上快速奔跑"
      },
      "editor": "qwen"
    }
  ]
}

if __name__ == '__main__':
    # 使用相对路径，从VideoEditor目录出发
    img_url = r"..\Images\hanfu.png"
    img_url_first = r"..\Images\wanx-demo-1.png"
    first_img_url = r"..\Images\first_frame.png"
    last_img_url = r"..\Images\last_frame.png"
    prompt = "小猫在草地上快速奔跑"
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")

    # 测试选项：1-图片生成视频, 2-视频延展
    test_mode = 2  # 修改这里选择测试模式
    
    if test_mode == 1:
        # 测试1: 从图片生成视频
        print("=" * 50)
        print("测试模式 1: 从图片生成视频")
        print("=" * 50)
        for op in op_json["operations"]:
            operation_name = op["operation"]
            params = op.get("params", {})

            # 使用 getattr 获取 editor 对象的方法
            func = getattr(editor, operation_name, None)
            if callable(func):
                try:
                    print(f"执行操作: {operation_name}，参数: {params}")
                    result = func(**params)  # 将 params 作为关键字参数传入
                    if result:
                        print(f"{operation_name} 成功，生成文件: {result}")
                    else:
                        print(f"{operation_name} 执行失败")
                except Exception as e:
                    print(f"{operation_name} 执行出错: {e}")
            else:
                print(f"未找到方法: {operation_name}")
    
    elif test_mode == 2:
        # 测试2: 视频延展功能（支持本地文件自动上传）
        print("=" * 50)
        print("测试模式 2: 视频延展功能")
        print("=" * 50)
        print()
        
        # 方式1: 使用本地视频文件（会自动上传到OSS临时存储）
        # 示例：使用之前生成的视频
        video_path = r"D:\test1\video016.mp4"
        
        # 检查文件是否存在（仅对本地文件）
        if not video_path.startswith("http") and not video_path.startswith("oss://"):
            if not os.path.exists(video_path):
                print(f"错误: 本地视频文件不存在: {video_path}")
                print("\n提示：")
                print("1. 先运行 test_mode = 1 生成一个视频")
                print("2. 或者修改 video_path 为实际的视频文件路径")
                print("3. 或者使用公网视频 URL")
                print("\n视频要求：")
                print("  - 格式: MP4")
                print("  - 帧率: ≥16FPS")
                print("  - 大小: ≤50MB")
                print("  - 长度: ≤3秒")
                exit(1)
        
        extend_prompt = "延续视频内容，保持流畅的动作连贯性"
        
        try:
            print(f"输入视频: {video_path}")
            print(f"提示词: {extend_prompt}")
            print(f"智能改写: {'开启' if False else '关闭'}")
            print()
            print("-" * 50)
            
            result = editor.extend_video(
                prompt=extend_prompt,
                first_clip_url=video_path,
                prompt_extend=False  # 是否开启prompt智能改写
            )
            
            if result:
                print()
                print("=" * 50)
                print("✓ 视频延展成功！")
                print("=" * 50)
                print(f"生成文件: {result}")
                print(f"视频时长: 5秒（延展后）")
            else:
                print()
                print("=" * 50)
                print("✗ 视频延展失败")
                print("=" * 50)
                
        except Exception as e:
            print()
            print("=" * 50)
            print(f"✗ 视频延展出错: {e}")
            print("=" * 50)
            import traceback
            traceback.print_exc()
    
