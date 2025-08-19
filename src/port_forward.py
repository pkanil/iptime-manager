"""
ipTIME 포트포워드 관리 모듈
"""
import logging
import re
from typing import Dict, List, Optional

import requests

from .iptime_api import IptimeAPI

logger = logging.getLogger(__name__)


class PortForwardManager:
    """포트포워드 관리 클래스"""
    
    def __init__(self, api_client: IptimeAPI):
        """
        초기화
        
        Args:
            api_client: IptimeAPI 인스턴스
        """
        self.api = api_client
        
    def get_port_forward_rules(self) -> List[Dict]:
        """현재 설정된 포트포워드 규칙 조회"""
        try:
            # 포트포워드 페이지 요청
            response = self.api._make_request(
                "sess-bin/timepro.cgi",
                {"tmenu": "iframe", "smenu": "user_portforward", "mode": "user"}
            )
            
            if not response:
                return []
            
            # 세션 타임아웃 체크
            if 'login_session' in response and 'session_timeout' in response:
                logger.info("세션 타임아웃 감지, 재로그인 시도...")
                # 새로운 세션으로 재시도
                self.api.session = requests.Session()
                self.api.session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                })
                
                # 로그인 후 즉시 요청
                login_data = {
                    'init_status': '1',
                    'captcha_on': '0',
                    'captcha_file': '',
                    'username': self.api.username,
                    'passwd': self.api.password,
                    'default_passwd': '초기암호:admin(변경필요)',
                    'captcha_code': ''
                }
                
                # 단일 세션에서 로그인과 데이터 요청을 연속으로 수행
                login_resp = self.api.session.post(
                    f"{self.api.base_url}/sess-bin/login_handler.cgi",
                    data=login_data,
                    verify=False,
                    timeout=10
                )
                
                # 로그인 직후 바로 데이터 요청 (세션 유지)
                response = self.api.session.get(
                    f"{self.api.base_url}/sess-bin/timepro.cgi",
                    params={"tmenu": "iframe", "smenu": "user_portforward", "mode": "user"},
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    response = response.text
                else:
                    logger.error(f"포트포워드 페이지 접근 실패: {response.status_code}")
                    return []
            
            # 디버그: 응답 내용 일부 출력
            logger.debug(f"포트포워드 페이지 응답 (처음 1000자): {response[:1000]}")
                
            rules = []
            
            # HTML에서 포트포워드 규칙 파싱
            # JavaScript onclick 이벤트에서 파라미터 추출
            # onClickedPFRule('user','nas','0','192.168.0.12','tcp','28080','28080','8080','8080','','','','',false,'1','1', false)
            # Parameters: mode, name, selserver, internal_ip, protocol, ext_sport, ext_eport, int_sport, int_eport,
            #            tsport, teport, tfprotocol, tfrange, disabled, priority, wan, fixed
            rule_pattern = re.compile(
                r"onClickedPFRule\('user','([^']*?)','[^']*?','([^']*?)','([^']*?)','([^']*?)','([^']*?)','([^']*?)','([^']*?)'",
                re.DOTALL
            )
            
            matches = rule_pattern.findall(response)
            
            for i, match in enumerate(matches):
                # match = (name, internal_ip, protocol, ext_sport, ext_eport, int_sport, int_eport)
                name, internal_ip, protocol, ext_sport, ext_eport, int_sport, int_eport = match
                
                if internal_ip and ext_sport:  # 빈 규칙은 제외
                    rules.append({
                        'id': i + 1,  # Use index as ID since it's not in the params
                        'description': name,
                        'internal_ip': internal_ip,
                        'protocol': protocol,
                        'external_port': ext_sport,
                        'internal_port': int_sport
                    })
                    
            logger.info(f"포트포워드 규칙 {len(rules)}개 조회 완료")
            return rules
            
        except Exception as e:
            logger.error(f"포트포워드 규칙 조회 실패: {e}")
            return []
    
    def get_port_forward_rule(self, rule_id_or_name) -> Optional[Dict]:
        """
        포트포워드 규칙 단건 조회
        
        Args:
            rule_id_or_name: 규칙 ID (int) 또는 이름 (str)
            
        Returns:
            찾은 규칙 또는 None
        """
        rules = self.get_port_forward_rules()
        
        if isinstance(rule_id_or_name, str):
            # 이름으로 찾기
            for rule in rules:
                if rule['description'] == rule_id_or_name:
                    return rule
        else:
            # ID로 찾기
            for rule in rules:
                if rule['id'] == rule_id_or_name:
                    return rule
        
        return None
    
    def find_rule_by_name(self, name: str) -> Optional[Dict]:
        """
        이름으로 포트포워드 규칙 찾기
        
        Args:
            name: 규칙 이름(description)
            
        Returns:
            찾은 규칙 또는 None
        """
        return self.get_port_forward_rule(name)
    
    def get_rule_id_by_name(self, name: str) -> Optional[int]:
        """
        이름으로 규칙 ID 찾기
        
        Args:
            name: 규칙 이름(description)
            
        Returns:
            규칙 ID 또는 None
        """
        rule = self.find_rule_by_name(name)
        return rule['id'] if rule else None
            
    def add_port_forward_rule(
        self,
        description: str,
        internal_ip: str,
        external_port: int,
        internal_port: int = None,
        protocol: str = "tcp"
    ) -> bool:
        """
        포트포워드 규칙 추가
        
        Args:
            description: 규칙 설명
            internal_ip: 내부 IP 주소
            external_port: 외부 포트
            internal_port: 내부 포트 (없으면 external_port와 동일)
            protocol: 프로토콜 (tcp/udp/both)
            
        Returns:
            성공 여부
        """
        try:
            if internal_port is None:
                internal_port = external_port
                
            # 현재 규칙 조회하여 새 priority 결정
            current_rules = self.get_port_forward_rules()
            new_priority = len(current_rules) + 1
                    
            # 포트포워드 추가 데이터 준비
            # Similar to modify but with act=add
            data = {
                'tmenu': 'iframe',
                'smenu': 'user_portforward',
                'act': 'add',
                'view_mode': 'user',
                'mode': 'user',
                'name': description,
                'int_sport': str(internal_port),
                'int_eport': str(internal_port),
                'ext_sport': str(external_port),
                'ext_eport': str(external_port),
                'trigger_protocol': '',
                'trigger_sport': '',
                'trigger_eport': '',
                'forward_ports': '',
                'forward_protocol': '',
                'internal_ip': internal_ip,
                'protocol': protocol,
                'disabled': '0',
                'priority': str(new_priority)
            }
                
            # 설정 저장
            response = self.api._make_request(
                "sess-bin/timepro.cgi",
                data,
                method="POST"
            )
            
            if response:
                logger.info(f"포트포워드 규칙 추가 성공: {description}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"포트포워드 규칙 추가 실패: {e}")
            return False
            
    def delete_port_forward_rule(self, rule_id_or_name) -> bool:
        """
        포트포워드 규칙 삭제
        
        Args:
            rule_id_or_name: 삭제할 규칙 ID (int) 또는 이름 (str)
            
        Returns:
            성공 여부
        """
        try:
            # 현재 규칙 조회
            current_rules = self.get_port_forward_rules()
            
            # ID 또는 이름으로 규칙 찾기
            if isinstance(rule_id_or_name, str):
                # 이름으로 찾기
                target_rule = None
                for rule in current_rules:
                    if rule['description'] == rule_id_or_name:
                        target_rule = rule
                        rule_id = rule['id']
                        break
                if not target_rule:
                    logger.warning(f"규칙 이름 '{rule_id_or_name}'을 찾을 수 없습니다")
                    return False
            else:
                # ID로 찾기
                rule_id = rule_id_or_name
                target_rule = None
                for rule in current_rules:
                    if rule['id'] == rule_id:
                        target_rule = rule
                        break
                if not target_rule:
                    logger.warning(f"규칙 ID {rule_id}가 존재하지 않습니다")
                    return False
                
            # 포트포워드 삭제 데이터 준비
            # Based on actual payload: act=del with delcheck parameter containing the rule name
            data = {
                'tmenu': 'iframe',
                'smenu': 'user_portforward',
                'act': 'del',
                'view_mode': 'user',
                'mode': '',
                'name': '',
                'int_sport': '',
                'int_eport': '',
                'ext_sport': '',
                'ext_eport': '',
                'trigger_protocol': '',
                'trigger_sport': '',
                'trigger_eport': '',
                'forward_ports': '',
                'forward_protocol': '',
                'internal_ip': '',
                'protocol': '',
                'disabled': '',
                'priority': '',
                'old_priority': '',
                'delcheck': target_rule['description']  # The rule name to delete
            }
                    
            # 설정 저장
            response = self.api._make_request(
                "sess-bin/timepro.cgi",
                data,
                method="POST"
            )
            
            if response:
                logger.info(f"포트포워드 규칙 ID {rule_id} 삭제 성공")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"포트포워드 규칙 삭제 실패: {e}")
            return False
            
    def update_port_forward_rule(
        self,
        rule_id_or_name,
        description: str = None,
        internal_ip: str = None,
        external_port: int = None,
        internal_port: int = None,
        protocol: str = None
    ) -> bool:
        """
        포트포워드 규칙 수정
        
        Args:
            rule_id_or_name: 수정할 규칙 ID (int) 또는 이름 (str)
            description: 새 설명 (옵션)
            internal_ip: 새 내부 IP (옵션)
            external_port: 새 외부 포트 (옵션)
            internal_port: 새 내부 포트 (옵션)
            protocol: 새 프로토콜 (옵션)
            
        Returns:
            성공 여부
        """
        try:
            # 현재 규칙 조회
            current_rules = self.get_port_forward_rules()
            
            # ID 또는 이름으로 규칙 찾기
            if isinstance(rule_id_or_name, str):
                # 이름으로 찾기
                target_rule = None
                for rule in current_rules:
                    if rule['description'] == rule_id_or_name:
                        target_rule = rule
                        rule_id = rule['id']
                        break
                if not target_rule:
                    logger.warning(f"규칙 이름 '{rule_id_or_name}'을 찾을 수 없습니다")
                    return False
            else:
                # ID로 찾기
                rule_id = rule_id_or_name
                target_rule = None
                for rule in current_rules:
                    if rule['id'] == rule_id:
                        target_rule = rule
                        break
                if not target_rule:
                    logger.warning(f"규칙 ID {rule_id}가 존재하지 않습니다")
                    return False
                
            # 업데이트할 값 설정
            if description is not None:
                target_rule['description'] = description
            if internal_ip is not None:
                target_rule['internal_ip'] = internal_ip
            if external_port is not None:
                target_rule['external_port'] = str(external_port)
            if internal_port is not None:
                target_rule['internal_port'] = str(internal_port)
            if protocol is not None:
                target_rule['protocol'] = protocol
                
            # 포트포워드 수정 데이터 준비
            # Based on actual payload: tmenu=iframe&smenu=user_portforward&act=modify&view_mode=user&mode=user
            data = {
                'tmenu': 'iframe',
                'smenu': 'user_portforward',
                'act': 'modify',
                'view_mode': 'user',
                'mode': 'user',
                'name': target_rule['description'],
                'int_sport': target_rule['internal_port'],
                'int_eport': target_rule['internal_port'],
                'ext_sport': target_rule['external_port'],
                'ext_eport': target_rule['external_port'],
                'trigger_protocol': '',
                'trigger_sport': '',
                'trigger_eport': '',
                'forward_ports': '',
                'forward_protocol': '',
                'internal_ip': target_rule['internal_ip'],
                'protocol': target_rule['protocol'],
                'disabled': '0',
                'priority': str(rule_id),
                'old_priority': str(rule_id)
            }
                
            # 설정 저장
            response = self.api._make_request(
                "sess-bin/timepro.cgi",
                data,
                method="POST"
            )
            
            if response:
                logger.info(f"포트포워드 규칙 ID {rule_id} 수정 성공")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"포트포워드 규칙 수정 실패: {e}")
            return False
            
