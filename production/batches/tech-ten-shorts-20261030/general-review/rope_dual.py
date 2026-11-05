"""One scene, two concurrent line layers. Reuses the measured Unity camera poses."""
import math
import shutil
import subprocess as sp
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from render import HERE, MEDIA, WORK, SOURCES, editor
from diagrams import NATIVE, data
from visuals import frame, label, foot, clamp, smooth, WHITE, MUTE, GOLD, TEAL, RED

SLUG=SOURCES[5]['slug']
OLD=MEDIA/SLUG/'local/final-reviewed-general-v3'
VERSION='final-reviewed-rope-dual-v4'
REV='rope-simultaneous-paths-v4'
OUT=OLD.parent/VERSION
TEMP=WORK/'rope-dual'
BASE='1c692d8b2d4fabfb5ea6ee5aeae5e3aec68d96f746997560bfd57c7920b8a042'
# Only replace Unity explanation windows. The genuine gameplay and end cut stay as edited.
WINDOWS=[(415,3618),(3978,4208)]
YELLOW='#ffd459'; MINT='#65f0cf'; DARK='#112124'; ERROR='#ff715d'
SAMPLE=[3.1,11,18.8,24.6,33,36.8,42.7,46.6,54.8,59,62,67.6]

def lerp(a,b,u):return tuple(p+(q-p)*u for p,q in zip(a,b))
def progress(t,a,b):return smooth((t-a)/(b-a))
def row(mode,n):return data(NATIVE/mode/'poses.csv')[n]
def xy(r,key):return tuple(float(r[key+i]) for i in ('X','Y'))
def mixpos(t,*keys):
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return round(x+(y-x)*progress(t,a,b))
    return keys[-1][1]
def dashes(draw,path,color,width,on=23,off=16):
    phase=0.
    for a,b in zip(path,path[1:]):
        dist=math.dist(a,b)
        if dist<.01:continue
        pos=0.
        while pos<dist-.001:
            lit=phase<on
            step=min(dist-pos,(on if lit else on+off)-phase)
            if lit:draw.line([lerp(a,b,pos/dist),lerp(a,b,(pos+step)/dist)],fill=color,width=width)
            pos+=step;phase=(phase+step)%(on+off)
def rounded(draw,pt,r,col):
    x,y=pt;draw.ellipse((x-r,y-r,x+r,y+r),fill=col)
def raw(mode,n):
    with Image.open(NATIVE/mode/f'{n:04}.jpg') as im:return im.convert('RGB')

@lru_cache(91)
def clean_top(n):
    # Static cross section from a pose where the post is not crossed. The jeep is
    # the native model from this exact pose. Remove the native single-line pass
    # before drawing the two explanatory layers, to avoid a false third rope.
    ref=raw('direct',0)
    im=Image.new('RGB',ref.size,ref.getpixel((30,290)))
    im.paste(ref.crop((430,179,650,370)),(430,179))
    p=ImageDraw.Draw(im);r=row('direct',n);a=xy(r,'anchor');b=xy(r,'end')
    rounded(p,a,16,ref.getpixel((154,114)))
    left,top=int(b[0]-32),max(0,int(b[1]-49))
    right,bottom=1033,min(im.height,int(b[1]+51))
    vehicle=np.array(raw('direct',n).crop((left,top,right,bottom)))
    rr,gg,bb=vehicle.astype(np.int16).transpose(2,0,1)
    # Distinguish the yellow line from the muted green vehicle and wheel trim.
    wire=(rr>128)&(gg>88)&(rr>bb+60)&(gg>bb+45)&(rr>gg+12)
    vehicle[wire]=ref.getpixel((30,290));im.paste(Image.fromarray(vehicle),(left,top));return im

def clip_seg(a,b):
    # Projected top-view AABB of the actual Unity post; same ortho scale as CSV.
    enter,leave=0.,1.
    for o,e,lo,hi in [(a[0],b[0],441.8,638.2),(a[1],b[1],186.1,361.9)]:
        delta=e-o
        if abs(delta)<1e-6:
            if o<lo or o>hi:return None
        else:
            u,v=sorted(((lo-o)/delta,(hi-o)/delta))
            enter=max(enter,u);leave=min(leave,v)
    return (lerp(a,b,enter),lerp(a,b,leave)) if enter<leave else None

