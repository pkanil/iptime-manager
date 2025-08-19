# ipTIME Router Manager

ipTIME 공유기의 포트포워딩 규칙을 관리하는 Python 라이브러리 및 CLI 도구입니다.

## 기능

- 포트포워딩 규칙 조회
- 새 포트포워딩 규칙 추가
- 기존 포트포워딩 규칙 수정 (ID 또는 이름으로)
- 포트포워딩 규칙 삭제 (ID 또는 이름으로)
- 시스템 정보 조회

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### CLI 인터페이스

#### 포트포워딩 규칙 목록 조회
```bash
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword list
```

#### 포트포워딩 규칙 단건 조회
```bash
# ID로 조회
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword get 1

# 이름으로 조회
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword get "Web Server"
```

#### 새 포트포워딩 규칙 추가
```bash
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword add \
    --description "Web Server" \
    --internal-ip 192.168.0.100 \
    --external-port 8080 \
    --internal-port 80 \
    --protocol tcp
```

#### 포트포워딩 규칙 수정
```bash
# ID로 수정
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword update 1 \
    --description "Updated Web Server" \
    --internal-ip 192.168.0.101 \
    --external-port 8081

# 이름으로 수정
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword update "Web Server" \
    --internal-ip 192.168.0.101 \
    --external-port 8081
```

#### 포트포워딩 규칙 삭제
```bash
# ID로 삭제
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword delete 1

# 이름으로 삭제
python iptime_cli.py --host 192.168.0.1 --username admin --password yourpassword delete "Web Server"
```

### Python API 사용

```python
from src.iptime_api import IptimeAPI
from src.port_forward import PortForwardManager

# API 초기화
api = IptimeAPI('192.168.0.1', 'admin', 'yourpassword')

# 로그인
if api.login():
    # 포트포워드 매니저 생성
    pf_manager = PortForwardManager(api)
    
    # 모든 규칙 조회
    rules = pf_manager.get_port_forward_rules()
    for rule in rules:
        print(f"{rule['description']}: {rule['internal_ip']}:{rule['internal_port']} <- {rule['external_port']}")
    
    # 단건 조회 (ID 또는 이름으로)
    rule = pf_manager.get_port_forward_rule("SSH")  # 이름으로 조회
    if rule:
        print(f"Found: {rule['description']} at {rule['internal_ip']}")
    
    rule = pf_manager.get_port_forward_rule(1)  # ID로 조회
    if rule:
        print(f"Found: {rule['description']} at {rule['internal_ip']}")
    
    # 새 규칙 추가
    pf_manager.add_port_forward_rule(
        description="SSH",
        internal_ip="192.168.0.100",
        external_port=2222,
        internal_port=22,
        protocol="tcp"
    )
    
    # 규칙 수정 (ID 또는 이름으로)
    pf_manager.update_port_forward_rule(
        rule_id_or_name="SSH",  # 이름으로 수정
        internal_ip="192.168.0.101"
    )
    
    pf_manager.update_port_forward_rule(
        rule_id_or_name=1,  # ID로 수정
        internal_ip="192.168.0.102"
    )
    
    # 규칙 삭제 (ID 또는 이름으로)
    pf_manager.delete_port_forward_rule("SSH")  # 이름으로 삭제
    pf_manager.delete_port_forward_rule(1)  # ID로 삭제
    
    # 이름으로 규칙 찾기
    rule = pf_manager.find_rule_by_name("Web Server")
    if rule:
        print(f"Found: {rule['description']} (ID: {rule['id']})")
    
    # 이름으로 ID 찾기
    rule_id = pf_manager.get_rule_id_by_name("Web Server")
    if rule_id:
        print(f"Rule ID: {rule_id}")
    
    # 로그아웃
    api.logout()
```

## 원격 라우터 접근

HTTP/HTTPS URL을 통한 원격 접근도 지원합니다:

```bash
python iptime_cli.py --host http://router.example.com:5555 --username admin --password yourpassword list
```

## API 서버

REST API 서버도 제공됩니다:

```bash
# 서버 시작
python api_server.py

# API 사용 예제 - 전체 목록 조회
curl -X GET http://localhost:6000/api/portforward \
  -H "Authorization: Bearer your-token"

# 단건 조회 (ID 또는 이름)
curl -X GET http://localhost:6000/api/portforward/1 \
  -H "Authorization: Bearer your-token"

curl -X GET http://localhost:6000/api/portforward/SSH \
  -H "Authorization: Bearer your-token"

# 이름으로 규칙 수정
curl -X PUT http://localhost:6000/api/portforward/SSH \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"internal_ip": "192.168.0.101"}'

# ID로 규칙 삭제
curl -X DELETE http://localhost:6000/api/portforward/1 \
  -H "Authorization: Bearer your-token"
```

## 요구사항

- Python 3.6+
- requests 라이브러리
- ipTIME 공유기 (CGI 인터페이스 지원 모델)

## 주의사항

- 이 도구는 ipTIME 공유기의 CGI 인터페이스를 사용합니다
- 공유기 펌웨어 버전에 따라 일부 기능이 다를 수 있습니다
- 관리자 권한이 필요합니다
- 규칙 이름(description)이 중복될 경우 첫 번째 매칭되는 규칙이 선택됩니다
