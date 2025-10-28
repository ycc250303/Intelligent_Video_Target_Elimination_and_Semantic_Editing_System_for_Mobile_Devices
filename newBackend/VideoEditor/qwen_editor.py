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
            print(f"❌ API调用失败, status_code: {rsp.status_code}, code: {rsp.code}, message: {rsp.message}")
            return None
        
        print("✅ API调用成功，等待视频生成...")
        print("task_id:", rsp.output.task_id)

        # 获取异步任务状态
        status = VideoSynthesis.fetch(rsp)
        if status.status_code == HTTPStatus.OK:
            print("task_status:", status.output.task_status)
        else:
            print(f"❌ 获取状态失败, status_code: {status.status_code}, code: {status.code}, message: {status.message}")
            return None

        # 等待异步任务结束
        final_rsp = VideoSynthesis.wait(rsp)
        # 优化：只打印关键信息，不打印完整响应（太冗长）
        # print(final_rsp)  # 注释掉完整响应打印

        if final_rsp.status_code == HTTPStatus.OK:
            print("✅ 视频生成成功，URL:", final_rsp.output.video_url)
            return final_rsp.output.video_url
        else:
            print(f"❌ 等待失败, status_code: {final_rsp.status_code}, code: {final_rsp.code}, message: {final_rsp.message}")
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

        # 简化URL显示（只显示关键部分）
        display_url = video_url.split("?")[0].split("/")[-1]
        print(f"正在下载视频: {display_url}")
        rsp = requests.get(video_url, stream=True)
        if rsp.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in rsp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ 视频下载完成: {save_path}")
            return save_path
        else:
            print(f"❌ 下载失败，状态码: {rsp.status_code}")
            return None

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


if __name__ == '__main__':
    # 获取脚本所在目录，构建正确的图片路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(os.path.dirname(script_dir), "Images")
    
    img_url = os.path.join(images_dir, "hanfu.png")
    img_url_first = os.path.join(images_dir, "wanx-demo-1.png")
    first_img_url = os.path.join(images_dir, "first_frame.png")
    last_img_url = os.path.join(images_dir, "last_frame.png")
    
    prompt = "小猫在草地上快速奔跑"
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")

    # 动态构建操作配置
    op_json = {
        "operations": [
            {
                "operation": "make_video_by_first_frame",
                "params": {
                    "img_url": img_url_first,
                    "prompt": prompt
                },
                "editor": "qwen"
            }
        ]
    }

    # 测试: 从图片生成视频
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
 