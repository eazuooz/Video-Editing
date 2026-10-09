"""Seal actually read Tetris boards; extract only missing Balatro native targets."""
import hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
PR = Path(__file__).parent
OLD = ROOT/'shared/output/presenting-game-scores/native-cut-trials-v1'
CACHED = ROOT/'shared/output/presenting-game-scores/native-framing-v2'
OUT = ROOT/'shared/output/presenting-game-scores/balatro-caption-native-v3'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def save(p,d):
    p=Path(p); tmp=p.with_name(p.name+'.tmp-'+str(os.getpid()))
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def main():
    state=read(CACHED/'execution.json')
    assert state['exitCode']==0 and len(state['boards'])==23 and len(state['images'])==133
    for row in state['images']+state['boards']: assert sha(row['path'])==row['sha256']
    review=dict(schemaVersion=2,reviewedAt=now(),execution=str(CACHED/'execution.json'),
        executionSha256=sha(CACHED/'execution.json'),all23BoardsDirectlyRead=True,
        reviewedBoardNumbers=list(range(1,24)),sampleCount=133,allListedHashesMatched=True,
        scope='Exact native Tetris source samples with fixed two-line placeholder caption; actual narration and final encoded pixels are still separate gates.',
        framing=state['variant'],foregroundCrop=state['foregroundCrop'],foregroundPosition=[0,0],foregroundScale=1,
        bottomFill=state['bottomFill'],fixedCaptionCenter=[960,970],
        findings=['Both SCORE/LINES, SPEED LV/TIME, playing fields and bottom player names/WINS remain above the fixed caption in all active samples.',
            'Classic f0 is black and remains rejected; adoption starts no earlier than directly read active f50 at2.0s.',
            'Modern may start at f607 PTS607607=20.2535667s with actual placement/score, excluding readiness and initial empty-field samples.',
            'Modern f3455 PTS3458455 shows left29lines/19919 vs right32lines/19778, signed left+141. Subsequent samples show another lead change. Exact score formula and final victory are not inferred.',
            'Native source rates are classic25fps and modern30000/1001fps; final60fps must preserve real duration, without slowdown or loop.'],
        sourceFramingSamplesApproved=True,finalNarrationCaptionPixelsApproved=False,
        allNativeFramesDirectlyReviewed=False,wholeContinuousPlaybackDirectlyWatched=False,
        footageAdopted=False,allFinalPixelsReviewed=False,rasterGitAdditions=0)
    assert not (PR/'native-framing-direct-review-v2.json').exists()
    save(PR/'native-framing-direct-review-v2.json',review)
    oldreview=read(PR/'native-cut-trials-direct-review-v1.json')
    if 'footprintAdopted' in oldreview:
        oldreview['footageAdopted']=oldreview.pop('footprintAdopted')
        oldreview['schemaSpellingCorrectedAt']=now();save(PR/'native-cut-trials-direct-review-v1.json',oldreview)
    procs=[]
    for p in psutil.process_iter(['pid','ppid','create_time','cmdline','name']):
        try:
            if p.info['name'] and 'python' in p.info['name'].lower(): procs.append(p.info)
        except (psutil.NoSuchProcess,psutil.AccessDenied): pass
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    save(PR/'resources-before-balatro-native-v3.json',dict(recordedAt=now(),processes=procs,gpu=gpu,cpuThreads=2,gpuRequested=0,researchPauseOrProcessChanges=0))
    assert not OUT.exists(),'Read existing execution instead of repeating extraction'
    OUT.mkdir(parents=True)
    prior=read(OLD/'execution-resume-v1.json');src=next(s for s in prior['sources'] if s['name']=='balatro')
    pts=read(src['ptsPath']);assert len(pts)==2191
    frames=sorted(set(list(range(1680,1887,10))+[1722,1782,1842,1886]))
    existing={r['frame']:r for r in src['samples']}
    missing=[n for n in frames if n not in existing]
    for row in existing.values(): assert sha(row['rawPath'])==row['rawSha256']
    ep=OUT/'execution.json';e=dict(startedAt=now(),pid=os.getpid(),processCreatedEpoch=time.time(),cpuThreads=2,gpu=0,stage='extracting-only-missing-native-targets',exitCode=None,
        startFrame=1680,endFrameExclusive=1887,nativeFps=30,timebase='1/30000',
        startPts=1680000,lastPts=1886000,endPtsExclusive=1887000,startSeconds=56,endSecondsExclusive=62.9,
        source=src['rawPath'],sourceSha256=src['rawSha256'],sourcePtsSha256=src['ptsSha256'],
        cachedFramesReused=[n for n in frames if n in existing],newFrames=missing,
        noRepeatedSampleExtraction=True,fixedCaptionCenter=[960,970],captionMaxLines=1,
        actualFootageAdopted=False,allFinalPixelsReviewed=False,rastersGit=False,images=[],boards=[])
    save(ep,e)
    select='select='+ '+'.join('eq(n\\,%d)'%n for n in missing)
    cmd=[FF,'-nostdin','-v','error','-threads','2','-i',src['rawPath'],'-an','-vf',select,'-vsync','0','-threads','2','-q:v','2',str(OUT/'raw-new-%04d.jpg')]
    e['command']=cmd;save(ep,e)
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        e['extractionExitCode']=r.returncode;e['stderr']=r.stderr
        assert r.returncode==0,r.stderr
        rawfiles=sorted(OUT.glob('raw-new-*.jpg'));assert len(rawfiles)==len(missing)
        paths={n:p for n,p in zip(missing,rawfiles)}
        paths.update({n:Path(existing[n]['rawPath']) for n in frames if n in existing})
        font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
        label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
        text='패의 이름과 칩·배율이 차례로 표시됩니다.'
        w=ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(text,font=font)
        assert w<=1570
        left=round(960-(w+44)/2);right=round(960+(w+44)/2)
        e['placeholderText']=text;e['captionBox']=[left,928,right,1012]
        for n in frames:
            p=paths[n];im=Image.open(p).convert('RGB');assert im.size==(1920,1080)
            d=ImageDraw.Draw(im);d.rectangle((left+14,942,right+14,1026),fill='#073c32')
            d.rectangle((left,928,right,1012),fill='white',outline='#161b18',width=3)
            d.text((960,970),text,font=font,fill='#080b09',anchor='mm')
            dest=OUT/f'overlay-{n:06}.jpg';im.save(dest,quality=94)
            e['images'].append(dict(frame=n,pts=n*1000,seconds=n/30,rawPath=str(p),rawSha256=sha(p),path=str(dest),sha256=sha(dest)))
        for start in range(0,len(e['images']),6):
            b=Image.new('RGB',(1920,1683),'#151515');d=ImageDraw.Draw(b);entries=e['images'][start:start+6]
            for j,row in enumerate(entries):
                im=Image.open(row['path']);im.thumbnail((948,533));x=j%2*960+6;y=j//2*561+28;b.paste(im,(x,y))
                d.text((x,y-26),f"balatro f{row['frame']} PTS{row['pts']}",font=label,fill='white')
            dest=OUT/f'board-{start//6+1:03}.jpg';b.save(dest,quality=94)
            e['boards'].append(dict(path=str(dest),sha256=sha(dest),entries=entries))
        e.update(stage='native-one-line-caption-trials-ready-direct-review-pending',exitCode=0,finishedAt=now(),sampleCount=len(frames),boardCount=len(e['boards']))
        save(ep,e);print(json.dumps(dict(exit=0,samples=len(frames),boards=len(e['boards']),adopted=False)))
    except BaseException as err:
        e.update(stage='failed',exitCode=1,error=repr(err),finishedAt=now());save(ep,e);raise

if __name__=='__main__':main()
