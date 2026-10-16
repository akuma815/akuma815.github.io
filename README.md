# AKUMA815 한글 패치 아카이브

**사이트: https://akuma815.github.io/nds-another-code-kr-patch/**

현재 기존 패치 저장소의 독립된 `gh-pages` 브랜치에서 게시합니다. 전용 저장소 생성 제한이 해제되면 계정 루트 Pages로 옮길 수 있습니다. [최신 인계](docs/HANDOFF.md)

게임별 한글 패치·최종 릴리즈·적용 안내를 모은 GitHub Pages 정적 사이트입니다.

## 기능

- 한국어·영문 게임명 검색, 플랫폼 필터, 정렬, 배포 중인 패치만 보기
- 게임별 상세 안내와 공개 릴리즈·소스 링크
- 공개 등록 대기와 배포 중 상태 구분
- 모바일 레이아웃, 키보드 탐색, 상세 대화상자

## 로컬 미리보기

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8765`를 엽니다. 빌드 및 npm 설치가 필요 없습니다.

## 목록 갱신

`data/catalog.json`이 목록 원장입니다. `data/catalog.js`는 같은 내용을 브라우저에서 읽을 수 있도록 생성한 파일입니다.

```powershell
python scripts/update_catalog.py --verify-remote
```

로그인된 GitHub CLI로 공개 저장소와 릴리즈 첨부 존재 여부를 확인합니다. 아직 공개되지 않은 주소에는 다운로드 링크를 만들지 않습니다. 새 게임을 추가하려면 JSON에 항목을 추가한 뒤 스크립트를 실행합니다. 자동 예약 갱신은 설정하지 않았습니다.

## 배포

GitHub Pages에서 배포 브랜치의 루트를 게시합니다. `index.html`, `assets/`, `data/`, `.nojekyll`을 함께 유지합니다. 모든 내부 경로는 상대 경로여서 계정 루트와 프로젝트 Pages 주소에서 모두 동작합니다.

원본 게임·BIOS·패치 완료 게임 파일·인증정보는 사이트에 포함하지 않습니다. 장식 그래픽은 사이트용 타이포그래피이며 게임 실행 화면이 아닙니다.
