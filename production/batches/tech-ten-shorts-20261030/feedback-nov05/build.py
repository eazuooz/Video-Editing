"""Re-cut the frozen, delivered ten masters; never read an already revised master as an input."""
import argparse, hashlib, html, json, math, re, shutil, subprocess as sp, wave
from datetime import datetime, timezone
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
MEDIA=Path(read(HERE.parent/'batch.json')['mediaRoot'])
WORK=MEDIA/'feedback-nov05'
BASE=read(MEDIA/'delivery/review-ten-be331655c1ba.json')['projects']
ED=read(HERE/'edit.json')['episodes']
FILES=['clean.mp4','captioned.mp4','captions.ko.srt','captions.en.srt']
@lru_cache(None)
def font(px):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',px)
def header(e,p):
    im=Image.new('RGB',(1080,440));d=ImageDraw.Draw(im)
    for v,y,color in zip(e['head'],(105,230),('white','#FFD25A')):
        px=91
        while font(px).getlength(v)>940:px-=1
        d.text((540,y),v,font=font(px),fill=color,anchor='mm',stroke_width=1)
    d.text((540,374),'얌얌코딩  ·  게임 속 기술',font=font(34),fill='#B8C3BC',anchor='mm');im.save(p)
def srtread(p):
    def sec(s):h,m,t=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(t)
    out=[]
    for block in re.split(r'\n\s*\n',p.read_text(encoding='utf-8-sig').strip()):
        _,tm,*ss=block.splitlines();a,b=tm.split(' --> ');out.append((sec(a),sec(b),'\n'.join(ss)))
    return out
