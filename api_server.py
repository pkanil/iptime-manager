#!/usr/bin/env python3
"""
ipTIME 포트포워드 REST API 서버
Flask를 사용한 HTTP API 제공
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.iptime_api import IptimeAPI
from src.port_forward import PortForwardManager
import os
from functools import wraps

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 환경 변수에서 설정 읽기
ROUTER_IP = os.environ.get('IPTIME_ROUTER_IP', 'http://192.168.0.1')
USERNAME = os.environ.get('IPTIME_USERNAME', 'admin')
PASSWORD = os.environ.get('IPTIME_PASSWORD', 'admin')

# API 인증 토큰 (선택사항)
API_TOKEN = os.environ.get('API_TOKEN', '')


def require_token(f):
    """API 토큰 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if API_TOKEN:
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid token'}), 401
            
            if token[7:] != API_TOKEN:
                return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def get_api_client():
    """API 클라이언트 생성 및 로그인"""
    api = IptimeAPI(ROUTER_IP, USERNAME, PASSWORD)
    if not api.login():
        raise Exception("Failed to login to router")
    return api


@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'healthy', 'router_ip': ROUTER_IP})


@app.route('/api/system/info', methods=['GET'])
@require_token
def get_system_info():
    """시스템 정보 조회"""
    try:
        api = get_api_client()
        info = api.get_system_info()
        api.logout()
        
        if info:
            return jsonify({'status': 'success', 'data': info})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get system info'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portforward', methods=['GET'])
@require_token
def list_port_forward_rules():
    """포트포워드 규칙 목록 조회"""
    try:
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        rules = pf_manager.get_port_forward_rules()
        api.logout()
        
        return jsonify({
            'status': 'success',
            'data': rules,
            'count': len(rules)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portforward', methods=['POST'])
@require_token
def add_port_forward_rule():
    """포트포워드 규칙 추가"""
    try:
        data = request.get_json()
        
        # 필수 파라미터 검증
        required = ['description', 'internal_ip', 'external_port']
        for field in required:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        
        success = pf_manager.add_port_forward_rule(
            description=data['description'],
            internal_ip=data['internal_ip'],
            external_port=data['external_port'],
            internal_port=data.get('internal_port'),
            protocol=data.get('protocol', 'tcp')
        )
        
        api.logout()
        
        if success:
            return jsonify({'status': 'success', 'message': 'Rule added successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to add rule'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portforward/<rule_identifier>', methods=['GET'])
@require_token
def get_port_forward_rule(rule_identifier):
    """포트포워드 규칙 단건 조회 (ID 또는 이름)"""
    try:
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(rule_identifier)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = rule_identifier  # 문자열인 경우 이름으로 처리
        
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        
        rule = pf_manager.get_port_forward_rule(rule_id_or_name)
        
        api.logout()
        
        if rule:
            return jsonify({'status': 'success', 'rule': rule})
        else:
            return jsonify({'status': 'error', 'message': 'Rule not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portforward/<rule_identifier>', methods=['PUT'])
@require_token
def update_port_forward_rule(rule_identifier):
    """포트포워드 규칙 수정 (ID 또는 이름)"""
    try:
        data = request.get_json()
        
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(rule_identifier)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = rule_identifier  # 문자열인 경우 이름으로 처리
        
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        
        success = pf_manager.update_port_forward_rule(
            rule_id_or_name=rule_id_or_name,
            description=data.get('description'),
            internal_ip=data.get('internal_ip'),
            external_port=data.get('external_port'),
            internal_port=data.get('internal_port'),
            protocol=data.get('protocol')
        )
        
        api.logout()
        
        if success:
            return jsonify({'status': 'success', 'message': 'Rule updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update rule'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portforward/<rule_identifier>', methods=['DELETE'])
@require_token
def delete_port_forward_rule(rule_identifier):
    """포트포워드 규칙 삭제 (ID 또는 이름)"""
    try:
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(rule_identifier)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = rule_identifier  # 문자열인 경우 이름으로 처리
        
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        
        success = pf_manager.delete_port_forward_rule(rule_id_or_name)
        
        api.logout()
        
        if success:
            return jsonify({'status': 'success', 'message': 'Rule deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete rule'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/portforward/batch', methods=['POST'])
@require_token
def batch_add_rules():
    """여러 포트포워드 규칙 일괄 추가"""
    try:
        data = request.get_json()
        
        if 'rules' not in data or not isinstance(data['rules'], list):
            return jsonify({
                'status': 'error',
                'message': 'Invalid request: rules array required'
            }), 400
        
        api = get_api_client()
        pf_manager = PortForwardManager(api)
        
        results = []
        for rule in data['rules']:
            success = pf_manager.add_port_forward_rule(
                description=rule.get('description', ''),
                internal_ip=rule.get('internal_ip'),
                external_port=rule.get('external_port'),
                internal_port=rule.get('internal_port'),
                protocol=rule.get('protocol', 'tcp')
            )
            results.append({
                'description': rule.get('description'),
                'success': success
            })
        
        api.logout()
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    # 개발 서버 실행
    port = int(os.environ.get('PORT', 6000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting ipTIME API Server on port {port}")
    print(f"Router IP: {ROUTER_IP}")
    print(f"API Token Required: {'Yes' if API_TOKEN else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
