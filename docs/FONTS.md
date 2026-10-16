# 사이트 손글씨 폰트

페이지의 한글 제목·본문·버튼에는 JIKJI SOFT의 **개구(Gaegu)**를 사용합니다. 어린 시절 공책에 쓴 글씨처럼 편안한 인상을 주기 위한 선택입니다. 제목은 Bold 700, 본문은 Regular 400이며 손글씨가 작은 화면에서도 읽히도록 크기와 줄 간격을 조정했습니다. 버전 번호와 TV 장식의 작은 영문 표시는 기존 고정폭 글꼴을 유지합니다.

- 소개: https://fonts.google.com/specimen/Gaegu
- 원본: https://github.com/google/fonts/tree/main/ofl/gaegu
- 저작권: Copyright 2018 The Gaegu Project Authors
- 라이선스: SIL Open Font License 1.1. [라이선스 전문](../assets/fonts/gaegu/OFL.txt)
- 원본 커밋·파일 해시·배포 WOFF2 해시: [manifest.json](../assets/fonts/gaegu/manifest.json)

전체 한글·라틴 글리프를 보존한 WOFF2로 압축하여 사이트에서 직접 제공합니다. 글리프를 줄이거나 윤곽을 수정하지 않았습니다. `font-display: swap`을 사용하고 기본 시스템 글꼴로 대체할 수 있습니다. 폰트 서비스를 외부에서 호출하지 않습니다.

재현: `python scripts/import_gaegu.py`. Python `fonttools`와 `brotli`가 필요합니다. 이미 manifest가 있으면 같은 원본 커밋을 사용합니다. 변환 후 cmap·glyph outline·layout·metric 테이블 보존을 확인합니다.

검증: 정적 페이지·검색·필터·대화상자 검사, 페이지와 게임 목록의 한글 글리프 포함 여부, headless Edge의 1440·820·390·320px 뷰포트에서 폰트 로드와 가로 넘침 확인, 데스크톱·모바일 캡처 시각 확인. QA 산출물은 로컬 `qa/handwriting/`에 보관합니다. 폰트 변경은 게임 캡처나 릴리즈 파일에 적용하지 않습니다.
