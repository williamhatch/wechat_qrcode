from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
import time
import hashlib
import logging
import xml.etree.ElementTree as ET
from functools import wraps

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 用户登录状态存储
user_login_info = {}

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

# 配置 CORS
CORS(app, 
     resources={
         r"/api/*": {  # 只对 /api 路由启用 CORS
             "origins": ["http://localhost:5173", "http://localhost:5174"],  # 允许的源
             "methods": ["GET", "POST", "OPTIONS"],  # 允许的方法
             "allow_headers": ["Content-Type", "Authorization", "Bypass-Tunnel-Reminder"],  # 允许的头部
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": False,
             "max_age": 600  # 预检请求的缓存时间
         }
     })

@app.after_request
def after_request(response):
    """添加响应头"""
    # 确保 OPTIONS 请求也返回正确的 CORS 头
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Bypass-Tunnel-Reminder'
        response.headers['Access-Control-Max-Age'] = '600'
    return response

# WeChat configuration
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')
WECHAT_TOKEN = os.getenv('WECHAT_TOKEN')

def parse_xml(xml_data):
    """解析微信发送的XML数据"""
    try:
        root = ET.fromstring(xml_data)
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data
    except Exception as e:
        logger.error(f"解析XML出错: {str(e)}")
        return None

def get_access_token():
    """获取微信access_token"""
    try:
        url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}'
        response = requests.get(url)
        result = response.json()
        
        if 'access_token' in result:
            return result['access_token']
        else:
            logger.error(f"获取access_token失败: {result}")
            return None
    except Exception as e:
        logger.error(f"获取access_token出错: {str(e)}")
        return None

def get_user_info(openid):
    """获取用户信息"""
    try:
        access_token = get_access_token()
        if not access_token:
            return None
            
        url = f'https://api.weixin.qq.com/cgi-bin/user/info?access_token={access_token}&openid={openid}&lang=zh_CN'
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logger.error(f"获取用户信息出错: {str(e)}")
        return None

def check_signature():
    """验证微信服务器的签名"""
    try:
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        token = WECHAT_TOKEN
        
        logger.debug(f"收到验证请求：signature={signature}, timestamp={timestamp}, nonce={nonce}, token={token}")
        
        # 按照微信的规则进行签名验证
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        
        logger.debug(f"排序后的字符串：{tmp_str}")
        
        hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
        calc_signature = hash_obj.hexdigest()
        
        logger.debug(f"计算得到的签名：{calc_signature}")
        logger.debug(f"微信发送的签名：{signature}")
        
        return calc_signature == signature
    except Exception as e:
        logger.error(f"验证签名时出错：{str(e)}")
        return False

@app.route('/api/wechat/callback', methods=['GET', 'POST'])
def wechat_callback():
    """处理微信服务器的回调"""
    if request.method == 'GET':
        # 处理服务器配置验证
        logger.info("收到微信服务器验证请求")
        if check_signature():
            return request.args.get('echostr', '')
        return 'signature check failed', 403

    elif request.method == 'POST':
        # 处理微信消息推送
        if not check_signature():
            return 'signature check failed', 403

        try:
            xml_data = request.data
            logger.info(f"收到微信消息: {xml_data}")
            
            # 解析XML数据
            msg_data = parse_xml(xml_data)
            if not msg_data:
                return 'success'
            
            msg_type = msg_data.get('MsgType')
            event = msg_data.get('Event')
            
            if msg_type == 'event':
                if event == 'SCAN':  # 已关注用户扫码
                    scene_str = msg_data.get('EventKey')
                    openid = msg_data.get('FromUserName')
                elif event == 'subscribe':  # 未关注用户扫码关注
                    scene_str = msg_data.get('EventKey', '')[8:]  # qrscene_xxx
                    openid = msg_data.get('FromUserName')
                else:
                    return 'success'
                
                # 处理扫码事件
                if scene_str and openid:
                    # 获取用户信息
                    user_info = get_user_info(openid)
                    if user_info:
                        # 保存用户信息到内存
                        user_login_info[scene_str] = {
                            'user_id': openid,
                            'user_info': user_info,
                            'login_time': time.time()
                        }
                        logger.info(f"用户登录成功: {user_info}")
                    
            return 'success'
            
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
            return 'success'

@app.route('/api/wechat/get_qr_code', methods=['GET'])
def get_qr_code():
    """获取微信登录二维码"""
    try:
        # 获取access_token
        access_token = get_access_token()
        if not access_token:
            return jsonify({'error': '获取access_token失败'}), 500

        # 创建临时二维码
        qr_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + access_token
        scene_str = f"login_{int(time.time())}"  # 使用时间戳创建唯一的场景值
        qr_data = {
            'expire_seconds': 600,  # 10分钟过期
            'action_name': 'QR_STR_SCENE',
            'action_info': {'scene': {'scene_str': scene_str}}
        }
        
        qr_response = requests.post(qr_url, json=qr_data)
        qr_result = qr_response.json()
        
        if 'ticket' not in qr_result:
            logger.error(f"获取二维码ticket失败: {qr_response.text}")
            return jsonify({'error': '获取二维码失败'}), 500

        # 生成二维码URL
        qr_code_url = f"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={qr_result['ticket']}"
        
        return jsonify({
            'status': 'success',
            'qr_code_url': qr_code_url,
            'scene': scene_str
        })

    except Exception as e:
        logger.error(f"生成二维码时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/wechat/check_login', methods=['POST'])
def check_login():
    """检查用户是否已登录"""
    scene = request.json.get('scene')
    if not scene:
        return jsonify({
            'status': 'error',
            'is_logged_in': False,
            'message': '无效的场景值'
        })

    # 检查用户是否已扫码并关注
    login_info = user_login_info.get(scene)
    is_logged_in = login_info is not None
    
    if is_logged_in:
        # 清理超时的登录信息（10分钟后）
        if time.time() - login_info['login_time'] > 600:
            del user_login_info[scene]
            is_logged_in = False
    
    return jsonify({
        'status': 'success',
        'is_logged_in': is_logged_in,
        'user_info': login_info['user_info'] if is_logged_in else None
    })

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        scene = request.json.get('scene')
        if not scene:
            return jsonify({'error': 'Unauthorized'}), 401
        
        login_info = user_login_info.get(scene)
        if not login_info:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/user/status', methods=['GET'])
@login_required
def get_user_status():
    return jsonify({
        'status': 'success',
        'user_id': request.json.get('scene')
    })

if __name__ == '__main__':
    app.run(debug=True)
