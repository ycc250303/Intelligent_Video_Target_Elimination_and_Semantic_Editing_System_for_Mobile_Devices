from flask import Flask, request, jsonify, make_response, send_from_directory, send_file
from flask_cors import CORS
import socket
import os
import logging
import netifaces  # 用于获取网络接口信息
from nlp_parser import process_instruction, DialogueManager
from video_editor import MoviePyVideoEditor
import mimetypes
import re

# 导入新的ClipPersona Studio模块
from clip_persona_studio import ClipPersonaStudio
from enhanced_nlp_parser import EnhancedNLPParser
from enhanced_video_comprehension import EnhancedVideoComprehension

# 导入新的Persona API
from api.persona_api import persona_bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_ip_addresses():
    ip_list = []
    interfaces = netifaces.interfaces()
    
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if not ip.startswith('127.'):  # 排除本地回环地址
                    ip_list.append((interface, ip))
    return ip_list

app = Flask(__name__)

# 注册Persona API蓝图
app.register_blueprint(persona_bp)

# 配置 CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
}
})

# 初始化ClipPersona Studio系统
clip_persona_studio = ClipPersonaStudio()
enhanced_nlp_parser = EnhancedNLPParser()
enhanced_video_comprehension = EnhancedVideoComprehension()

# 文件名映射管理
class FileManager:
    def __init__(self):
        self.file_counter = 0
        self.filename_map = {}  # 原始文件名 -> 简化文件名的映射
        self.reverse_map = {}   # 简化文件名 -> 原始文件名的映射
        
    def get_simplified_name(self, original_filename):
        # 如果原始文件名已经有映射，直接返回
        if original_filename in self.filename_map:
            return self.filename_map[original_filename]
            
        # 生成新的简化文件名
        self.file_counter += 1
        simplified_name = f"{self.file_counter:03d}.mp4"  # 例如：001.mp4
        
        # 保存映射关系
        self.filename_map[original_filename] = simplified_name
        self.reverse_map[simplified_name] = original_filename
        
        return simplified_name
        
    def get_original_name(self, simplified_name):
        return self.reverse_map.get(simplified_name)
        
    def has_file(self, original_filename):
        return original_filename in self.filename_map

# 创建文件管理器实例
file_manager = FileManager()
# 创建对话管理器实例
dialogue_manager = DialogueManager()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

# 健康检查端点
@app.route('/health-check', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    client_ip = request.remote_addr
    logger.info(f"收到健康检查请求，来自: {client_ip}")
    return jsonify({
        "status": "ok",
        "message": "服务器运行正常",
        "client_ip": client_ip
    })

# Favicon 端点
@app.route('/favicon.ico')
def favicon():
    # 返回204 No Content，避免浏览器重复请求
    # 这是处理favicon请求的标准做法
    response = make_response('', 204)
    response.headers['Cache-Control'] = 'public, max-age=3600'  # 缓存1小时
    return response

# 处理其他静态资源请求
@app.route('/robots.txt')
def robots():
    return make_response('User-agent: *\nDisallow: /', 200, {'Content-Type': 'text/plain'})

# 根路径重定向到健康检查
@app.route('/')
def root():
    return jsonify({
        "message": "ClipPersona API Server",
        "endpoints": {
            "health_check": "/health-check",
            "upload_video": "/upload-video",
            "process_video": "/process-video",
            "check_file": "/check-file",
            "persona": {
                "create": "/api/persona/create",
                "get": "/api/persona/get/<id>",
                "update": "/api/persona/update/<id>",
                "delete": "/api/persona/delete/<id>",
                "list": "/api/persona/list",
                "featured": "/api/persona/featured",
                "popular": "/api/persona/popular",
                "search": "/api/persona/search",
                "analyze_video": "/api/persona/analyze-video",
                "feedback": "/api/persona/feedback",
                "generate_plan": "/api/persona/generate-plan",
                "record_operation": "/api/persona/record-operation",
                "recommendations": "/api/persona/recommendations",
                "user_personas": "/api/persona/user/<author>",
                "statistics": "/api/persona/statistics/<id>",
                "categories": "/api/persona/categories"
            }
        }
    })

# 上传视频端点
@app.route('/upload-video', methods=['POST', 'OPTIONS'])
def upload_video():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    try:
        client_ip = request.remote_addr
        logger.info(f"收到视频上传请求，客户端IP: {client_ip}")
        logger.info(f"请求头: {dict(request.headers)}")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"内容类型: {request.content_type}")
        
        # 检查文件大小
        content_length = request.content_length
        if content_length:
            logger.info(f"请求内容长度: {content_length} bytes ({content_length/1024/1024:.2f} MB)")
        
        if 'video' not in request.files:
            logger.error("请求中没有找到 'video' 字段")
            logger.info(f"可用的文件字段: {list(request.files.keys())}")
            return jsonify({"error": "没有上传文件", "available_fields": list(request.files.keys())}), 400
            
        video_file = request.files['video']
        if video_file.filename == '':
            logger.error("文件名为空")
            return jsonify({"error": "未选择文件"}), 400
            
        original_filename = video_file.filename
        logger.info(f"原始文件名: {original_filename}")
        
        # 检查文件类型
        if not original_filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
            logger.warning(f"不支持的文件类型: {original_filename}")
            return jsonify({"error": "不支持的文件类型，请上传视频文件"}), 400
        
        simplified_name = file_manager.get_simplified_name(original_filename)
        logger.info(f"简化文件名: {simplified_name}")
        
        # 保存文件
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            logger.info(f"创建上传目录: {upload_folder}")
            
        file_path = os.path.join(upload_folder, simplified_name)
        
        # 保存文件并记录进度
        logger.info(f"开始保存文件: {file_path}")
        video_file.save(file_path)
        
        # 验证文件是否保存成功
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"视频保存成功: {file_path} (大小: {file_size} bytes)")
        else:
            logger.error(f"文件保存失败: {file_path}")
            return jsonify({"error": "文件保存失败"}), 500
        
        return jsonify({
            "status": "success",
            "message": "视频上传成功",
            "file_path": file_path,
            "simplified_name": simplified_name,
            "file_size": os.path.getsize(file_path)
        })
        
    except Exception as e:
        logger.error(f"上传视频时出错: {str(e)}")
        logger.exception("详细错误信息：")
        return jsonify({"error": str(e), "type": "upload_error"}), 500

