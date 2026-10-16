"""Package reviewed images with identical decoded pixels; large images use lossless WebP."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image

SITE=Path(__file__).resolve().parents[1]
PROJECT=SITE.parents[1]
CURATED={
 'nds-another-code-kr-patch':('web/akuma815.github.io/qa/another_embedded_4.png','오프닝 한글 그래픽 비교','graphics','공개 작업기 내 오프닝 그래픽 비교. 실제 게임 캡처가 아닌 비교 자료입니다.'),
 'nes-battletoads-kr-patch':('Games/Battletoads/work/qa/final_release/mesen/f01500.png','한글 타이틀','runtime','final_release Mesen 캡처'),
 'ps1-bushido-blade-kr-patch':('Games/Bushido Blade/work/screenshots/poc_title/ブシドーブレード 2026-07-29-21-55-42.png','한글 타이틀 · 작업 당시 캡처','runtime','poc_title 2026-07-29 캡처'),
 'nes-city-connection-kr-patch':('Games/City Connection/work/qa/logo22/f00240.png','한글 타이틀 · 작업 당시 캡처','runtime','logo22 Mesen 캡처'),
 'arcade-dark-seal-kr-patch':('Games/Dark Seal/darksealj/work/dumps_kr_attract/screenshot.png','한글 프롤로그','runtime','dumps_kr_attract 게임 캡처'),
 'arcade-dark-seal-2-kr-patch':('Games/Dark Seal/darkseal2/work/dumps_Korean_v101_check/screenshot.png','한글 프롤로그 · v1.0.1 캡처','runtime','dumps_Korean_v101_check 게임 캡처'),
 'psp-death-jr-kr-patch':('Games/Death Jr/workspace/video/subtitled_001_kyobo24/qa/GAMEINTRO_005.png','한글 영상 자막 · 미리보기','video','자막 삽입 영상의 QA 프레임. 에뮬레이터 실행 캡처가 아닙니다.'),
 'gba-metroid-zero-mission-kr-patch':('Games/Metroid - Zero Mission/qa/logs/title_ko/t2400_screen.png','한글 타이틀','runtime','title_ko Mesen 캡처'),
 'gba-metroid-fusion-kr-patch':('Games/Metroid Fusion/qa/screenshots/v24_korean_title_vramsafe/03450_f.png','한글 타이틀 · 작업 당시 캡처','runtime','v24_korean_title_vramsafe Mesen 캡처'),
 'nes-ninja-jajamaru-kun-kr-patch':('Games/Ninja Jajamaru-kun/qa/title_kr_menu_003/cold_boot_001/frame_0240.png','한글 타이틀 · 메뉴 003','runtime','title_kr_menu_003 Mesen 콜드 부팅 캡처'),
 'psp-prinny-kr-patch':('Games/Prinny - Ore ga Shujinkou de Iinsuka/work/live/base_menu/091591e09a963304c67a3ca6.png','한글 메뉴 그래픽 · 캡처 준비 중','graphics','한글 메뉴 텍스처 작업 이미지. 게임 전체 화면 캡처가 아닙니다.'),
 'ps1-rakugaki-showtime-kr-patch':('Games/Rakugaki Showtime/work/runtime/hangul_atlas_001_title/title_013.png','한글 메뉴 · 작업 당시 캡처','runtime','hangul_atlas_001_title DuckStation 캡처. 대형 로고는 원문입니다.'),
 'pc-shivers-kr-patch':('Games/Shivers1/qa/screenshots/scummvm/full_audio_subtitles_017_20260903_01/capture_027s.png','한글 타이틀 · 작업 당시 캡처','runtime','full_audio_subtitles_017 커스텀 ScummVM 캡처'),
 'pce-tenshi-no-uta-2-kr-patch':('Games/Tenshi no Uta II - Datenshi no Sentaku (Japan)/qa/release_Tenshi2_KR_v1.0_20261014/smoke/single_pcefast_0031.png','한글 타이틀 · v1.0','runtime','release_Tenshi2_KR_v1.0_20261014 pce_fast 캡처'),
 'nes-tiny-toon-adventures-kr-patch':('Games/Tiny Toon Adventures/qa/title/kr_smoke_001/frame_0240.png','한글 타이틀','runtime','kr_smoke_001 Mesen 캡처'),
 'nes-tiny-toon-adventures-2-kr-patch':('Games/Tiny Toon Adventures 2/qa/title/title_kr_ai_003_attract/frame_00840.png','한글 타이틀','runtime','title_kr_ai_003_attract Mesen 캡처'),
}

# Preserve user attachments as PNG without format conversion on future imports.
USER_CAPTURES = {
 'nds-another-code-kr-patch': ('Another  Code', '한글 타이틀', '사용자 제공 어나더 코드 타이틀 화면. 이번 실행 ROM은 최종 배포 패치 결과 해시와 일치합니다.'),
 'pc-shivers-kr-patch': ('Shivers1', '한글 타이틀', '사용자 제공 쉬버스 타이틀 화면. RC1과 같은 025 커스텀 실행기를 사용했으며 메뉴 일부는 영어로 표시됩니다.'),
 'ps1-rakugaki-showtime-kr-patch': ('Rakugaki Showtime', '타이틀 · 한글 시작 안내', '사용자 제공 라쿠가키 쇼타임 전체 타이틀 화면. 대형 로고는 원문이며 양옆 시작 안내는 한글입니다.'),
 'psp-prinny-kr-patch': ('Prinny - Ore ga Shujinkou de Iinsuka', '한글 타이틀·메뉴', '사용자 제공 프리니 타이틀·메뉴 화면. 촬영 당시 FPS 표시와 화면 비율을 그대로 보존했습니다.'),
}
for slug,(folder,caption,note) in USER_CAPTURES.items():
    CURATED[slug]=(f'Games/{folder}/qa/user_capture_20261016/title.png',caption,'runtime',note)
CURATED['psp-death-jr-kr-patch']=('Games/Death Jr/qa/public_title_20261016/title.png','타이틀 · 한글 시작 안내','runtime','기존 PPSSPP 타이틀 캡처. 로고는 원문이며 시작 안내는 한글입니다. 촬영 당시 버전과 최종 배포본의 일치 여부는 확인하지 않았습니다.')
NATIVE_CAPTURES={
 'psp-valhalla-knights-kr-patch':('Valhalla Knights (Korea)','타이틀 · 원문 로고','사용자가 PPSSPP에서 촬영한 발할라 나이츠 전체 타이틀 화면입니다. 로고와 시작 안내는 원문입니다. 촬영 CHD와 최종 배포 결과 ISO의 해시 대조는 수행하지 않았습니다.'),
 'arcade-dark-seal-kr-patch':('Dark Seal','타이틀 · 원문 로고','사용자가 촬영한 FBNeo 타이틀 화면. 설치 패치 7개가 공개 v1.0과 해시 일치하며 타이틀 로고는 원문입니다.'),
 'arcade-dark-seal-2-kr-patch':('Dark Seal','타이틀 · 원문 로고','사용자가 촬영한 FBNeo 타이틀 화면. 현재 설치 패치 9개가 공개 v1.0.3과 해시 일치하며 타이틀 로고는 원문입니다.'),
 'switch-tenshi-no-uta-kr-patch':('Tenshi no Uta','게임 소개·한글 메뉴','사용자가 Citron에서 촬영한 Switch판 게임 소개·한글 메뉴 화면입니다. 현재 설치 패치와 공개 배포본의 일부 컨테이너가 달라 최종 배포본과 동일한 화면으로 확정하지 않았습니다.'),
 'switch-tenshi-no-uta-2-kr-patch':('Tenshi no Uta 2','게임 소개·한글 메뉴','사용자가 Citron에서 촬영한 Switch판 게임 소개·한글 메뉴 화면입니다. 설치 패치와 공개 배포본의 파일별 일치는 대조하지 않았습니다.'),
}
for slug,(folder,caption,note) in NATIVE_CAPTURES.items():
    CURATED[slug]=(f'Games/{folder}/qa/user_public_capture_20261016/{slug}/screen.png',caption,'runtime',note)

def main():
    dest=SITE/'assets/screenshots';dest.mkdir(exist_ok=True)
    records={}
    for slug,(rel,caption,kind,description) in CURATED.items():
        src=PROJECT/rel
        with Image.open(src) as image:
            width,height=image.size
            pixels=image.convert('RGBA').tobytes()
            if slug in NATIVE_CAPTURES:
                dst=dest/(slug+'-capture-20261016.png');shutil.copyfile(src,dst)
            elif slug in USER_CAPTURES:
                dst=dest/(slug+'-user-20261016.png');shutil.copyfile(src,dst)
            elif slug=='psp-death-jr-kr-patch':
                dst=dest/(slug+'-title-20261016.png');shutil.copyfile(src,dst)
            elif src.stat().st_size>200000:
                dst=dest/(slug+'.webp')
                image.save(dst,'WEBP',lossless=True,quality=100,method=6,exact=True)
            else:
                dst=dest/(slug+'.png');shutil.copyfile(src,dst)
        with Image.open(dst) as packed:assert packed.convert('RGBA').tobytes()==pixels
        digest=hashlib.sha256(src.read_bytes()).hexdigest()
        records[slug]=dict(src=dst.relative_to(SITE).as_posix(),caption=caption,kind=kind,width=width,height=height,source=rel,sourceSHA256=digest,assetSHA256=hashlib.sha256(dst.read_bytes()).hexdigest(),pixelSHA256=hashlib.sha256(pixels).hexdigest(),sourceNote=description)
    (SITE/'data/screenshots.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Imported',len(records),'unmodified reviewed images;',sum(r['kind']=='runtime' for r in records.values()),'game captures')

if __name__=='__main__':main()