def route(span,u):
    # Arc-length sampling keeps the comparison anchored at both ends, even when
    # adding a new corner or blending the deliberate bad segment toward recovery.
    lengths=[math.dist(a,b) for a,b in zip(span,span[1:])]
    dist=sum(lengths)*u
    for i,length in enumerate(lengths):
        if dist<=length or i==len(lengths)-1:
            f=clamp(dist/max(.001,length))
            return lerp(span[i],span[i+1],f),i,f
        dist-=length

def top(t,n,fail,mark):
    info=row('wrapped',n);a,b,c=(xy(info,k) for k in ('anchor','end','corner'))
    safe=[a,c,b] if info['wrapped']=='1' else [a,b]
    bed=clean_top(n).copy();d=ImageDraw.Draw(bed)
    def vertex(u):
        p,i,f=route(safe,u)
        # Outside of each segment: the left side on the way to the corner;
        # the right-hand side of the post on the way from the corner to the jeep.
        v,w=safe[i],safe[i+1];length=math.dist(v,w);nx=(w[1]-v[1])/length;ny=-(w[0]-v[0])/length
        disp=math.sin(math.pi*f)*(62+15*math.sin(t*2+u*3))
        body=(p[0]+nx*disp,p[1]+ny*disp)
        v=lerp(a,b,u)
        # Weak-solver demonstration: the two contact samples are outside wood,
        # but their connecting span cuts through it. This is not retail telemetry.
        wobble=(16*math.sin(t*2.1+u*4))
        if u<.33:v=(v[0],v[1]-wobble*math.sin(u/.33*math.pi))
        if u>.74:v=(v[0],v[1]+wobble*math.sin((u-.74)/.26*math.pi))
        return lerp(body,v,fail)
    us=sorted(set([i/80 for i in range(81)]+[.33,.74]))
    pts=[vertex(u) for u in us];d.line(pts,fill=YELLOW,width=14,joint='curve')
    if mark and fail>.96:
        for v,w in zip(pts,pts[1:]):
            inside=clip_seg(v,w)
            if inside:d.line(inside,fill=ERROR,width=17)
        for u in (.33,.74):
            pt=vertex(u);rounded(d,pt,12,DARK);rounded(d,pt,8,YELLOW)
    if len(safe)==3:
        rounded(d,c,11,DARK);rounded(d,c,7,MINT)
    dashes(d,safe,MINT,8)
    for end in (a,b):
        rounded(d,end,9,DARK);rounded(d,end,5,WHITE)
    return bed

def side(t,n,points):
    im=raw('side',n);d=ImageDraw.Draw(im);r=row('side',n);a,b=xy(r,'anchor'),xy(r,'end')
    if points:
        rgb=np.array(im)
        for u in (.12,.26,.4,.54,.68,.82):
            x=round(lerp(a,b,u)[0]);col=rgb[:,x].astype('int16')
            ys=np.where((col[:,0]>180)&(col[:,1]>135)&(col[:,2]<155)&(col[:,0]>col[:,2]+80))[0]
            if len(ys):rounded(d,(x,float(np.median(ys))),6,DARK)
    dashes(d,[a,b],MINT,7)
    for end in (a,b):
        rounded(d,end,9,DARK);rounded(d,end,5,WHITE)
    return im

