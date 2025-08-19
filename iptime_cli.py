#!/usr/bin/env python3
"""
ipTIME 포트포워드 관리 예제
"""
import sys
import json
from src.iptime_api import IptimeAPI
from src.port_forward import PortForwardManager


def cli_interface():
    """간단한 CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ipTIME 포트포워드 관리 도구')
    parser.add_argument('--host', required=True, help='공유기 IP 주소')
    parser.add_argument('--username', default='admin', help='관리자 계정')
    parser.add_argument('--password', required=True, help='관리자 비밀번호')
    
    subparsers = parser.add_subparsers(dest='command', help='명령어')
    
    # list 명령어
    subparsers.add_parser('list', help='포트포워드 규칙 목록 조회')
    
    # get 명령어
    get_parser = subparsers.add_parser('get', help='포트포워드 규칙 단건 조회')
    get_parser.add_argument('rule', help='규칙 ID (숫자) 또는 이름 (문자열)')
    
    # add 명령어
    add_parser = subparsers.add_parser('add', help='포트포워드 규칙 추가')
    add_parser.add_argument('--description', required=True, help='규칙 설명')
    add_parser.add_argument('--internal-ip', required=True, help='내부 IP 주소')
    add_parser.add_argument('--external-port', type=int, required=True, help='외부 포트')
    add_parser.add_argument('--internal-port', type=int, help='내부 포트 (기본값: 외부 포트와 동일)')
    add_parser.add_argument('--protocol', choices=['tcp', 'udp', 'both'], default='tcp', help='프로토콜')
    
    # update 명령어
    update_parser = subparsers.add_parser('update', help='포트포워드 규칙 수정')
    update_parser.add_argument('rule', help='규칙 ID (숫자) 또는 이름 (문자열)')
    update_parser.add_argument('--description', help='새 규칙 설명')
    update_parser.add_argument('--internal-ip', help='새 내부 IP 주소')
    update_parser.add_argument('--external-port', type=int, help='새 외부 포트')
    update_parser.add_argument('--internal-port', type=int, help='새 내부 포트')
    update_parser.add_argument('--protocol', choices=['tcp', 'udp', 'both'], help='새 프로토콜')
    
    # delete 명령어
    delete_parser = subparsers.add_parser('delete', help='포트포워드 규칙 삭제')
    delete_parser.add_argument('rule', help='규칙 ID (숫자) 또는 이름 (문자열)')
    
    args = parser.parse_args()
    
    # API 초기화
    api = IptimeAPI(args.host, args.username, args.password)
    
    if not api.login():
        print("로그인 실패!")
        return 1
    
    pf_manager = PortForwardManager(api)
    
    # 명령어 처리
    if args.command == 'list':
        rules = pf_manager.get_port_forward_rules()
        print(json.dumps(rules, indent=2, ensure_ascii=False))
        
    elif args.command == 'get':
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(args.rule)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = args.rule  # 문자열인 경우 이름으로 처리
        
        rule = pf_manager.get_port_forward_rule(rule_id_or_name)
        if rule:
            print(json.dumps(rule, indent=2, ensure_ascii=False))
        else:
            print(f"규칙을 찾을 수 없습니다: {args.rule}")
        
    elif args.command == 'add':
        success = pf_manager.add_port_forward_rule(
            description=args.description,
            internal_ip=args.internal_ip,
            external_port=args.external_port,
            internal_port=args.internal_port or args.external_port,
            protocol=args.protocol
        )
        print("성공" if success else "실패")
        
    elif args.command == 'update':
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(args.rule)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = args.rule  # 문자열인 경우 이름으로 처리
        
        success = pf_manager.update_port_forward_rule(
            rule_id_or_name=rule_id_or_name,
            description=args.description,
            internal_ip=args.internal_ip,
            external_port=args.external_port,
            internal_port=args.internal_port,
            protocol=args.protocol
        )
        print("성공" if success else "실패")
        
    elif args.command == 'delete':
        # ID 또는 이름 파싱
        try:
            rule_id_or_name = int(args.rule)  # 숫자인 경우 ID로 처리
        except ValueError:
            rule_id_or_name = args.rule  # 문자열인 경우 이름으로 처리
            
        success = pf_manager.delete_port_forward_rule(rule_id_or_name)
        print("성공" if success else "실패")
    
    api.logout()
    return 0


if __name__ == "__main__":
    sys.exit(cli_interface())