# 添加视频文件访问端点
@app.route('/uploads/<path:filename>')
def serve_video(filename):
    try:
        video_path = os.path.join('uploads', filename)
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return jsonify({"error": "文件不存在"}), 404

        # 获取文件大小
        file_size = os.path.getsize(video_path)
        
        # 处理范围请求
        range_header = request.headers.get('Range', None)
        if range_header:
            byte1, byte2 = 0, None
            match = re.search('bytes=(\d+)-(\d*)', range_header)
            if match:
                groups = match.groups()
                if groups[0]:
                    byte1 = int(groups[0])
                if groups[1]:
                    byte2 = int(groups[1])
            
            if byte2 is None:
                byte2 = file_size - 1
            length = byte2 - byte1 + 1

            # 打开文件并读取指定范围的数据
            with open(video_path, 'rb') as f:
                f.seek(byte1)
                data = f.read(length)

            response = make_response(data)
            response.headers.add('Content-Type', 'video/mp4')
            response.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(length))
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Range')
            response.status_code = 206
            
            return response
            
        # 非范围请求，返回完整文件
        response = send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=False,
            conditional=True
        )
        
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(file_size))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Range')
        return response

    except Exception as e:
        logger.error(f"访问视频文件失败: {str(e)}")
        logger.exception("详细错误信息：")
        return jsonify({"error": str(e)}), 500

