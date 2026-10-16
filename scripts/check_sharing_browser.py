"""Real-browser direct-link, clipboard, history and social-metadata verification."""
from pathlib import Path
import argparse,functools,http.server,json,threading
from html.parser import HTMLParser
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
from generate_game_pages import ROOT,render_game_page

class Metadata(HTMLParser):
    def __init__(self):super().__init__();self.tags={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.tags[a.get('property',a.get('name',''))]=a.get('content')
        if tag=='link' and a.get('rel')=='canonical':self.tags['canonical']=a['href']

def main():
    p=argparse.ArgumentParser();p.add_argument('--url');p.add_argument('--channel',default='msedge');p.add_argument('--out',type=Path,default=ROOT/'qa/sharing/local');a=p.parse_args()
    a.out.mkdir(exist_ok=True,parents=True)
    games=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf8'))['games'];by_id={g['id']:g for g in games}
    template=(ROOT/'index.html').read_text(encoding='utf8');server=None
    if a.url:base=a.url.rstrip('/')+'/'
    else:
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                path=urlsplit(self.path).path
                parts=path.strip('/').split('/')
                if len(parts)==2 and parts[0]=='games' and parts[1] in by_id:
                    data=render_game_page(template,by_id[parts[1]],base).encode('utf8')
                    self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                else:super().do_GET()
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
        base=f'http://127.0.0.1:{server.server_address[1]}/';threading.Thread(target=server.serve_forever,daemon=True).start()
    checks=[];errors=[];slug='nes-tom-and-jerry-kr-patch';canonical=base+'games/'+slug+'/'
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel=a.channel,headless=True)
            context=browser.new_context(viewport=dict(width=1440,height=1000),permissions=['clipboard-read','clipboard-write'])
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base,wait_until='networkidle')
            expect(page).to_have_title('akuma815 — 우리들의 작은 게임방')
            expect(page.locator('meta[property="og:title"]')).to_have_attribute('content','akuma815 — 우리들의 작은 게임방')
            expect(page.locator('.brand')).to_contain_text('akuma815')
            expect(page.locator('.footer-brand')).to_have_text('akuma815 우리들의 작은 게임방')
            checks.append('Home/browser/social title and header/footer use lowercase akuma815 and the game-room name')
            page.locator(f'.pack-pick[data-details="{slug}"]').click()
            expect(page).to_have_url(base+'?game='+slug)
            expect(page.locator('#insert-stage')).to_be_visible()
            page.keyboard.press('Tab');expect(page.locator('#skip-insert')).to_be_focused()
            page.keyboard.press('Enter');expect(page.locator('#game-introduction')).to_be_visible()
            expect(page.locator('#close-dialog')).to_be_focused()
            expect(page.locator('#game-share-url')).to_have_value(canonical)
            page.locator('#copy-game-link').click();expect(page.locator('#game-share-feedback')).to_contain_text('링크를 복사했어')
            assert page.evaluate('navigator.clipboard.readText()')==canonical
            checks.append('Card selection updates address; canonical per-game clipboard link; existing skip works')
            page.reload(wait_until='networkidle');expect(page.locator('#details')).to_be_visible();expect(page.locator('#details')).to_have_attribute('data-loading','false')
            expect(page.locator('#dialog-title')).to_have_text('톰과 제리')
            checks.append('Reloading query link restores the game without insertion delay')
            page.goto(canonical,wait_until='networkidle');expect(page.locator('#dialog-title')).to_have_text('톰과 제리')
            expect(page.locator('#dialog-actions a.primary')).to_have_attribute('href',by_id[slug]['release'])
            expect(page.locator('#game-share-url')).to_have_value(canonical)
            assert page.title().startswith('톰과 제리 한글 패치')
            assert page.title().endswith('| akuma815')
            assert page.locator('#details').evaluate('(el)=>el.scrollWidth<=el.clientWidth')
            page.locator('#details').screenshot(path=str(a.out/'desktop-game.png'))
            page.keyboard.press('Escape');expect(page.locator('#details')).not_to_be_visible()
            assert page.url==base+'#catalog'
            page.reload(wait_until='networkidle');expect(page.locator('#details')).not_to_be_visible()
            expect(page).to_have_title('akuma815 — 우리들의 작은 게임방')
            checks.append('Static game address opens correct image and release; Escape returns to catalog and stays closed after reload')
            page.goto(base,wait_until='networkidle');page.locator(f'.pack-pick[data-details="{slug}"]').click()
            page.go_back();expect(page.locator('#details')).not_to_be_visible()
            page.wait_for_timeout(1200);expect(page.locator('#game-introduction')).to_be_hidden()
            page.go_forward();expect(page.locator('#details')).to_be_visible();expect(page.locator('#dialog-title')).to_have_text('톰과 제리')
            checks.append('Browser Back closes and Forward restores the selected game')
            other=next(g for g in games if g['platform']=='GBA')
            page.evaluate('(id)=>window.PATCH_DETAILS.open(id,{instant:true})',other['id'])
            expect(page.locator('#dialog-title')).to_have_text(other['title'])
            page.go_back();expect(page.locator('#dialog-title')).to_have_text('톰과 제리')
            expect(page.locator('[data-community-game]').first).to_have_text('톰과 제리')
            expect(page.locator('#bugs-version')).to_have_value(by_id[slug]['version'])
            checks.append('History switches between two games without stale dialog/community content')
            page.evaluate('Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText:async()=>{throw new Error("denied")}}})')
            page.locator('#copy-game-link').click();expect(page.locator('#game-share-feedback')).to_contain_text('직접 복사')
            assert page.locator('#game-share-url').evaluate('(el)=>el.selectionStart===0 && el.selectionEnd===el.value.length')
            checks.append('Clipboard denial selects the real URL and reports manual-copy fallback')
            page.goto(base+'?game=%3Cscript%3Ebad%3C%2Fscript%3E',wait_until='networkidle')
            expect(page.locator('#details')).not_to_be_visible();expect(page.locator('#game-link-feedback')).to_be_visible()
            assert page.locator('.game-card').count()==len(games)
            checks.append('Unknown/untrusted game ID safely keeps the full catalog')
            for game in games:
                response=page.request.get(base+'games/'+game['id']+'/');assert response.status==200,game['id']
                meta=Metadata();meta.feed(response.text());url=base+'games/'+game['id']+'/'
                assert meta.tags['og:url']==meta.tags['canonical']==url
                assert game['title'] in meta.tags['og:title'] and meta.tags['og:description']==game['description']
                assert meta.tags['og:title'].endswith('| akuma815')
                assert meta.tags['og:site_name']=='akuma815 — 우리들의 작은 게임방'
                if game.get('screenshot'):assert meta.tags['og:image']==base+game['screenshot']['src']
            checks.append(f'All {len(games)} game entry pages have HTTP 200, game-specific canonical/title/description/image metadata')
            mobile=browser.new_context(viewport=dict(width=390,height=844),is_mobile=True,has_touch=True,permissions=['clipboard-read','clipboard-write'])
            m=mobile.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.goto(canonical,wait_until='networkidle')
            expect(m.locator('#dialog-title')).to_have_text('톰과 제리');expect(m.locator('#copy-game-link')).to_be_visible()
            assert m.locator('#details').evaluate('(el)=>el.scrollWidth<=el.clientWidth')
            m.locator('#details').screenshot(path=str(a.out/'mobile-game.png'))
            m.locator('#copy-game-link').click();expect(m.locator('#game-share-feedback')).to_contain_text('링크를 복사했어')
            assert m.evaluate('navigator.clipboard.readText()')==canonical
            checks.append('390px mobile direct link and clipboard button fit without horizontal overflow')
            nojs=browser.new_context(java_script_enabled=False);n=nojs.new_page();n.goto(canonical,wait_until='networkidle')
            expect(n.get_by_role('link',name='이 게임 한글 패치 받기',exact=True)).to_have_attribute('href',by_id[slug]['release'])
            checks.append('JavaScript-disabled entry page retains game-specific patch download and notes')
            browser.close()
    finally:
        if server:server.shutdown();server.server_close()
    assert not errors,errors
    report=dict(status='PASS',url=base,browser=a.channel,games=len(games),checks=checks,javascript_errors=errors)
    (a.out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
