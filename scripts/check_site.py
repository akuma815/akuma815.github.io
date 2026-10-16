"""Static and DOM-emulated interaction checks; these do not replace browser QA."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
import quickjs

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
    assert len({g['id'] for g in catalog['games']})==len(catalog['games'])
    for g in catalog['games']:
        assert g['title'] and g['description'] and isinstance(g['notes'],list)
        if g['available']:
            assert g['repository']=='https://github.com/akuma815/'+g['id']
            assert g['release'].startswith(g['repository']+'/releases/tag/')
        else:assert g['repository'] is None and g['release'] is None
    ctx=quickjs.Context()
    ctx.eval('''
    var window=globalThis;
    var elements={}; var platformButtons=[];
    function element(id){return elements[id]||(elements[id]={id:id,innerHTML:"",textContent:"",hidden:false,value:"",checked:false,handlers:{},addEventListener:function(event,fn){this.handlers[event]=fn},setAttribute:function(k,v){this[k]=v},showModal:function(){this.open=true},close:function(){this.open=false;if(this.handlers.close)this.handlers.close()},focus:function(){this.focused=true}})};
    var document={getElementById:element,querySelectorAll:function(){return platformButtons}};
    function fire(id,event,value){var e=element(id);if(event==="input"||event==="change"){if(typeof value==="boolean")e.checked=value;else e.value=value}e.handlers[event]({target:e});}
    function cards(){return (element("games").innerHTML.match(/class="game-card"/g)||[]).length;}
    function choose(p){element("filters").handlers.click({target:{closest:function(){return {dataset:{platform:p}}}}});}
    function detail(id){element("games").handlers.click({target:{closest:function(){return {dataset:{details:id},focus:function(){}}}}});}
    ''')
    ctx.eval((ROOT/'data/catalog.js').read_text(encoding='utf-8'))
    ctx.eval((ROOT/'assets/app.js').read_text(encoding='utf-8'))
    assert ctx.eval('cards()')==len(catalog['games'])
    assert ctx.eval('element("catalog-summary").textContent')=='배포 중 9개 · 등록 준비 10개'
    ctx.eval('fire("search","input","메트로이드")');assert ctx.eval('cards()')==2
    ctx.eval('fire("search","input","Another Code")');assert ctx.eval('cards()')==1
    ctx.eval('fire("search","input","no-such-game-815")');assert ctx.eval('cards()')==0 and not ctx.eval('element("empty").hidden')
    ctx.eval('fire("empty-reset","click")');assert ctx.eval('cards()')==19
    ctx.eval('choose("GBA")');assert ctx.eval('cards()')==2
    ctx.eval('choose("PSP")');assert ctx.eval('cards()')==3
    ctx.eval('fire("available-only","change",true)');assert ctx.eval('cards()')==1
    ctx.eval('fire("reset","click")');assert ctx.eval('cards()')==19
    ctx.eval('fire("available-only","change",true)');assert ctx.eval('cards()')==9
    ctx.eval('fire("reset","click");detail("gba-metroid-fusion-kr-patch")');assert ctx.eval('element("details").open')
    assert ctx.eval('element("dialog-actions").innerHTML.includes("releases/tag/v1.0")')
    ctx.eval('fire("close-dialog","click")');assert not ctx.eval('element("details").open')
    ctx.eval('detail("psp-prinny-kr-patch")');assert ctx.eval('element("dialog-actions").innerHTML.includes("등록 후")')
    assert not ctx.eval('element("dialog-actions").innerHTML.includes("href")')
    ctx.eval('fire("close-dialog","click");fire("search","input","<img onerror=alert(1)>")');assert ctx.eval('cards()')==0
    result=dict(status='PASS',games=19,public_releases=9,checks=['HTML IDs and assets','catalog schema and safe links','Korean/English search','platform and availability filters','empty state and reset','available/pending details','dialog open and close','HTML search input'],visual_browser_qa='NOT_PERFORMED_NO_CONNECTED_BROWSER')
    (ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa/checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