def animated(t):
    if t<15.783 or 30.1667<=t<37.30:
        if t<15.783:
            n=mixpos(t,(6.91,5),(10,21),(12.8,8),(15.783,39))
            title='밧줄 하나에 두 경로가 있어요';bottom='실선은 처져도, 점선은 양 끝을 곧게 잇습니다'
        else:
            n=mixpos(t,(30.16,0),(33.4,4),(36.65,90))
            title='지프가 당기면 두 선은 어떻게 될까?'
            bottom='줄이 팽팽해지면 두 선이 겹칩니다' if t>35.4 else '남는 길이만큼 노란 줄의 가운데가 처집니다'
        shot=side(t,n,t<15.783);view='옆에서 본 모습'
    else:
        n=mixpos(t,(15.783,31),(19.9,86),(22,89),(24.8,79),(29.8,87),
                 (37.30,59),(39.8,78),(42.1,90),(46.9,90),(48.8,72),(51.4,35),
                 (54.6,88),(57.3,71),(59.8,78),(66.3,80),(69.65,88))
        fail=(progress(t,15.78,18.3)*(1-progress(t,25.4,29.2)) if t<30 else
              progress(t,37.30,39.85)*(1-progress(t,44.23,48.0)))
        mark=(17<=t<25.8 or 39.88<=t<45.2)
        if t<21.267 or 37.30<=t<44.23:
            title='같은 양 끝인데 실선은 기둥을 뚫어요';bottom='빨간 부분만 기둥 안으로 들어갑니다'
        elif t<30 or 44.23<=t<51.65:
            title='점선은 기둥 모서리에서 꺾여요';bottom='밧줄이 뚫고 가도 점선은 바깥을 돕니다' if fail>.8 else '양 끝은 같고, 기둥에 닿는 경로가 달라요'
        else:
            title='흔들리는 밧줄 뒤에 남는 경로';bottom='게임에서는 점선이 보이지 않아요'
        shot=top(t,n,fail,mark);view='위에서 본 단면'
    im,d=frame(5,title,'자체 원리 시연   /   '+view)
    im.paste(shot.resize((1000,508),Image.Resampling.LANCZOS),(40,154))
    line_y=706
    d.line((60,line_y,133,line_y),fill=YELLOW,width=12)
    label(im,149,684,'기존 밧줄',39,YELLOW)
    dashes(d,[(510,line_y),(594,line_y)],MINT,8,20,12)
    label(im,610,684,'숨은 팽팽한 경로',39,MINT)
    foot(im,d,bottom);return im

def cut_art():
    path=TEMP/'dual-window.mkv'
    # Render time in the original 60fps timeline, 30 distinct poses/second.
    first=WINDOWS[0][0];end=WINDOWS[-1][1]
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x840',
         '-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','2','-crf','13','-preset','ultrafast','-pix_fmt','yuv420p',str(path)]
    with sp.Popen(cmd,stdin=sp.PIPE) as p:
        for f in range(first,end,2):
            # The 60fps game cut can land on the second display of a 30fps cel.
            # Render its next explanation cel too; the overlay gate keeps gameplay exact.
            im=animated(max(f,3978)/60 if f==3977 else f/60) if any(a-1<=f<b for a,b in WINDOWS) else Image.new('RGB',(1080,840))
            p.stdin.write(im.tobytes())
        p.stdin.close()
        if p.wait():raise RuntimeError('Dual-path layer encode failed')
    return path

def build():
    TEMP.mkdir(parents=True,exist_ok=True);OUT.mkdir(exist_ok=True)
    old=editor.read(OLD/'delivery.json');assert editor.sha(OLD/'captioned.mp4')==BASE
    assert all(editor.sha(OLD/file['name'])==file['sha256'] for file in old['files'])
    native=editor.read(HERE/'native-evidence.json')['rope']['traceSHA256']
    assert all(editor.sha(NATIVE/k/'poses.csv')==v for k,v in native.items())
    if (OUT/'delivery.json').exists():raise RuntimeError('Immutable completed revision already exists')
    overlay=cut_art()
    a=WINDOWS[0][0]
    # Position by integral frame count, not rounded container milliseconds.
    enable='+'.join(f'between(n,{x},{y-1})' for x,y in WINDOWS)
    for kind in ('clean','captioned'):
        file=kind+'.mp4'
        graph=f"[1:v]fps=60,settb=1/60,setpts=N+{a}[art];[0:v][art]overlay=0:440:eof_action=pass:enable='{enable}'[out]"
        editor.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(OLD/file),'-i',str(overlay),
                    '-filter_complex_threads','2','-filter_complex',graph,'-map','[out]','-map','0:a:0','-c:a','copy',
                    '-c:v','libx264','-threads','4','-crf','16','-preset','ultrafast','-pix_fmt','yuv420p',
                    '-movflags','+faststart',str(OUT/file)])
        sv=next(s for s in editor.probe(OUT/file) if s['codec_type']=='video')
        assert (sv['width'],sv['height'],sv['r_frame_rate'],int(sv['nb_frames']))==(1080,1920,'60/1',old['frames'])
    editor.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(OUT/'captioned.mp4'),'-vf','scale=376:-2','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','21','-c:a','copy','-movflags','+faststart',str(OUT/'mobile-review.mp4')])
    for name in ['captions.ko.srt','captions.en.srt']:shutil.copyfile(OLD/name,OUT/name)
    page=(OLD/'index.html').read_text('utf-8')
    links='<p><b>두 경로 겹쳐 보기</b> · <button data-sec="32.6">0:33 처진 밧줄과 점선</button> · <button data-sec="41.6">0:42 기둥 관통과 우회</button> · <button data-sec="53.2">0:53 두 경로의 움직임</button></p>'
    (OUT/'index.html').write_text(page.replace('<h2>대본 검수',links+'<h2>대본 검수'),encoding='utf-8')
    desc='노란 실선은 흔들리는 밧줄이고, 청록 점선은 같은 양 끝을 이으면서 장애물을 피하는 숨은 경로입니다. 지프가 줄을 당길 때, 그리고 줄 한 구간이 기둥을 뚫을 때 두 선을 한 화면에서 비교합니다.'+'\n\n'+old['description'].split('\n\n',1)[1]
    receipt={**old,'revision':REV,'description':desc,'baseMasterSha256':BASE,'additionFrames':0,'generatedAt':datetime.now(timezone.utc).isoformat(),
             'files':[dict(name=k,path=str(OUT/k),sha256=editor.sha(OUT/k),bytes=(OUT/k).stat().st_size) for k in editor.FILES]}
    editor.save(OUT/'metadata.json',{'title':receipt['title'],'description':desc})
    (OUT/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['name']}\n" for r in receipt['files']),encoding='ascii')
    editor.save(OUT/'delivery.json',receipt)

