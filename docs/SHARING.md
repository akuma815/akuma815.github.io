# 게임별 패치 공유

게임 소개의 **이 게임 링크 복사**를 누르면 그 게임의 고유 주소를 복사합니다. 링크를 받은 사람은 해당 게임 소개와 다운로드 안내를 바로 볼 수 있습니다. 주소 입력 칸을 직접 선택해 복사할 수도 있습니다.

예: [톰과 제리 한글 패치](https://akuma815.github.io/games/nes-tom-and-jerry-kr-patch/)

## 주소와 동작

- 고유 공유 주소: `/games/{catalog의 게임 id}/`.
- 호환 주소: `/?game={게임 id}`. 게임 소개를 열면 주소창에도 게임 ID가 반영됩니다.
- 공유 주소로 직접 들어가거나 새로고침하면 팩 삽입을 기다리지 않고 해당 게임 소개를 엽니다. 목록에서 팩을 고를 때는 기존 삽입 연출을 유지합니다.
- 닫기/Escape는 목록 주소로 돌아갑니다. 브라우저 뒤로·앞으로 가기도 게임 소개 상태를 반영합니다.
- 없는 게임 ID는 전체 목록과 안내를 표시합니다. URL의 문자열을 HTML로 삽입하지 않습니다.
- 클립보드 복사가 거부되면 실제 주소를 선택해 수동 복사를 안내합니다. 실패를 성공으로 표시하지 않습니다.

## 공유 미리보기와 게시

`scripts/generate_game_pages.py`가 카탈로그의 모든 게임에 대해 개별 HTML을 만듭니다. 게임별 제목·설명·대표 캡처·정식 주소를 Open Graph와 Twitter 메타 태그에 넣습니다. JavaScript를 실행하지 않는 환경에서도 해당 게임 안내와 다운로드 링크를 읽을 수 있습니다. 실제 외부 메신저로 메시지를 보내는 검사는 수행하지 않습니다.

기존 Actions가 목록 갱신과 검사를 마친 뒤 `_site/games/{id}/index.html`을 생성해 Pages에 포함합니다. 생성 HTML은 Git에서 따로 편집하거나 중복 보관하지 않습니다. 새 게임도 카탈로그 등록 시 같은 방식으로 자동 생성됩니다. 기준 도메인을 바꾸면 `--site-url`도 함께 지정합니다.

```text
python scripts/check_site.py
python scripts/check_sharing_browser.py
python scripts/check_sharing_browser.py --url https://akuma815.github.io/ --out qa/sharing/live
```

브라우저 검사는 독립된 Edge로 PC/모바일 공유 주소 진입·복사·새로고침·뒤로/앞으로·클립보드 거부·미등록 ID·모든 게임의 HTTP/공유 메타데이터·JavaScript 없는 다운로드를 확인합니다. 첫 명령의 정적/DOM 검사는 실제 브라우저 검사와 구분합니다. PNG·결과 JSON은 기존 무시 경로 `qa/sharing`에 보관합니다.

메인 페이지 디자인·기존 게임별 번역 범위와 다운로드 주소·방명록/버그 신고 저장 방식은 기존 데이터를 사용합니다.
