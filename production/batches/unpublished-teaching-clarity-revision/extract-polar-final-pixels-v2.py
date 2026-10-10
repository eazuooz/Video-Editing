"""Exact absolute-PTS final cue/cut coverage; all images stay local."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, math, re, hashlib, argparse, subprocess, traceback
os.environ['OMP_NUM_THREADS']='2'
import psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/final-pixel-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def secs(t):
    a,b,c=t.replace(',','.').split(':');return int(a)*3600+int(b)*60+float(c)
def coverage():
    points={}
    def add(f,reason):
        if 0<=f<54115:points.setdefault(f,set()).add(reason)
    def edge(f,reason):
        for d in [-1,0,1]:add(f+d,reason+f':{d:+d}')
    for f in range(0,54115,60):add(f,'whole-video1s')
    for f in [0,119,120,53514,53515,54114]:edge(f,'intro/member-boundary')
    timeline=read(ROOT/'projects/game-math-polar-3d/production/timeline.json')
    for sc in timeline['scenes']:
        start=round(sc['start']*60)
        edge(start,'scene'+sc['id']+'-start');edge(start+sc['frames'],'scene'+sc['id']+'-end')
    ko=[]
    for line in (ROOT/'projects/game-math-polar-3d/script/final.ko.ass').read_text(encoding='utf-8').splitlines():
        if not line.startswith('Dialogue:'):continue
        fields=line.split(',',9)
        if fields[3]!='Text':continue
        a=math.ceil(secs(fields[1])*60-1e-7);b=math.ceil(secs(fields[2])*60-1e-7)
        n=len(ko)+1;ko.append({'cue':n,'fromFrame':a,'toFrameExclusive':b,'text':re.sub(r'\{[^}]*\}','',fields[9]).replace('\\N',' / ')})
        edge(a,f'KO{n:03d}-start');edge(b,f'KO{n:03d}-end');add((a+b-1)//2,f'KO{n:03d}-mid')
    en=[]
    for block in re.split(r'\n\s*\n',(ROOT/'projects/game-math-polar-3d/script/final.en.srt').read_text(encoding='utf-8-sig').strip()):
        lines=block.splitlines();a,b=lines[1].split(' --> ')
        af=math.ceil(secs(a)*60-1e-7);bf=math.ceil(secs(b)*60-1e-7);n=len(en)+1
        en.append({'cue':n,'fromFrame':af,'toFrameExclusive':bf,'text':' '.join(lines[2:])})
        edge(af,f'EN{n:03d}-start');edge(bf,f'EN{n:03d}-end');add((af+bf-1)//2,f'EN{n:03d}-mid')
    assert len(ko)==len(en)==206
    jobs=[{'scene':'02','globalStartFrame':1669,'plan':'projects/game-math-polar-3d/revision-teaching-clarity-v1/scene02-editorial-annotations-v3.json'}]
    jobs.extend(j for j in read(OUT/'six-moving-pilots-execution-v4.json')['jobs'] if j['scene'] not in ['11','16'])
    jobs.extend(read(OUT/'minus-glyph-moving-pilots-execution-v5.json')['jobs'])
    for j in jobs:
        p=read(ROOT/j['plan']);start=j['globalStartFrame']
        for cut in p['cuts']:edge(start+cut['sceneStartFrame'],'native-cut'+j['scene'])
        for t in p['stagesSeconds']:edge(start+round(t*60),'annotation-stage'+j['scene'])
    def scene(f):
        if f<120:return 'intro'
        if f>=53515:return 'member'
        return next(sc['id'] for sc in timeline['scenes'] if round(sc['start']*60)<=f<round(sc['start']*60)+sc['frames'])
    return {'createdAt':now(),'frames':54115,'fps':60,'timebase':'1/90000','koCues':ko,'enCues':en,
      'points':[{'frame':f,'pts':f*1500,'scene':scene(f),'reasons':sorted(points[f])} for f in sorted(points)],
      'coverage':'1s whole-video, every KO/EN cue start/end +/-1frame and mid, every scene/native cut/annotation stage +/-1frame, original intro/member boundaries',
      'allFinalPixelsApproved':False,'preparedOnly':True,'sourceMediaChanged':False,'imageGitAdded':0}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--resource');ap.add_argument('--pair-outer-exit-code',type=int);args=ap.parse_args()
    planfile=OUT/'final-pixel-coverage-plan-v2.json'
    if args.prepare_only:
        assert not planfile.exists();p=coverage();planfile.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'preparedSamples':len(p['points']),'koCues':len(p['koCues']),'enCues':len(p['enCues']),'finalApproval':False}));return
    assert args.pair_outer_exit_code==0 and args.resource
    pair=read(OUT/'final-pair-execution-v3.json')
    assert pair['exitCode']==0 and pair['status']=='completed-await-all-final-pixel-review'
    assert not psutil.pid_exists(pair['pid']) or psutil.Process(pair['pid']).create_time()!=pair['createTime']
    resource=read(ROOT/args.resource)
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    source=ROOT/pair['pair'][1]['path'];assert sha(source)==pair['pair'][1]['sha256']
    plan=read(planfile);assert len(plan['koCues'])==len(plan['enCues'])==206
    LOCAL.mkdir(parents=True,exist_ok=False)
    statefile=OUT/'final-pixel-extraction-execution-v2.json';assert not statefile.exists()
    process=psutil.Process()
    state={'pid':process.pid,'createTime':process.create_time(),'commandLine':process.cmdline(),'cwd':str(ROOT),
      'startedAt':now(),'cpuThreads':2,'gpuJobs':0,'resourceEvidence':args.resource,
      'pairActualOuterExitCode':0,'pairEvidence':'final-pair-execution-v3.json','source':rel(source),'sourceSha256':sha(source),
      'plan':rel(planfile),'planSha256':sha(planfile),'status':'extracting','allFinalPixelsApproved':False,
      'humanListeningApproved':False,'publicRightsApproved':False,'researchControlChanges':0,'imageGitAdded':0}
    def save():state['observedAt']=now();statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save();print(json.dumps({'pid':process.pid,'createTime':process.create_time(),'samples':len(plan['points'])}),flush=True)
    try:
        vf='select='+ '+'.join(f"eq(pts\\,{p['pts']})" for p in plan['points'])+',showinfo'
        filterfile=LOCAL/'absolute-pts-select.filter';filterfile.write_text(vf,encoding='utf-8')
        cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(source),
          '-filter_script:v',str(filterfile),'-frames:v',str(len(plan['points'])),'-fps_mode','passthrough',
          '-threads','2','-compression_level','3',str(LOCAL/'sample-%05d.png')]
        state['currentCommand']=cmd;save()
        log=LOCAL/'absolute-pts-extraction.log'
        with log.open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=f,cwd=ROOT,check=True)
        state['extractionExitCode']=r.returncode
        actual=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',log.read_text(encoding='utf-8',errors='replace'))]
        assert actual==[p['pts'] for p in plan['points']],('exact source PTS coverage mismatch',len(actual))
        files=sorted(LOCAL.glob('sample-*.png'));assert len(files)==len(plan['points'])
        state.update(status='building-contact-boards',samples=[dict(p,path=rel(f),sha256=sha(f)) for p,f in zip(plan['points'],files)],allExtractedPtsMatched=True);save()
        font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);state['boards']=[]
        for sc in ['intro']+[f'{i:02d}' for i in range(1,20)]+['member']:
            samples=[p for p in state['samples'] if p['scene']==sc]
            for k in range(0,len(samples),6):
                block=samples[k:k+6];board=Image.new('RGB',(1280,1170),'#e8e8e8');draw=ImageDraw.Draw(board)
                for i,v in enumerate(block):
                    x=(i%2)*640;y=(i//2)*390
                    with Image.open(ROOT/v['path']) as img:board.paste(img.resize((640,360)),(x,y))
                    draw.text((x+4,y+362),f"{sc} f{v['frame']} | {v['frame']/60:.3f}s | "+','.join(v['reasons'])[:44],font=font,fill='#111111')
                file=LOCAL/f"board-{sc}-{k//6+1:03d}.png";board.save(file)
                state['boards'].append({'scene':sc,'board':k//6+1,'path':rel(file),'sha256':sha(file),'frames':[p['frame'] for p in block]})
            save();print(json.dumps({'scene':sc,'samples':len(samples),'boards':math.ceil(len(samples)/6)}),flush=True)
        protected=read(OUT/'baseline-protected-sha-v1.json')
        assert all(sha(ROOT/f['path'])==f['sha256'] for f in protected['files'])
        state.update(status='completed-await-direct-pixel-review',exitCode=0,finishedAt=now(),protectedBaselineUnchanged=True,
          samplesCount=len(state['samples']),boardsCount=len(state['boards']),allFinalPixelsApproved=False);save()
        print(json.dumps({'exitCode':0,'samples':state['samplesCount'],'boards':state['boardsCount'],'directReviewApproved':False}),flush=True)
    except Exception:
        state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
if __name__=='__main__':main()
