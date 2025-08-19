# iptime-manager 빌드 가이드

## 빠른 시작

### 1. 리눅스 실행 파일 빌드

```bash
# 방법 1: build.sh 스크립트 사용
chmod +x build.sh
./build.sh

# 방법 2: Python 빌드 스크립트 사용
python3 build.py

# 방법 3: Makefile 사용
make build
```

### 2. 빌드된 파일 실행

```bash
# 빌드된 파일 실행
./dist/iptime-manager --help

# 포트포워드 규칙 조회
./dist/iptime-manager --host http://mercuryx.net:5555 --username admin --password MPDev123! list
```

### 3. 시스템 전역 설치 (선택사항)

```bash
# /usr/local/bin에 설치
sudo cp dist/iptime-manager /usr/local/bin/

# 이제 어디서든 실행 가능
iptime-manager --help
```

## 빌드 요구사항

- Python 3.7 이상
- PyInstaller 6.0.0 이상

```bash
# PyInstaller 설치
pip install pyinstaller
```

## 빌드 옵션

### build.py 사용

Python 스크립트로 대화형 빌드:

```bash
python3 build.py
```

특징:
- 빌드 진행 상황 표시
- 자동 권한 설정
- 빌드 아티팩트 정리 옵션

### Makefile 사용

Make 명령으로 빌드 자동화:

```bash
# 빌드
make build

# 설치
make install

# 정리
make clean
```

### 직접 PyInstaller 사용

```bash
pyinstaller \
    --name iptime-manager \
    --onefile \
    --clean \
    --add-data "src:src" \
    --hidden-import requests \
    --strip \
    iptime_cli.py
```

## 빌드 결과

빌드가 완료되면 `dist/` 디렉토리에 실행 파일이 생성됩니다:

- **Linux/Mac**: `dist/iptime-manager`
- **Windows**: `dist/iptime-manager.exe`

파일 크기: 약 15-25MB (Python 인터프리터 포함)

## 트러블슈팅

### 1. PyInstaller not found

```bash
pip install pyinstaller
```

### 2. 권한 오류

```bash
chmod +x dist/iptime-manager
```

### 3. 실행 시 모듈 찾을 수 없음

hidden imports 추가:
```bash
pyinstaller --hidden-import requests --hidden-import urllib3 ...
```

### 4. 파일 크기 최적화

UPX 사용 (선택사항):
```bash
# UPX 설치
sudo apt-get install upx  # Ubuntu/Debian
brew install upx           # macOS

# PyInstaller에서 UPX 사용
pyinstaller --upx-dir=/usr/local/bin ...
```

## Docker 컨테이너로 빌드 (선택사항)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install pyinstaller

RUN pyinstaller \
    --name iptime-manager \
    --onefile \
    --clean \
    --add-data "src:src" \
    --hidden-import requests \
    iptime_cli.py

CMD ["cp", "dist/iptime-manager", "/output/"]
```

사용:
```bash
docker build -t iptime-builder .
docker run -v $(pwd)/output:/output iptime-builder
```

## 배포

### GitHub Releases

1. 태그 생성:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

2. GitHub에서 Release 생성 후 빌드된 바이너리 업로드

### 자동 빌드 (GitHub Actions)

`.github/workflows/build.yml`:
```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
    - run: pip install pyinstaller
    - run: python build.py
    - uses: actions/upload-artifact@v2
      with:
        name: iptime-manager-linux
        path: dist/iptime-manager
```