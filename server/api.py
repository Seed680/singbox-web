import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, make_response, send_from_directory, send_file
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import platform
import subprocess
import signal
import psutil
import shutil
import threading
import time
from functools import wraps

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')

# PID 文件路径
PID_FILE = os.path.join(current_dir, 'singbox.pid')

# 配置文件路径
CONFIG_FILE = os.path.join(current_dir, 'config.json')
SUBSCRIBE_CONFIG_FILE = os.path.join(current_dir, 'subscribe_config.json')
MAIN_CONFIG_FILE = os.path.join(current_dir, 'base_config.json')
TASKS_CONFIG_FILE = os.path.join(current_dir, 'tasks_config.json')

# 认证配置文件路径
AUTH_CONFIG_FILE = os.path.join(current_dir, 'auth_config.json')

def init_auth_config():
    """初始化认证配置文件"""
    try:
        if not os.path.exists(AUTH_CONFIG_FILE):
            # 创建默认认证配置
            default_auth = {
                'username': 'admin',
                'password': 'admin'
            }
            with open(AUTH_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_auth, f, indent=2, ensure_ascii=False)
            print(f'认证配置文件已创建: {AUTH_CONFIG_FILE}')
        return True
    except Exception as e:
        print(f'初始化认证配置文件失败: {str(e)}')
        return False

def read_auth_config():
    """读取认证配置"""
    try:
        with open(AUTH_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'读取认证配置失败: {str(e)}')
        return {'username': 'admin', 'password': 'admin'}

def save_auth_config(auth_data):
    """保存认证配置"""
    try:
        with open(AUTH_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'保存认证配置失败: {str(e)}')
        return False

