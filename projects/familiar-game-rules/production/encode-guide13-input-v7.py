"""One CPU worker, only the five corrected guide13 inputs and actual ASS pixels."""
from pathlib import Path
from datetime import datetime,timezone
import argparse, hashlib, json, math, os, subprocess, sys, traceback
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);a=parser.parse_args()
resource=read(ROOT/a.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
s_path=BASE/'word-action-source-candidate-v6.json';c_path=BASE/'word-caption-candidate-v4/captions.json'
s,c=read(s_path),read(c_path);review=read(PROOF/'moving-source-direct-review-v6.json')
assert review['allSourceMotionReviewed'] and review['allWordActionAligned'] and review['directlyReviewedCuts']==85
assert review['sourceCandidateSha256']==sha(s_path)
piece=next(p for p in s['pieces'] if p['id']=='13');cuts=piece['selectedSourceCuts']
assert len(cuts)==5 and sum(t['durationFrames'] for t in cuts)==495
out=ROOT/'shared/output/familiar-game-rules/research/guide13-encoded-input-v7'
state_path=PROOF/'guide13-encoded-input-execution-v7.json';assert not out.exists() and not state_path.exists()
out.mkdir(parents=True);(out/'frames').mkdir();(out/'boards').mkdir()
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
           status='encoding-guide13-input-only',cpuThreads=2,gpuJobs=0,resource=a.resource,
           sourceCandidateSha256=sha(s_path),captionCandidateSha256=sha(c_path),commands=[],activeTasks=[],exitCode=None,
           finalTimelineAdopted=False,allFinalCaptionPixelsReviewed=False,newGitImages=0)
