# 릴리스 가이드

## 자동 릴리스 (GitHub Actions)

### 1. 태그 기반 자동 릴리스

새 버전을 릴리스하려면 Git 태그를 생성하고 푸시하면 자동으로 빌드 및 릴리스가 생성됩니다.

```bash
# 버전 태그 생성 (v로 시작해야 함)
git tag -a v1.0.0 -m "Release version 1.0.0"

# GitHub에 태그 푸시
git push origin v1.0.0
```

### 2. 자동 처리 과정

태그 푸시 후 GitHub Actions가 자동으로:

1. **멀티 플랫폼 빌드**: Linux, macOS, Windows 바이너리 생성
2. **GitHub Release 생성**: 릴리스 페이지 자동 생성
3. **바이너리 업로드**: 각 플랫폼별 실행 파일 자동 첨부

### 3. 릴리스 확인

- GitHub 저장소의 [Releases](https://github.com/[username]/iptime-manager/releases) 페이지에서 확인
- 각 플랫폼별 바이너리 다운로드 가능

## 개발 빌드

### main/develop 브랜치 푸시

```bash
git push origin main
```

- 자동으로 테스트 빌드 실행
- Actions 탭에서 빌드 상태 확인
- Artifacts에서 개발 빌드 다운로드 (7일간 보관)

## 수동 릴리스

### GitHub UI에서 수동 실행

1. Actions 탭 → "Build and Release" 워크플로우
2. "Run workflow" 버튼 클릭
3. 브랜치 선택 후 실행

## 버전 관리

### Semantic Versioning

```
v[MAJOR].[MINOR].[PATCH]

예시:
- v1.0.0: 첫 정식 릴리스
- v1.1.0: 새 기능 추가
- v1.1.1: 버그 수정
- v2.0.0: 메이저 변경 (호환성 깨짐)
```

### 릴리스 전 체크리스트

- [ ] CHANGELOG.md 업데이트
- [ ] 버전 번호 확인
- [ ] 로컬 테스트 완료
- [ ] README.md 업데이트 (필요시)

## 릴리스 노트 작성

### 자동 생성된 릴리스 노트 편집

1. Releases 페이지에서 생성된 릴리스 선택
2. "Edit release" 클릭
3. 다음 섹션 추가/수정:
   - **새 기능** (New Features)
   - **개선사항** (Improvements)
   - **버그 수정** (Bug Fixes)
   - **주의사항** (Breaking Changes)

### 릴리스 노트 예시

```markdown
## iptime-manager v1.0.0

### 🎉 새 기능
- 포트포워드 규칙 관리 CLI
- REST API 서버 지원
- 이름 기반 규칙 관리

### 🔧 개선사항
- 로깅 레벨 최적화
- 디버그 모드 추가

### 🐛 버그 수정
- 원격 라우터 연결 문제 해결
- 세션 관리 개선

### 📦 다운로드
- Linux: iptime-manager-linux-amd64
- macOS: iptime-manager-macos-amd64  
- Windows: iptime-manager-windows-amd64.exe
```

## 문제 해결

### 빌드 실패 시

1. Actions 탭에서 실패한 워크플로우 확인
2. 로그 확인 및 오류 수정
3. 코드 수정 후 다시 푸시

### 릴리스 생성 실패

- GITHUB_TOKEN 권한 확인
- 태그 형식 확인 (v로 시작)
- 중복 태그 확인

### 바이너리 업로드 실패

- 파일 크기 제한 확인 (2GB 이하)
- 네트워크 상태 확인
- GitHub API 상태 확인