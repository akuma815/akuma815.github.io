# 게임별 담벼락과 버그 칠판

게임 팩을 고른 뒤 소개창에서 **담벼락 낙서** 또는 **버그 칠판** 탭을 선택합니다. 방명록은 색연필 낙서와 벽돌 담벼락, 버그 신고는 분필·목재 테두리·지우개가 있는 칠판으로 표현합니다.

## 글을 남기는 순서

1. 해당 게임의 방명록 또는 신고 양식에 내용을 적습니다.
2. GitHub에서 등록하기 버튼을 누릅니다.
3. GitHub 계정으로 로그인하고 내용을 확인한 뒤 **최종 등록**합니다. 스크린샷이나 긴 로그는 이 단계에서 첨부할 수 있습니다.
4. 사이트로 돌아와 새로 보기를 누릅니다.

사이트에서 버튼을 누른 것만으로 글이 저장되었다고 표시하지 않습니다. GitHub에서 최종 등록해야 다른 방문자도 읽을 수 있습니다. 글은 공개이며 실제 작성자의 GitHub 계정명이 표시됩니다. GitHub의 글에서 답글을 읽거나 작성할 수 있습니다.

긴 글로 GitHub 초안 URL이 7,000자를 넘으면 내용을 자르지 않고 **내용 복사 → GitHub에서 이어 쓰기**를 제공합니다. 입력한 초안은 게임·게시판별로 현재 페이지 메모리에만 보관합니다. 창을 새로고침하거나 닫으면 등록하지 않은 초안은 사라집니다.

## 저장 및 조회

- 각 게임의 공개 저장소 **Issues**가 실제 저장소입니다. 서로 다른 게임의 글이 섞이지 않습니다.
- 방명록 분류: `site-guestbook`, 템플릿: `.github/ISSUE_TEMPLATE/site-guestbook.md`.
- 버그 신고 분류: `site-bug`, 템플릿: `.github/ISSUE_TEMPLATE/site-bug-report.md`.
- 템플릿이 기본 라벨을 적용합니다. 방문자에게 라벨 편집 권한을 요구하는 `labels` URL 매개변수를 사용하지 않습니다. [GitHub 이슈 생성 URL과 템플릿 안내](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue)를 따릅니다.
- 사이트에는 토큰이나 로그인 자격 증명을 넣지 않습니다. 선택한 게시판만 공개 [GitHub Issues REST API](https://docs.github.com/en/rest/issues/issues)로 조회합니다. 페이지당 12개씩 읽고 5분간 메모리에 보관합니다. 새로 보기는 캐시를 우회합니다.
- 열린 신고와 닫힌 신고를 모두 읽습니다. 닫힌 신고를 수정 완료 또는 실행 검증 완료와 동일하게 표시하지 않습니다.
- 공개 API의 조회 제한·네트워크 오류가 생기면 실패 안내와 해당 게임의 GitHub 목록 링크를 표시합니다. 빈 게시판과 조회 실패를 구분합니다.
- 외부 글은 일반 텍스트로 표시합니다. HTML·스크립트·Markdown 이미지·외부 추적 이미지를 실행하거나 불러오지 않습니다. PR과 다른 라벨·다른 저장소 주소는 제외합니다.
- 팩을 닫거나 다른 게임으로 바꾸면 진행 중 조회를 취소합니다. 늦게 도착한 이전 게임의 응답도 무시합니다.

## 운영 및 새 게임 추가

삭제·수정·잠금·라벨 정리는 해당 게임의 GitHub Issues에서 합니다. 방명록 글을 닫아도 전체 보기에는 남습니다. 글을 사이트 분류에서 제외하려면 해당 `site-*` 라벨을 제거합니다. 기존 `bug` 등의 다른 라벨 글은 자동으로 가져오지 않으므로, 칠판에 표시하려면 `site-bug`를 추가합니다.

새 게임을 catalog.json에 등록하고 공개 저장소를 준비한 뒤 다음을 실행합니다.

```powershell
# 기본은 조회만 수행. 게임별 Issues/라벨/템플릿 상태 확인
python scripts/setup_community.py

# 필요한 경우 공개 저장소에 라벨과 양식 추가
python scripts/setup_community.py --apply
```

`--apply`는 사용자의 GitHub CLI 인증으로 작업합니다. 필요한 경우 Issues를 켜고 누락 라벨을 생성한 뒤, 원래 Git 트리에 두 템플릿만 더한 커밋을 만듭니다. 강제 푸시하지 않으며 다른 파일과 기존 Issue 양식은 보존합니다. 같은 이름의 관리되지 않은 양식은 덮어쓰지 않습니다. 사이트 관리 표시가 있는 양식은 `community-templates/` 원본으로 갱신할 수 있습니다. 이미 동일하면 변경하지 않습니다. 결과는 `qa/community/setup_*.json`에 기록합니다.

기존 20개 게임의 초기 연결 결과는 [COMMUNITY_SETUP.json](COMMUNITY_SETUP.json)에 있습니다. 게시판 연결은 패치 바이너리·번역문·릴리즈 파일을 바꾸지 않습니다.

## 검사

독립 테스트 브라우저의 선택적 의존성은 requirements-browser.txt를 사용합니다. 로컬 HTTP 서버를 켠 뒤:

```powershell
python scripts/check_site.py
python scripts/check_community_browser.py --channel msedge
python scripts/check_community_browser.py --channel msedge --live-readonly
```

Chromium 설치 환경에서는 `--channel chromium`을 사용합니다. 실제 배포 주소는 `--url https://akuma815.github.io/`로 검사합니다.

- 기본 브라우저 검사는 GitHub API 응답을 **테스트 데이터**로 대체합니다. 글 분리·페이지 넘기기·중복 제거·캐시·안전한 텍스트 표시·초안 URL·긴 글·오류·키보드·임시 초안·지연 응답·모바일을 검증합니다. 글쓰기와 클립보드도 테스트 안에서 가로채어 실제 글 게시나 OS 클립보드 변경을 하지 않습니다.
- `--live-readonly`는 테스트 데이터 없이 실제 공개 GitHub 목록을 읽습니다. 글을 등록하지 않습니다.
- 실제 GitHub 로그인과 최종 게시 동작을 자동으로 대행하지 않습니다. 테스트 글을 공개 저장소에 남기지 않습니다.
- 캡처와 결과는 qa/community에만 저장하며 배포 아티팩트에서 제외합니다.

2026-10-16 추가한 톰과 제리 저장소에는 기존 사이트와 같은 방명록/버그 신고 템플릿, `site-guestbook`/`site-bug` 라벨을 연결했습니다. 현재 등록 게임은 21개입니다.
