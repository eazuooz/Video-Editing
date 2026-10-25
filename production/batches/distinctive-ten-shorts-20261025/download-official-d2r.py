"""Download the publisher's explicitly offered gameplay B-roll, without login."""
from pathlib import Path
import hashlib, json, requests, subprocess, time
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
L=B/'local/d2r-official'; L.mkdir(parents=True,exist_ok=True)
url='https://blizzard.gamespress.com/en/Kit/Details/Diablo-II-Resurrected-Launch-Press-Kit'
dest=L/'D2R_Launch_Broll_.mp4'
session=requests.Session()
response=session.get(url,timeout=40);response.raise_for_status()
soup=BeautifulSoup(response.text,'html.parser')
entry=soup.find('input',{'data-filename':dest.name})
assert entry, 'Expected public B-roll entry not found'
node=entry.find_parent('div',class_='tn-inner').find('i',attrs={'data-preview':True})
expected=int(entry['data-filesize'])
if not dest.exists():
    partial=dest.with_suffix('.mp4.partial')
    offset=partial.stat().st_size if partial.exists() else 0
    assert offset<expected, 'Inspect already complete partial before retry'
    with session.get(node['data-preview'],headers={'Range':f'bytes={offset}-'} if offset else {},stream=True,timeout=(30,90)) as stream:
        stream.raise_for_status()
        if offset:
            assert stream.status_code==206 and stream.headers.get('Content-Range','').startswith(f'bytes {offset}-'), 'Server did not honor exact resume; preserve partial'
        completed=offset; last=time.monotonic()
        with partial.open('ab' if offset else 'xb') as f:
            for block in stream.iter_content(4*1024*1024):
                if block: f.write(block); completed+=len(block)
                if time.monotonic()-last>20:
                    print('Official B-roll bytes',completed,'/',expected,flush=True);last=time.monotonic()
    assert partial.stat().st_size==expected
    partial.rename(dest)
assert dest.stat().st_size==expected
h=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert v['width']>=1920 and v['height']>=1080
record=dict(sourceUrl=url,publisher='Blizzard Entertainment',distribution='Official gameplay B-roll in launch press kit',
    sourceKind='independent-publisher-gameplay',path=dest.relative_to(R).as_posix(),bytes=expected,sha256=h,
    width=v['width'],height=v['height'],fps=v['r_frame_rate'],duration=probe['format']['duration'],
    actualViewing='pending',usageTerms='publisher media-use terms separately reviewed before production selection')
(L/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False),flush=True)
