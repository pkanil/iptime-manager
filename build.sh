#!/bin/bash

# iptime-manager 리눅스 빌드 스크립트

echo "🚀 iptime-manager Linux Build Script"
echo "===================================="

# PyInstaller 설치 확인
if ! command -v pyinstaller &> /dev/null; then
    echo "⚠️  PyInstaller가 설치되어 있지 않습니다."
    echo "📦 PyInstaller 설치 중..."
    pip install pyinstaller
fi

# 빌드 디렉토리 정리
echo "🧹 이전 빌드 정리..."
rm -rf build dist *.spec

# PyInstaller로 빌드
echo "🔨 실행 파일 빌드 중..."
pyinstaller \
    --name iptime-manager \
    --onefile \
    --clean \
    --noconfirm \
    --add-data "src:src" \
    --hidden-import requests \
    --hidden-import urllib3 \
    --hidden-import certifi \
    --hidden-import charset_normalizer \
    --hidden-import idna \
    --strip \
    iptime_cli.py

# 빌드 결과 확인
if [ -f "dist/iptime-manager" ]; then
    # 실행 권한 부여
    chmod +x dist/iptime-manager
    
    # 파일 크기 확인
    SIZE=$(du -h dist/iptime-manager | cut -f1)
    
    echo ""
    echo "✅ 빌드 성공!"
    echo "📦 실행 파일: dist/iptime-manager"
    echo "📊 파일 크기: $SIZE"
    echo ""
    echo "실행 방법:"
    echo "  ./dist/iptime-manager --help"
    echo ""
    echo "시스템 전역 설치 (선택사항):"
    echo "  sudo cp dist/iptime-manager /usr/local/bin/"
    echo "  iptime-manager --help"
else
    echo "❌ 빌드 실패!"
    exit 1
fi