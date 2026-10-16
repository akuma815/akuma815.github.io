"""Refresh checked public release links; no credentials are written to the catalog."""
from pathlib import Path
import argparse,datetime,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
def gh(path):
    p=subprocess.run(['gh','api',path],capture_output=True,text=True,encoding='utf-8')
    if p.returncode:
        if '404' in p.stderr:return None
        raise RuntimeError('GitHub API failed for '+path+': '+p.stderr)
    return json.loads(p.stdout)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--from-publication',type=Path);ap.add_argument('--verify-remote',action='store_true');args=ap.parse_args()
    if args.from_publication:
        plan=json.loads((args.from_publication/'publication_plan.json').read_text(encoding='utf-8'))
        published=json.loads((args.from_publication/'published.json').read_text(encoding='utf-8'))
        platform={'nes':'NES','ps1':'PS1','psp':'PSP','gba':'GBA','nds':'NDS','arcade':'ARCADE','pc':'PC','switch':'SWITCH','pce':'PCE'}
        data={'checkedAt':'2026-10-16','owner':'akuma815','games':[]}
        for s in plan:
            is_public=s['slug'] in published
            english=s['folder'].strip()
            if s['method']=='darksealj':english='Dark Seal'
            if s['method']=='darkseal2':english='Dark Seal 2'
            data['games'].append(dict(id=s['slug'],title=s['title'],english=english,platform=platform[s['slug'].split('-')[0]],description=s['about'],version=s['tag'],available=is_public,repository=s['url'] if is_public else None,release=published[s['slug']]['release_url'] if is_public else None,notes=s['notes']))
    else:data=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    if args.verify_remote:
        for game in data['games']:
            repo=gh('repos/akuma815/'+game['id'])
            if not repo or repo.get('private'):
                game.update(available=False,repository=None,release=None);continue
            releases=gh('repos/akuma815/'+game['id']+'/releases')
            release=next((r for r in releases if not r['draft'] and r['assets']),None)
            game.update(available=bool(release),repository=repo['html_url'] if release else None,release=release['html_url'] if release else None)
            if release:game['version']=release['tag_name']
        data['checkedAt']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    media_path=ROOT/'data/screenshots.json'
    media=json.loads(media_path.read_text(encoding='utf-8')) if media_path.exists() else {}
    for game in data['games']:
        if game['id'] in media:game['screenshot']=media[game['id']]
    target=ROOT/'data';target.mkdir(exist_ok=True)
    text=json.dumps(data,ensure_ascii=False,indent=2)
    (target/'catalog.json').write_text(text+'\n',encoding='utf-8')
    (target/'catalog.js').write_text('window.PATCH_CATALOG = '+text+';\n',encoding='utf-8')
    print(len(data['games']),'games,',sum(g['available'] for g in data['games']),'public releases')

if __name__=='__main__':main()
