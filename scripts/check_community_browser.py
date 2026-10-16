"""Community UI tests using labelled API fixtures; never submits a GitHub issue."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
FUSION = 'gba-metroid-fusion-kr-patch'
OTHER = 'nds-another-code-kr-patch'


def issue(slug, number, kind, title, body, **extra):
    return dict(number=number, html_url=f'https://github.com/akuma815/{slug}/issues/{number}',
                title=title, body=body, state='open', comments=2, user={'login':'fixture-friend'},
                created_at='2026-10-16T00:00:00Z', labels=[{'name':'site-guestbook' if kind == 'guestbook' else 'site-bug'}], **extra)


def live_readonly(args, output):
    reads = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel=None if args.channel == 'chromium' else args.channel)
        page = browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(args.url,wait_until='networkidle')
        for slug in [FUSION,OTHER]:
            page.locator(f'.pack-pick[data-details="{slug}"]').click()
            for kind in ['guestbook','bugs']:
                with page.expect_response(lambda response: response.url.startswith(f'https://api.github.com/repos/akuma815/{slug}/issues?')) as pending:
                    page.locator('#tab-'+kind).click()
                response = pending.value
                assert response.status == 200, f'public GitHub API: {response.status}'
                posts = response.json()
                assert isinstance(posts,list)
                expected = sum(not row.get('pull_request') and row.get('html_url') == f'https://github.com/akuma815/{slug}/issues/{row.get("number")}' for row in posts)
                expect(page.locator('#'+kind+'-posts > article')).to_have_count(expected)
                page.wait_for_function('(kind)=>!document.querySelector(`[data-board-refresh="${kind}"]`).disabled',arg=kind)
                expect(page.locator('#'+kind+'-status')).to_contain_text(re.compile('개의|아직'))
                reads.append(dict(game=slug,board=kind,status=response.status,posts=expected))
                if slug == FUSION:
                    page.evaluate('document.fonts.ready')
                    page.screenshot(path=str(output/f'{kind}-desktop-live-readonly.png'))
                    page.set_viewport_size({'width':390,'height':844})
                    assert page.locator('#details').evaluate('(el)=>el.scrollWidth<=el.clientWidth')
                    page.screenshot(path=str(output/f'{kind}-mobile-live-readonly.png'))
                    page.set_viewport_size({'width':1440,'height':1000})
            page.keyboard.press('Escape')
        assert not errors,errors
        browser.close()
    result=dict(status='PASS',url=args.url,actual_public_github_reads=reads,page_errors=errors,actual_github_issue_submitted=False)
    (output/'live_readonly_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--channel', default='msedge')
    parser.add_argument('--live-readonly', action='store_true', help='Read actual public boards without fixtures or writes')
    args = parser.parse_args()
    output = ROOT/'qa/community'
    output.mkdir(parents=True, exist_ok=True)
    if args.live_readonly:
        live_readonly(args,output)
        return
    errors = []
    requests = []
    checks = []
    mode = {'value':'normal'}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel=None if args.channel == 'chromium' else args.channel)
        context = browser.new_context(viewport={'width':1440,'height':1000}, reduced_motion='reduce')
        page = context.new_page()
        page.set_default_timeout(10000)
        page.on('pageerror',lambda error:errors.append(str(error)))
        # Record draft navigation and clipboard contents without posting or altering the OS clipboard.
        page.add_init_script('window.__drafts=[];window.open=(url)=>{window.__drafts.push(url);return null};Object.defineProperty(navigator,"clipboard",{value:{writeText:async text=>{window.__copied=text}}});')
        def api(route):
            request = route.request
            requests.append(request.url)
            assert request.method == 'GET' and not request.headers.get('authorization')
            parsed = urlparse(request.url)
            slug = parsed.path.split('/')[3]
            query = parse_qs(parsed.query)
            kind = 'guestbook' if query['labels'][0] == 'site-guestbook' else 'bugs'
            if mode['value'] == 'rate':
                route.fulfill(status=403,json={'message':'API rate limit exceeded'});return
            if mode['value'] == 'offline':
                route.abort('failed');return
            if kind == 'guestbook':
                posts = [issue(slug,1,kind,'[방명록] [테스트] 다시 만나서 반가워!','### 낙서\n\n[테스트 글] 친구랑 나란히 앉아서 하던 기억이 나.\n한글로 다시 만나서 반가워!'),
                         issue(slug,2,kind,'[방명록] [테스트] 글은 글로만 보여 줘','<img src=x onerror="window.__xss=true"><script>window.__xss=true</script>')]
                posts += [dict(issue(slug,3,kind,'unsafe','bad'),html_url='javascript:alert(1)'),
                          dict(issue(slug,4,kind,'pull request','bad'),pull_request={}),
                          issue(slug,5,'bugs','wrong label','must not appear')]
                if query.get('page') == ['2']:
                    posts = [posts[0],issue(slug,6,kind,'[방명록] [테스트] 담벼락 뒷장','다른 낙서도 읽을 수 있어.')]
                if slug == OTHER:
                    posts = [issue(slug,7,kind,'[방명록] [테스트] 어나더 코드의 담벼락','이 글은 다른 게임에 섞이면 안 돼.')]
                headers = {'Link': '<https://api.github.com/next>; rel="next"'} if query.get('page') == ['1'] and slug == FUSION else {}
            else:
                posts = [issue(slug,10,kind,'[버그] [테스트] 메뉴에서 글자가 겹쳐 보여','### 패치 버전\n\nv1.0\n\n### 실행 환경\n\n테스트 기기\n\n### 어떤 일이 있었어?\n\n[테스트 신고] 메뉴에서 글자가 겹쳐 보여.'),
                         dict(issue(slug,11,kind,'[버그] [테스트] 예전에 남긴 신고','[테스트 신고] 닫힌 신고도 함께 읽을 수 있어.'),state='closed')]
                headers = {}
            route.fulfill(json=posts, headers={**headers, 'Access-Control-Allow-Origin':'*','Access-Control-Expose-Headers':'Link'})
        page.route('https://api.github.com/repos/akuma815/*/issues?*',api)
        page.goto(args.url,wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        assert not requests, 'boards should load only when a community tab is selected'
        page.locator(f'.pack-pick[data-details="{FUSION}"]').click()
        expect(page.locator('#panel-intro')).to_be_visible()
        page.locator('#tab-guestbook').click()
        expect(page.locator('.graffiti-note')).to_have_count(2)
        assert page.locator('#guestbook-posts img, #guestbook-posts script').count() == 0
        assert page.evaluate('window.__xss === undefined')
        expect(page.locator('#guestbook-posts')).to_contain_text('<img src=x')
        page.locator('#guestbook-more').click()
        expect(page.locator('.graffiti-note')).to_have_count(3)
        checks.append('label/repository/PR isolation; pagination deduplicates; untrusted HTML is text')
        count = len(requests)
        page.locator('#tab-intro').click();page.locator('#tab-guestbook').click()
        assert len(requests) == count, 'five-minute cache not used'
        page.locator('[data-board-refresh="guestbook"]').click()
        expect(page.locator('.graffiti-note')).to_have_count(2)
        assert len(requests) == count + 1
        page.locator('#guestbook-title').fill('기억을 다시 만났어')
        page.locator('#guestbook-message').fill('친구랑 같이 하던 게임을 한글로 다시 만나서 좋아!')
        page.locator('#guestbook-form button[type=submit]').click()
        parsed = urlparse(page.evaluate('window.__drafts.at(-1)'))
        query = parse_qs(parsed.query)
        assert parsed.netloc == 'github.com' and parsed.path == f'/akuma815/{FUSION}/issues/new'
        assert query['template'] == ['site-guestbook.md'] and 'labels' not in query
        assert '친구랑 같이 하던 게임' in query['body'][0]
        checks.append('site draft opens correct game template; no label permission query; never POSTs')
        page.locator('#guestbook-message').fill('가'*1000)
        count = page.evaluate('window.__drafts.length')
        page.locator('#guestbook-form button[type=submit]').click()
        assert page.evaluate('window.__drafts.length') == count
        expect(page.locator('#guestbook-feedback a')).to_have_attribute('href',f'https://github.com/akuma815/{FUSION}/issues/new?template=site-guestbook.md')
        page.locator('[data-board-copy="guestbook"]').click()
        assert '가'*1000 in page.evaluate('window.__copied')
        page.locator('#guestbook-message').fill('친구랑 같이 하던 기억을 남겨 둬.')
        checks.append('oversized URLs use copy-and-continue flow without silently truncating the draft')
        page.screenshot(path=str(output/'guestbook-form-desktop-fixture.png'))
        page.locator('#details').evaluate('(el)=>el.scrollTop=0')
        page.screenshot(path=str(output/'guestbook-desktop-fixture.png'))
        page.locator('#tab-bugs').click()
        expect(page.locator('.chalk-note')).to_have_count(2)
        expect(page.locator('.chalk-state').nth(1)).to_have_text('닫힌 신고')
        expect(page.locator('#bugs-version')).to_have_value('v1.0')
        page.locator('#bugs-title').fill('메뉴에서 글자가 겹쳐 보여')
        page.locator('#bugs-environment').fill('PPSSPP / 테스트 환경')
        page.locator('#bugs-message').fill('메뉴를 열면 두 줄이 겹쳐 보여.')
        page.locator('#bugs-steps').fill('1. 게임을 켜기\n2. 메뉴 열기')
        page.locator('#bugs-expected').fill('각 줄이 따로 보여야 해.')
        page.locator('#bugs-form button[type=submit]').click()
        query = parse_qs(urlparse(page.evaluate('window.__drafts.at(-1)')).query)
        assert query['template'] == ['site-bug-report.md']
        for value in ['v1.0','PPSSPP / 테스트 환경','두 줄이 겹쳐','2. 메뉴 열기','각 줄이 따로']:
            assert value in query['body'][0]
        page.locator('.chalk-note details').first.evaluate('(el)=>el.open=true')
        page.locator('#details').evaluate('(el)=>el.scrollTop=0')
        page.screenshot(path=str(output/'chalkboard-desktop-fixture.png'))
        checks.append('bug report preserves patch version, environment, symptoms, reproduction and expected behavior')
        mode['value'] = 'rate'
        page.locator('[data-board-refresh="bugs"]').click()
        expect(page.locator('#bugs-status')).to_contain_text('조금 쉬어 달래')
        expect(page.locator('#bugs-all')).to_have_attribute('href',f'https://github.com/akuma815/{FUSION}/issues?q=is%3Aissue%20label%3Asite-bug%20sort%3Acreated-desc')
        mode['value'] = 'offline'
        page.locator('[data-board-refresh="bugs"]').click()
        expect(page.locator('#bugs-status')).to_contain_text('글을 불러오지 못했어')
        mode['value'] = 'normal'
        checks.append('rate-limit/offline states offer direct GitHub reading; existing posts remain')
        page.locator('#tab-intro').focus();page.keyboard.press('ArrowRight')
        expect(page.locator('#tab-guestbook')).to_be_focused()
        expect(page.locator('#panel-guestbook')).to_be_visible()
        page.keyboard.press('End');expect(page.locator('#tab-bugs')).to_be_focused()
        page.keyboard.press('Home');expect(page.locator('#tab-intro')).to_be_focused()
        page.keyboard.press('Escape')
        page.locator(f'.pack-pick[data-details="{OTHER}"]').click()
        page.locator('#tab-guestbook').click()
        expect(page.locator('.graffiti-note')).to_have_count(1)
        expect(page.locator('#guestbook-title')).to_have_value('')
        expect(page.locator('#guestbook-posts')).to_contain_text('어나더 코드의 담벼락')
        page.keyboard.press('Escape')
        page.locator(f'.pack-pick[data-details="{FUSION}"]').click()
        page.locator('#tab-guestbook').click()
        expect(page.locator('#guestbook-title')).to_have_value('기억을 다시 만났어')
        expect(page.locator('#guestbook-message')).to_have_value('친구랑 같이 하던 기억을 남겨 둬.')
        checks.append('keyboard tabs; drafts persist in memory per game and never mix between games')
        # A slow response from a closed game must not overwrite the next game's wall.
        late = issue(FUSION,99,'guestbook','LATE-MUST-NOT-APPEAR','old request')
        page.evaluate('''payload => {
            window.__realFetch = window.fetch;
            window.fetch = (...args) => String(args[0]).includes("/gba-metroid-fusion-kr-patch/issues")
                ? new Promise(resolve => {window.__resolveLate = () => resolve(new Response(JSON.stringify([payload]),{headers:{"Content-Type":"application/json"}}));})
                : window.__realFetch(...args);
        }''',late)
        page.locator('[data-board-refresh="guestbook"]').click()
        page.keyboard.press('Escape')
        page.locator(f'.pack-pick[data-details="{OTHER}"]').click()
        page.locator('#tab-guestbook').click()
        page.evaluate('async () => {window.__resolveLate(); await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));window.fetch=window.__realFetch;}')
        expect(page.locator('#guestbook-posts')).to_contain_text('어나더 코드의 담벼락')
        expect(page.locator('#guestbook-posts')).not_to_contain_text('LATE-MUST-NOT-APPEAR')
        page.keyboard.press('Escape')
        page.locator(f'.pack-pick[data-details="{FUSION}"]').click()
        checks.append('late responses from a closed game cannot overwrite another game')
        for width in [768,390,320]:
            page.set_viewport_size({'width':width,'height':900})
            for kind in ['guestbook','bugs']:
                page.locator('#tab-'+kind).click()
                assert page.locator('#details').evaluate('(el)=>el.scrollWidth<=el.clientWidth'),f'{kind} overflows at {width}'
                if width == 390:
                    page.screenshot(path=str(output/f'{kind}-mobile-fixture.png'))
        checks.append('wall/chalkboard/forms fit 320/390/768px dialogs')
        assert not errors,errors
        browser.close()
    result=dict(status='PASS',url=args.url,checks=checks,api_fixture_requests=len(requests),page_errors=errors,
                actual_github_issue_submitted=False,fixture_posts_publicly_published=False)
    (output/'browser_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
