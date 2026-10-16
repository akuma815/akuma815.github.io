"""Generate per-game entry pages with crawler-visible sharing metadata."""
from pathlib import Path
import argparse,html,json,re
from urllib.parse import urljoin

ROOT=Path(__file__).resolve().parents[1]
SITE_URL='https://akuma815.github.io/'
def render_game_page(template,game,site_url=SITE_URL):
    slug=game['id']
    if not re.fullmatch(r'[a-z0-9-]+',slug):raise ValueError('Invalid game ID: '+slug)
    esc=lambda v:html.escape(str(v),quote=True)
    title=f"{game['title']} 한글 패치 {'작업 중 · ' if game.get('status')=='in-progress' else ''}{game['version']} | akuma815"
    url=urljoin(site_url.rstrip('/')+'/',f'games/{slug}/')
    text=template.replace('<head>','<head>\n  <base href="../../">',1)
    text,n=re.subn(r'<title>.*?</title>',lambda _:f'<title>{esc(title)}</title>',text,count=1);assert n==1
    for pattern,replacement in [
        (r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{esc(game["description"])}">'),
        (r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{esc(title)}">'),
        (r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{esc(game["description"])}">')]:
        text,n=re.subn(pattern,lambda _:replacement,text,count=1);assert n==1
    tags=[f'<link rel="canonical" href="{esc(url)}">',f'<meta property="og:url" content="{esc(url)}">',
          f'<meta name="twitter:title" content="{esc(title)}">',f'<meta name="twitter:description" content="{esc(game["description"])}">']
    image=game.get('screenshot')
    if image and re.fullmatch(r'assets/screenshots/[a-z0-9-]+\.(png|webp)',image['src']):
        image_url=urljoin(site_url.rstrip('/')+'/',image['src'])
        tags.extend([f'<meta property="og:image" content="{esc(image_url)}">',f'<meta property="og:image:alt" content="{esc(game["title"])} — {esc(image["caption"])}">',
                     f'<meta property="og:image:width" content="{int(image["width"])}">',f'<meta property="og:image:height" content="{int(image["height"])}">',
                     '<meta name="twitter:card" content="summary_large_image">',f'<meta name="twitter:image" content="{esc(image_url)}">'])
    else:tags.append('<meta name="twitter:card" content="summary">')
    text=text.replace('</head>','  '+'\n  '.join(tags)+'\n</head>',1)
    fallback=f'<noscript><section><h2>{esc(title)}</h2><p>{esc(game["description"])}</p><ul>'+''.join(f'<li>{esc(note)}</li>' for note in game['notes'])+'</ul>'
    if game['available'] and re.fullmatch(r'https://github\.com/akuma815/[a-z0-9-]+/releases/tag/[A-Za-z0-9._-]+',game.get('release','')):
        fallback+=f'<a href="{esc(game["release"])}">{"작업 중인 시험판 보기" if game.get("status")=="in-progress" else "이 게임 한글 패치 받기"}</a>'
    fallback+='</section></noscript>'
    text,n=re.subn(r'<noscript>.*?</noscript>',lambda _:fallback,text,count=1,flags=re.S);assert n==1
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'_site');p.add_argument('--site-url',default=SITE_URL);a=p.parse_args()
    template=(ROOT/'index.html').read_text(encoding='utf8');catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf8'))
    for game in catalog['games']:
        target=a.out/'games'/game['id']/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(render_game_page(template,game,a.site_url),encoding='utf8',newline='\n')
    print(f'Generated {len(catalog["games"])} per-game sharing pages')
if __name__=='__main__':main()