# 修改处理视频编辑请求的函数
@app.route('/process-video', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        logger.info(f"收到视频处理请求，来自: {request.remote_addr}")
        
        # 检查文件和指令
        if 'video' not in request.files:
            return jsonify({"error": "请上传视频文件"}), 400
        if 'instruction' not in request.form:
            return jsonify({"error": "请提供处理指令"}), 400
            
        video_file = request.files['video']
        instruction = request.form['instruction']
        
        if video_file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
            
        # 获取或创建简化文件名
        original_filename = video_file.filename
        simplified_name = file_manager.get_simplified_name(original_filename)
        
        # 保存视频文件
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        video_path = os.path.join(upload_folder, simplified_name)
        
        # 如果文件不存在才保存
        if not os.path.exists(video_path):
            video_file.save(video_path)
            logger.info(f"视频保存成功: {video_path} (原始文件名: {original_filename})")
            
        # 处理视频
        dialogue_manager.set_current_video(video_path)
        action, confirmation, _ = process_instruction(instruction)
        
        if action:
            editor = MoviePyVideoEditor(video_path)
            try:
                success = editor.execute_action(action)
                if not success:
                    return jsonify({
                        "status": "error",
                        "message": "操作执行失败，请检查参数是否正确"
                    }), 400
            except Exception as e:
                logger.error(f"执行操作时发生异常: {e}")
                return jsonify({
                    "status": "error",
                    "message": f"操作执行失败: {str(e)}"
                }), 400
            
            # 为处理后的视频创建新的简化文件名
            output_simplified_name = f"output_{simplified_name}"
            output_path = os.path.join(upload_folder, output_simplified_name)
            
            # 保存处理后的视频
            editor.output_path = output_path
            editor.save()
            editor.close()

            # 确保输出文件存在
            if not os.path.exists(output_path):
                raise Exception("处理后的视频文件未生成")

            # 构建相对路径的URL
            video_url = f"/uploads/{output_simplified_name}"
            
            logger.info(f"视频处理完成，输出URL: {video_url}")
            
            return jsonify({
                "status": "success",
                "message": confirmation,
                "output_path": video_url,
                "simplified_name": output_simplified_name
            })
        else:
            return jsonify({
                "status": "error",
                "message": confirmation
            }), 400
            
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        logger.exception("详细错误信息：")
        return jsonify({"error": str(e)}), 500

# 检查文件是否已上传
@app.route('/check-file', methods=['POST'])
def check_file():
    try:
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({"error": "未提供文件名"}), 400
            
        original_filename = data['filename']
        is_uploaded = file_manager.has_file(original_filename)
        
        if is_uploaded:
            simplified_name = file_manager.get_simplified_name(original_filename)
            return jsonify({
                "status": "success",
                "exists": True,
                "simplified_name": simplified_name
            })
        else:
            return jsonify({
                "status": "success",
                "exists": False
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ClipPersona Studio API端点

@app.route('/api/persona/create', methods=['POST', 'OPTIONS'])
def create_persona():
    """创建新的剪辑人格"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        persona_name = data.get('persona_name')
        
        if not persona_name:
            return jsonify({'error': 'persona_name is required'}), 400
        
        # 创建新的人格
        persona = clip_persona_studio.create_persona(user_id, persona_name)
        persona.save_persona()
        
        return jsonify({
            'success': True,
            'persona': {
                'user_id': persona.user_id,
                'persona_name': persona.persona_name,
                'creation_date': persona.creation_date.isoformat(),
                'style_summary': persona.get_style_summary()
            }
        })
    
    except Exception as e:
        logger.error(f"创建人格失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/get', methods=['POST', 'OPTIONS'])
def get_persona():
    """获取用户的人格"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        persona_name = data.get('persona_name')
        
        if not persona_name:
            return jsonify({'error': 'persona_name is required'}), 400
        
        # 获取人格
        persona = clip_persona_studio.get_persona(user_id, persona_name)
        
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        return jsonify({
            'success': True,
            'persona': {
                'user_id': persona.user_id,
                'persona_name': persona.persona_name,
                'creation_date': persona.creation_date.isoformat(),
                'last_updated': persona.last_updated.isoformat(),
                'style_summary': persona.get_style_summary(),
                'preference_tags': [tag['tag'] for tag in persona.preference_tags],
                'editing_history_count': len(persona.editing_history)
            }
        })
    
    except Exception as e:
        logger.error(f"获取人格失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/analyze-video', methods=['POST', 'OPTIONS'])
def analyze_video_preferences():
    """分析视频偏好"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        persona_name = data.get('persona_name')
        video_path = data.get('video_path')
        
        if not all([persona_name, video_path]):
            return jsonify({'error': 'persona_name and video_path are required'}), 400
        
        # 获取人格
        persona = clip_persona_studio.get_persona(user_id, persona_name)
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # 分析视频偏好
        analysis_result = clip_persona_studio.analyze_video_preferences(persona, video_path)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
    
    except Exception as e:
        logger.error(f"分析视频偏好失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/feedback', methods=['POST', 'OPTIONS'])
def process_user_feedback():
    """处理用户反馈"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        persona_name = data.get('persona_name')
        feedback = data.get('feedback', {})
        
        if not persona_name:
            return jsonify({'error': 'persona_name is required'}), 400
        
        # 获取人格
        persona = clip_persona_studio.get_persona(user_id, persona_name)
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # 处理反馈
        clip_persona_studio.process_user_feedback(persona, feedback)
        
        return jsonify({
            'success': True,
            'message': '反馈已处理并更新人格',
            'updated_style_summary': persona.get_style_summary()
        })
    
    except Exception as e:
        logger.error(f"处理用户反馈失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/generate-plan', methods=['POST', 'OPTIONS'])
def generate_editing_plan():
    """根据人格和用户指令生成剪辑方案"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        persona_name = data.get('persona_name')
        user_instruction = data.get('instruction')
        video_path = data.get('video_path')
        
        if not all([persona_name, user_instruction]):
            return jsonify({'error': 'persona_name and instruction are required'}), 400
        
        # 获取人格
        persona = clip_persona_studio.get_persona(user_id, persona_name)
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # 生成剪辑方案
        editing_plan = clip_persona_studio.generate_editing_plan(persona, user_instruction, video_path)
        
        return jsonify({
            'success': True,
            'editing_plan': editing_plan
        })
    
    except Exception as e:
        logger.error(f"生成剪辑方案失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nlp/parse-instruction', methods=['POST', 'OPTIONS'])
def parse_instruction():
    """解析自然语言指令"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        instruction = data.get('instruction')
        context = data.get('context', {})
        
        if not instruction:
            return jsonify({'error': 'instruction is required'}), 400
        
        # 解析指令
        parsed_result = enhanced_nlp_parser.parse_instruction(instruction, context)
        
        # 验证指令
        validation_result = enhanced_nlp_parser.validate_instruction(instruction)
        
        return jsonify({
            'success': True,
            'parsed_result': parsed_result,
            'validation': validation_result
        })
    
    except Exception as e:
        logger.error(f"解析指令失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nlp/generate-plan', methods=['POST', 'OPTIONS'])
def generate_nlp_plan():
    """根据NLP解析结果生成剪辑方案"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        parsed_instruction = data.get('parsed_instruction')
        persona_style = data.get('persona_style', {})
        
        if not parsed_instruction:
            return jsonify({'error': 'parsed_instruction is required'}), 400
        
        # 生成剪辑方案
        editing_plan = enhanced_nlp_parser.generate_editing_plan(parsed_instruction, persona_style)
        
        return jsonify({
            'success': True,
            'editing_plan': editing_plan
        })
    
    except Exception as e:
        logger.error(f"生成NLP剪辑方案失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/analyze', methods=['POST', 'OPTIONS'])
def analyze_video():
    """综合视频分析"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        analysis_level = data.get('analysis_level', 'full')
        
        if not video_path:
            return jsonify({'error': 'video_path is required'}), 400
        
        # 分析视频
        analysis_result = enhanced_video_comprehension.comprehensive_analysis(video_path, analysis_level)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
    
    except Exception as e:
        logger.error(f"视频分析失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/list', methods=['POST', 'OPTIONS'])
def list_personas():
    """列出用户的所有人格"""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        # 获取人格列表（这里需要实现从文件系统读取）
        persona_dir = f"persona_models"
        personas = []
        
        if os.path.exists(persona_dir):
            for item in os.listdir(persona_dir):
                if item.startswith(f"{user_id}_") and os.path.isdir(os.path.join(persona_dir, item)):
                    persona_name = item.replace(f"{user_id}_", "")
                    persona = clip_persona_studio.get_persona(user_id, persona_name)
                    if persona:
                        personas.append({
                            'persona_name': persona.persona_name,
                            'creation_date': persona.creation_date.isoformat(),
                            'last_updated': persona.last_updated.isoformat(),
                            'style_summary': persona.get_style_summary()
                        })
        
        return jsonify({
            'success': True,
            'personas': personas
        })
    
    except Exception as e:
        logger.error(f"列出人格失败: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("服务器启动配置:")
    print("="*50)
    
    # 获取所有可用的 IP 地址
    ip_addresses = get_all_ip_addresses()
    print("\n可用的网络接口和IP地址:")
    for interface, ip in ip_addresses:
        print(f"接口: {interface}")
        print(f"IP地址: {ip}")
        print("-" * 30)
    
    print("\n请尝试使用以上任一IP地址访问服务器")
    print(f"端口: 8000")
    print("\n提示:")
    print("1. 请确保手机和电脑在同一网络下")
    print("2. 依次尝试使用上述每个IP地址")
    print("3. 在手机浏览器中访问 http://[IP地址]:8000/health-check")
    print("4. 如果仍然无法访问，请检查防火墙设置")
    print("="*50 + "\n")
    
    try:
        # 启动 Flask 服务器
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"\n启动服务器时出错: {e}")
        print("请检查端口 8000 是否被占用")