def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 跳过下载API的认证
        if request.path.startswith('/api/config/download/'):
            return f(*args, **kwargs)
        
        # 跳过登录API本身
        if request.path in ['/api/auth/login', '/api/auth/check']:
            return f(*args, **kwargs)
            
        # 检查Authorization头
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未授权访问'}), 401
            
        token = auth_header.split(' ')[1]
        # 简单的token验证（在实际应用中应该使用更安全的JWT）
        if token != 'authenticated':
            return jsonify({'error': '无效的令牌'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def init_config_files():
    """初始化配置文件，如果config.json不存在则从base_config.json复制"""
    try:
        # 检查base_config.json是否存在
        if not os.path.exists(MAIN_CONFIG_FILE):
            print(f"错误：基础配置文件 {MAIN_CONFIG_FILE} 不存在")
            return False
            
        # 如果config.json不存在，从base_config.json复制
        if not os.path.exists(CONFIG_FILE):
            print(f"配置文件 {CONFIG_FILE} 不存在，正在从 {MAIN_CONFIG_FILE} 复制...")
            shutil.copy2(MAIN_CONFIG_FILE, CONFIG_FILE)
            print(f"已创建配置文件：{CONFIG_FILE}")
        
        # 初始化认证配置文件
        init_auth_config()
        
        return True
    except Exception as e:
        print(f"初始化配置文件失败: {str(e)}")
        return False

# 在创建Flask应用之前初始化配置文件
if not init_config_files():
    print("初始化配置文件失败，程序退出")
    exit(1)

app = Flask(__name__)  # 禁用默认静态服务
CORS(app)

# 节点缓存
node_cache = {}

# 创建调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 全局变量用于存储下载密码
download_password = None

# 下载配置文件路径
DOWNLOAD_CONFIG_FILE = os.path.join(current_dir, 'download_config.json')

def init_subscribe_config():
    """初始化订阅配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, SUBSCRIBE_CONFIG_FILE)
        
        initial_config = {
            'subscriptions': [],
            'filters': [],
            'ex_outbounds': []
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(initial_config, f, indent=2, ensure_ascii=False)
        return initial_config
    except Exception as e:
        print(f'初始化订阅配置文件失败: {str(e)}')
        raise

def read_subscribe_config():
    """读取订阅配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, SUBSCRIBE_CONFIG_FILE)
        
        if not os.path.exists(config_path):
            return init_subscribe_config()
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 确保所有必需的字段都存在
        if not isinstance(config, dict):
            return init_subscribe_config()
            
        required_fields = ['subscriptions', 'filters', 'ex_outbounds']
        for field in required_fields:
            if field not in config:
                config[field] = []
                
        return config
    except Exception as e:
        print(f'读取订阅配置文件出错: {str(e)}')
        return init_subscribe_config()

def save_subscribe_config(config):
    """保存订阅配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, SUBSCRIBE_CONFIG_FILE)
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f'订阅配置文件已保存到: {config_path}')
    except Exception as e:
        print(f'保存订阅配置文件失败: {str(e)}')
        raise

def read_config():
    """读取主配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, CONFIG_FILE)
        base_config_path = os.path.join(current_dir, MAIN_CONFIG_FILE)
        
        # 如果主配置文件不存在，使用基础配置
        if not os.path.exists(config_path):
            print(f'主配置文件 {config_path} 不存在，返回基础配置')
            with open(base_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        # 读取主配置文件，直接返回原始内容，不做任何修改
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        print(f'读取主配置文件出错: {str(e)}')
        # 如果出错，返回基础配置
        try:
            with open(base_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as base_e:
            print(f'读取基础配置文件也失败: {str(base_e)}')
            # 返回一个最小配置
            return {
                "outbounds": [],
                "inbounds": [],
                "dns": {},
                "route": {}
            }

def save_config(config, preserve_outbounds=True):
    """保存主配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, CONFIG_FILE)
        
        # 读取现有配置
        if preserve_outbounds and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
                # 保留现有的 outbounds
                if 'outbounds' in existing_config:
                    config['outbounds'] = existing_config['outbounds']
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f'主配置文件已保存到: {config_path}')
    except Exception as e:
        print(f'保存主配置文件失败: {str(e)}')
        raise

def is_node_match_filter(node_tag, filter):
    """检查节点是否匹配过滤器条件"""
    # 检查包含条件
    if filter.get('include'):
        include_keywords = [k.strip() for k in filter['include'].split(',') if k.strip()]
        if not any(keyword in node_tag for keyword in include_keywords):
            return False
    
    # 检查排除条件
    if filter.get('exclude'):
        exclude_keywords = [k.strip() for k in filter['exclude'].split(',') if k.strip()]
        if any(keyword in node_tag for keyword in exclude_keywords):
            return False
    
    return True

def preserve_outbounds(outbounds, subscription_names):
    """递归保留非订阅和过滤器节点"""
    preserved = []
    for outbound in outbounds:
        # 如果节点有 outbounds 属性，递归处理
        if 'outbounds' in outbound:
            # 保留原有的非订阅和过滤器节点
            original_outbounds = [
                ob for ob in outbound['outbounds']
                if not (
                    any(ob.startswith(f"{name}.") for name in subscription_names) or
                    ob.startswith('filter.')
                )
            ]
            # 更新节点的 outbounds
            outbound['outbounds'] = original_outbounds
        preserved.append(outbound)
    return preserved

def process_subscriptions():
    """处理订阅"""
    try:
        print('开始处理订阅...')
        config = read_subscribe_config()
        main_config = read_config()
        subscriptions = config['subscriptions']
        filters = config.get('filters', [])
        
        print(f'找到 {len(subscriptions)} 个订阅和 {len(filters)} 个过滤器')
        
        total_added = 0
        errors = []
        
        # 清空节点缓存
        node_cache.clear()
        
        # 确保主配置中有 outbounds 数组
        if 'outbounds' not in main_config or not isinstance(main_config['outbounds'], list):
            print(f'警告: process_subscriptions中main_config["outbounds"]不是有效的列表, 类型: {type(main_config.get("outbounds"))}')
            main_config['outbounds'] = []
        
        # === 第一步：分类现有节点 ===
        print('=== 开始节点分类 ===')
        default_nodes = []      # 默认节点
        subscription_nodes = [] # 订阅节点
        filter_nodes = []       # 过滤器节点  
        extra_nodes = []        # 额外节点
        
        for outbound in main_config['outbounds']:
            tag = outbound.get('tag', '')
            if tag.startswith('filter.'):
                filter_nodes.append(outbound)
                print(f'分类为过滤器节点: {tag}')
            elif tag.startswith('extra.'):
                extra_nodes.append(outbound)
                print(f'分类为额外节点: {tag}')
            elif any(tag.startswith(f"{sub['name']}.") for sub in subscriptions):
                subscription_nodes.append(outbound)
                print(f'分类为订阅节点: {tag}')
            else:
                default_nodes.append(outbound)
                print(f'分类为默认节点: {tag}')
        
        print(f'节点分类完成 - 默认:{len(default_nodes)}, 订阅:{len(subscription_nodes)}, 过滤器:{len(filter_nodes)}, 额外:{len(extra_nodes)}')
        
        # === 第二步：清理和重置 ===
        # 清空默认节点的outbounds中的三类节点引用
        for node in default_nodes:
            if 'outbounds' in node and isinstance(node['outbounds'], list):
                original_outbounds = node['outbounds'].copy()
                # 移除所有订阅节点、过滤器节点、额外节点的引用
                node['outbounds'] = [
                    out for out in node['outbounds'] 
                    if not (
                        out.startswith('filter.') or 
                        out.startswith('extra.') or 
                        any(out.startswith(f"{sub['name']}.") for sub in subscriptions)
                    )
                ]
                if original_outbounds != node['outbounds']:
                    print(f'清理节点 {node.get("tag")} 的outbounds: {original_outbounds} -> {node["outbounds"]}')
        
        # === 第三步：处理订阅节点 ===
        print('=== 开始处理订阅 ===')
        new_subscription_nodes = []
        
        for subscription in subscriptions:
            try:
                print(f'处理订阅: {subscription["name"]}')
                response = requests.get(subscription['url'])
                response.raise_for_status()
                data = response.json()
                
                if not data.get('outbounds') or not isinstance(data['outbounds'], list):
                    raise ValueError('无效的订阅格式')
                
                print(f'从订阅 {subscription["name"]} 获取到 {len(data["outbounds"])} 个节点')
                
                # 处理节点，添加订阅来源到 tag
                for outbound in data['outbounds']:
                    # 创建订阅节点副本
                    subscription_node = outbound.copy()
                    # 修改 tag 为订阅节点格式
                    subscription_node['tag'] = f"{subscription['name']}.{outbound['tag']}"
                    # 添加到新订阅节点列表
                    new_subscription_nodes.append(subscription_node)
                    # 添加到缓存供过滤器使用
                    node_cache[subscription_node['tag']] = subscription_node
                    print(f'创建订阅节点: {subscription_node["tag"]}')
                
                total_added += len(data['outbounds'])
                
                # 更新订阅的最后更新时间
                subscription['lastUpdate'] = datetime.now().isoformat()
                
            except Exception as error:
                print(f'处理订阅 {subscription["name"]} 时出错:', str(error))
                errors.append({
                    'subscription': subscription['name'],
                    'error': str(error)
                })
        
        # === 第四步：处理过滤器节点 ===
        print('=== 开始处理过滤器 ===')
        new_filter_nodes = []
        
        for filter_config in filters:
            try:
                print(f'处理过滤器: {filter_config["name"]}')
                
                # 获取符合条件的订阅节点
                matched_nodes = []
                if filter_config.get('allNodes'):
                    # 如果选择所有节点，使用所有缓存的订阅节点
                    matched_nodes = [
                        node for node in node_cache.values()
                        if is_node_match_filter(node['tag'], filter_config)
                    ]
                elif filter_config.get('node'):
                    # 如果指定了具体节点，只使用该节点
                    node = node_cache.get(filter_config['node'])
                    if node and is_node_match_filter(node['tag'], filter_config):
                        matched_nodes = [node]
                
                if matched_nodes:
                    # 创建过滤器节点
                    filter_node = {
                        'type': filter_config.get('mode', 'select'),
                        'tag': f"filter.{filter_config['name']}",
                        'outbounds': [node['tag'] for node in matched_nodes]
                    }
                    
                    # 如果是速度测试模式，添加额外参数
                    if filter_config.get('mode') == 'urltest':
                        if filter_config.get('url'):
                            filter_node['url'] = filter_config['url']
                        if filter_config.get('interval'):
                            filter_node['interval'] = filter_config['interval']
                        if filter_config.get('idle_timeout'):
                            filter_node['idle_timeout'] = filter_config['idle_timeout']
                    
                    new_filter_nodes.append(filter_node)
                    print(f'创建过滤器节点: {filter_node["tag"]}，包含 {len(matched_nodes)} 个订阅节点')
                
            except Exception as error:
                print(f'处理过滤器 {filter_config["name"]} 时出错:', str(error))
                errors.append({
                    'filter': filter_config['name'],
                    'error': str(error)
                })
        
        # === 第五步：验证和保留额外节点 ===
        print('=== 验证额外节点 ===')
        valid_extra_nodes = []
        for node in extra_nodes:
            tag = node.get('tag', '')
            if tag.startswith('extra.'):
                valid_extra_nodes.append(node)
                print(f'保留有效额外节点: {tag}')
            else:
                print(f'跳过无效额外节点: {tag}')
        
        # === 第六步：收集所有三类节点的tag ===
        all_managed_node_tags = []
        all_managed_node_tags.extend([node['tag'] for node in valid_extra_nodes])
        all_managed_node_tags.extend([node['tag'] for node in new_filter_nodes]) 
        all_managed_node_tags.extend([node['tag'] for node in new_subscription_nodes])

        print(f'管理的节点tags: {all_managed_node_tags}')
        
        # === 第七步：更新默认节点的outbounds ===
        print('=== 更新默认节点outbounds ===')
        for node in default_nodes:
            if 'outbounds' in node and isinstance(node['outbounds'], list):
                # 添加所有三类节点到默认节点的outbounds中
                original_count = len(node['outbounds'])
                node['outbounds'].extend(all_managed_node_tags)
                print(f'更新默认节点 {node.get("tag")} 的outbounds: 从{original_count}个增加到{len(node["outbounds"])}个')
        
        # === 第八步：重新组装主配置的outbounds ===
        print('=== 重新组装outbounds ===')
        main_config['outbounds'] = []
        main_config['outbounds'].extend(default_nodes)
        main_config['outbounds'].extend(valid_extra_nodes)
        main_config['outbounds'].extend(new_filter_nodes)
        main_config['outbounds'].extend(new_subscription_nodes)
        
        
        print(f'最终outbounds组成: 默认:{len(default_nodes)}, 订阅:{len(new_subscription_nodes)}, 过滤器:{len(new_filter_nodes)}, 额外:{len(valid_extra_nodes)}')
        
        # === 第九步：保存配置 ===
        save_config(main_config, preserve_outbounds=False)
        save_subscribe_config(config)
        print('配置文件保存成功')
        
        return {
            'success': True,
            'totalAdded': total_added,
            'errors': errors if errors else None
        }
        
    except Exception as error:
        print('处理订阅时出错:', str(error))
        return {
            'success': False,
            'error': str(error)
        }

def validate_extra_outbounds(outbounds):
    """验证额外出站配置"""
    if not isinstance(outbounds, list):
        try:
            # 尝试解析 JSON 字符串
            outbounds = json.loads(outbounds)
        except:
            raise ValueError('额外出站必须是数组')
    
    if not isinstance(outbounds, list):
        raise ValueError('额外出站必须是数组')
    
    for outbound in outbounds:
        if not isinstance(outbound, dict):
            raise ValueError('额外出站配置项必须是对象')
        if 'type' not in outbound:
            raise ValueError('额外出站配置项必须包含 type 字段')
        if 'tag' not in outbound:
            raise ValueError('额外出站配置项必须包含 tag 字段')
    
    return outbounds

@app.route('/api/config', methods=['GET'])
@require_auth
def get_config():
    """获取配置"""
    try:
        main_config = read_config()
        subscribe_config = read_subscribe_config()
        
        # 返回主配置给配置文件页面，同时也保持兼容性
        response = {
            'success': True,
            'config': main_config,
            'main': main_config,
            'subscribe': {
                'subscriptions': subscribe_config.get('subscriptions', []),
                'filters': subscribe_config.get('filters', []),
                'ex_outbounds': subscribe_config.get('ex_outbounds', [])
            }
        }
        
        return jsonify(response)
    except Exception as error:
        return jsonify({'success': False, 'error': str(error)}), 500

@app.route('/api/subscription', methods=['POST'])
@require_auth
def save_subscription():
    """保存订阅"""
    try:
        print('收到保存订阅请求:', request.json)
        if not request.json:
            return jsonify({'error': '请求体不能为空'}), 400
            
        config = read_subscribe_config()
        data = request.json
        name = data.get('name')
        url = data.get('url')
        
        if not name or not url:
            return jsonify({'error': '名称和URL不能为空'}), 400
        
        # 检查是否已存在同名订阅
        existing_index = next((i for i, s in enumerate(config['subscriptions']) if s['name'] == name), -1)
        if existing_index != -1:
            # 更新现有订阅
            config['subscriptions'][existing_index].update({
                'url': url,
                'lastUpdate': datetime.now().isoformat()
            })
        else:
            # 添加新订阅
            config['subscriptions'].append({
                'name': name,
                'url': url,
                'lastUpdate': datetime.now().isoformat()
            })
        
        # 保存配置
        try:
            save_subscribe_config(config)
            print('订阅配置保存成功')
        except Exception as e:
            print(f'保存配置文件失败: {str(e)}')
            return jsonify({'error': f'保存配置文件失败: {str(e)}'}), 500
        
        # 处理订阅
        print('开始处理订阅...')
        result = process_subscriptions()
        print('订阅处理完成，结果:', result)
        
        return jsonify({'success': True, 'result': result})
    except Exception as error:
        print('保存订阅失败:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/filter', methods=['POST'])
def save_filter():
    """保存过滤器"""
    try:
        print('收到保存过滤器请求')
        config = read_subscribe_config()
        data = request.json
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'error': '缺少必填字段: name'}), 400
        
        # 检查是否已存在同名过滤器
        existing_filter = next((f for f in config['filters'] if f['name'] == data['name']), None)
        if existing_filter:
            # 更新现有过滤器
            existing_filter.update(data)
        else:
            # 添加新过滤器
            config['filters'].append(data)
        
        # 保存配置
        save_subscribe_config(config)
        
        # 处理订阅以更新配置
        result = process_subscriptions()
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        print('过滤器保存成功')
        return jsonify({'success': True})
        
    except Exception as error:
        print('保存过滤器失败:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/extra-outbounds', methods=['POST'])
def save_extra_outbounds():
    """保存额外出站"""
    try:
        print('收到保存额外出站请求')
        config = read_subscribe_config()
        main_config = read_config()
        data = request.json
        
        if not isinstance(data, list):
            return jsonify({'error': '额外出站必须是数组'}), 400
        
        # === 验证额外节点的tag前缀 ===
        print('=== 验证额外节点tag前缀 ===')
        valid_extra_outbounds = []
        invalid_nodes = []
        
        for outbound in data:
            if isinstance(outbound, dict) and 'tag' in outbound:
                tag = outbound['tag']
                if tag.startswith('extra.'):
                    valid_extra_outbounds.append(outbound)
                    print(f'有效额外节点: {tag}')
                else:
                    # 自动添加前缀
                    outbound['tag'] = f"extra.{tag}"
                    valid_extra_outbounds.append(outbound)
                    print(f'自动添加前缀: {tag} -> {outbound["tag"]}')
            else:
                invalid_nodes.append(outbound)
                print(f'无效节点配置: {outbound}')
        
        if invalid_nodes:
            return jsonify({'error': f'发现无效节点配置: {invalid_nodes}'}), 400
        
        # 保存额外出站配置
        config['ex_outbounds'] = valid_extra_outbounds
        save_subscribe_config(config)
        
        # === 分类现有节点并处理额外节点 ===
        print('=== 分类现有节点并处理额外节点 ===')
        default_nodes = []
        subscription_nodes = []
        filter_nodes = []
        extra_nodes = []
        
        # 确保 main_config['outbounds'] 是一个列表
        if 'outbounds' not in main_config or not isinstance(main_config['outbounds'], list):
            print(f'警告: main_config["outbounds"] 不是有效的列表, 类型: {type(main_config.get("outbounds"))}')
            main_config['outbounds'] = []
        
        print(f'main_config["outbounds"]的类型: {type(main_config["outbounds"])}, 长度: {len(main_config["outbounds"])}')
        
        # 分类现有节点
        for outbound in main_config['outbounds']:
            tag = outbound.get('tag', '')
            if tag.startswith('filter.'):
                filter_nodes.append(outbound)
            elif tag.startswith('extra.'):
                # 跳过旧的额外节点，我们会用新的替换
                continue
            elif '.' in tag and not tag.startswith('extra.') and not tag.startswith('filter.'):
                subscription_nodes.append(outbound)
            else:
                default_nodes.append(outbound)
        
        # 添加新的额外节点
        extra_nodes = valid_extra_outbounds
        
        # === 更新默认节点的outbounds ===
        print('=== 更新默认节点的outbounds ===')
        all_managed_node_tags = []
        all_managed_node_tags.extend([node['tag'] for node in subscription_nodes])
        all_managed_node_tags.extend([node['tag'] for node in filter_nodes])
        all_managed_node_tags.extend([node['tag'] for node in extra_nodes])
        
        for node in default_nodes:
            if 'outbounds' in node and isinstance(node['outbounds'], list):
                # 清理旧的三类节点引用
                original_outbounds = node['outbounds'].copy()
                print(f'处理默认节点 {node.get("tag")}, 原始outbounds: {original_outbounds}')
                
                # 检查outbounds中元素的类型并过滤
                filtered_outbounds = []
                for out in node['outbounds']:
                    if not isinstance(out, str):
                        print(f'警告: 节点 {node.get("tag")} 的outbounds中发现非字符串元素: {out} (类型: {type(out)})')
                        continue
                    
                    # 过滤三类节点引用
                    if not (
                        out.startswith('filter.') or 
                        out.startswith('extra.') or 
                        ('.' in out and not out.startswith('filter.') and not out.startswith('extra.'))
                    ):
                        filtered_outbounds.append(out)
                
                node['outbounds'] = filtered_outbounds
                # 添加新的三类节点
                node['outbounds'].extend(all_managed_node_tags)
                print(f'更新默认节点 {node.get("tag")} 的outbounds: {original_outbounds} -> {node["outbounds"]}')
        
        # === 重新组装主配置的outbounds ===
        main_config['outbounds'] = []
        main_config['outbounds'].extend(default_nodes)
        main_config['outbounds'].extend(subscription_nodes)
        main_config['outbounds'].extend(filter_nodes)
        main_config['outbounds'].extend(extra_nodes)
        
        print(f'最终outbounds组成: 默认:{len(default_nodes)}, 订阅:{len(subscription_nodes)}, 过滤器:{len(filter_nodes)}, 额外:{len(extra_nodes)}')
        
        # 保存更新后的主配置
        save_config(main_config, preserve_outbounds=False)
        print('额外出站配置保存成功')
        
        return jsonify({'success': True})
    except Exception as error:
        print('保存额外出站失败:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新主配置"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': '无效的请求数据'})
        
        # 如果传入的数据直接是配置对象，就使用它
        # 这样配置文件页面可以直接传入编辑器的内容
        if isinstance(data, dict) and ('inbounds' in data or 'outbounds' in data or 'route' in data):
            config_data = data
        else:
            return jsonify({'success': False, 'error': '无效的配置数据格式'})
        
        # 保存配置
        save_config(config_data, preserve_outbounds=True)
        
        # 统一更新所有节点的 outbounds
        update_all_node_outbounds(config_data)
        
        return jsonify({'success': True, 'message': '配置保存成功'})
        
    except Exception as error:
        print('更新配置时出错:', str(error))
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/subscription/<name>', methods=['DELETE', 'OPTIONS'])
def delete_subscription(name):
    """删除订阅"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print(f'收到删除订阅请求: {name}')
        config = read_subscribe_config()
        main_config = read_config()
        
        # 查找并删除订阅
        config['subscriptions'] = [s for s in config['subscriptions'] if s['name'] != name]
        
        # 清理主配置中的相关节点
        if 'outbounds' in main_config:
            # 删除以订阅名称开头的节点
            main_config['outbounds'] = [
                outbound for outbound in main_config['outbounds']
                if not outbound.get('tag', '').startswith(f"{name}.")
            ]
            
            # 更新 Proxy 的 outbounds
            proxy_outbound = next((outbound for outbound in main_config['outbounds'] if outbound.get('tag') == 'Proxy'), None)
            if proxy_outbound and 'outbounds' in proxy_outbound:
                proxy_outbound['outbounds'] = [
                    outbound for outbound in proxy_outbound['outbounds']
                    if not outbound.startswith(f"{name}.")
                ]
        
        # 保存配置
        save_subscribe_config(config)
        save_config(main_config)
        
        # 处理订阅以更新配置
        result = process_subscriptions()
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        print('订阅删除成功')
        return jsonify({'success': True})
        
    except Exception as error:
        print('删除订阅失败:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/filter/<name>', methods=['DELETE', 'OPTIONS'])
def delete_filter(name):
    """删除过滤器"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print(f'收到删除过滤器请求: {name}')
        config = read_subscribe_config()
        
        # 查找并删除过滤器
        config['filters'] = [f for f in config['filters'] if f['name'] != name]
        
        # 保存配置
        save_subscribe_config(config)
        
        # 处理订阅以更新配置
        result = process_subscriptions()
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        print('过滤器删除成功')
        return jsonify({'success': True})
        
    except Exception as error:
        print('删除过滤器失败:', str(error))
        return jsonify({'error': str(error)}), 500

@app.route('/api/outbounds', methods=['GET', 'OPTIONS'])
@require_auth
def get_outbounds():
    """获取所有 outbounds"""
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        print('开始获取 outbounds...')
        config = read_config()
        outbounds = []
        
        # 遍历所有 outbounds，收集 tag
        for outbound in config.get('outbounds', []):
            print(f'处理 outbound: {outbound}')
            if 'tag' in outbound:
                outbounds.append(outbound['tag'])
                print(f'添加 outbound tag: {outbound["tag"]}')
        
        print(f'收集到的 outbounds: {outbounds}')
        
        response = jsonify({
            'success': True,
            'outbounds': outbounds
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as error:
        print('获取 outbounds 失败:', str(error))
        response = jsonify({
            'success': False,
            'error': str(error)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

@app.route('/api/rules', methods=['GET', 'POST', 'OPTIONS'])
@require_auth
def handle_rules():
    """处理规则配置"""
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    if request.method == 'GET':
        try:
            print('开始获取规则...')
            config = read_config()
            rules = []
            
            # 从 route.rules 中获取规则
            if 'route' in config and 'rules' in config['route']:
                print(f'找到 route.rules: {config["route"]["rules"]}')
                for rule in config['route']['rules']:
                    print(f'处理规则: {rule}')
                    # 确保规则是字典类型
                    if isinstance(rule, dict):
                        # 规范化规则数据结构
                        normalized_rule = {}
                        
                        # 处理 action 字段
                        if 'action' in rule:
                            normalized_rule['action'] = rule['action']
                        
                        # 处理其他字段
                        for key, value in rule.items():
                            if key != 'action':
                                normalized_rule[key] = value
                        
                        rules.append(normalized_rule)
                        print(f'规范化后的规则: {normalized_rule}')
                    else:
                        print(f'跳过非字典类型的规则: {rule}')
            
            print(f'收集到的规则: {rules}')
            
            response = jsonify({
                'success': True,
                'rules': rules
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('获取规则失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
            
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print('接收到的规则数据:', data)
            
            if 'rules' not in data:
                raise ValueError('缺少 rules 字段')
                
            # 更新配置
            config = read_config()
            if 'route' not in config:
                config['route'] = {}
            config['route']['rules'] = data['rules']
            
            # 保存配置
            save_config(config, preserve_outbounds=True)
            
            # 统一更新所有节点的 outbounds
            update_all_node_outbounds(config)
            
            response = jsonify({
                'success': True
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('保存规则失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500

@app.route('/api/rule-sets', methods=['GET', 'POST', 'OPTIONS'])
@require_auth
def handle_rule_sets():
    """处理规则集配置"""
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    if request.method == 'GET':
        try:
            print('开始获取规则集...')
            config = read_config()
            rule_sets = []
            
            # 从 route.rule_set 中获取规则集
            if 'route' in config and 'rule_set' in config['route']:
                print(f'找到 route.rule_set: {config["route"]["rule_set"]}')
                rule_sets = config['route']['rule_set']
            
            print(f'收集到的规则集: {rule_sets}')
            
            response = jsonify({
                'success': True,
                'rule_sets': rule_sets
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('获取规则集失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
            
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print('接收到的规则集数据:', data)
            
            if 'rule_sets' not in data:
                raise ValueError('缺少 rule_sets 字段')
                
            # 更新配置
            config = read_config()
            if 'route' not in config:
                config['route'] = {}
            config['route']['rule_set'] = data['rule_sets']
            
            # 保存配置
            save_config(config, preserve_outbounds=True)
            
            # 统一更新所有节点的 outbounds
            update_all_node_outbounds(config)
            
            response = jsonify({
                'success': True
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('保存规则集失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500

@app.route('/api/inbounds', methods=['GET', 'POST', 'OPTIONS'])
def handle_inbounds():
    """处理入站配置"""
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    if request.method == 'GET':
        try:
            print('开始获取入站配置...')
            config = read_config()
            inbounds = []
            
            # 从配置中获取入站配置
            if 'inbounds' in config:
                print(f'找到 inbounds: {config["inbounds"]}')
                inbounds = config['inbounds']
            
            print(f'收集到的入站配置: {inbounds}')
            
            response = jsonify({
                'success': True,
                'inbounds': inbounds
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('获取入站配置失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
            
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print('接收到的入站配置数据:', data)
            
            if 'inbounds' not in data:
                raise ValueError('缺少 inbounds 字段')
                
            # 更新配置
            config = read_config()
            config['inbounds'] = data['inbounds']
            
            # 保存配置
            save_config(config, preserve_outbounds=True)
            
            # 统一更新所有节点的 outbounds
            update_all_node_outbounds(config)
            
            response = jsonify({
                'success': True
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as error:
            print('保存入站配置失败:', str(error))
            response = jsonify({
                'success': False,
                'error': str(error)
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500

@app.route('/api/dns', methods=['GET', 'POST', 'OPTIONS'])
def handle_dns():
    """处理 DNS 配置的获取和保存"""
    try:
        if request.method == 'OPTIONS':
            return make_response('', 204)
            
        config = read_config()
        
        if request.method == 'GET':
            # 返回 DNS 配置
            return jsonify({
                'success': True,
                'dns': config.get('dns', {})
            })
            
        elif request.method == 'POST':
            # 获取请求数据
            data = request.get_json()
            if not data or 'dns' not in data:
                return jsonify({
                    'success': False,
                    'error': '无效的请求数据'
                }), 400
                
            # 更新 DNS 配置
            config['dns'] = data['dns']
            
            # 保存配置
            save_config(config, preserve_outbounds=True)
            
            # 统一更新所有节点的 outbounds
            update_all_node_outbounds(config)
            
            return jsonify({
                'success': True
            })
            
    except Exception as e:
        print(f'处理 DNS 配置时出错: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experimental', methods=['POST', 'OPTIONS'])
def handle_experimental():
    """处理实验性功能配置的保存"""
    try:
        if request.method == 'OPTIONS':
            return make_response('', 204)
            
        # 获取请求数据
        data = request.get_json()
        if not data or 'experimental' not in data:
            return jsonify({
                'success': False,
                'error': '无效的请求数据'
            }), 400
            
        # 读取当前配置
        config = read_config()
        
        # 更新实验性功能配置
        config['experimental'] = data['experimental']
        
        # 保存配置
        save_config(config, preserve_outbounds=True)
        
        # 统一更新所有节点的 outbounds
        update_all_node_outbounds(config)
        
        return jsonify({
            'success': True
        })
            
    except Exception as e:
        print(f'处理实验性功能配置时出错: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/log', methods=['POST', 'OPTIONS'])
def handle_log():
    """处理日志配置的保存"""
    try:
        if request.method == 'OPTIONS':
            return make_response('', 204)
            
        # 获取请求数据
        data = request.get_json()
        if not data or 'log' not in data:
            return jsonify({
                'success': False,
                'error': '无效的请求数据'
            }), 400
            
        # 读取当前配置
        config = read_config()
        
        # 更新日志配置
        config['log'] = data['log']
        
        # 保存配置
        save_config(config, preserve_outbounds=True)
        
        # 统一更新所有节点的 outbounds
        update_all_node_outbounds(config)
        
        return jsonify({
            'success': True
        })
            
    except Exception as e:
        print(f'处理日志配置时出错: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def read_tasks_config():
    """读取任务配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, TASKS_CONFIG_FILE)
        
        if not os.path.exists(config_path):
            # 如果配置文件不存在，创建默认配置
            default_config = {
                "subscription": {
                    "enabled": True,
                    "schedule": {
                        "type": "daily",
                        "time": "03:00",
                        "dayOfWeek": "1",
                        "minute": 0,
                        "cron": "0 3 * * *"
                    }
                },
                "singbox": {
                    "enabled": True,
                    "schedule": {
                        "type": "weekly",
                        "time": "04:00",
                        "dayOfWeek": "1",
                        "minute": 0,
                        "cron": "0 4 * * 1"
                    }
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'读取任务配置文件出错: {str(e)}')
        return None

def save_tasks_config(config):
    """保存任务配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, TASKS_CONFIG_FILE)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f'保存任务配置文件失败: {str(e)}')
        raise

def update_task_schedule(task_id, task_config):
    """更新任务调度"""
    try:
        # 移除现有的任务
        scheduler.remove_job(task_id)
    except:
        pass
    
    if not task_config['enabled']:
        return
    
    # 根据任务类型设置执行函数
    if task_id == 'subscription':
        func = update_subscriptions
    else:  # singbox
        func = update_singbox
    
    # 根据调度类型设置 cron 表达式
    schedule = task_config['schedule']
    if schedule['type'] == 'custom':
        cron = schedule['cron']
    elif schedule['type'] == 'hourly':
        cron = f"{schedule['minute']} * * * *"
    elif schedule['type'] == 'daily':
        time_parts = schedule['time'].split(':')
        cron = f"{time_parts[1]} {time_parts[0]} * * *"
    else:  # weekly
        time_parts = schedule['time'].split(':')
        cron = f"{time_parts[1]} {time_parts[0]} * * {schedule['dayOfWeek']}"
    
    # 添加新的任务
    scheduler.add_job(
        func,
        CronTrigger.from_crontab(cron),
        id=task_id,
        replace_existing=True
    )

def update_subscriptions():
    """更新订阅"""
    try:
        print('开始更新订阅...')
        process_subscriptions()
        print('订阅更新完成')
    except Exception as e:
        print(f'更新订阅失败: {str(e)}')

def update_singbox():
    """更新 Singbox 内核"""
    try:
        print('开始更新 Singbox 内核...')
        
        # 获取系统信息
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # 调整架构名称以匹配 sing-box 发布格式
        if machine == 'amd64' or machine == 'x86_64':
            machine = 'amd64'
        elif machine == 'x86' or machine == 'i386':
            machine = '386'
        elif machine == 'aarch64':
            machine = 'arm64'
        elif machine.startswith('arm'):
            machine = 'arm'
            
        # 获取最新版本信息
        print('获取最新版本信息...')
        latest_release_url = 'https://api.github.com/repos/SagerNet/sing-box/releases/latest'
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        response = requests.get(latest_release_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f'获取版本信息失败，状态码: {response.status_code}')
            
        release_data = response.json()
        version = release_data['tag_name'].lstrip('v')  # 移除版本号前的 'v' 前缀
        print(f'最新版本: {version}')
        
        # 构建目标文件名
        if system == 'windows':
            target_filename = f"sing-box-{version}-windows-{machine}.zip"
        elif system == 'darwin':
            target_filename = f"sing-box-{version}-darwin-{machine}.tar.gz"
        else:  # linux
            target_filename = f"sing-box-{version}-linux-{machine}.tar.gz"
            
        print(f'目标文件名: {target_filename}')
            
        # 从 assets 中查找对应的下载链接
        download_url = None
        for asset in release_data['assets']:
            if asset['name'] == target_filename:
                download_url = asset['browser_download_url']
                break
                
        if not download_url:
            raise Exception(f'未找到对应的下载文件: {target_filename}')
            
        print(f'下载地址: {download_url}')
        
        # 创建临时目录
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 下载文件
        print('开始下载文件...')
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            raise Exception(f'下载失败，状态码: {response.status_code}')
            
        file_path = os.path.join(temp_dir, target_filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print('文件下载完成')
        
        # 解压文件
        print('开始解压文件...')
        extract_dir = os.path.join(temp_dir, 'extract')
        os.makedirs(extract_dir, exist_ok=True)
        
        if system == 'windows':
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Windows 版本会解压到带版本号的子目录中
            versioned_dir = os.path.join(extract_dir, f"sing-box-{version}-windows-{machine}")
            if os.path.exists(versioned_dir):
                extract_dir = versioned_dir
        else:
            import tarfile
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
            # Linux/Darwin 版本也会解压到带版本号的子目录中
            versioned_dir = os.path.join(extract_dir, f"sing-box-{version}-{system}-{machine}")
            if os.path.exists(versioned_dir):
                extract_dir = versioned_dir
        print('文件解压完成')
        
        # 获取当前 sing-box 可执行文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if system == 'windows':
            singbox_path = os.path.join(current_dir, 'sing-box.exe')
            new_singbox_path = os.path.join(extract_dir, 'sing-box.exe')
        else:
            singbox_path = os.path.join(current_dir, 'sing-box')
            new_singbox_path = os.path.join(extract_dir, 'sing-box')
            
        # 检查新文件是否存在
        if not os.path.exists(new_singbox_path):
            raise Exception(f'找不到解压后的文件: {new_singbox_path}')
        
        # 备份当前文件
        if os.path.exists(singbox_path):
            backup_path = f"{singbox_path}.bak"
            print(f'备份当前文件到: {backup_path}')
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(singbox_path, backup_path)
        
        # 替换文件
        print('替换文件...')
        os.rename(new_singbox_path, singbox_path)
        
        # 设置执行权限（非 Windows 系统）
        if system != 'windows':
            os.chmod(singbox_path, 0o755)
        
        # 清理临时文件
        print('清理临时文件...')
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f'Singbox 内核更新完成，版本: {version}')
        
    except Exception as e:
        print(f'更新 Singbox 内核失败: {str(e)}')
        # 如果更新失败，尝试恢复备份
        try:
            if os.path.exists(f"{singbox_path}.bak"):
                os.rename(f"{singbox_path}.bak", singbox_path)
                print('已恢复备份文件')
        except:
            pass
        raise

@app.route('/api/tasks', methods=['GET', 'POST', 'OPTIONS'])
def handle_tasks():
    """处理任务配置的获取和保存"""
    try:
        if request.method == 'OPTIONS':
            return make_response('', 204)
            
        if request.method == 'GET':
            # 返回任务配置
            tasks = read_tasks_config()
            return jsonify({
                'success': True,
                'tasks': tasks
            })
            
        elif request.method == 'POST':
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '无效的请求数据'
                }), 400
                
            # 保存配置
            save_tasks_config(data)
            
            # 更新任务调度
            update_task_schedule('subscription', data['subscription'])
            update_task_schedule('singbox', data['singbox'])
            
            return jsonify({
                'success': True
            })
            
    except Exception as e:
        print(f'处理任务配置时出错: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/run/<task_type>', methods=['POST', 'OPTIONS'])
def run_task(task_type):
    """立即运行指定任务"""
    try:
        if request.method == 'OPTIONS':
            return make_response('', 204)
            
        if task_type not in ['subscription', 'singbox']:
            return jsonify({
                'success': False,
                'error': '无效的任务类型'
            }), 400
            
        # 获取任务配置
        tasks_config = read_tasks_config()
        if not tasks_config:
            return jsonify({
                'success': False,
                'error': '获取任务配置失败'
            }), 500
            
        task_config = tasks_config[task_type]
        
        # 执行任务
        if task_type == 'subscription':
            update_subscriptions()
        else:  # singbox
            update_singbox()
            
        return jsonify({
            'success': True
        })
            
    except Exception as e:
        print(f'执行任务时出错: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def init_config_file():
    """初始化配置文件"""
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, CONFIG_FILE)
        base_config_path = os.path.join(current_dir, MAIN_CONFIG_FILE)
        
        # 如果配置文件不存在且基础配置文件存在，则复制一份
        if not os.path.exists(config_path) and os.path.exists(base_config_path):
            print(f'配置文件 {CONFIG_FILE} 不存在，正在从 {MAIN_CONFIG_FILE} 创建...')
            shutil.copy2(base_config_path, config_path)
            print(f'配置文件已创建: {config_path}')
        elif not os.path.exists(base_config_path):
            print(f'警告: 基础配置文件 {MAIN_CONFIG_FILE} 不存在')
            
    except Exception as e:
        print(f'初始化配置文件失败: {str(e)}')

# 应用启动时的初始化函数
def init_app():
    """初始化应用"""
    # 初始化配置文件
    init_config_file()
    
    # 初始化任务调度
    try:
        print('正在初始化任务调度...')
        tasks_config = read_tasks_config()
        if tasks_config:
            update_task_schedule('subscription', tasks_config['subscription'])
            update_task_schedule('singbox', tasks_config['singbox'])
            print('任务调度初始化成功')
    except Exception as e:
        print(f'初始化任务调度失败: {str(e)}')

def check_singbox_exists():
    """检查singbox可执行文件是否存在"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        singbox_path = os.path.join(current_dir, 'sing-box')
        exists = os.path.exists(singbox_path) and os.access(singbox_path, os.X_OK)
        if exists:
            print(f'找到 sing-box 可执行文件: {singbox_path}')
        else:
            print(f'未找到 sing-box 可执行文件: {singbox_path}')
        return exists
    except Exception as e:
        print(f'检查singbox文件失败: {str(e)}')
        return False

def get_singbox_status():
    """获取 sing-box 核心状态 (通过 PID 文件)"""
    if not os.path.exists(PID_FILE):
        return 'stopped', None
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
    except (IOError, ValueError):
        try:
            os.remove(PID_FILE)
        except OSError:
            pass
        return 'stopped', None

    if psutil.pid_exists(pid):
        try:
            p = psutil.Process(pid)
            if 'sing-box' in p.name():
                return 'running', pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    print(f"检测到过期的 PID 文件 (PID: {pid})，正在清理...")
    try:
        os.remove(PID_FILE)
    except OSError:
        pass
    return 'stopped', None

def start_singbox():
    """启动 sing-box 核心并记录 PID"""
    status, pid = get_singbox_status()
    if status == 'running':
        return f'Singbox is already running with PID: {pid}'

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        singbox_path = os.path.join(current_dir, 'sing-box')
        config_path = os.path.join(current_dir, CONFIG_FILE)

        if not os.path.exists(singbox_path) or not os.access(singbox_path, os.X_OK):
            return f"Error: 'sing-box' not found or not executable at {singbox_path}"
        
        if not os.path.exists(config_path):
            return f"Error: '{CONFIG_FILE}' not found at {config_path}"

        print(f"Starting sing-box with command: {singbox_path} run -c {config_path}")
        
        process = subprocess.Popen([singbox_path, 'run', '-c', config_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   cwd=current_dir)
        
        pid = process.pid
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))

        def monitor_output(pipe):
            with pipe:
                for line in iter(pipe.readline, ''):
                    line = line.strip()
                    if line:
                        print(f"[sing-box] {line}")

        threading.Thread(target=monitor_output, args=[process.stdout], daemon=True).start()
        threading.Thread(target=monitor_output, args=[process.stderr], daemon=True).start()

        time.sleep(2)
        if process.poll() is not None:
            print(f"Singbox process terminated unexpectedly with code {process.returncode}.")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            return f"Singbox process terminated unexpectedly."

        print(f"Singbox started successfully with PID: {pid}")
        return 'Singbox started successfully'
    except Exception as e:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return f"Failed to start Singbox: {str(e)}"

def stop_singbox():
    """停止 sing-box 核心 (通过 PID 文件)"""
    status, pid = get_singbox_status()
    if status == 'stopped':
        return 'Singbox is not running'

    try:
        print(f"Stopping sing-box process with PID: {pid}")
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        parent.wait(timeout=5)
    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} not found, might have been stopped already.")
    except Exception as e:
        return f"Failed to stop Singbox: {str(e)}"
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    
    return 'Singbox stopped successfully'

