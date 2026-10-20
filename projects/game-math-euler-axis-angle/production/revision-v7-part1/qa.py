"""One current-master decode/PTS pass with selected actual-pixel evidence.

Run in the existing Qwen environment for PyAV. No ASR/model generation here.
Automated integrity, text geometry and direct visual review remain distinct.
"""
from pathlib import Path
import argparse, hashlib, html, importlib.util, json, math, subprocess
from PIL import Image,ImageDraw,ImageFont

H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v7-part1';Q=O/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def selected():
    sp=importlib.util.spec_from_file_location('v7_qa_timing',H/'timing.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.authorized()
def sample_plan(left,right):
    timeline=read(H/'timeline.json');captions=read(O/'captions/captions.json');events={};motions=[]
    def add(frame,label,kind):
        frame=max(0,min(timeline['totalFrames']-1,int(frame)))
        events.setdefault(frame,[]).append(dict(label=label,kind=kind))
    for cue in captions['cues']:add(round((cue['start']+cue['end'])*30),cue['id'],'every-current-caption')
    for scene in timeline['scenes']:
        for frame,tag in [(scene['startFrame'],'first'),(scene['endFrame']-1,'last')]:add(frame,scene['id']+'.'+tag,'every-scene-boundary')
    for side,file in [('left',left),('right',right)]:
        data=read(file);rows=data.get('segments',data.get('visualSegments'))
        if rows is None:rows=[r for s in data['scenes']for r in s['segments']]
        for i,row in enumerate(rows):
            a=row['startFrame'];b=row.get('endFrameExclusive',row.get('endFrame'))
            add(a,f'{side}.{i}.first','every-pane-cut');add(b-1,f'{side}.{i}.last','every-pane-cut')
            if row['kind']=='video'or any(x['kind']=='video'for x in row.get('overlayLayers',[])):
                motions.append(dict(startFrame=a,endFrameExclusive=b,side=side,scene=row.get('sceneId',row.get('scene')),sourceBeatId=row.get('sourceBeatId',row.get('sourceId'))))
                # Dense still sequence is evidence of progression, not a
                # claimed continuous human playback/listening approval.
                for f in range(a,b,15):add(f,f'{side}.{i}.f{f-a}','native-action-quarter-second-sample')
    early=[]
    for receipt in sorted((O/'sample').glob('*/samples.json')):
        proof=read(receipt);source=R/proof['movie']
        assert sha(source)==proof['movieSha256'],'Early scene proof must bind the exact reused captioned clip'
        for item in proof['samples']:
            add(item['globalFrame'],proof['scene']+'.early-proof','reused-early-scene-decoded-pixel-proof')
            early.append(dict(frame=item['globalFrame'],rgbSha256=item['rgbSha256'],scene=proof['scene'],
                sourceMovieSha256=proof['movieSha256'],receipt=rel(receipt)))
    merged=[]
    for row in sorted(motions,key=lambda x:x['startFrame']):
        a=max(120,row['startFrame']-30);b=min(timeline['bodyEndFrame'],row['endFrameExclusive']+30)
        if merged and a<=merged[-1]['endFrameExclusive']+30:
            merged[-1]['endFrameExclusive']=max(b,merged[-1]['endFrameExclusive']);merged[-1]['sources'].append(row)
        else:merged.append(dict(startFrame=a,endFrameExclusive=b,sources=[row]))
    for i,row in enumerate(merged,1):row.update(id=f'motion-{i:02}',start=row['startFrame']/60,end=row['endFrameExclusive']/60)
    return dict(schemaVersion=1,timelineSha256=sha(H/'timeline.json'),captionJsonSha256=sha(O/'captions/captions.json'),implementationSha256=sha(Path(__file__)),
        leftManifestSha256=sha(left),rightManifestSha256=sha(right),totalFrames=timeline['totalFrames'],
        events=[dict(frame=f,time=f/60,labels=v)for f,v in sorted(events.items())],motionCases=merged,earlyScenePixelProofs=early,
        limitation='Dense frame sequences and automatic full decode do not replace continuous human playback or listening.')
def decode(path,plan,captioned):
    import av
    current=sha(path);target=Q/(path.stem+'.integrity.json')
    if target.exists():
        cached=read(target)
        if cached['sha256']==current and cached['samplePlanSha256']==sha(Q/'sample-plan.json')and cached['complete']:
            print('Reused exact successful current-master decode',path.name,flush=True);return cached
        raise RuntimeError('Preserve differing QA receipt before selected repair')
    requested={x['frame']:x for x in plan['events']}if captioned else{}
    early={x['frame']:x for x in plan.get('earlyScenePixelProofs',[])}if captioned else{}
    early_checked=0
    folder=Q/'frames';folder.mkdir(parents=True,exist_ok=True);samples=[];pts_errors=[];sizes=set();first_pts=None;last_pts=None;count=0
    with av.open(str(path))as container:
        stream=container.streams.video[0];stream.thread_type='AUTO';stream.codec_context.thread_count=2
        avg=str(stream.average_rate);assert avg=='60',avg
        time_base=float(stream.time_base)
        for index,frame in enumerate(container.decode(stream)):
            timestamp=float(frame.pts*frame.time_base)if frame.pts is not None else None
            if first_pts is None:first_pts=timestamp
            if timestamp is None or abs(timestamp-index/60)>max(time_base*.51,1e-7):
                if len(pts_errors)<30:pts_errors.append(dict(frame=index,pts=frame.pts,time=timestamp,expected=index/60))
            sizes.add((frame.width,frame.height));last_pts=timestamp;count=index+1
            if index in requested:
                im=frame.to_image();native=folder/f'{index:07}.jpg';mobile=folder/f'{index:07}.375.png'
                if index in early:
                    assert hashlib.sha256(im.tobytes()).hexdigest()==early[index]['rgbSha256'],('Reused scene decoded pixels changed',index,early[index]['scene'])
                    early_checked+=1
                im.save(native,quality=92,subsampling=0);im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
                samples.append(dict(requested[index],native=rel(native),mobile=rel(mobile),nativeSha256=sha(native),mobileSha256=sha(mobile)))
    assert count==plan['totalFrames']and sizes=={(1920,1080)}and not pts_errors,(path,count,sizes,pts_errors)
    assert not captioned or len(samples)==len(requested)
    assert not captioned or early_checked==len(early)
    audio=audio_integrity(path)
    result=dict(schemaVersion=1,file=rel(path),sha256=current,bytes=path.stat().st_size,complete=True,
        decodedFrames=count,width=1920,height=1080,fps=60,firstPtsSeconds=first_pts,lastPtsSeconds=last_pts,
        ptsErrorCount=len(pts_errors),ptsErrors=pts_errors,allFramesDecoded=True,audio=audio,
        samplePlanSha256=sha(Q/'sample-plan.json'),samples=samples,earlySceneDecodedPixelProofsPassed=early_checked,
        semanticVisualReview='pending direct current-pixel review',continuousHumanPlayback='pending',humanWholeListening='pending')
    save(target,result);print('Decoded full current master',path.name,count,'frames',flush=True);return result
def audio_integrity(path):
    import av,numpy as np
    digest=hashlib.sha256();count=0;peak=0.;channels=set();rates=set();pts_missing=0;backwards=0;previous=-1.;first=None;last=None
    with av.open(str(path))as container:
        stream=container.streams.audio[0];stream.codec_context.thread_count=2
        for f in container.decode(stream):
            rates.add(f.sample_rate);channels.add(len(f.layout.channels));count+=f.samples
            t=float(f.pts*f.time_base)if f.pts is not None else None
            if t is None:pts_missing+=1
            elif t<previous-1e-6:backwards+=1
            else:
                if first is None:first=t
                previous=t;last=t+f.samples/f.sample_rate
            arr=f.to_ndarray();assert np.isfinite(arr).all();peak=max(peak,float(np.max(np.abs(arr))));digest.update(arr.tobytes())
    assert rates=={48000}and channels=={2}and not pts_missing and not backwards
    return dict(decodedSamplesPerChannel=count,sampleRates=sorted(rates),channels=sorted(channels),
        finite=True,peakFloat=peak,firstPts=first,lastEnd=last,missingPts=pts_missing,backwardsPts=backwards,decodedPcmSha256=digest.hexdigest())
def contact_pages(samples):
    # Every caption/cut is available at actual native pixels plus375px. The
    # overview pages only support navigation, not a false full-resolution pass.
    pages=[];folder=Q/'contact';folder.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
    for i in range(0,len(samples),6):
        group=samples[i:i+6];sheet=Image.new('RGB',(1920,3*580),'#151515');d=ImageDraw.Draw(sheet)
        for j,item in enumerate(group):
            x=(j%2)*960;y=(j//2)*580
            im=Image.open(R/item['native']);im=im.resize((960,540),Image.Resampling.LANCZOS);sheet.paste(im,(x,y))
            label=f'{item["frame"]/60:.2f}s '+', '.join(x['label']for x in item['labels'])[:60]
            d.text((x+8,y+544),label,font=font,fill='white')
        dest=folder/f'{i//6:04}.jpg';sheet.save(dest,quality=90,subsampling=0);pages.append(dict(file=rel(dest),frames=[s['frame']for s in group]))
    save(Q/'contact-pages.json',dict(pages=pages,limitation='Navigation overview; open linked native/mobile images for actual-pixel review.'))
    return pages
def review_page(samples,pages,plan):
    rows=[]
    for item in samples:
        n='frames/'+Path(item['native']).name
        m='frames/'+Path(item['mobile']).name
        labels=' · '.join(x['label']for x in item['labels'])
        rows.append(f'<section id="f{item["frame"]}"><h3>{item["time"]:.2f}s · {html.escape(labels)}</h3><a href="{n}"><img loading="lazy" src="{n}" width="960"></a><a href="{m}"><img loading="lazy" src="{m}" width="375"></a></section>')
    buttons=''.join(f'<button data-case="{i}">{html.escape(c["id"])} · {c["start"]:.2f}–{c["end"]:.2f}초</button>'for i,c in enumerate(plan['motionCases']))
    cases=json.dumps(plan['motionCases'],ensure_ascii=False).replace('</','<\\/')
    script='''<script>const cases=CASES;const video=document.querySelector('video');const status=document.querySelector('#status');let selected=null,queue=[],completed=[];
function start(i){selected=cases[i];video.playbackRate=1;video.currentTime=selected.start;video.play();status.textContent=selected.id+' 1배 재생 중';}
document.querySelectorAll('[data-case]').forEach(button=>button.onclick=()=>{queue=[];start(+button.dataset.case);});
document.querySelector('#all-motion').onclick=()=>{completed=[];queue=cases.map((c,i)=>i);start(queue.shift());};
video.ontimeupdate=()=>{document.querySelector('#clock').textContent=video.currentTime.toFixed(3)+'초';if(selected&&video.currentTime>=selected.end){video.pause();completed.push(selected.id);document.querySelector('#completed').textContent='실제 동작 재생 완료 '+completed.length+'/'+cases.length+': '+completed.join(', ');status.textContent=selected.id+' 재생 완료';selected=null;if(queue.length)start(queue.shift());}};
video.onerror=()=>{queue=[];status.textContent='재생 오류: '+video.error.code;};video.onended=()=>status.textContent='전체 재생 끝';</script>'''.replace('CASES',cases)
    doc='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>회전1편 실제 출력 검수</title><style>body{margin:24px;background:#080b0d;color:#f5f5f5;font:16px/1.5 Malgun Gothic,sans-serif}video{width:min(100%,1200px)}img{max-width:100%;height:auto}h3{color:#e8cf83}section{margin:40px 0}button{margin:6px;padding:9px;background:#111;color:white;border:1px solid #777;cursor:pointer}</style><h1>3차원 회전1편 · 실제 출력</h1><video controls muted preload="metadata" src="../part1-captioned.mp4"></video><p>내부 화면 검수용으로 기본 음소거입니다. 완성 영상의 게임 소리·내레이션은 그대로 들어 있습니다.</p><p id="status">대기</p><output id="clock">0.000초</output><div>'+buttons+'</div><p>아래는 현재 인코딩에서 추출한 자막·컷·동작 표본입니다. 연속 재생과 전체 청취 승인은 별도입니다.</p>'+''.join(rows)+script
    doc=doc.replace('<div>'+buttons,'<p><button id="all-motion">모든 동작 구간 1배 재생</button></p><p id="completed">실제 동작 재생 완료 0</p><div>'+buttons)
    (Q/'review.html').write_text(doc,encoding='utf8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--left',type=Path,required=True);ap.add_argument('--right',type=Path,required=True);args=ap.parse_args();selected();Q.mkdir(parents=True,exist_ok=True)
    plan=sample_plan(args.left,args.right);save(Q/'sample-plan.json',plan)
    clean=decode(O/'part1-clean.mp4',plan,False);captioned=decode(O/'part1-captioned.mp4',plan,True)
    assert clean['audio']['decodedPcmSha256']==captioned['audio']['decodedPcmSha256'],'Burning captions must preserve exact encoded audio'
    pages=contact_pages(captioned['samples']);review_page(captioned['samples'],pages,plan)
    save(Q/'integrity-summary.json',dict(schemaVersion=1,part=1,completeDecodeBothMasters=True,frames=plan['totalFrames'],
        cleanSha256=clean['sha256'],captionedSha256=captioned['sha256'],decodedAudioIdentical=True,
        reusedEarlySceneDecodedPixelProofsPassed=captioned['earlySceneDecodedPixelProofsPassed'],
        sampledActualOutputFrames=len(captioned['samples']),contactPages=len(pages),
        noAutomaticHumanApproval=True,currentPixelSemanticReview='pending',finalMixAsr='separate current encoded-mix review',humanWholeListening='pending'))
    print(json.dumps(dict(fullDecode=True,frames=plan['totalFrames'],pairedAudioIdentical=True,pixelSamples=len(captioned['samples']),pages=len(pages))),flush=True)
if __name__=='__main__':main()
