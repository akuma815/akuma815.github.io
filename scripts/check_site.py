"""Static and DOM-emulated interaction checks; these do not replace browser QA."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import json,re
import quickjs
from PIL import Image
from generate_game_pages import render_game_page

ROOT=Path(__file__).resolve().parents[1]
class HTMLCheck(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.assets=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='script' and 'src' in a:self.assets.append(a['src'])
        if tag=='link' and a.get('rel') in {'stylesheet','icon'}:self.assets.append(a['href'])

def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8');p=HTMLCheck();p.feed(html)
    assert len(p.ids)==len(set(p.ids)),'Duplicate HTML IDs'
    assert '\ufffd' not in html and '<html lang="ko">' in html
    for src in p.assets:assert (ROOT/src).is_file(),src
    catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    browser_catalog=(ROOT/'data/catalog.js').read_text(encoding='utf-8')
    assert browser_catalog.startswith('window.PATCH_CATALOG = ') and browser_catalog.endswith(';\n')
    assert json.loads(browser_catalog[len('window.PATCH_CATALOG = '):-2])==catalog,'Browser catalog differs from JSON'
    total=len(catalog['games']);public=sum(g['available'] for g in catalog['games'])
    assert len({g['id'] for g in catalog['games']})==len(catalog['games'])
    for g in catalog['games']:
        assert g['title'] and g['description'] and isinstance(g['notes'],list)
        if g['available']:
            assert g['repository']=='https://github.com/akuma815/'+g['id']
            assert g['release'].startswith(g['repository']+'/releases/tag/')
        else:assert g['repository'] is None and g['release'] is None
        if g.get('screenshot'):
            image=g['screenshot'];f=ROOT/image['src']
            assert f.is_file()
            assert hashlib.sha256(f.read_bytes()).hexdigest()==image.get('assetSHA256',image['sourceSHA256'])
            if image.get('pixelSHA256'):
                with Image.open(f) as im:assert hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()==image['pixelSHA256']
            assert image['kind'] in {'runtime','graphics','video'} and image['sourceNote']
        shared=render_game_page(html,g)
        parsed=HTMLCheck();parsed.feed(shared)
        assert len(parsed.ids)==len(set(parsed.ids))
        assert '<base href="../../">' in shared
        assert f'/games/{g["id"]}/' in shared and '<link rel="canonical"' in shared
        assert '<meta property="og:url"' in shared
        assert '<meta property="og:image"' in shared if g.get('screenshot') else True
    ctx=quickjs.Context()
    ctx.eval('new Function('+json.dumps((ROOT/'assets/community.js').read_text(encoding='utf-8'))+')')
    ctx.eval('new Function('+json.dumps((ROOT/'assets/sharing.js').read_text(encoding='utf-8'))+')')
    ctx.eval('''
    var window=globalThis;
    var elements={}; var platformButtons=[];
    var nextTimer=0; var timers={}; var reducedMotion=false;
    window.setTimeout=function(fn){timers[++nextTimer]=fn;return nextTimer};
    window.clearTimeout=function(id){delete timers[id]};
    window.matchMedia=function(){return {matches:reducedMotion}};
    function flushTimers(){var pending=timers;timers={};Object.values(pending).forEach(function(fn){fn()})};
    function element(id){return elements[id]||(elements[id]={id:id,innerHTML:"",textContent:"",hidden:false,value:"",checked:false,dataset:{},handlers:{},addEventListener:function(event,fn){this.handlers[event]=fn},setAttribute:function(k,v){this[k]=v},showModal:function(){this.open=true},close:function(){this.open=false;if(this.handlers.close)this.handlers.close()},focus:function(){this.focused=true;document.activeElement=this}})};
    var document={getElementById:element,querySelectorAll:function(){return platformButtons}};
    function fire(id,event,value){var e=element(id);if(event==="input"||event==="change"){if(typeof value==="boolean")e.checked=value;else e.value=value}e.handlers[event]({target:e});}
    function cards(){return (element("games").innerHTML.match(/class="game-card"/g)||[]).length;}
    function choose(p){element("filters").handlers.click({target:{closest:function(){return {dataset:{platform:p}}}}});}
    function detail(id){element("games").handlers.click({target:{closest:function(){return {dataset:{details:id},focus:function(){}}}}});}
    ''')
    ctx.eval((ROOT/'data/catalog.js').read_text(encoding='utf-8'))
    ctx.eval((ROOT/'assets/app.js').read_text(encoding='utf-8'))
    assert ctx.eval('cards()')==len(catalog['games'])
    assert ctx.eval('(element("games").innerHTML.match(/<img /g)||[]).length')==sum(bool(g.get('screenshot')) for g in catalog['games'])
    assert ctx.eval('(element("games").innerHTML.match(/class="pack-pick"/g)||[]).length')==total
    assert ctx.eval('element("games").innerHTML.includes("media-advance") && element("games").innerHTML.includes("media-disc")')
    assert ctx.eval('element("catalog-summary").textContent')==f'지금 받을 수 있는 패치 {public}개 · 등록 준비 {total-public}개'
    ctx.eval('fire("search","input","메트로이드")');assert ctx.eval('cards()')==2
    ctx.eval('fire("search","input","Another Code")');assert ctx.eval('cards()')==1
    ctx.eval('fire("search","input","no-such-game-815")');assert ctx.eval('cards()')==0 and not ctx.eval('element("empty").hidden')
    ctx.eval('fire("empty-reset","click")');assert ctx.eval('cards()')==total
    ctx.eval('choose("GBA")');assert ctx.eval('cards()')==2
    ctx.eval('choose("PSP")');assert ctx.eval('cards()')==3
    ctx.eval('fire("available-only","change",true)');assert ctx.eval('cards()')==sum(g['platform']=='PSP' and g['available'] for g in catalog['games'])
    ctx.eval('fire("reset","click")');assert ctx.eval('cards()')==total
    ctx.eval('fire("available-only","change",true)');assert ctx.eval('cards()')==public
    ctx.eval('fire("reset","click");detail("gba-metroid-fusion-kr-patch")');assert ctx.eval('element("details").open')
    assert ctx.eval('element("insert-pack").innerHTML.includes("media-advance")')
    assert ctx.eval('element("game-introduction").hidden && !element("insert-stage").hidden')
    assert ctx.eval('element("details").dataset.loading')=='true'
    ctx.eval('flushTimers()')
    assert ctx.eval('!element("game-introduction").hidden && element("insert-stage").hidden')
    assert ctx.eval('element("details").dataset.loading')=='false'
    assert not ctx.eval('element("dialog-media").hidden')
    assert ctx.eval('element("dialog-media").innerHTML.includes("assets/screenshots/gba-metroid-fusion-kr-patch.png")')
    assert ctx.eval('element("dialog-actions").innerHTML.includes("releases/tag/v1.0")')
    ctx.eval('fire("close-dialog","click")');assert not ctx.eval('element("details").open')
    # Closing before insertion finishes must cancel the timer and restore focus.
    ctx.eval('detail("gba-metroid-fusion-kr-patch");fire("close-dialog","click");flushTimers()')
    assert not ctx.eval('element("details").open') and ctx.eval('element("game-introduction").hidden')
    assert ctx.eval('element("insert-pack").innerHTML')==''
    # Users can skip; focus cannot be left on a hidden skip button.
    ctx.eval('detail("gba-metroid-fusion-kr-patch");element("skip-insert").focus();fire("skip-insert","click")')
    assert not ctx.eval('element("game-introduction").hidden')
    assert ctx.eval('document.activeElement===element("close-dialog")')
    ctx.eval('fire("close-dialog","click");reducedMotion=true;detail("gba-metroid-fusion-kr-patch")')
    assert not ctx.eval('element("game-introduction").hidden')
    assert ctx.eval('Object.keys(timers).length')==0
    ctx.eval('fire("close-dialog","click");reducedMotion=false')
    pending=next((g for g in catalog['games'] if not g['available']),None)
    if pending:
        ctx.eval('detail('+json.dumps(pending['id'])+')');assert ctx.eval('element("dialog-actions").innerHTML.includes("등록 후")')
        assert not ctx.eval('element("dialog-actions").innerHTML.includes("href")')
    ctx.eval('fire("close-dialog","click");fire("search","input","<img onerror=alert(1)>")');assert ctx.eval('cards()')==0
    result=dict(status='PASS',games=total,public_releases=public,checks=['HTML IDs and assets','catalog schema and safe links','Korean/English search','platform and availability filters','empty state and reset','available/pending details','dialog open and close','HTML search input','platform cartridge cards','insertion before introduction','close cancels insertion','skip restores visible focus','reduced motion skips insertion'],visual_browser_qa='NOT_PERFORMED_BY_THIS_SCRIPT')
    (ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa/checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
