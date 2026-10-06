"""One CPU worker for silent encoded-white inputs, boss90frames and new Pedro cue edges."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math,subprocess,os,argparse
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
write=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
a=argparse.ArgumentParser();a.add_argument('--resource',required=True);args=a.parse_args()
r=read(ROOT/args.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
s_path=BASE/'word-action-source-candidate-v4.json';s=read(s_path)
c_path=BASE/'word-caption-candidate-v3/captions.json';caption=read(c_path)
w_path=ROOT/'motion-canvas/src/projects/familiar-game-rules/timed-white-reel-plan-v1.json';white=read(w_path)
w_ver=read(PROOF/'timed-white-input-verification-v1.json')
assert w_ver['frames']==9140 and w_ver['fullDecodeExitCode']==0
cutlist=[c for p in s['pieces'] for c in p['selectedSourceCuts']]
boss=next(c for c in cutlist if c['id']=='06-part3-cut07')
pedro=next(c for c in cutlist if c['id']=='10-part2-cut01')
white_path=ROOT/w_ver['output'];assert sha(white_path)==w_ver['sha256']
out=ROOT/'shared/output/familiar-game-rules/research/white-boss-pedro-input-v4'
state_path=PROOF/'white-boss-pedro-input-execution-v4.json';assert not out.exists() and not state_path.exists()
(out/'native').mkdir(parents=True);(out/'captioned').mkdir();(out/'boards').mkdir()
samples=[];by_source={};tags={}
def add(key,frame,outframe,tag,rowid,cut=None):
    k=(key,frame,outframe);tags.setdefault(k,set()).add(tag)
    if k in {(x['key'],x['sourceFrame'],x['outputFrame']) for x in samples}:return
    samples.append(dict(key=key,sourceFrame=frame,outputFrame=outframe,scene=rowid,cutId=cut['id'] if cut else None,
                        sourceCrop=cut['sourceCrop'] if cut else [0,0,1920,1080]))
    by_source.setdefault(key,set()).add(frame)
for sf in range(3515,3605):add('boss',sf,boss['startFrame']+sf-3515,'every-boss-frame','06',boss)
for q in caption['ko']:
    start=math.ceil(q['startSeconds']*60);end=math.ceil(q['endSeconds']*60)-1
    if q['pieceId']=='10-part2':
        for n in [start-1,start,start+1,(start+end)//2,end,end+1]:
            if pedro['startFrame']<=n<pedro['endFrame']:add('pedro',pedro['inFrameInclusive']+n-pedro['startFrame'],n,f'pedro-cue:{q["index"]}',q['scene'],pedro)
    for row in white['rows']:
        aa,zz=row['finalStartFrame'],row['finalEndFrame']
        if start<zz and end>=aa:
            for n in [max(aa,start),max(aa,min(zz-1,(start+end)//2)),min(zz-1,end)]:
                add('white',row['reelStartFrame']+n-aa,n,f'white-cue:{q["index"]}',row['id'])
for row in white['rows']:
    for offset in sorted({0,1,18,30,45,60,72,90,120,150,180,row['frames']//2,row['frames']-2,row['frames']-1}):
        if offset<row['frames']:add('white',row['reelStartFrame']+offset,row['finalStartFrame']+offset,'white-animation-boundary',row['id'])
state=dict(status='extracting-white-boss-pedro-inputs',pid=os.getpid(),commandLine=[os.sys.executable,*os.sys.argv],
           sessionId=None,startedAt=now(),cpuThreads=2,gpuJobs=0,resourceObservation=args.resource,
           sourceCandidate=rel(s_path),sourceCandidateSha256=sha(s_path),captionCandidate=rel(c_path),captionCandidateSha256=sha(c_path),
           whiteSha256=w_ver['sha256'],tasks=[],activeTasks=[],completedSources=0,totalSources=3,
           exitCode=None,log=rel(PROOF/'white-boss-pedro-input-v4.log'),allDirectlyRead=False,allFinalPixelsReviewed=False,newGitImages=0)
def checkpoint():
    session=state_path.with_name(state_path.stem+'.session.json')
    if session.exists():state['sessionId']=read(session)['sessionId']
    state['updatedAt']=now();write(state_path,state)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        j=read(p);j.update(updatedAt=now(),stage='single-white-boss-pedro-input-CPU-extraction',wordActionSourceCandidate=rel(s_path),
                           execution=state,browserReviewServer=read(PROOF/'browser-word-action-review-server-v1.json'),
                           nextAction='After actual exit, directly review every local white/boss/Pedro board and retain final gates false. Finish all78 moving source-word reviews.');write(p,j)
    p=PROOF.parent/'queue.json';q=read(p);it=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
    it.update(stage='single-white-boss-pedro-input-CPU-extraction',wordActionSourceCandidate=rel(s_path),execution=state,
              browserReviewServer=read(PROOF/'browser-word-action-review-server-v1.json'));q['updatedAt']=now();write(p,q)
paths={};checkpoint()
try:
    with (PROOF/'white-boss-pedro-input-v4.log').open('x',encoding='utf-8') as log:
        for key,frames in by_source.items():
            target=out/'native'/key;target.mkdir();selected=sorted(frames)
            src=white_path if key=='white' else ROOT/(boss if key=='boss' else pedro)['sourcePath']
            expected=w_ver['sha256'] if key=='white' else (boss if key=='boss' else pedro)['sourceSha256'];assert sha(src)==expected
            expr='+'.join(f'eq(n,{n})' for n in selected)
            cmd=[FF,'-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(src),'-an',
                 '-vf',f"select='{expr}',scale=1920:1080",'-vsync','0','-q:v','3','-threads','2',str(target/'%05d.jpg')]
            proc=subprocess.Popen(cmd,stdout=log,stderr=log);task=dict(source=key,pid=proc.pid,commandLine=cmd,startedAt=now(),expectedFrames=len(selected))
            state['tasks'].append(task);state['activeTasks']=[task];checkpoint();rc=proc.wait()
            task.update(exitCode=rc,endedAt=now());assert rc==0
            files=sorted(target.glob('*.jpg'));assert len(files)==len(selected)
            paths.update({(key,n):p for n,p in zip(selected,files)})
            state['completedSources']+=1;state['activeTasks']=[];checkpoint();print(json.dumps(dict(source=key,frames=len(files))),flush=True)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    samples.sort(key=lambda x:({'boss':0,'pedro':1,'white':2}[x['key']],x['outputFrame']))
    for i,t in enumerate(samples,1):
        raw=paths[t['key'],t['sourceFrame']];t.update(index=i,nativePath=rel(raw),nativeSha256=sha(raw),tags=sorted(tags[t['key'],t['sourceFrame'],t['outputFrame']]))
        im=Image.open(raw).convert('RGB');q=next((q for q in caption['ko'] if q['startSeconds']<=t['outputFrame']/60<q['endSeconds']),None)
        t.update(captionIndex=q['index'] if q else None,literalKo=q['ko'] if q else None)
        if q:
            d=ImageDraw.Draw(im);w=round(font.getlength(q['ko'])+44);left=960-w/2
            d.rectangle((left+14,942,left+w+14,1026),fill='#073c32');d.rectangle((left,928,left+w,1012),fill='white',outline='#161b18',width=3)
            d.text((960,939),q['ko'],font=font,fill='#080b09',anchor='mt')
        path=out/'captioned'/f'{i:04}.jpg';im.save(path,quality=95);t.update(path=rel(path),sha256=sha(path),directlyRead=False)
    boards=[]
    for first in range(0,len(samples),6):
        group=samples[first:first+6];im=Image.new('RGB',(1920,1710),'white');d=ImageDraw.Draw(im)
        for i,t in enumerate(group):
            x,y=i%2*960,i//2*570;d.text((x+6,y+1),f'{t["index"]} {t["key"]}/{t["scene"]} f{t["outputFrame"]} src{t["sourceFrame"]} cue{t["captionIndex"]}',font=label,fill='black')
            im.paste(Image.open(ROOT/t['path']).resize((960,540)),(x,y+30))
        p=out/'boards'/f'{len(boards)+1:03}.jpg';im.save(p,quality=95)
        boards.append(dict(index=len(boards)+1,path=rel(p),sha256=sha(p),sampleIndices=[t['index'] for t in group],directlyRead=False))
    evidence=dict(schemaVersion=1,createdAt=now(),sourceCandidate=rel(s_path),sourceCandidateSha256=sha(s_path),captionCandidate=rel(c_path),captionCandidateSha256=sha(c_path),
                  whiteInputSha256=w_ver['sha256'],whiteInputFrames=9140,samples=samples,boards=boards,sampleCount=len(samples),boardCount=len(boards),
                  bossEvery90Frames=True,pedroNewCues=[q['index'] for q in caption['ko'] if q['pieceId']=='10-part2'],
                  whiteCueIndices=sorted({t['captionIndex'] for t in samples if t['key']=='white' and t['captionIndex']}),
                  allDirectlyRead=False,allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,newGitImages=0,imagesGitPolicy='local-only',
                  scope='Encoded silent white inputs plus source boss/Pedro with PIL literal overlay trials. These are not final burned-caption pair pixels.')
    ep=PROOF/'white-boss-pedro-input-v4.json';write(ep,evidence)
    state.update(status='closed-white-boss-pedro-inputs-pending-direct-review',exitCode=0,endedAt=now(),activeTasks=[],evidence=rel(ep),sampleCount=len(samples),boardCount=len(boards));checkpoint()
    print(json.dumps(dict(samples=len(samples),boards=len(boards),finalApproved=False)),flush=True)
except BaseException as e:
    state.update(status='failed-white-boss-pedro-inputs',exitCode=1,error=repr(e),endedAt=now());checkpoint();raise
