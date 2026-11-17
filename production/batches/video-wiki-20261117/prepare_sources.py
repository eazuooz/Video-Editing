"""Resolve approved lesson text and retained full-resolution frame evidence."""
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path('D:/Github/VideoEditing'); HERE=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def parse_srt(p):
    result=[]
    for b in Path(p).read_text(encoding='utf-8-sig').replace('\r','').strip().split('\n\n'):
        lines=b.splitlines();time=next((i for i,s in enumerate(lines) if '-->' in s),None)
        if time is None:continue
        hh,mm,ss=map(float,lines[time].split(' --> ')[0].replace(',','.').split(':'))
        result.append(dict(seconds=hh*3600+mm*60+ss,text=' '.join(lines[time+1:])))
    return result

def source(row,anim):
    out=dict(id=row['id'],slug=row['slug'],series=row['series'],title=row['title'],videoId=row.get('videoId'))
    project=ROOT/'projects'/row['slug'];srt=None;frames=None
    if row['id'] in anim:
        ep=anim[row['id']]
        srt=next((Path(f['path']) for f in ep['files'] if f['kind']=='ko.srt' and Path(f['path']).is_file()),None)
        framefile=Path('C:/Users/1/Videos/YamyamProduction/animation-gameplay-v8')/row['id']/'encoded-qa/frames.json'
        if framefile.exists():frames=rd(framefile)
    media=row['sourceEvidence'].get('currentMediaCandidates',[])
    if srt is None:
        srt=next((Path(f['resolved']) for f in media if f['exists'] and f['path'].endswith('.srt') and not f['path'].endswith('en.srt')),None)
    if srt is None:
        p=ROOT/'projects'/row['slug']/'publishing/youtube-upload.json'
        if p.exists():
            receipt=rd(p);original=receipt.get('approvedFile')
            if original:
                candidates=[Path(original).parent/'captions.ko.srt',Path(original).parent/'ko.srt']
                srt=next((p for p in candidates if p.is_file()),None)
    if srt is not None:
        out.update(textSource=str(srt),textSourceSha256=hashlib.sha256(srt.read_bytes()).hexdigest(),cues=parse_srt(srt))
    # Scene source is retained alongside exact caption text, so chapter semantics can be reviewed.
    scripts=[Path(p) for p in row['sourceEvidence'].get('scriptCandidates',[]) if p.endswith('narration.ko.json')]
    manifest=project/'project.json';proj=rd(manifest) if manifest.exists() else {}
    revision=proj.get('finalRender',{}).get('revision')
    if revision and (project/'production'/revision/'narration.ko.json').exists():scripts.insert(0,project/'production'/revision/'narration.ko.json')
    if not scripts:
        scripts=[Path(p) for p in row['sourceEvidence'].get('scriptCandidates',[]) if not p.endswith('.en.json')]
    if scripts:
        p=scripts[0];data=rd(p)
        out.update(sceneSource=str(p),sceneSourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),sceneDocument=data)
    if frames:
        out['retainedFrameEvidence']=frames
    if not out.get('cues') and not out.get('sceneDocument'):
        out['status']='original-video-transcript-needed'
    else:out['status']='text-resolved-for-editorial-review'
    return out

def subtitle(row):
    dest=HERE/'evidence/captions';dest.mkdir(exist_ok=True)
    prefix=dest/row['id']
    existing=list(dest.glob(row['id']+'.*.vtt'))
    if existing:return dict(id=row['id'],status='available',files=[str(p) for p in existing])
    cmd=['yt-dlp','--quiet','--no-progress','--no-warnings','--skip-download','--write-subs','--write-auto-subs',
         '--sub-langs','ko,ko-orig,en,en-orig','--sub-format','vtt','--no-playlist','--retries','1',
         '-o',str(prefix)+'.%(ext)s','https://www.youtube.com/watch?v='+row['videoId']]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True)
    files=list(dest.glob(row['id']+'.*.vtt'))
    error=p.stderr.decode('utf8',errors='replace')
    status='available' if files else ('rate-limited' if '429' in error else 'subtitle-retrieval-unavailable')
    return dict(id=row['id'],status=status,returnCode=p.returncode,files=[str(p) for p in files])

def main():
    inv=rd(HERE/'inventory.json')
    a=rd(ROOT/'production/batches/animation-18-20261031/gameplay-v8/delivery-review-manifest.json')
    anim={e['id']:e for e in a['episodes']}
    rows=[source(r,anim) for r in inv['rows']]
    wr(HERE/'sources.json',dict(status='editorial-review-pending',rows=rows))
    needed=[r for r in rows if r['status']=='original-video-transcript-needed' and r.get('videoId')]
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(subtitle,needed):
            results.append(result)
            wr(HERE/'transcript-progress.json',dict(total=len(needed),completed=len(results),rows=results))
            print(result['id'],result['status'],flush=True)
    print('Text source map saved:',len(rows),'items;',len(needed),'public transcript lookups.')

if __name__=='__main__':main()
