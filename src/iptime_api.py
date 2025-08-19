"""
ipTIME Router API Client
CGI 스크립트를 사용한 ipTIME 공유기 제어 라이브러리
"""
import logging
import re
from typing import Dict, Optional

import requests
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class IptimeAPI:
    """ipTIME 공유기 API 클라이언트"""
    
    def __init__(self, host: str, username: str = "admin", password: str = ""):
        """
        초기화
        
        Args:
            host: 공유기 IP 주소 또는 URL (예: 192.168.0.1 또는 https://router.example.com)
            username: 관리자 계정 (기본값: admin)
            password: 관리자 비밀번호
        """
        # URL 형식 처리
        if host.startswith('http://') or host.startswith('https://'):
            self.base_url = host
            # Extract host from URL for self.host
            from urllib.parse import urlparse
            parsed = urlparse(host)
            self.host = parsed.netloc
        else:
            self.host = host
            self.base_url = f"http://{host}"
        
        self.username = username
        self.password = password
        self.session = requests.Session()
        # 세션 유지를 위한 헤더 추가
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        })
        self.session_id = None
        self.captcha = None
        self.logged_in = False
        
    def _get_session_info(self) -> Dict:
        """세션 정보 획득"""
        try:
            url = f"{self.base_url}/sess-bin/login_session.cgi"
            logger.info(f"세션 정보 요청: {url}")
            response = self.session.get(url, verify=False, timeout=10)
            response.raise_for_status()
            
            # 세션 정보 파싱
            content = response.text
            logger.debug(f"응답 내용 (처음 500자): {content[:500]}")
            session_info = {}
            
            # captcha 추출
            captcha_match = re.search(r'captcha_on\s*=\s*"(\d+)"', content)
            if captcha_match:
                session_info['captcha_on'] = captcha_match.group(1)
                
            # default_login 추출  
            default_login_match = re.search(r'default_login\s*=\s*"([^"]+)"', content)
            if default_login_match:
                session_info['default_login'] = default_login_match.group(1)
                
            # session_id 추출
            session_id_match = re.search(r'session_id\s*=\s*"([^"]+)"', content)
            if session_id_match:
                session_info['session_id'] = session_id_match.group(1)
            
            logger.info(f"세션 정보 추출: {session_info}")
            return session_info
            
        except Exception as e:
            logger.error(f"세션 정보 획득 실패: {e}")
            raise
            
    def login(self) -> bool:
        """공유기 로그인"""
        try:
            # 세션 정보 획득 시도 (선택적)
            try:
                session_info = self._get_session_info()
                self.session_id = session_info.get('session_id', '')
                self.captcha = session_info.get('captcha_on', '0')
            except:
                logger.info("세션 정보 획득 실패, 기본값 사용")
                self.session_id = ''
                self.captcha = '0'
            
            # 로그인 데이터 준비
            login_data = {
                'init_status': '1',
                'captcha_on': '0',
                'captcha_file': '',
                'username': self.username,
                'passwd': self.password,
                'default_passwd': '초기암호:admin(변경필요)',
                'captcha_code': ''
            }
            
            logger.info(f"로그인 시도: {self.base_url}/sess-bin/login_handler.cgi")
            
            # 브라우저와 동일한 헤더 설정
            headers = {
                'Referer': f"{self.base_url}/sess-bin/login_session.cgi"
            }
            
            # 로그인 요청
            response = self.session.post(
                f"{self.base_url}/sess-bin/login_handler.cgi",
                data=login_data,
                headers=headers,
                verify=False,
                timeout=10,
                allow_redirects=False  # 리다이렉트를 따르지 않음
            )
            
            logger.debug(f"로그인 응답 상태: {response.status_code}")
            logger.debug(f"쿠키: {self.session.cookies}")
            logger.debug(f"응답 내용 (처음 500자): {response.text[:500]}")
            
            # JavaScript로 쿠키를 설정하는 경우 처리 (200 응답)
            if 'setCookie' in response.text:
                # JavaScript에서 세션 ID 추출
                session_match = re.search(r"setCookie\('([^']+)'\)", response.text)
                if session_match:
                    session_id = session_match.group(1)
                    logger.info(f"세션 ID 추출 성공: {session_id}")
                    # 쿠키 설정
                    self.session.cookies.set('efm_session_id', session_id, domain=self.host.split(':')[0], path='/')
                    self.logged_in = True
                    return True
            # 502 에러가 와도 리다이렉트 스크립트가 있으면 성공으로 간주
            elif 'top.location' in response.text and 'login_session' not in response.text:
                logger.info("로그인 성공 (리다이렉트 확인)")
                self.logged_in = True
                return True
            elif response.status_code == 200:
                # 쿠키 확인 또는 응답 내용 확인
                if 'efm_session_id' in self.session.cookies or 'sess_id' in self.session.cookies:
                    logger.info("로그인 성공 (쿠키 확인)")
                    return True
                # 응답 내용에서 성공 여부 확인
                elif 'timepro.cgi' in response.text:
                    logger.info("로그인 성공 (페이지 확인)")
                    return True
                    
            logger.error("로그인 실패")
            return False
            
        except Exception as e:
            logger.error(f"로그인 중 오류 발생: {e}")
            return False
            
    def logout(self) -> bool:
        """로그아웃"""
        try:
            response = self.session.get(f"{self.base_url}/sess-bin/logout.cgi")
            if response.status_code == 200:
                logger.info("로그아웃 성공")
                return True
            return False
        except Exception as e:
            logger.error(f"로그아웃 실패: {e}")
            return False
            
    def _make_request(self, cgi_path: str, data: Dict = None, method: str = "GET") -> Optional[str]:
        """CGI 요청 생성 및 전송"""
        try:
            # URL 구성 - cgi_path가 /로 시작하면 그대로, 아니면 / 추가
            if cgi_path.startswith('/'):
                url = f"{self.base_url}{cgi_path}"
            else:
                url = f"{self.base_url}/{cgi_path}"
            
            # ipTIME requires Referer header for session validation
            headers = {
                'Referer': f"{self.base_url}/sess-bin/login_session.cgi"
            }
            
            if method == "GET":
                # 파라미터를 URL에 직접 추가 (iptime 호환성)
                if data:
                    from urllib.parse import urlencode
                    url = f"{url}?{urlencode(data)}"
                response = self.session.get(url, headers=headers, verify=False, timeout=10)
            else:
                response = self.session.post(url, data=data, headers=headers, verify=False, timeout=10)
            
            # 502 에러는 iptime에서 정상 응답으로 처리될 수 있음
            if response.status_code in [200, 502]:
                return response.text
            else:
                response.raise_for_status()
                return response.text
            
        except Exception as e:
            logger.error(f"요청 실패: {e}")
            return None
            
    def get_system_info(self) -> Optional[Dict]:
        """시스템 정보 조회"""
        try:
            response = self._make_request("timepro.cgi", {"tmenu": "iframe", "smenu": "expertinfo"})
            if response:
                # 시스템 정보 파싱
                info = {}
                
                # 펌웨어 버전
                fw_match = re.search(r'펌웨어 버전.*?<td[^>]*>([^<]+)</td>', response, re.DOTALL)
                if fw_match:
                    info['firmware_version'] = fw_match.group(1).strip()
                    
                # 모델명
                model_match = re.search(r'모델명.*?<td[^>]*>([^<]+)</td>', response, re.DOTALL)
                if model_match:
                    info['model'] = model_match.group(1).strip()
                    
                return info
                
        except Exception as e:
            logger.error(f"시스템 정보 조회 실패: {e}")
            
        return None
