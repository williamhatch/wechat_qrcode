from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
import time
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

# 配置 CORS，允许所有来源访问
CORS(app, 
     origins="*",  # 允许所有来源
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"])

# WeChat configuration
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/wechat/get_qr_code', methods=['GET'])
def get_qr_code():
    print("收到获取二维码的请求")  # 调试日志
    try:
        # 测试用，返回一个占位图片
        scene_str = str(int(time.time()))
        return jsonify({
            'status': 'success',
            'qr_code_url': 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=WeChatLogin_' + scene_str,
            'scene': scene_str
        })

    except Exception as e:
        print(f"生成二维码时出错: {str(e)}")  # 调试日志
        return jsonify({'error': str(e)}), 500

@app.route('/api/wechat/check_login', methods=['POST'])
def check_login():
    scene = request.json.get('scene')
    if not scene:
        return jsonify({
            'status': 'error',
            'is_logged_in': False,
            'message': '无效的场景值'
        })

    # 测试用，始终返回未登录状态
    return jsonify({
        'status': 'success',
        'is_logged_in': False
    })

@app.route('/api/wechat/callback', methods=['GET', 'POST'])
def wechat_callback():
    """
    This endpoint would be called by WeChat's server when a user scans the QR code
    In a real application, you would verify the signature and process the login
    """
    if request.method == 'GET':
        # Handle WeChat server verification
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        # Verify the signature here
        # For demo purposes, we'll just return the echostr
        return echostr

    elif request.method == 'POST':
        # Handle WeChat message events
        try:
            data = request.get_data()
            # Process XML data from WeChat
            # For demo purposes, we'll just set the user as logged in
            session['user_id'] = 'demo_user'
            return 'success'
        except Exception as e:
            return str(e)

@app.route('/api/user/status', methods=['GET'])
@login_required
def get_user_status():
    return jsonify({
        'status': 'success',
        'user_id': session.get('user_id')
    })

if __name__ == '__main__':
    app.run(debug=True)