def verify_pair():
    from check import check
    check(5,dict(finalDirectory=str(OLD),masterSha256=BASE),VERSION,SAMPLE)
    # Count the two strokes inside the scene, excluding the legend, logo and captions.
    args=['ffmpeg','-v','error','-threads','2','-i',str(OUT/'captioned.mp4'),'-an','-vf',
          'fps=5,crop=1000:508:40:594,scale=348:176','-f','rawvideo','-pix_fmt','rgb24','-']
    frames=np.frombuffer(sp.check_output(args),np.uint8).reshape(-1,176,348,3)
    counts=[]
    for i,pixels in enumerate(frames):
        t=i/5
        if not any(a/60+.20<t<b/60-.2 for a,b in WINDOWS):continue
        r,g,b=pixels.astype(np.int16).transpose(2,0,1)
        gold=(r>175)&(g>118)&(r-b>70)&(g-b>40)&(r>=g+7)
        mint=(g>150)&(b>105)&(g-r>40)&(b-r>12)
        counts.append((round(t,2),int(gold.sum()),int(mint.sum())))
    assert min(x[1] for x in counts)>45 and min(x[2] for x in counts)>25,sorted(counts,key=lambda v:v[2])[:5]
    t=42.8
    r,g,b=frames[round(t*5)].astype(np.int16).transpose(2,0,1)
    red=(r>180)&(r-g>75)&(r-b>80)
    post=red[round(186/548*176):round(362/548*176),round(442/1080*348):round(638/1080*348)]
    assert post.sum()>30
    assert all(editor.sha(OUT/name)==editor.sha(OLD/name) for name in editor.FILES[2:])
    result=dict(matchedUnityPoseCount=91,regionalSampleCount=len(counts),samplesPerSecond=5,
                minGoldPixels=int(min(x[1] for x in counts)),minMintPixels=int(min(x[2] for x in counts)),
                helperCropSize=[348,176],redInsidePostPixelsAt42s8=int(post.sum()),
                simulationScope='Unity side capture, camera-matched illustrative loose polyline and measured corner route above the same native top-view model.',
                captionedSHA256=editor.sha(OUT/'captioned.mp4'),comparisonIntervalsFrames=WINDOWS)
    editor.save(OUT/'dual-path-check.json',result);print(result)

if __name__=='__main__':
    TEMP.mkdir(parents=True,exist_ok=True)
    if 'preview' in sys.argv:
        for t in (11,24,33,36.7,42.7,47,53.5):
            animated(t).resize((540,420)).save(TEMP/f'preview-{t}.jpg')
    elif 'verify' in sys.argv:verify_pair()
    else:build()