@app.route('/api/singbox/status', methods=['GET', 'OPTIONS'])
@require_auth
def get_status():
    """获取 sing-box 核心状态"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    status, pid = get_singbox_status()
    return jsonify({'status': status, 'pid': pid})

@app.route('/api/singbox/start', methods=['POST', 'OPTIONS'])
@require_auth
def start_service():
    """启动 sing-box 服务"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # 确保配置已合并
    print("Processing subscriptions before starting...")
    process_subscriptions()
    
    result = start_singbox()
    status, pid = get_singbox_status()
    
    return jsonify({'message': result, 'status': status, 'pid': pid})

@app.route('/api/singbox/stop', methods=['POST', 'OPTIONS'])
@require_auth
def stop_service():
    """停止 sing-box 服务"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    result = stop_singbox()
    status, pid = get_singbox_status()
    
    return jsonify({'message': result, 'status': status, 'pid': pid})

@app.route('/api/singbox/restart', methods=['POST', 'OPTIONS'])
@require_auth
def restart_service():
    """重启 sing-box 服务"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        # 先停止服务
        print("正在停止 sing-box 服务...")
        stop_result = stop_singbox()
        print(f"停止结果: {stop_result}")
        
        # 等待一小段时间确保服务完全停止
        import time
        time.sleep(2)
        
        # 确保配置已合并
        print("Processing subscriptions before restarting...")
        process_subscriptions()
        
        # 重新启动服务
        print("正在启动 sing-box 服务...")
        start_result = start_singbox()
        print(f"启动结果: {start_result}")
        
        # 获取最终状态
        status, pid = get_singbox_status()
        
        if status == 'running':
            message = "sing-box 服务重启成功"
        else:
            message = f"重启过程完成，但服务状态异常: {start_result}"
        
        return jsonify({'message': message, 'status': status, 'pid': pid})
        
    except Exception as e:
        print(f"重启服务时出错: {str(e)}")
        status, pid = get_singbox_status()
        return jsonify({
            'message': f'重启服务失败: {str(e)}', 
            'status': status, 
            'pid': pid
        }), 500