def timestamp(t):
    ms=round(t*1000);return '%02d:%02d:%02d,%03d'%(ms//3600000,ms//60000%60,ms//1000%60,ms%1000)
def srtwrite(p,rows):
    p.write_text('\n\n'.join(f'{i+1}\n{timestamp(a)} --> {timestamp(b)}\n{s}' for i,(a,b,s) in enumerate(rows))+'\n',encoding='utf8')
def wrap(s,limit):
    out=['']
    for w in s.split():
        if out[-1] and font(56).getlength(out[-1]+' '+w)>limit:out.append(w)
        else:out[-1]=(out[-1]+' '+w).strip()
    return out
def pcm(p):
    b=sp.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-'])
    return np.frombuffer(b,dtype='<f4').reshape(-1,2).copy()
def level(x):
    x=x[:len(x)//2400*2400].reshape(-1,2400,2)
    rms=np.sqrt(np.mean(x*x,axis=(1,2)));return np.median(rms[rms>max(.009,np.max(rms)*.075)])
def audio(n,e,old,tmp,frame):
    base=old.parent/'audio-v1'; orig=pcm(base/'final-mix.wav');music=pcm(base/'music-stem.wav');voice=pcm(base/'narration-stem.wav')
    # Final audio of this immutable review must be the same timeline as its PCM.
    if abs(len(orig)/48000-BASE[n-1]['seconds'])>.12:raise ValueError(('audio/master duration',n,len(orig)/48000))
    split=frame*800; parts=[np.zeros((5760,2),'f')]; cues=[[],[]]
    for j,lines in enumerate(e['lines'],1):
        path=ROOT/f'shared/output/tech-ten-feedback-nov05/extra-speech/chunks/{n:02}-{j:02}.wav'
        gpu=ROOT/f'shared/output/tech-ten-feedback-nov05/gpu/chunks/{n:02}-{j:02}-scene.wav'
        if gpu.exists():path=gpu
        if (tmp/'voice-files.json').exists():
            pin=read(tmp/'voice-files.json')[str(j)];path=Path(pin['path']);assert sha(path)==pin['sha256']
        v=pcm(path);v*=min(3,float(level(voice)/level(v)));t=sum(map(len,parts))/48000
        parts.extend([v,np.zeros((12000,2),'f')])
        for k,s in enumerate(lines):
            # Keep clauses on natural sentence, comma or word boundaries and inside the new take.
            groups=re.split(r'(?<=[.!?,])\s+',s.strip());groups=[g for g in groups if g]
            gs=[]
            for g in groups:
                w=wrap(g,820)
                gs.extend(' '.join(w[i:i+2]) for i in range(0,len(w),2))
            weights=[len(g.replace(' ','')) for g in gs];z=0
            for g,wt in zip(gs,weights):
                a=t+len(v)/48000*z/sum(weights);z+=wt;b=t+len(v)/48000*z/sum(weights)
                cues[k].append((a,b,'\n'.join(wrap(g,820))))
    ins=np.concatenate(parts);nd=math.ceil(len(ins)/800);ins=np.pad(ins,((0,nd*800-len(ins)),(0,0)))
    # The previous BGM bed already carries the correct rights and ducking.
    bed=music[split:split+len(ins)].copy()
    if len(bed)<len(ins):bed=np.concatenate([bed,music[24000:24000+len(ins)-len(bed)]])
    fade=2400;bed[-fade:]*=np.linspace(1,0,fade)[:,None];bed[-fade:]+=music[max(0,split-fade):split]*np.linspace(0,1,fade)[:,None]
    ins+=bed[:len(ins)];out=np.concatenate([orig[:split],ins,orig[split:]])
    with wave.open(str(tmp/'mix.wav'),'wb') as w:
        w.setparams((2,2,48000,0,'NONE',''));w.writeframes((np.clip(out,-.996,.996)*32767).astype('<i2').tobytes())
    for k,lang in enumerate(['ko','en']):
        origc=srtread(old/f'captions.{lang}.srt');cut=frame/60
        if any(a+.003<cut<b-.003 for a,b,_ in origc):raise ValueError(('splice inside original cue',n,cut))
        rows=[(a+(nd/60 if a>=cut-.003 else 0),b+(nd/60 if a>=cut-.003 else 0),s) for a,b,s in origc]
        rows+= [(cut+a,cut+b,s) for a,b,s in cues[k]]
        srtwrite(tmp/f'captions.{lang}.srt',sorted(rows))
    # ASS for new cues only; retain actual approved old captions directly from its old video.
    ass=(base/'captions.ko.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    def at(t):v=round(t*100);return f'0:{v//6000:02}:{v//100%60:02}.{v%100:02}'
    for a,b,s in cues[0]:
        lines=s.splitlines();width=max(font(56).getlength(st) for st in lines)+80;left=round(510-width/2);right=round(510+width/2);top=1380-39*len(lines)-14;bottom=2760-top
        prefix=f'{at(frame/60+a)},{at(frame/60+b)}'
        for layer,offset,col in [(10,10,'323C07'),(11,0,'FFFFFF')]:
            ass+=f'Dialogue: {layer},{prefix},Box,,0,0,0,,{{\\an7\\pos(0,0)\\1c&H{col}&\\p1}}m {left+offset} {top+offset} l {right+offset} {top+offset} {right+offset} {bottom+offset} {left+offset} {bottom+offset}\n'
        for ix,st in enumerate(lines):
            ass+=f'Dialogue: 12,{prefix},Text,,0,0,0,,{{\\an5\\pos(510,{1380+(2*ix-len(lines)+1)*39})\\fs56}}{st}\n'
    (tmp/'addition.ass').write_text(ass,encoding='utf8');return nd
def run(args,cwd=None):sp.run(args,check=True,cwd=cwd)
def probe(path):return json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))['streams']
def build(n, *, source=None, edit=None, scratch=None, directory='final-reviewed-feedback-nov05-r2',
          revision='feedback-20261105', body_ranges=None, draw_body=None, description=None):
    row=source if source is not None else BASE[n-1]
    e=edit if edit is not None else ED[n-1]
    old=Path(row['finalDirectory'])
    tmp=Path(scratch) if scratch is not None else WORK/f'{n:02}-r2'
    dest=old.parent/directory
    tmp.mkdir(parents=True,exist_ok=True);dest.mkdir(exist_ok=True)
    if (dest/'delivery.json').is_file():
        done=read(dest/'delivery.json')
        if all(sha(dest/x['name'])==x['sha256'] for x in done['files']):print(n,'already verified',flush=True);return
        raise ValueError('Changed finished master')
    for f in row['files']:
        assert sha(old/f['name'])==f['sha256']
    header(e,tmp/'header.png');frame=e.get('insertFrame',0);extra=audio(n,e,old,tmp,frame) if frame else 0
    for lang in ['ko','en']:
        name=f'captions.{lang}.srt';shutil.copyfile((tmp if frame else old)/name,dest/name)
    total=row['frames']+extra
    ranges=body_ranges if body_ranges is not None else {1:(689,1471),2:(400,2558),3:(402,2054),6:(922,923),8:(2478,2479),10:(459,2575)}
    if n in ranges:
        from visuals import make
        a,b=ranges[n]
        if draw_body is None:make(n,tmp/'body.mp4',a,b+extra,frame,extra,WORK)
        else:draw_body(n,tmp/'body.mp4',a,b+extra,frame,extra,tmp)
    for kind in ('clean','captioned'):
        args=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-threads','3','-i',str(old/(kind+'.mp4')),'-i',str(tmp/'header.png')]
        graph=[]
        if extra:
            graph+=[f'[0:v]split[x][y];[x]trim=end_frame={frame},setpts=PTS-STARTPTS,tpad=stop={extra}:stop_mode=clone[u];[y]trim=start_frame={frame},setpts=PTS-STARTPTS[v];[u][v]concat=n=2:v=1:a=0,settb=1/60,setpts=N[vbase]']
        else:graph+=['[0:v]null[vbase]']
        graph+=['[vbase][1:v]overlay=0:0[vtitle]']
        if n==2:graph+=[f"[vtitle]drawbox=x=0:y=0:w=1080:h=440:color=black:t=fill:enable='gte(t,{(total-31)/60:.8f})'[vhead]"]
        else:graph+=['[vtitle]null[vhead]']
        vid='vhead';audioidx=0
        if n in ranges:
            args+=['-i',str(tmp/'body.mp4')];graph +=[f"[2:v]setpts=PTS-STARTPTS+{a}/60/TB[art];[{vid}][art]overlay=x=0:y=440:eof_action=pass:enable='gte(t,{a/60:.8f})*lt(t,{(b+extra)/60:.8f})'[vb]"];vid='vb'
        if extra:
            audioidx=3;args+=['-i',str(tmp/'mix.wav')]
            if kind=='captioned':
                graph +=[f"[{vid}]drawbox=x=0:y=1278:w=1080:h=230:color=black:t=fill:enable='gte(t,{frame/60:.8f})*lt(t,{(frame+extra)/60:.8f})',ass=addition.ass[vc]"];vid='vc'
        args+=['-filter_complex_threads','3','-filter_complex',';'.join(graph),'-map',f'[{vid}]','-map',f'{audioidx}:a:0','-c:v','libx264','-threads','5','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p','-r','60','-c:a',('aac' if extra else 'copy')]
        if extra:args+=['-b:a','256k']
        args+=['-movflags','+faststart',str(dest/(kind+'.mp4'))];run(args,tmp)
        st=probe(dest/(kind+'.mp4'));sv=next(s for s in st if s['codec_type']=='video');sa=next(s for s in st if s['codec_type']=='audio')
        if (sv['width'],sv['height'],sv['r_frame_rate'],int(sv['nb_frames']))!=(1080,1920,'60/1',total) or abs(float(sa['duration'])-total/60)>.15:raise RuntimeError((n,sv['nb_frames'],total,sa['duration']))
    # Mobile review transcode carries the new full audio.
    run(['ffmpeg','-v','error','-y','-threads','3','-i',str(dest/'captioned.mp4'),'-vf','scale=376:-2','-c:v','libx264','-threads','3','-preset','ultrafast','-crf','22','-c:a','copy','-movflags','+faststart',str(dest/'mobile-review.mp4')])
    metadata={'title':e['title'],'description':description if description is not None else row['description']}
    if n==10 and description is None:metadata['description']+='\n자체 Unity 시연 모델: Army Pack – Cute Series (얌얌코딩 보유 에셋). 부대 6기·포탑·격납고는 원리를 설명하기 위한 자체 재현입니다.'
    receipt=dict(revision=revision,generatedAt=datetime.now(timezone.utc).isoformat(),width=1080,height=1920,fps=60,frames=total,durationSeconds=total/60,**metadata,files=[dict(name=k,path=str(dest/k),sha256=sha(dest/k),bytes=(dest/k).stat().st_size) for k in FILES],baseMasterSha256=row['masterSha256'],additionFrames=extra,localFinalReview='awaiting-human-review',actualCompleteHumanListening=False,youtubeUploaded=False,driveUploaded=False)
    save(dest/'metadata.json',metadata);(dest/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['name']+'\n' for x in receipt['files']),encoding='ascii')
    ko=srtread(dest/FILES[2]);safe=html.escape
    pg='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#101413;color:white;font:18px/1.7 Malgun Gothic,sans-serif;max-width:800px;padding:1rem;margin:auto}video{width:min(100%,375px);display:block;margin:auto}button,a{color:#86dfc3}button{background:#17221e;border:1px solid #34483c;cursor:pointer;font:inherit}h1{font-size:1.4em;color:#ffd25a}</style><h1>'+safe(e['title'])+'</h1><video controls playsinline preload="metadata" src="captioned.mp4"></video><p><a href="captioned.mp4">전체 자막 MP4</a> · <a href="clean.mp4">무자막</a> · <a href="captions.ko.srt">한국어</a> · <a href="captions.en.srt">English</a></p><h2>대본 검수</h2>'+''.join(f'<p><button data-sec="{a}">{int(a)//60}:{int(a)%60:02}</button> {safe(s.replace(chr(10)," "))}</p>' for a,b,s in ko)+'<script>const v=document.querySelector("video");document.querySelectorAll("button").forEach(b=>b.onclick=()=>{v.currentTime=Number(b.dataset.sec);v.play();});</script></html>'
    (dest/'index.html').write_text(pg,encoding='utf8');save(dest/'delivery.json',receipt);print(n,e['title'],total,flush=True)
if __name__=='__main__':
    import sys
    for num in sys.argv[1:]:build(int(num))
