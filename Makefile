# iptime-manager Makefile

.PHONY: help build install clean run test

help:
	@echo "iptime-manager 빌드 시스템"
	@echo "========================"
	@echo "사용 가능한 명령:"
	@echo "  make build    - 실행 파일 빌드"
	@echo "  make install  - 시스템에 설치 (/usr/local/bin)"
	@echo "  make clean    - 빌드 아티팩트 정리"
	@echo "  make run      - 개발 모드로 실행"
	@echo "  make test     - 테스트 실행"

build:
	@echo "🔨 실행 파일 빌드 중..."
	@python3 build.py

install: build
	@echo "📦 시스템에 설치 중..."
	@sudo cp dist/iptime-manager /usr/local/bin/
	@echo "✅ 설치 완료! 'iptime-manager --help'로 실행하세요"

clean:
	@echo "🧹 빌드 아티팩트 정리..."
	@rm -rf build dist __pycache__ *.spec
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 정리 완료"

run:
	@python3 iptime_cli.py --help

test:
	@echo "🧪 테스트 실행..."
	@python3 -m pytest tests/ -v