@app.route('/api/config/reset', methods=['POST', 'OPTIONS'])
def reset_main_config():
    """将当前配置重置为基础配置"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        base_config_path = os.path.join(current_dir, MAIN_CONFIG_FILE)
        main_config_path = os.path.join(current_dir, CONFIG_FILE)

        if not os.path.exists(base_config_path):
            return jsonify({'success': False, 'error': '基础配置文件不存在'}), 404

        # 使用 shutil.copy 来覆盖文件
        shutil.copy(base_config_path, main_config_path)
        
        return jsonify({'success': True, 'message': '当前配置已成功重置为基础配置'})

    except Exception as e:
        print(f'重置配置文件失败: {str(e)}')
        return jsonify({'success': False, 'error': f'重置配置文件失败: {str(e)}'}), 500

def update_all_node_outbounds(main_config):
    """统一更新所有默认节点的outbounds，添加订阅节点、过滤器节点和额外节点"""
    try:
        print('=== 开始更新默认节点的outbounds ===')
        
        # 读取订阅配置获取额外出站
        subscribe_config = read_subscribe_config()
        subscription_names = [sub['name'] for sub in subscribe_config.get('subscriptions', [])]
        
        # === 分类节点 ===
        default_nodes = []
        subscription_tags = []
        filter_tags = []
        extra_tags = []
        
        for outbound in main_config['outbounds']:
            tag = outbound.get('tag', '')
            if tag.startswith('filter.'):
                filter_tags.append(tag)
            elif tag.startswith('extra.'):
                extra_tags.append(tag)
            elif any(tag.startswith(f"{name}.") for name in subscription_names):
                subscription_tags.append(tag)
            else:
                # 这是默认节点
                if 'outbounds' in outbound and isinstance(outbound['outbounds'], list):
                    default_nodes.append(outbound)
        
        # 收集所有三类节点的tags
        all_managed_tags = subscription_tags + filter_tags + extra_tags
        
        print(f'订阅节点: {subscription_tags}')
        print(f'过滤器节点: {filter_tags}')
        print(f'额外节点: {extra_tags}')
        print(f'默认节点数量: {len(default_nodes)}')
        
        # === 更新默认节点的outbounds ===
        for node in default_nodes:
            original_outbounds = node['outbounds'].copy()
            
            # 清理旧的三类节点引用
            node['outbounds'] = [
                out for out in node['outbounds'] 
                if not (
                    out.startswith('filter.') or 
                    out.startswith('extra.') or 
                    any(out.startswith(f"{name}.") for name in subscription_names)
                )
            ]
            
            # 添加新的三类节点
            node['outbounds'].extend(all_managed_tags)
            
            print(f'更新默认节点 {node.get("tag")} 的outbounds: {len(original_outbounds)} -> {len(node["outbounds"])}')
        
        return True
    except Exception as e:
        print(f'更新节点outbounds失败: {str(e)}')
        return False

@app.route('/api/base-config', methods=['GET', 'POST', 'OPTIONS'])
def handle_base_config():
    """处理基础配置文件 base_config.json"""
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_config_path = os.path.join(current_dir, 'base_config.json')
        
        if request.method == 'GET':
            # 读取基础配置
            if not os.path.exists(base_config_path):
                response = jsonify({
                    'success': False,
                    'error': '基础配置文件不存在'
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response, 404
            
            with open(base_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            response = jsonify({
                'success': True,
                'config': config
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        elif request.method == 'POST':
            # 保存基础配置
            data = request.get_json()
            if not data or 'config' not in data:
                response = jsonify({
                    'success': False,
                    'error': '无效的请求数据'
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response, 400
            
            # 验证JSON格式
            config = data['config']
            if not isinstance(config, dict):
                response = jsonify({
                    'success': False,
                    'error': '配置必须是有效的JSON对象'
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response, 400
            
            # 保存到文件
            with open(base_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f'基础配置文件已保存: {base_config_path}')
            
            response = jsonify({
                'success': True,
                'message': '基础配置保存成功'
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {str(e)}')
        response = jsonify({
            'success': False,
            'error': f'JSON格式错误: {str(e)}'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400
    except Exception as e:
        print(f'处理基础配置时出错: {str(e)}')
        response = jsonify({
            'success': False,
            'error': str(e)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

def _build_cors_preflight_response():
    """构建CORS预检请求的响应"""
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

# 静态文件服务和前端路由处理 (放在所有API路由之后)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    统一处理前端静态文件和路由
    - 如果请求的路径对应一个存在的静态文件，则返回该文件
    - 否则，返回 index.html，让前端Vue Router处理路由
    """
    # 检查请求的路径是否是 API 调用，如果是则不处理
    if path.startswith('api/'):
        return jsonify(error='API not found'), 404

    # 尝试在 static 目录中查找文件
    file_path = os.path.join(static_dir, path)

    # 如果路径指向一个真实存在的文件，则直接返回
    if path and os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(static_dir, path)
    
    # 对于其他所有路径（如 /outbound, /dns 等），返回前端入口 index.html
    index_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    
    return "Frontend not built. Please run 'npm run build' in singbox-web directory.", 404

