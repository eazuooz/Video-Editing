"""Source PTS and cut trials only. No narration, final timing or adoption."""
import argparse, bisect, hashlib, json, os, subprocess, time
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[4]
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
OUT=ROOT/'shared/output/presenting-game-scores/native-cut-trials-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume-filter-repair',action='store_true');a=ap.parse_args()
    if a.resume_filter_repair:
        prior=json.loads((OUT/'execution.json').read_text())
        assert prior['stage']=='native-cut-trials-failed' and prior['exitCode']==1
        assert 'No such filter' in prior['error'] and not prior['sources']
        assert not list(OUT.glob('*/raw-*.jpg')), 'Do not repeat existing image extraction'
        assert not (OUT/'execution-resume-v1.json').exists()
    else:
        assert not OUT.exists(), 'Preserve completed trials; read checkpoint first'
        OUT.mkdir(parents=True)
    state=dict(schemaVersion=1,startedAt=now(),pid=os.getpid(),processCreatedEpoch=time.time(),
               cpuThreads=2,gpu=0,stage='extracting-native-cut-trials',exitCode=None,
               sourceAudioSelected=False,sourceIntervalsApproved=False,footageAdopted=False,
               allFinalPixelsReviewed=False,rastersGit=False,commands=[],sources=[])
    ep=OUT/('execution-resume-v1.json' if a.resume_filter_repair else 'execution.json')
    if a.resume_filter_repair:
        state['resumedFrom']=str(OUT/'execution.json');state['resumedFailureSha256']=sha(OUT/'execution.json')
    save(ep,state)
    sources=[
        ('classic','TEC_B-roll_MP-ClassicScoreAttack.mp4',[(0,24),(59,84),(88,103),(114,138)]),
        ('modern','TEC_B-roll_MP-ScoreAttack.mp4',[(18.25,42),(48,69),(90,104),(110,127),(130,148)]),
        ('balatro','Balatro_trailer_Master_Final.mp4',[(11.4,18.9),(53.4,62.9)]),
        ('ballionaire','Ballionaire_LaunchTrailer.mp4',[(4.6,9.1),(13.7,16.1),(18.1,19.9),(22.9,27.2),(31.7,33.8),(35.6,36.8)])]
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
    label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
    allimgs=[]
    try:
        for name,filename,cuts in sources:
            src=RAW/filename; base=OUT/name; base.mkdir(exist_ok=True)
            cmd=[str(FP),'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time,pkt_duration,pkt_duration_time,width,height','-of','json',str(src)]
            if (base/'native-pts.json').exists():
                frame_data=json.loads((base/'native-pts.json').read_text())
            else:
                p=subprocess.run(cmd,capture_output=True,text=True,check=True)
                frame_data=json.loads(p.stdout)['frames']; save(base/'native-pts.json',frame_data)
            ts=[float(f['best_effort_timestamp_time']) for f in frame_data]
            assert len(set(ts))==len(ts) and all(b>a for a,b in zip(ts,ts[1:]))
            rows=[]; indices=set()
            for ci,(start,end) in enumerate(cuts,1):
                lo=bisect.bisect_left(ts,start); hi=bisect.bisect_left(ts,end)
                assert hi>lo and 0<=lo<hi<=len(ts)
                picked={lo,hi-1}
                cursor=ts[lo]+2
                while cursor<ts[hi-1]:
                    picked.add(bisect.bisect_left(ts,cursor)); cursor+=2
                # Observe native frames across known score/line-change moments as well.
                special={'classic':[21.12,21.72,22.20,82.25,90.25,92.25,98.75,117.25,117.75,124.75,125.25,128.25,128.75,132.25,132.75,137.75],
                         'modern':[35.50,35.75,36.25,37.25,40.75,49.75,55.25,62.75,66.75,97.25,114.75,115.25,116.75,118.25,119.75,125.25],
                         'balatro':[], 'ballionaire':[]}[name]
                for s in special:
                    if ts[lo]<=s<end:
                        picked.add(bisect.bisect_left(ts,s))
                picked=sorted(picked); indices.update(picked)
                rows.append(dict(cutId=f'{name}-{ci:02}',startFrame=lo,endFrameExclusive=hi,
                                 startPts=frame_data[lo]['best_effort_timestamp'],
                                 lastPts=frame_data[hi-1]['best_effort_timestamp'],
                                 startSeconds=ts[lo],endSecondsExclusive=ts[hi] if hi<len(ts) else end,
                                 sampledNativeFrames=picked,directReview=False,adopted=False))
            select='+'.join(f'eq(n\\,{i})' for i in sorted(indices))
            cmd=[str(FF),'-nostdin','-v','error','-threads','2','-i',str(src),'-an','-vf',f'select={select}', '-vsync','0','-threads','2','-q:v','2',str(base/'raw-%04d.jpg')]
            state['commands'].append(cmd);save(ep,state)
            r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
            imgs=sorted(base.glob('raw-*.jpg'));assert len(imgs)==len(indices)
            samples=[]
            for i,(path,index) in enumerate(zip(imgs,sorted(indices)),1):
                im=Image.open(path).convert('RGB')
                # Two trial framings for Tetris; each will be directly read before selection.
                variants=['uncropped','crop-y120'] if name in ['classic','modern'] else ['uncropped']
                for v in variants:
                    pic=im.copy()
                    if v=='crop-y120':
                        pic=pic.crop((0,120,1920,1080)).resize((2160,1080),Image.Resampling.LANCZOS).crop((120,0,2040,1080))
                    # Full-width two-line limit trial, exact fixed center and box/shadow.
                    draw=ImageDraw.Draw(pic)
                    box=(153,897,1767,1043)
                    draw.rectangle((167,911,1781,1057),fill='#073c32')
                    draw.rectangle(box,fill='white',outline='#161b18',width=3)
                    for text,y in [('점수와 지운 줄 수는 서로 다른 기준입니다.',939),('지금 비교하는 값과 단위를 함께 확인하세요.',1001)]:
                        draw.text((960,y),text,font=font,fill='#080b09',anchor='mm')
                    dest=base/f'overlay-{v}-{index:06}.jpg';pic.save(dest,quality=94)
                    allimgs.append(dict(path=str(dest),sha256=sha(dest),source=name,frame=index,
                                        pts=frame_data[index]['best_effort_timestamp'],
                                        seconds=ts[index],variant=v))
                samples.append(dict(frame=index,pts=frame_data[index]['best_effort_timestamp'],
                                    seconds=ts[index],rawPath=str(path),rawSha256=sha(path)))
            row=dict(name=name,rawPath=str(src),rawSha256=sha(src),nativeFrameCount=len(ts),
                     ptsPath=str(base/'native-pts.json'),ptsSha256=sha(base/'native-pts.json'),
                     nativePtsUniqueAndIncreasing=True,cuts=rows,samples=samples)
            state['sources'].append(row);save(ep,state)
        boards=[]
        for start in range(0,len(allimgs),6):
            board=Image.new('RGB',(1920,1683),'#151515');draw=ImageDraw.Draw(board)
            entries=allimgs[start:start+6]
            for j,x in enumerate(entries):
                im=Image.open(x['path']);im.thumbnail((948,533))
                px=j%2*960+6;py=j//2*561+28;board.paste(im,(px,py))
                draw.text((px,py-26),f"{x['source']} {x['variant']} f{x['frame']} PTS{x['pts']}",fill='white',font=label)
            bp=OUT/f'board-{start//6+1:03}.jpg';board.save(bp,quality=94)
            boards.append(dict(path=str(bp),sha256=sha(bp),entries=entries))
        state.update(stage='native-cut-trials-ready-direct-review-pending',finishedAt=now(),exitCode=0,
                     boards=boards,sampleImageCount=len(allimgs),boardCount=len(boards))
        save(ep,state)
        print(json.dumps(dict(exit=0,images=len(allimgs),boards=len(boards),adopted=False)))
    except BaseException as e:
        state.update(stage='native-cut-trials-failed',finishedAt=now(),exitCode=1,error=repr(e));save(ep,state);raise

if __name__=='__main__': main()