def checkpoint():
    session=state_path.with_name(state_path.stem+'.session.json')
    if session.exists() and read(session).get('pid')==os.getpid():state['sessionId']=read(session)['sessionId']
    state['updatedAt']=now();write(state_path,state)
    qp=PROOF.parent/'queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='familiar-game-rules')
    item.update(stage='current85-source-reviewed-single-guide13-encoded-input-CPU-QA',allSourceMotionReviewed=True,
                guide13EncodedInputExecution=rel(state_path),wordCaptionCandidate=rel(c_path),execution=state,
                nextAction='Read every actual ASS encoded guide13 board including all89newframes and6-frame caption boundary; then adopt current timing and produce one final mix/current mixed ASR/pair/full encoded QA. Final gates false.')
    q['updatedAt']=state['updatedAt'];write(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        cp=read(p);cp.update(stage=item['stage'],updatedAt=state['updatedAt'],execution=state,
                            allSourceMotionReviewed=True,wordCaptionCandidate=rel(c_path),
                            guide13EncodedInputExecution=rel(state_path),nextAction=item['nextAction']);write(p,cp)
def run(exe,args,kind):
    command=[str(exe),*map(str,args)];log=out/f'{len(state["commands"])+1:02}-{kind}.log'
    with log.open('x',encoding='utf-8') as stream:
        p=subprocess.Popen(command,cwd=out,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        state['activeTasks']=[dict(pid=p.pid,commandLine=command,log=rel(log),kind=kind)];checkpoint();rc=p.wait()
    state['commands'].append(dict(pid=p.pid,commandLine=command,log=rel(log),kind=kind,exitCode=rc));state['activeTasks']=[];checkpoint()
    assert rc==0,f'{kind}: exit{rc}'
    return log.read_text('utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def astamp(t):
    n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
header=(ROOT/'projects/making-game-sequels/production/final-v1/captions.ko.ass').read_text('utf-8-sig').split('Dialogue:')[0]
lines=[]
for q in c['ko']:
    if q['pieceId']!='13':continue
    a0,z0=astamp(q['startSeconds']-piece['startFrame']/60),astamp(q['endSeconds']-piece['startFrame']/60)
    w=round(font.getlength(q['ko'])+44);left=round(960-w/2)
    for layer,color,x,y,bord in [(0,'323C07',left+14,942,0),(1,'FFFFFF',left,928,3)]:
        tags=f'{{\\an7\\pos({x},{y})\\p1\\bord{bord}\\shad0\\1c&H{color}&\\3c&H181B16&}}'
        lines.append(f'Dialogue: {layer},{a0},{z0},Default,,0,0,0,,{tags}m 0 0 l {w} 0 {w} 84 0 84')
    lines.append(f'Dialogue: 2,{a0},{z0},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0}}{q["ko"]}')
(out/'captions.ko.ass').write_text(header+'\n'.join(lines)+'\n','utf-8')
try:
    checkpoint();records=[]
    for cut in cuts:
        src=ROOT/cut['sourcePath'];assert sha(src)==cut['sourceSha256']
        video=out/f'{cut["id"]}.mp4'
        filt=f'trim=start_frame={cut["inFrameInclusive"]}:end_frame={cut["outFrameExclusive"]},setpts=N/(60*TB),setsar=1'
        run(FF,['-v','error','-nostdin','-threads','2','-filter_threads','1','-i',src,'-an','-vf',filt,
                '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-frames:v',cut['durationFrames'],
                '-video_track_timescale','90000',video],'native-cut')
        records.append(dict(cutId=cut['id'],path=rel(video),sha256=sha(video),frames=cut['durationFrames']))
    (out/'concat.txt').write_text('\n'.join(f"file '{Path(r['path']).name}'" for r in records)+'\n','utf-8')
    run(FF,['-v','error','-nostdin','-threads','2','-f','concat','-safe','0','-i','concat.txt','-an','-c:v','copy',
            '-video_track_timescale','90000','guide13.silent.mp4'],'silent-concat')
    run(FF,['-v','error','-nostdin','-threads','2','-i','guide13.silent.mp4','-an','-filter_threads','1','-vf','ass=captions.ko.ass',
            '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-frames:v','495',
            '-video_track_timescale','90000','guide13.captioned.input.mp4'],'ass-caption-input')
    p=json.loads(run(FP,['-v','error','-count_frames','-show_streams','-show_format','-of','json','guide13.captioned.input.mp4'],'probe'))
    v=p['streams'][0];assert len(p['streams'])==1 and v['codec_type']=='video' and v['nb_read_frames']=='495' and v['time_base']=='1/90000'
    assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1'
    run(FF,['-v','error','-nostdin','-threads','2','-i','guide13.captioned.input.mp4','-f','null','-'],'whole-decode')
    frames=set(range(5931,6020))|set(range(5870,5879))
    for cut in cuts:
        frames.update([cut['startFrame'],cut['startFrame']+1,cut['endFrame']-2,cut['endFrame']-1])
        frames.update(range(cut['startFrame'],cut['endFrame'],30))
    for q in c['ko']:
        if q['pieceId']=='13':
            start=math.ceil(q['startSeconds']*60-1e-7);end=math.ceil(q['endSeconds']*60-1e-7)-1
            frames.update([start-1,start,start+1,(start+end)//2,end,end+1])
    selected=sorted(f for f in frames if 5787<=f<6282)
    expr='+'.join(f'eq(n,{f-5787})' for f in selected)
    run(FF,['-v','error','-nostdin','-threads','2','-filter_threads','1','-i','guide13.captioned.input.mp4','-an',
            '-vf',f"select='{expr}'",'-fps_mode','vfr','-q:v','2','-threads','2','frames/%04d.jpg'],'extract-encoded-frames')
    files=sorted((out/'frames').glob('*.jpg'));assert len(files)==len(selected)
    samples=[]
    for i,(f,path) in enumerate(zip(selected,files),1):
        cut=next(t for t in cuts if t['startFrame']<=f<t['endFrame'])
        q=next((t for t in c['ko'] if t['startSeconds']<=f/60<t['endSeconds']),None)
        samples.append(dict(index=i,outputFrame=f,sourceFrame=cut['inFrameInclusive']+f-cut['startFrame'],cutId=cut['id'],
                            captionIndex=q['index'] if q else None,path=rel(path),sha256=sha(path),directlyRead=False))
    boards=[];label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    for first in range(0,len(samples),6):
        group=samples[first:first+6];im=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(im)
        for i,t in enumerate(group):
            x,y=i%2*960,i//2*570;draw.text((x+6,y+1),f'{t["index"]} out{t["outputFrame"]} src{t["sourceFrame"]} cue{t["captionIndex"]}',font=label,fill='black')
            im.paste(Image.open(ROOT/t['path']).resize((960,540)),(x,y+30))
        path=out/'boards'/f'{len(boards)+1:03}.jpg';im.save(path,quality=95)
        boards.append(dict(index=len(boards)+1,path=rel(path),sha256=sha(path),sampleIndices=[t['index'] for t in group],directlyRead=False))
    ep=PROOF/'guide13-encoded-input-v7.json'
    evidence=dict(schemaVersion=1,createdAt=now(),sourceCandidate=rel(s_path),sourceCandidateSha256=sha(s_path),
                  captionCandidate=rel(c_path),captionCandidateSha256=sha(c_path),nativeCuts=records,
                  video=rel(out/'guide13.captioned.input.mp4'),videoSha256=sha(out/'guide13.captioned.input.mp4'),
                  ass=rel(out/'captions.ko.ass'),assSha256=sha(out/'captions.ko.ass'),probe=p,frames=495,wholeDecodeExitCode=0,
                  samples=samples,boards=boards,sampleCount=len(samples),boardCount=len(boards),all89NewFramesExtracted=True,
                  allDirectlyRead=False,allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,newGitImages=0,imagesGitPolicy='local-only')
    write(ep,evidence);state.update(status='closed-guide13-encoded-input-awaiting-direct-review',exitCode=0,endedAt=now(),evidence=rel(ep),
                                   sampleCount=len(samples),boardCount=len(boards));checkpoint()
    print(json.dumps(dict(frames=495,samples=len(samples),boards=len(boards),exitCode=0,finalApproved=False)),flush=True)
except BaseException:
    state.update(status='failed-guide13-encoded-input',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
