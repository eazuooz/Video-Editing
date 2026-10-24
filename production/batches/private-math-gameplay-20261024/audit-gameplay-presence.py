"""Audit delivered pixels and time accounting; never render or alter a master."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime, hashlib, json, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

B = Path(__file__).resolve().parent
R = B.parents[2]
A = R / 'shared/output/private-math-gameplay-20261024/presence-audit'
A.mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text('utf-8-sig'))
def rel(p): return p.resolve().relative_to(R).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**20), b''): h.update(b)
    return h.hexdigest()
def stamp(t):
    return f'{int(t)//60:02}:{t%60:05.2f}'
manifest=read(B/'delivery-manifest.json')
original={e['id']:e for e in read(B/'edit-list-audit.json')['entries']}
names={'totk':'The Legend of Zelda: Tears of the Kingdom','besiege':'Besiege','dorf':'Dorfromantik','se2':'Space Engineers 2'}
entries=[]
jobs=[]
for delivery in manifest['entries']:
    slug=Path(delivery['index']).parent.name.removesuffix('-gameplay-v3')
    P=R/'projects'/slug/'production'
    timeline=read(P/'concept-fit-v2/timeline.json')
    slots={s['id']:s for s in timeline['scenes']}
    cap=next(f for f in delivery['outputs'] if f['path'].endswith('.captioned.mp4'))
    master=R/cap['path']
    index=R/delivery['index']
    src=re.search(r'<video\b[^>]*\bsrc="([^"]+)"',index.read_text('utf8'))[1]
    resolved=(index.parent/src).resolve()
    e=dict(id=delivery['id'],title=delivery['title'],slug=slug,master=cap['path'],sha256=sha(master),
           expectedSha256=cap['sha256'],index=delivery['index'],indexPointsToMaster=resolved==master.resolve(),
           seconds=timeline['seconds'],shots=[],pixelReview='pending',scope='latest delivered captioned master')
    assert e['sha256']==cap['sha256']
    planfile=B/(e['id'].lower()+'-gameplay-plan.json')
    if planfile.exists():
        plan=read(planfile)
        for i,p in enumerate(plan['patches']):
            at=slots[p['scene']]['start']+p['offset']; start=at; segments=[]
            for s in p['segments']:
                segments.append(dict(kind=s['kind'],start=at,end=at+s['seconds'],seconds=s['seconds'],sourceIn=s['in']))
                at+=s['seconds']
            e['shots'].append(dict(scene=p['scene'],title=p['title'],game=plan['sources'][p['source']]['game'],
                source=plan['sources'][p['source']]['path'],start=start,end=at,segments=segments))
    else:
        for p in original[e['id']]['shots']:
            at=slots[p['scene']]['start']+p['offset']
            e['shots'].append(dict(scene=p['scene'],title=p['title'],game=names.get(p['source'],p['source']),
                start=at,end=at+p['seconds'],segments=[dict(kind='motion',start=at,end=at+p['seconds'],seconds=p['seconds'],sourceIn=p['sourceIn'])]))
    motion=[s for p in e['shots'] for s in p['segments'] if s['kind']=='motion']
    e['nativeSeconds']=round(sum(s['seconds'] for s in motion),3)
    e['stillSeconds']=round(sum(s['seconds'] for p in e['shots'] for s in p['segments'] if s['kind']=='still'),3)
    e['nativePercentOfFullVideo']=round(e['nativeSeconds']/e['seconds']*100,2)
    e['shortMotionSegmentsUnder5s']=sum(s['seconds']<5 for s in motion)
    e['longestMotionSeconds']=max((s['seconds'] for s in motion),default=0)
    e['firstMotionStart']=min((s['start'] for s in motion),default=None)
    e['lastMotionEnd']=max((s['end'] for s in motion),default=None)
    ordered=sorted(motion,key=lambda s:s['start'])
    e['longestGameFreeGapSeconds']=max([ordered[0]['start']]+[b['start']-a['end'] for a,b in zip(ordered,ordered[1:])]+[e['seconds']-ordered[-1]['end']]) if ordered else e['seconds']
    for i,p in enumerate(e['shots']):
        p['samples']=[]
        for j,s in enumerate(p['segments']):
            if s['kind']!='motion': continue
            for q in [.2,.8]:
                at=s['start']+s['seconds']*q
                path=A/f'{e["id"]}-{i:02}-{j:02}-{int(q*10)}.jpg'
                p['samples'].append(dict(at=at,path=rel(path),segment=j))
                jobs.append((master,at,path))
    entries.append(e)
def extract(job):
    master,at,path=job
    subprocess.run(['ffmpeg','-v','error','-threads','1','-ss',str(at),'-i',str(master),'-frames:v','1','-vf','scale=960:540','-q:v','3','-y',str(path)],check=True)
    return path
with ThreadPoolExecutor(max_workers=3) as pool:
    for _ in pool.map(extract,jobs): pass
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
for e in entries:
    frames=[]
    for i,p in enumerate(e['shots']):
        for sample in p['samples']:
            frames.append((sample,f'{i+1}. {p["game"]} | {stamp(sample["at"])}'))
        differences=[]
        for j in sorted(set(x['segment'] for x in p['samples'])):
            pair=[x for x in p['samples'] if x['segment']==j]
            images=[Image.open(R/x['path']).crop((0,65,640,425)).convert('RGB') for x in pair]
            differences.append(dict(segment=j,leftPaneMeanAbsoluteDifference=round(sum(ImageStat.Stat(ImageChops.difference(*images)).mean)/3,3)))
        p['motionPixelDifferences']=differences
    e['contactSheets']=[]
    for batch in range(0,len(frames),8):
        subset=frames[batch:batch+8];sheet=Image.new('RGB',(1280,396*((len(subset)+1)//2)),(18,20,21));d=ImageDraw.Draw(sheet)
        for k,(sample,label) in enumerate(subset):
            x=(k%2)*640;y=(k//2)*396
            d.text((x+8,y+5),label,font=font,fill='white')
            im=Image.open(R/sample['path']).resize((640,360));sheet.paste(im,(x,y+34))
        out=A/f'{e["id"]}-sheet-{batch//8}.jpg';sheet.save(out,quality=90);e['contactSheets'].append(rel(out))
    print(e['id'], 'native',e['nativeSeconds'],'/',round(e['seconds'],2),'still',e['stillSeconds'],'short',e['shortMotionSegmentsUnder5s'],'index',e['indexPointsToMaster'],flush=True)
report=dict(recordedAt=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
    request='전수조사해서 없는영상 다 찾아줘',method='Hash and index destination validation; two decoded final-master samples inside every scheduled native-motion segment; left game-pane pixel change. Human-visible sample inspection is recorded separately; metadata is not treated as proof of teaching sufficiency.',
    noNewRender=True,noMasterModified=True,thresholdNote='Under five seconds is a diagnostic flag, not an automatic pedagogical fail/pass. Still frames and self-authored models are excluded from native gameplay duration.',
    entries=entries,pixelReviewComplete=False)
(B/'gameplay-presence-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Extracted final-master samples:',len(jobs),flush=True)
