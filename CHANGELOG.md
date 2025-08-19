# Changelog

모든 주요 변경사항이 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 기반으로 하며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

## [Unreleased]

### Added
- 초기 릴리스
- ipTIME 라우터 포트포워드 관리 기능
- CLI 인터페이스
- REST API 서버
- 이름 기반 규칙 관리
- 단건 조회 기능
- 디버그 모드 지원

### Changed
- 로깅 레벨 최적화 (기본 WARNING, --debug 플래그로 상세 로그)

### Fixed
- 원격 라우터 연결 지원
- 세션 관리 개선
- JavaScript 쿠키 추출
- Delete 작업 페이로드 수정

## [1.0.0] - 2024-01-XX

### Added
- 첫 정식 릴리스
- Linux, macOS, Windows 바이너리 지원
- GitHub Actions 자동 빌드 및 릴리스

### Features
- 포트포워드 규칙 CRUD (생성, 조회, 수정, 삭제)
- 이름 또는 ID로 규칙 관리
- HTTP/HTTPS 프로토콜 지원
- 세션 기반 인증

### Supported Platforms
- Linux (amd64)
- macOS (amd64)
- Windows (amd64)

---

## 버전 규칙

- **Major (X.0.0)**: 호환성이 깨지는 큰 변경
- **Minor (0.X.0)**: 새로운 기능 추가
- **Patch (0.0.X)**: 버그 수정 및 작은 개선