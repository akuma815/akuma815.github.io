# 패치 목록 이미지 출처

이미지는 직접 확인한 기존 작업 자료에서 가져왔으며 원본 픽셀을 수정하지 않았습니다. 한글 타이틀을 우선 사용했습니다. 작업 당시 빌드 캡처를 현재 배포본의 전 구간 검수 근거로 확대하지 않습니다.

| 게임 ID | 종류 | 설명 | 원본 SHA-256 |
| --- | --- | --- | --- |
| nds-another-code-kr-patch | graphics | 공개 작업기 내 오프닝 그래픽 비교. 실제 게임 캡처가 아닌 비교 자료입니다. | `293cebf9b5dc26cd187c49a7e53273aa034aa4fc965e84d8dc5d64110f70385b` |
| nes-battletoads-kr-patch | runtime | final_release Mesen 캡처 | `13181f7e0099b1b4523e3ece5babd7111d739128ea54c77c09678f87b0d07251` |
| ps1-bushido-blade-kr-patch | runtime | poc_title 2026-07-29 캡처 | `ceea68ac9c1ba135d8910fbcbd3c8736985429363b1fcd23e8dd44dd96fa6907` |
| nes-city-connection-kr-patch | runtime | logo22 Mesen 캡처 | `61a381823a2fc99af8019f8e1af1aa3aa78522e2dae743cb4ea326b08a3b1705` |
| arcade-dark-seal-kr-patch | runtime | dumps_kr_attract 게임 캡처 | `a5314bf097e968b5c55c9cf731eb7135562a7b0d6762d3828ecc3d25aa0dd98b` |
| arcade-dark-seal-2-kr-patch | runtime | dumps_Korean_v101_check 게임 캡처 | `05f9fd3d8baebfcf287fc4bb98f17df1def0162b21dfebbdc51fcedae31b42f3` |
| psp-death-jr-kr-patch | video | 자막 삽입 영상의 QA 프레임. 에뮬레이터 실행 캡처가 아닙니다. | `6a792e67220625d5ed6df418014b6b6355bf6da10ae5637322d2b18e6007e4b1` |
| gba-metroid-zero-mission-kr-patch | runtime | title_ko Mesen 캡처 | `ea7dd80cd349bbde1afb55b7ee772a608247ac4100aa77356b927a525e524a2a` |
| gba-metroid-fusion-kr-patch | runtime | v24_korean_title_vramsafe Mesen 캡처 | `d5a09b21e12504e2acb392167250bc0c9f0ce2a916792c8f6ad3c3a13d18f404` |
| nes-ninja-jajamaru-kun-kr-patch | runtime | title_kr_menu_003 Mesen 콜드 부팅 캡처 | `ddecbbb92debd5611cd3242da5fb642b22a4e0ca18b76a4bf9487a5800d6a7eb` |
| psp-prinny-kr-patch | graphics | 한글 메뉴 텍스처 작업 이미지. 게임 전체 화면 캡처가 아닙니다. | `f5dd9b65bc85483f41e61ceb2212502f8df34f824ab2973d60c95f45ca679eba` |
| ps1-rakugaki-showtime-kr-patch | runtime | hangul_atlas_001_title DuckStation 캡처. 대형 로고는 원문입니다. | `486593937f921e5425db4fc509885c76a7d920c77163290f92b86b109c381fe0` |
| pc-shivers-kr-patch | runtime | full_audio_subtitles_017 커스텀 ScummVM 캡처 | `35fbb7922a2093998fff412f25d404204b4fa1bffa9dd22be31ace872afeba08` |
| pce-tenshi-no-uta-2-kr-patch | runtime | release_Tenshi2_KR_v1.0_20261014 pce_fast 캡처 | `cf345f38aca3f587da400ab989dca5c016593102f63be85f5007a7dafecb08eb` |
| nes-tiny-toon-adventures-kr-patch | runtime | kr_smoke_001 Mesen 캡처 | `00a6db5868f7fb989b80ebaa40f1820694bb38790f1f9e6acac514013f81f69e` |
| nes-tiny-toon-adventures-2-kr-patch | runtime | title_kr_ai_003_attract Mesen 캡처 | `772d8ff10d5612fd3016f580111fd9ba8c8c1c2ae77381563567f31f52f4ef95` |

Switch판 천사의 시 1·2와 발할라 나이츠는 확인된 전체 화면 캡처가 없어 준비 중으로 표시했습니다. 어나더 코드와 프리니는 그래픽 작업 이미지, 데스 주니어는 영상 자막 QA 프레임이며 게임 실행 캡처가 아닙니다.

큰 이미지의 배포 형식은 무손실 WebP입니다. 컨테이너 바이트 해시는 원본 PNG와 달라도 디코딩한 RGBA 픽셀은 원본과 같으며 data/screenshots.json의 pixelSHA256으로 검증합니다.
