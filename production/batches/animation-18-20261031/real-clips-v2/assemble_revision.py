"""Replace verified explanation cuts while preserving baseline footage, PCM and captions."""
from pathlib import Path
import json,sys,subprocess,hashlib,shutil,html,functools,ast,os,uuid
from datetime import datetime,timezone
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
import numpy as np
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];NATIVE=B/'local/real-clips-v2'
sys.path.insert(0,str(NATIVE/'python-deps'))
from scipy.ndimage import binary_fill_holes,binary_closing,label as connected_labels
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
ENC=['-r','60','-c:v','h264_nvenc','-preset','p4','-cq','18','-b:v','0','-bf','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
@functools.lru_cache(None)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def text(d,xy,s,size=36,c='#f1f0e8'):d.text(xy,s,font=font(size),fill=c,anchor='lt')
@functools.lru_cache(None)
def frame_files(key):return sorted((NATIVE/'study-frames'/key).glob('*.png'))
@functools.lru_cache(maxsize=1536)
def frame(key,n):
    files=frame_files(key)
    return Image.open(files[min(len(files)-1,max(0,n))]).convert('RGB')
@functools.lru_cache(maxsize=16)
def study_data(key):return read(NATIVE/'studies'/(key+'.json'))
def ff(args,log):
    with log.open('wb') as f:subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-progress',str(log.with_suffix('.progress')),'-stats_period','3',*map(str,args)],stdout=f,stderr=f,check=True)
def normalized_endcard(source,frames):
    directory=NATIVE/'normalized-endcards';directory.mkdir(exist_ok=True)
    dest=directory/(sha(source)+'.mp4')
    if not dest.exists():ff(['-threads','2','-i',source,'-vf','settb=1/60,setpts=N','-an','-frames:v',frames,*ENC,dest],dest.with_suffix('.log'))
    info=probe(dest);v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==frames and v['time_base']=='1/60000'
    return dest
def regular_packets(file,n):
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_packets','-show_entries','packet=pts,dts','-of','json',str(file)]))['packets']
    assert len(d)==n and all(p['pts']==i*1000 and p['dts']==i*1000 for i,p in enumerate(d)),('Nonuniform frame timing',file)
def render_cut(dest,images,log,frames,key=None):
    redraw=set(next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--redraw=')),'').split(','))
    if '--reuse-verified-pictures' in sys.argv and key not in redraw and dest.exists():
        info=probe(dest);s=next(s for s in info['streams'] if s['codec_type']=='video')
        assert int(s['nb_frames'])==frames and (s['width'],s['height'])==(1920,1080)
        return
    encoder(dest,images,log)
def encoder(path,images,log):
    with log.open('wb') as f:
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-an',*ENC,str(path)],stdin=subprocess.PIPE,stderr=f)
        try:
            previous=None;pixels=None
            for image in images:
                if image is not previous:pixels=image.tobytes();previous=image
                proc.stdin.write(pixels)
        finally:proc.stdin.close()
        assert proc.wait()==0,path
def state_index(f,n,study):
    frames=study['frames'];a,b=study.get('observationFrames',[frames//3,frames//2])
    if f<frames:return min(f,frames-1),'동작 비교'
    slow=a+(f-frames)//4
    return min(b,slow),'구간 분석' if slow<b else '자세 분석'
def projected(study,p,side=0,world=False):
    p=np.array(p,dtype=float)
    if not world:
        yaw=np.radians(study.get('sideYaws',[study.get('yaw',-65)]*2)[side]);x,y,z=p
        p=np.array([x*np.cos(yaw)-y*np.sin(yaw),x*np.sin(yaw)+y*np.cos(yaw),z])
        p+=study['actorLocations'][side] if 'actorLocations' in study else study['animations'][side].get('location',[0,0,0])
    camera=study.get('cameraLocation',[0,900,study.get('cameraHeight',100)]);yaw=study.get('cameraYaw',-90);pitch=study.get('cameraPitch',0)
    if study.get('cameraView')=='top':camera=[0,35,720];yaw=-90;pitch=-88
    yaw,pitch=np.radians([yaw,pitch]);relative=p-np.array(camera);right=np.array([-np.sin(yaw),np.cos(yaw),0]);up=np.array([-np.sin(pitch)*np.cos(yaw),-np.sin(pitch)*np.sin(yaw),np.cos(pitch)])
    scale=1920/study['cameraWidth'];return (960+np.dot(relative,right)*scale,540-np.dot(relative,up)*scale)
def arrow(d,a,b,color,width=6):
    a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
    if length<.1:return
    direction=v/length;normal=np.array([-direction[1],direction[0]])
    d.line([tuple(a),tuple(b)],fill=color,width=width);d.polygon([tuple(b),tuple(b-direction*17+normal*9),tuple(b-direction*17-normal*9)],fill=color)
def guides(ep,key,study,index,im):
    d=ImageDraw.Draw(im)
    if ep=='A16':
        for side in (0,1):
            view=study
            if key=='path' and side==1:view=study_data('A16-overhead')
            rec=study['collisionEvidence'][side][index];a=np.array(projected(view,rec['start'],world=True));b=np.array(projected(view,rec['end'],world=True));target=np.array(projected(view,rec['target'],world=True))
            delta=b-a;normal=np.array([-delta[1],delta[0]])/max(.001,np.linalg.norm(delta));radius=rec['radius']*1920/view['cameraWidth']
            color='#d74636' if rec['hit'] else '#229579' if rec['enabled'] else '#648a9e'
            for sign in (-1,1):d.line([tuple(a+sign*normal*radius),tuple(b+sign*normal*radius)],fill=color,width=5)
            r=rec['hurt']*1920/view['cameraWidth'];d.ellipse((target[0]-r,target[1]-r,target[0]+r,target[1]+r),outline=color,width=5)
            x=70+960*side;d.rectangle((x,700,x+330,769),fill='#14261f');text(d,(x+12,715),'닿음' if rec['hit'] else '판정 켜짐' if rec['enabled'] else '판정 꺼짐',30)
    elif ep=='A13' and key=='direction':
        for side in (0,1):
            view=study if not side else study_data('A13-observer');row=view['animations'][0];root=np.array(row['tracks']['root']['p'][index]);angle=np.radians(view['yaw']);rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
            location=np.array(view['actorLocations'][0]);center=rot@root+location;center[2]=3
            arrow(d,projected(view,center+[-25,0,0],world=True),projected(view,center+[55,0,0],world=True),'#bf742a',7)
            arrow(d,projected(view,center+[0,0,20],world=True),projected(view,center+rot@np.array([0,60,20]),world=True),'#2475ad',6)
        text(d,(80,710),'이동 방향',27,'#985414');text(d,(240,710),'몸 방향',27,'#175f91')
    elif ep=='A13' and key=='tool':
        for side in (0,1):
            bone='hand_r' if not side else 'hand_l';x,y=projected(study,study['motionEvidence'][side][index][bone],side)
            d.ellipse((x-33,y-33,x+33,y+33),outline='#b74635' if not side else '#247a9b',width=5)
    elif ep in ('A05','A08','A09','A10','A11','A15') and study.get('motionEvidence'):
        for side,trace in enumerate(study['motionEvidence']):
            color='#b74635' if not side else '#247a9b'
            if ep=='A08' and key=='flow':
                names=['head','upperarm_r','pelvis'];points=[projected(study,trace[index][name],side) for name in names if name in trace[index]]
                if len(points)>1:d.line(points,fill=color,width=6)
            elif (ep=='A05' and key in ('plane','top')) or (ep=='A11' and key in ('kick','returning')):
                bone='foot_r' if key=='kick' else 'hand_r';points=[projected(study,t[bone],side) for t in trace[12:index+1:3]]
                if len(points)>1:d.line(points,fill=color,width=5)
                x,y=projected(study,trace[index][bone],side);d.ellipse((x-12,y-12,x+12,y+12),outline=color,width=5)
            elif ep=='A10' and key=='root':
                root=study['animations'][side]['tracks']['root']['p'][index];a=projected(study,[0,0,2],side);b=projected(study,np.array(root)+[0,0,2],side)
                arrow(d,a,b,color,6)
                for x,y in (a,b):d.ellipse((x-10,y-10,x+10,y+10),outline=color,width=4)
            elif ep=='A09' and index>=45:
                x,y=projected(study,trace[index]['hand_r'],side);radius=27 if not side else 42
                d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=color,width=5)
            elif ep=='A15' and index>=30:
                x,y=projected(study,trace[index]['hand_r'],side)
                d.rectangle((x-110,y-10,x+105,min(785,y+230)),outline=color,width=5)
    return im
def meter(d,x,w,clock):
    for a,b,c in [(0,12,'#82cec0'),(12,18,'#ed9583'),(18,48,'#d8c87e')]:d.rectangle((x+w*a/48,778,x+w*b/48-3,794),fill=c)
    px=x+w*min(48,clock)/48;d.polygon([(px,774),(px-9,758),(px+9,758)],fill='white')
def a03_topics(path):
    tree=ast.parse(path.read_text('utf-8'))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='topics' for t in n.targets))
def a03_images(s,topics):
    pid=int(s['paragraph']);ch=int(s['chapter']);n=s['frames'];seq=int(s['inPoint'])
    title,legend,lt,rt=topics[pid];compare=13<=pid<=18
    left='A03-noinput' if pid==18 else 'A03-cancel48' if compare else 'A03-attack'
    right='A03-cancel36' if compare else 'A03-attack'
    metadata={k:read(NATIVE/'studies'/(k+'.json')) for k in (left,right)}
    trace={k:d['trace'] for k,d in metadata.items()}
    contact=18+metadata['A03-attack' if not compare else right]['contactEvidence']['firstContactFrame']
    segments={2:(18,18,24),3:(23,contact-2,contact+2),4:(18,18,25),5:(18,18,25),6:(18,18,25),
              7:(23,contact-2,contact+2),8:(23,contact-2,contact+2),9:(contact-1,contact,contact+2),
              10:(contact,contact+4,65),11:(18,40,65),12:(contact+4,50,68),19:(18,contact-2,contact+2),
              20:(23,contact-2,contact+2),21:(23,40,65)}
    cached=None;previous=None
    for f in range(n):
        u=(f+.5)/n
        if compare:fa=fb=round(18+min(77,78*u))
        elif pid in segments:
            fa,start,end=segments[pid];fb=round(start+(end-start)*min(1,u*1.5))
        else:fa=18;fb=min(84,max(0,int(12+u*80)))
        identity=fa,fb
        if identity==previous:yield cached;continue
        im=Image.new('RGB',(1920,1080),'#101712');d=ImageDraw.Draw(im)
        text(d,(78,58),title,66,'#f2d787');text(d,(1430,83),'언리얼 · 클립 기반 시연',29,'#bdd3c5')
        for x,key,k,caption in ((78,left,fa,lt),(1017,right,fb,rt)):
            native=frame(key,k).crop((160,0,1760,1080)).resize((825,557),Image.Resampling.LANCZOS)
            im.paste(native,(x,185));text(d,(x,137),caption,33,'#91d0b8' if x==78 else '#f2cd89')
            rec=trace[key][k]
            if pid in (8,9,20) and rec['hit'] and rec['simulationFrame']<=20:
                study=metadata[key];target=rec['target'];width=study['cameraWidth'];height=study['cameraHeight']
                px=x+(960+target[0]*1920/width-160)*825/1600;py=185+(540-(target[2]-height)*1920/width)*557/1080
                d.ellipse((px-30,py-30,px+30,py+30),outline='#d94735',width=7)
            if compare:meter(d,x,825,rec['simulationFrame'])
        rec=trace[right][fb]
        if not compare:meter(d,80,1760,rec['simulationFrame'])
        text(d,(80,831),legend,42)
        cached=im;previous=identity;yield im
def a02_images(s):
    study=study_data('A02-combat');preview=s['id']=='A02-E004'
    last=None;cached=None
    for f in range(s['frames']):
        sec=f/60;first=not preview and sec<5.4
        if preview:index=min(179,f+12)
        elif first:index=min(144,f+12)
        elif sec<8.6:index=12
        elif sec<11.4:index=min(179,12+int((sec-8.6)*60))
        else:index=min(85,32+int((sec-11.4)*12))
        identity=index,first
        if identity==last:yield cached;continue
        im=Image.new('RGB',(1920,1080),'#101713');d=ImageDraw.Draw(im);native=frame('A02-combat',index)
        text(d,(78,55),'화면 크기에 묻히지 않는 동작',61,'#f2d787')
        text(d,(1370,77),'언리얼 · 실제 클립 기반 비교',29,'#b9d2c3')
        for side,x in enumerate((78,1017)):
            crop=(0 if first or not side else 960,150,960 if first or not side else 1920,798)
            plate=native.crop(crop).resize((825,557),Image.Resampling.LANCZOS)
            scale=1. if preview or (first and not side) else .64
            if scale<1:
                board=Image.new('RGB',(825,557),'#e5e6e5');small=plate.resize((round(825*scale),round(557*scale)),Image.Resampling.LANCZOS);board.paste(small,((825-small.width)//2,(557-small.height)//2));plate=board
            im.paste(plate,(x,185))
            label=('같은 동작 · 큰 화면' if not side else '같은 동작 · 작은 화면') if first else ('기본 회전 진폭 1.0×' if not side else '어깨·허리 회전 진폭 1.8×')
            text(d,(x,135),label,35,'#92d4bb' if not side else '#f3ce82')
        text(d,(78,810),'동일한 동작도 화면에서 차지하는 크기가 달라집니다.' if first else '모델 크기·카메라·재생 시간 고정  /  선택한 관절의 회전만 확대',39)
        cached=im;last=identity;yield im
def series_images(ep,s,study,visual):
    key=ep+'-'+s['key'];last=None;cached=None
    for f in range(s['frames']):
        index,mode=state_index(f,s['frames'],study)
        if key in ('A04-anticipation','A11-kick'):
            span=12 if ep=='A04' else 8
            index=12+round(span*f/max(1,s['frames']-1))
            mode='프레임 확대 분석'
        identity=index,mode
        if identity==last:yield cached;continue
        im=frame(key,index).copy()
        if ep=='A16' and s['key']=='path':im.paste(frame('A16-overhead',index).crop((960,0,1920,1080)),(960,0))
        if ep=='A13' and s['key']=='direction':im.paste(frame('A13-observer',index).crop((960,0,1920,1080)),(960,0))
        im=guides(ep,s['key'],study,index,im);d=ImageDraw.Draw(im)
        d.line((960,112,960,794),fill='#98a69f',width=3)
        if s['key']=='outline':
            a=np.array(im);region=a[210:795,960:]
            mask=binary_fill_holes(binary_closing(region.mean(axis=2)<160,iterations=6))
            components,count=connected_labels(mask);sizes=np.bincount(components.ravel());sizes[0]=0
            region[components==sizes.argmax()]=[21,30,26];im=Image.fromarray(a);d=ImageDraw.Draw(im)
        d.rectangle((42,37,690,104),fill='#14261f');text(d,(64,52),'언리얼 · 실제 클립 기반 비교',34,'#e7efe7')
        labels=visual['studyLabels'][s['key']]
        if ep=='A07':labels=['작은 몸짓','큰 몸짓'] if s['key']=='gesture' else ['같은 동작','같은 동작']
        if ep=='A08' and s['key']=='flow':labels=['상체를 고정','머리·어깨·골반의 흐름']
        for side,label in enumerate(labels):
            x=75+side*960;w=d.textlength(label,font=font(37))+40
            d.rounded_rectangle((x,130,x+w,199),radius=8,fill='#28443a');text(d,(x+17,143),label,37)
        focus=s['focus'];w=d.textlength(focus,font=font(35))+42
        d.rounded_rectangle((46,804,46+w,870),radius=9,fill='#13241e');text(d,(65,817),focus,35,'#f5d983')
        text(d,(1645,57),mode,29,'#355a49')
        if ep=='A11' and s['key']=='kick':
            d.rectangle((1120,37,1600,104),fill='#14261f')
            text(d,(1140,52),'준비 → 타격 8F · 60fps',30)
        if ep=='A14':
            length=(1 if not side else 14) if s['key']=='blend' else 24
            for side in (0,1):
                length=(1 if not side else 14) if s['key']=='blend' else (6 if not side else 24)
                z=np.clip((index-42)/length,0,1);weight=z*z*(3-2*z);x=70+960*side
                d.rectangle((x,690,x+340,766),fill='#172721');text(d,(x+12,704),f'걷기 가중치 {weight:.2f}',29)
        if ep=='A06':
            clock=min(60,max(0,index-12))
            for side in (0,1):
                x=75+960*side;value=min(clock,15) if s['key']=='timing' and not side else clock
                d.rectangle((x,699,x+530,773),fill='#172721')
                state='준비' if value<15 else '타격' if value==15 else '후속 동작'
                if s['key']=='control' and value>=(42 if side else 60):state='다음 행동 가능'
                text(d,(x+12,714),f'{value} / 60 F   ·   '+state,30)
        cached=im;last=identity;yield im
def main(ep):
    pending=NATIVE/'pending-native-updates.json'
    if pending.is_file():assert ep not in read(pending),'Native correction must finish before '+ep
    plan=read(H/'revision-plan.json');row=next(e for e in plan['episodes'] if e['id']==ep)
    p=R/'projects'/row['slug'];base=p/'production/local'/row['baselineRevision'];oldh=p/'production'/row['baselineRevision']
    l=p/'production/local/real-clips-v2';v=l/'picture';v.mkdir(parents=True,exist_ok=True)
    control=read(R/'shared/publishing/video-production-control.json');assert read(B/'batch.json')['renderAuthorized']
    timeline=read(oldh/('edit-plan.json' if ep=='A02' else 'edit-plan-final.json'));parts=[];changed=[];preserved=[]
    audio=base/('edit/pair-audio.m4a' if ep=='A02' else 'audio.m4a');captions=base/'edit' if ep=='A02' else base
    if ep=='A02':
        for s in timeline['cuts']:
            original=base/'edit'/(s['id']+'.mp4')
            if s['id'] not in ('A02-E004','A02-E011'):parts.append(original);preserved.append({'file':str(original),'sha256':sha(original)});continue
            dest=v/original.name;render_cut(dest,a02_images(s),v/(dest.stem+'.log'),s['frames'],s['id']);parts.append(dest);changed.append(s)
    elif ep=='A03':
        topics=a03_topics(oldh/'picture.py')
        for s in timeline['cuts']:
            original=base/'picture'/f"shot-{s['index']:03}.mp4"
            if s['kind']=='game':parts.append(original);preserved.append({'file':str(original),'sha256':sha(original)});continue
            dest=v/original.name;render_cut(dest,a03_images(s,topics),v/(dest.stem+'.log'),s['frames']);parts.append(dest);changed.append(s)
    else:
        visual=read(oldh/'visual-plan.json')
        for i,s in enumerate(timeline['cuts']):
            original=base/'picture'/f'cut-{i:03}.mp4';study=NATIVE/'studies'/(ep+'-'+s['key']+'.json')
            if s['key'] in timeline['sourceEvidence'] or not study.is_file() or (ep=='A04' and s['key']=='jab') or (ep=='A11' and s['key']=='upper'):
                parts.append(original);preserved.append({'file':str(original),'sha256':sha(original)});continue
            dest=v/original.name;render_cut(dest,series_images(ep,s,read(study),visual),v/(dest.stem+'.log'),s['frames'],s['key']);parts.append(dest);changed.append(s)
    assert changed
    concat=v/'parts.txt';concat.write_text(''.join("file '"+str(f).replace('\\','/')+"'\n" for f in parts),'utf-8')
    ff(['-f','concat','-safe','0','-i',concat,'-c','copy',l/'body.mp4'],l/'join.log')
    body=l/'body.mp4'
    if ep=='A02':
        # This older edit uses B-frames and a different video time base.
        # Preserve every picture in its order and assign a new exact 60 Hz PTS.
        body=l/'body-normalized.mp4'
        ff(['-threads','2','-i',l/'body.mp4','-vf','settb=1/60,setpts=N','-an',*ENC,body],l/'body-normalize.log')
    branding=base/'edit' if ep=='A02' else R/'projects/animation-assigning/production/local/grid-v1/edit'
    n=timeline['totalFrames'];inputs=[normalized_endcard(branding/'branding.mp4',120),body,normalized_endcard(branding/'membership.mp4',600)]
    # Preserve the already encoded pictures in the clean master. Only caption
    # burn-in needs another encode; validate both complete bitstreams below.
    masterparts=v/'master-parts.txt';masterparts.write_text(''.join("file '"+str(f).replace('\\','/')+"'\n" for f in inputs),'utf-8')
    ff(['-f','concat','-safe','0','-i',masterparts,'-i',audio,'-map','0:v','-map','1:a','-c','copy','-t',n/60,'-video_track_timescale','60000','-movflags','+faststart',l/'clean.mp4'],l/'clean-mux.log')
    regular_packets(l/'clean.mp4',n)
    captionfilter='ass='+str((captions/'captions.ko.ass').relative_to(R)).replace('\\','/')
    ff(['-threads','4','-i',l/'clean.mp4','-vf',captionfilter,'-filter_threads','4','-frames:v',n,*ENC,'-c:a','copy','-movflags','+faststart',l/'captioned.mp4'],l/'caption-encode.log')
    progress=(l/'caption-encode.progress').read_text('utf-8');last={line.split('=',1)[0]:line.split('=',1)[1] for line in progress.splitlines() if '=' in line}
    assert last.get('drop_frames')=='0' and last.get('dup_frames')=='0',last
    receipt={'episode':ep,'slug':p.name,'revision':'real-clips-v2','changedCuts':changed,'preservedCuts':preserved,'totalFrames':n,'durationSeconds':n/60,'baselineAudio':str(audio),'baselineAudioSHA256':sha(audio),'baselineNarrationPreserved':True,'humanReviewed':False,'platformMutation':False,'masters':{}}
    receipt['changedCutFiles']=[dict(path=str(f),sha256=sha(f)) for f in parts if f.parent==v]
    packet=lambda f:subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
    expected_audio=packet(audio)
    for name in ('clean','captioned'):
        file=l/(name+'.mp4');info=probe(file);stream=next(s for s in info['streams'] if s['codec_type']=='video')
        assert (stream['width'],stream['height'],Fraction(stream['avg_frame_rate']),int(stream['nb_frames']))==(1920,1080,60,n)
        regular_packets(file,n)
        assert packet(file)==expected_audio
        ff(['-xerror','-threads','4','-i',file,'-f','null','-'],l/('decode-'+name+'.log'))
        receipt['masters'][name]={'sha256':sha(file),'format':'1920x1080/60','fullDecode':True,'uniformPTSAndDTS':True,'audioPacketsIdenticalToBaseline':True}
    dest=l/'delivery/output'/p.name;dest.mkdir(parents=True,exist_ok=True)
    for name in ('clean','captioned'):shutil.copy2(l/(name+'.mp4'),dest/(p.name+'.'+name+'.mp4'))
    for lang in ('ko','en'):shutil.copy2(captions/('captions.'+lang+'.srt'),dest/(p.name+'.'+lang+'.srt'))
    title=read(p/'project.json')['title'];links=' · '.join('<a href="'+p.name+'.'+kind+'">'+label+'</a>' for kind,label in [('clean.mp4','무자막'),('captioned.mp4','자막영상'),('ko.srt','한국어 자막'),('en.srt','영어 자막')])
    (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#101713;color:#eee;font:18px/1.6 sans-serif;max-width:1100px;margin:30px auto;padding:16px}a{color:#b9e5cb}video{width:100%}</style><h1>'+html.escape(title)+'</h1><p>실제 애니메이션 클립 적용 수정본 · 1080p 60fps</p><video controls playsinline src="'+p.name+'.captioned.mp4"></video><p>'+links+'</p>','utf-8')
    receipt['directory']=str(dest.relative_to(R)).replace('\\','/');(l/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf-8')
    print(ep,'paired and decoded; visual review still pending',flush=True)
if __name__=='__main__':
    lease=R/'shared/output/GPU_HANDOFF.json';token=uuid.uuid4().hex
    with lease.open('x',encoding='utf-8') as f:json.dump(dict(owner='animation-real-clips-v2-assembly',id=token,pid=os.getpid(),createdAt=datetime.now(timezone.utc).isoformat()),f)
    try:main(sys.argv[1])
    finally:
        if lease.is_file() and read(lease).get('id')==token:lease.unlink()