def load_download_password():
    """从配置文件加载下载密码"""
    global download_password
    try:
        if os.path.exists(DOWNLOAD_CONFIG_FILE):
            with open(DOWNLOAD_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                download_password = config.get('password', '')
    except Exception as e:
        print(f"加载下载密码失败: {str(e)}")
        download_password = ''

def save_download_password(password):
    """保存下载密码到配置文件"""
    try:
        with open(DOWNLOAD_CONFIG_FILE, 'w') as f:
            json.dump({'password': password}, f, indent=4)
        return True
    except Exception as e:
        print(f"保存下载密码失败: {str(e)}")
        return False

@app.route('/api/config/download-password', methods=['GET', 'POST'])
def handle_download_password():
    global download_password
    
    if request.method == 'GET':
        return jsonify({'password': download_password or ''})
    
    # POST 请求处理
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': '密码不能为空'}), 400
    
    password = data['password']
    if save_download_password(password):
        download_password = password
        return jsonify({'success': True})
    else:
        return jsonify({'error': '保存密码失败'}), 500

@app.route('/api/config/download/<password>')
@app.route('/api/config/download/<password>/<target>')
def download_config(password, target=None):
    if not download_password:
        return jsonify({'error': '未设置下载密码'}), 400
    
    if not password or password != download_password:
        return jsonify({'error': '密码错误'}), 401
    
    try:
        # 读取配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 如果target是android，处理tun节点的auto_route属性
        if target == 'android':
            if 'inbounds' in config:
                for inbound in config['inbounds']:
                    if isinstance(inbound, dict) and inbound.get('type') == 'tun':
                        # 删除auto_route属性
                        if 'auto_redirect' in inbound:
                            del inbound['auto_redirect']
            
            # 创建临时文件来保存修改后的配置
            temp_config_path = 'temp_config.json'
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            try:
                # 发送临时文件
                return send_file(temp_config_path,
                            as_attachment=True,
                            download_name='config.json',
                            mimetype='application/json')
            finally:
                # 删除临时文件
                try:
                    os.remove(temp_config_path)
                except:
                    pass
        
        # 如果没有target参数或target不是android，直接返回原始配置文件
        return send_file('config.json', 
                        as_attachment=True,
                        download_name='config.json',
                        mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 认证相关API
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def auth_login():
    """用户登录"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'}), 400
        
        auth_config = read_auth_config()
        if data['username'] == auth_config['username'] and data['password'] == auth_config['password']:
            return jsonify({'success': True, 'token': 'authenticated'})
        else:
            return jsonify({'success': False, 'error': '用户名或密码错误'}), 401
    
    except Exception as e:
        print(f'登录失败: {str(e)}')
        return jsonify({'success': False, 'error': '登录失败'}), 500

@app.route('/api/auth/check', methods=['GET', 'OPTIONS'])
def auth_check():
    """检查认证状态"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if token == 'authenticated':
            return jsonify({'authenticated': True})
    
    return jsonify({'authenticated': False})

@app.route('/api/auth/change-password', methods=['POST', 'OPTIONS'])
@require_auth
def change_password():
    """修改密码"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        if not data or 'oldPassword' not in data or 'newPassword' not in data:
            return jsonify({'success': False, 'error': '旧密码和新密码不能为空'}), 400
        
        auth_config = read_auth_config()
        if data['oldPassword'] != auth_config['password']:
            return jsonify({'success': False, 'error': '旧密码错误'}), 401
        
        # 更新密码
        auth_config['password'] = data['newPassword']
        if save_auth_config(auth_config):
            return jsonify({'success': True, 'message': '密码修改成功'})
        else:
            return jsonify({'success': False, 'error': '密码保存失败'}), 500
    
    except Exception as e:
        print(f'修改密码失败: {str(e)}')
        return jsonify({'success': False, 'error': '修改密码失败'}), 500

# 在应用启动时加载下载密码
load_download_password()

# 主程序入口
if __name__ == '__main__':
    # 在应用启动前初始化配置文件
    if not init_config_files():
        print("初始化配置文件失败，程序退出")
        exit(1)
        
    # 加载下载密码
    load_download_password()
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000)

# 确保 gunicorn 启动时不会重复初始化
# init_app() 