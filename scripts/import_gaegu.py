"""Package full Gaegu regular/bold fonts as WOFF2 from a pinned upstream commit."""
from io import BytesIO
import hashlib,json,urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM='https://api.github.com/repos/google/fonts/commits?path=ofl/gaegu&per_page=1'


def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'akuma815-patch-archive'})
    with urllib.request.urlopen(request,timeout=45) as response:return response.read()


def main():
    target=ROOT/'assets/fonts/gaegu';target.mkdir(parents=True,exist_ok=True)
    manifest_path=target/'manifest.json'
    existing=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    commit=existing['upstreamCommit'] if existing else json.loads(fetch(UPSTREAM))[0]['sha']
    base='https://raw.githubusercontent.com/google/fonts/'+commit+'/ofl/gaegu/'
    license_data=fetch(base+'OFL.txt');assert b'SIL OPEN FONT LICENSE Version 1.1' in license_data
    (target/'OFL.txt').write_bytes(license_data)
    records=[]
    for style in ['Regular','Bold']:
        source=fetch(base+'Gaegu-'+style+'.ttf')
        font=TTFont(BytesIO(source),recalcTimestamp=False)
        assert font['name'].getDebugName(1)=='Gaegu'
        original_cmap=font.getBestCmap();font.flavor='woff2'
        packed=target/('Gaegu-'+style+'.woff2');font.save(packed)
        reloaded=TTFont(packed);assert reloaded.getBestCmap()==original_cmap
        # Compression must preserve glyph outlines and layout/metric tables.
        for table in ['glyf','hmtx','cmap','GPOS','GSUB']:
            if table in font:assert font[table].compile(font)==reloaded[table].compile(reloaded),table
        records.append({'style':style,'weight':400 if style=='Regular' else 700,'sourceUrl':base+'Gaegu-'+style+'.ttf','sourceSHA256':hashlib.sha256(source).hexdigest(),'file':packed.name,'bytes':packed.stat().st_size,'sha256':hashlib.sha256(packed.read_bytes()).hexdigest(),'glyphs':len(original_cmap)})
        print(style,len(source),'->',packed.stat().st_size,'bytes',flush=True)
    manifest={'family':'Gaegu','designer':'JIKJI SOFT','license':'SIL OFL 1.1','upstreamCommit':commit,'licenseSHA256':hashlib.sha256(license_data).hexdigest(),'conversion':'Full font WOFF2 compression; no glyph subsetting or outline changes.','fonts':records}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
