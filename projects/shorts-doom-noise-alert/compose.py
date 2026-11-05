"""Cut original Freedoom footage and narrated sector diagrams into the daily arm's local review files."""
import bisect
import csv
import hashlib
import html
import json
import math
import shutil
import subprocess
import sys
import time
import wave
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

PROJECT=Path(__file__).resolve().parent
ROOT=PROJECT.parents[1]
sys.path.insert(0,str(ROOT/'production/batches/tech-ten-shorts-20261030/feedback-nov05'))
import build as ed
from visuals import frame,foot,label,arrow,line,glyph,TEAL,GOLD,RED,MUTE,WHITE,clamp,smooth
PLAN=ed.read(PROJECT/'plan.json')
MEDIA=Path(ed.read(PROJECT/'project.json')['mediaRoot'])
RAW=MEDIA/'raw'
FINAL=MEDIA/'final-reviewed-v2'
WORK=MEDIA/'edit'
FINAL.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
MUSIC=ROOT/'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3'
CATS=ROOT/'shared/assets/branding/cat-reactions-v1'
DESC=('같은 복도에서 같은 자리에 서서 총을 한 번 쐈습니다. 첫 번째 경계만 소리 차단으로 지정하면 돌아보던 괴물이, 두 번째 경계에도 표시를 켜자 가만히 있습니다. 둠의 섹터 경보 전파(P_NoiseAlert, P_RecursiveSound)를 실제 플레이와 움직이는 지도로 설명합니다.\n\n'
      '게임 화면: Freedoom: Phase 2, Contributors to the Freedoom project. MAP04·MAP02는 원래 캠페인을 직접 플레이했고, 복도 비교는 같은 엔진에서 얌얌코딩이 만든 실험 레벨입니다. 원게임 음원은 제외했습니다. Freedoom 저작권·BSD 라이선스: https://github.com/freedoom/freedoom/blob/master/COPYING.adoc\n'
      '기술 자료: https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_enemy.c · 실제 실행한 포트: https://github.com/Farama-Foundation/ViZDoom/blob/1.3.2/src/vizdoom/src/p_enemy.cpp\n'
      '음악: Pixel Peeker Polka - faster, Kevin MacLeod (incompetech.com). 편집·음량 조정. CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/')

def sequence_audio():
    records=[];chunks=[];captions=[[],[]];time_frames=0;spoken=[]
    for i,langs in enumerate(PLAN['lines'],1):
        wav=ROOT/f'shared/output/shorts-doom-noise-alert/voice-v1/chunks/s{i:02}-scene.wav'
        if not wav.is_file():raise RuntimeError('Wait for the selected voice file: '+str(wav))
        v=ed.pcm(wav);v*=min(3,0.0794/ed.level(v));pre=5760 if i==1 else 0
        count=math.ceil((pre+len(v)+12000)/800)
        chunk=np.zeros((count*800,2),np.float32);chunk[pre:pre+len(v)]=v
        start=time_frames/60;voicestart=start+pre/48000;duration=len(v)/48000
        for k,s in enumerate(langs):
            import re
            phrases=re.split(r'(?<=[.!?,])\s+',s)
            cue=[]
            for phrase in phrases:
                wraps=ed.wrap(phrase,824)
                cue+=['\n'.join(wraps[j:j+2]) for j in range(0,len(wraps),2)]
            weights=[len(t.replace(' ','').replace('\n','')) for t in cue];acc=0;last=0
            for j,(st,weight) in enumerate(zip(cue,weights)):
                acc+=weight;estimate=duration*acc/sum(weights)
                if j==len(cue)-1:end=duration
                else:
                    offsets=np.arange(max(last+.15,estimate-.25),min(duration-.15,estimate+.25),.015)
                    end=estimate if not len(offsets) else min(offsets,key=lambda t:np.mean(v[int(t*48000):int(t*48000)+480]**2)+.001*abs(t-estimate))
                captions[k].append((voicestart+last,voicestart+end,st));last=end
        time_frames+=count;records.append(dict(n=i,start=start,end=time_frames/60,source=str(wav),sha256=ed.sha(wav)))
        chunks.append(chunk);spoken.append(v)
    voice=np.concatenate(chunks)
    assert ed.sha(MUSIC)=='b2609a077fae292679f25b83519f470ed308abb40d11f89bff8c6f896deefed3'
    bg=ed.pcm(MUSIC)[48000:48000+len(voice)]
    # Match the quiet music bed to the narration, lift slightly between phrases.
    rms=np.sqrt(np.mean(bg*bg));gain=.013/max(rms,.001)
    vol=np.sqrt(np.mean(voice.reshape(-1,800,2)**2,axis=(1,2)))
    envelope=np.convolve(np.clip(vol/.035,0,1),np.ones(9)/9,'same')
    bed=bg*gain*np.repeat(1-.34*envelope,800)[:,None];bed[:12000]*=np.linspace(0,1,12000)[:,None]
    bed[-21600:]*=np.linspace(1,0,21600)[:,None];mix=voice+bed
    peak=float(np.max(abs(mix)));mix*=min(1,.946/peak)
    with wave.open(str(WORK/'mix.wav'),'wb') as w:
        w.setparams((2,2,48000,0,'NONE',''));w.writeframes((mix*32767).astype('<i2').tobytes())
    for lang,cues in zip(['ko','en'],captions):ed.srtwrite(FINAL/f'captions.{lang}.srt',cues)
    write_ass(captions[0])
    ed.save(WORK/'timing.json',records);return records,time_frames

def write_ass(cues):
    style=(ROOT/'projects/shorts-alyx-liquid-shader/production/local/audio-v1/captions.ko.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    def at(t):
        n=round(t*100);return f'0:{n//6000:02}:{n//100%60:02}.{n%100:02}'
    events=[]
    for a,b,st in cues:
        lines=st.splitlines();w=max(ed.font(56).getlength(line) for line in lines)+74
        assert w<965 and len(lines)<=2
        l,r=round(510-w/2),round(510+w/2);t=1380-39*len(lines)-14;bt=2760-t;times=f'{at(a)},{at(b)}'
        for layer,off,color in [(10,10,'323C07'),(11,0,'FFFFFF')]:
            events.append(f'Dialogue: {layer},{times},Box,,0,0,0,,{{\\an7\\pos(0,0)\\1c&H{color}&\\p1}}m {l+off} {t+off} l {r+off} {t+off} {r+off} {bt+off} {l+off} {bt+off}')
        for j,ln in enumerate(lines):
            for word in ['소리 차단','섹터','경보']:
                if word in ln:ln=ln.replace(word,'{\\1c&H595000&}'+word+'{\\1c&H090B08&}',1);break
            events.append(f'Dialogue: 12,{times},Text,,0,0,0,,{{\\an5\\pos(510,{1380+(2*j-len(lines)+1)*39})\\fs56}}{ln}')
    (WORK/'sub.ass').write_text(style+'\n'.join(events)+'\n',encoding='utf8')

used=['campaign-map04-shot-fhd','campaign-map04-quiet-fhd','test-one-map01-shot-fhd','test-two-map01-shot-fhd','campaign-map02-shot-fhd']
def prepare_frames():
    sourceinfo={}
    for k in used:
        folder=RAW/k;movie=folder/'actual.mp4';s=next(x for x in ed.probe(movie) if x['codec_type']=='video')
        assert (s['width'],s['height'],s['r_frame_rate'])==(1920,1080,'35/1')
        dest=WORK/k;dest.mkdir(exist_ok=True)
        if not (dest/'complete').is_file():
            ed.run(['ffmpeg','-hide_banner','-v','error','-y','-threads','2','-i',str(movie),'-q:v','3','-start_number','0',str(dest/'%04d.jpg')])
            (dest/'complete').write_text(ed.sha(movie))
        assert (dest/'complete').read_text()==ed.sha(movie)
        sourceinfo[k]=dict(path=str(movie),sha256=ed.sha(movie),width=1920,height=1080,fps=35,frames=int(s['nb_frames']))
    ed.save(PROJECT/'source-footage.json',sourceinfo);return sourceinfo
@lru_cache(5)
def boxes(key):return ed.read(RAW/key/'visible-object.json')
def actual(key,seconds,size,zoom=False,close=False,mark=False):
    frame_id=int(seconds*35)
    p=WORK/key/f'{frame_id:04d}.jpg'
    if not p.is_file():raise ValueError(f'Out-of-range real footage: {p}')
    with Image.open(p) as img:
        # Centered aspect-preserving cut. The test monster stands to the right of the reticle.
        w,h=img.size;cx=w*(.57 if key.startswith('test-') else .5);cy=h*.49
        cw=round(w*(.255 if close else .63 if zoom else .82));ch=round(cw*size[1]/size[0])
        if close:cx,cy=1141,578
        if ch>h:ch=h;cw=round(h*size[0]/size[1])
        x=round(max(0,min(w-cw,cx-cw/2)));y=round(max(0,min(h-ch,cy-ch/2)))
        result=img.crop((x,y,x+cw,y+ch)).resize(size,Image.Resampling.LANCZOS)
        if mark:
            tracked=boxes(key);actor_id=tracked[0][0]['id'];actor=next((a for a in tracked[frame_id] if a['id']==actor_id),None)
            if actor:
                sx,sy=size[0]/cw,size[1]/ch
                bounds=[(actor['x']-x)*sx-9,(actor['y']-y)*sy-7,(actor['x']+actor['w']-x)*sx+9,(actor['y']+actor['h']-y)*sy+7]
                ImageDraw.Draw(result).ellipse(bounds,outline=TEAL,width=5)
        return result
def bar(im,x,y,text,color=WHITE,sz=30):
    d=ImageDraw.Draw(im);g=glyph(text,sz,color);d.rounded_rectangle((x-8,y-7,x+g.width+8,y+g.height+7),radius=8,fill='#102020');label(im,x,y,text,sz,color)
def map_view(t,stage,second,bypass=False):
    title='옆방까지 어떻게 전해질까?' if stage==0 else ('둘째 경계에서 멈추는 경보' if second else '첫째 경계 너머로 가는 경보')
    im,d=frame(1,title,'원리 도식  /  위에서 본 복도')
    left=72;step=311;top=303;bottom=524
    for i in range(3):
        x=left+i*step;active=(i==0 or (i==1 and t>.23) or (i==2 and (not second or bypass) and t>.69))
        d.rectangle((x,top,x+step,bottom),fill='#185348' if active else '#213136',outline=MUTE,width=4)
        label(im,x+step/2,top+26,['A · 플레이어','B · 통로','C · 괴물'][i],32,WHITE,True)
    for i in [1,2]:
        x=left+i*step;flag=stage!=0 and (i==1 or second)
        d.line((x,top+73,x,bottom-24),fill=GOLD if flag else MUTE,width=7)
        if flag:label(im,x,top-55,'표시 '+str(i),30,GOLD,True)
    source=(left+90,445)
    d.ellipse((source[0]-14,source[1]-14,source[0]+14,source[1]+14),fill=TEAL)
    if t>.06:
        endx=left+step*2-13 if second else left+step*2+160
        x=source[0]+(endx-source[0])*smooth((t-.06)/.64);arrow(d,source,(max(source[0]+3,x),source[1]),TEAL,10)
    if second and t>.57:
        x=left+step*2;d.line((x-12,427,x+12,457),fill=RED,width=8);d.line((x+12,427,x-12,457),fill=RED,width=8)
    if bypass and t>.68:
        pts=[(left+step+120,515),(left+step+120,611),(left+step*2+161,611),(left+step*2+161,521)]
        line(d,pts[:3],TEAL,7);arrow(d,pts[2],pts[3],TEAL,7)
        label(im,350,642,'열린 우회로가 있다면',31,TEAL)
    foot(im,d,'연결된 구역을 따라 경보가 퍼져요' if stage==0 else ('이 경로에서 두 번째 표시는 통과하지 못해요' if second else '표시 한 개는 통과해요'));return im
def gameplay(key,local,heading,status,extra,zoom=False):
    im,d=frame(1,heading,'Freedoom · 실제 캠페인' if key.startswith('campaign') else 'Freedoom 엔진 · 동일 복도 실험')
    focus=(key in used[:2] and .1<local<3.3) or (key in used[2:4] and 1.15<local<3.4)
    im.paste(actual(key,local,(986,530),zoom,mark=focus),(47,176));bar(im,70,198,status,TEAL)
    foot(im,d,extra);return im
def pair(t):
    im,d=frame(1,'한 번 쏘고, 같은 순간을 비교','Freedoom 실험  /  둘째 경계의 표시만 바꿨어요')
    for i,k in enumerate(['one','two']):
        x=44+i*506
        im.paste(actual(f'test-{k}-map01-shot-fhd',t,(482,390),True,close=True),(x,259));col=TEAL if i==0 else GOLD
        d.rectangle((x,259,x+482,649),outline=col,width=4);label(im,x+241,183,'표시 하나' if i==0 else '표시 둘',37,col,True)
    foot(im,d,'왼쪽은 돌아보고, 오른쪽은 등을 보여요');return im
def visuals(n,t,dur):
    u=t/dur
    if n==1:
        if t<2.80:return gameplay(used[0],t+.5,'총을 쏘자 괴물이 돌아봅니다','총 한 발' if t>=.5 else '발사 직전','등을 보이던 괴물에 주목하세요',True)
        return gameplay(used[1],max(0,t-2.80),'같은 자리에서 기다리면?','발사하지 않음','같은 캠페인 · 같은 시작 위치',True)
    if n==2:return map_view(u,0,False)
    if n==3:
        if t<6:return gameplay(used[2],t,'첫 경계만 표시한 복도','표시 하나','괴물을 비껴서 벽을 쏩니다',True)
        return map_view(.55+.45*(t-6)/max(dur-6,.1),1,False)
    if n==4:
        if t<2.45:return gameplay(used[3],t,'둘째 경계에도 표시하면?','표시 둘','같은 복도 · 같은 거리 · 같은 공격',True)
        return pair(min(6.82,t-.7))
    if n==5:return map_view(u,1,True,bypass=u>.71)
    if n==6:
        im,d=frame(1,'무엇이 막혔을까?','같은 발사  /  서로 다른 두 가지 계산')
        im.paste(actual(used[3],min(6.8,t),(488,374),True),(44,253))
        label(im,570,263,'괴물에게',37,TEAL);label(im,570,321,'경보가 닿았나?',37,WHITE)
        label(im,570,458,'플레이어에게',37,GOLD);label(im,570,516,'얼마나 크게 들리나?',35,WHITE)
        foot(im,d,'지도 경계가 막은 것은 괴물 경보');return im
    if t<3.7:return pair(min(6.85,t+1))
    return gameplay(used[4],min(6.75,t-2.75),'어느 구역까지 깨울까?','캠페인에서 다시 보기','경계를 어떻게 놓았는지가 결과를 바꿔요',True)
@lru_cache(3)
def cat(pose):
    im=Image.open(CATS/(pose+'.png')).convert('RGBA');im=im.crop(im.getbbox());return im.resize((492,round(im.height*492/im.width)),Image.Resampling.LANCZOS)
def render(records,frames):
    ed.header({'head':PLAN['head']},WORK/'header.png')
    header=Image.open(WORK/'header.png').convert('RGB')
    times=[r['end'] for r in records]
    command=['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','60','-i','pipe:0','-i',str(WORK/'mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','5','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(FINAL/'clean.mp4')]
    with subprocess.Popen(command,stdin=subprocess.PIPE) as proc:
        for f in range(frames):
            t=f/60;idx=min(len(records)-1,bisect.bisect_right(times,t));r=records[idx];dt=t-r['start'];dur=r['end']-r['start']
            im=Image.new('RGB',(1080,1920));im.paste(header,(0,0));im.paste(visuals(idx+1,dt,dur),(0,440))
            if idx in [3,6] and .7<dt<min(2.7,dur-.1):
                bust=cat('realize' if idx==3 else 'relief');ease=smooth((dt-.7)/.24)*smooth((min(2.7,dur-.1)-dt)/.24)
                pos=(int(1080-bust.width+18+(1-ease)*75),int(1920-bust.height+8+(1-ease)*45))
                if ease<.99:
                    bust=bust.copy();bust.putalpha(bust.getchannel('A').point(lambda v:int(v*ease)))
                im.paste(bust,pos,bust)
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Clean encoding failed')
    ed.run(['ffmpeg','-nostdin','-v','error','-y','-threads','3','-i',str(FINAL/'clean.mp4'),'-vf','ass=sub.ass','-c:v','libx264','-threads','5','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(FINAL/'captioned.mp4')],cwd=WORK)
def deliver(records,frames):
    files=[]
    for name in ed.FILES:
        p=FINAL/name;files.append(dict(name=name,path=str(p),sha256=ed.sha(p),bytes=p.stat().st_size))
    ed.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(FINAL/'captioned.mp4'),'-vf','scale=376:-2','-c:v','libx264','-threads','3','-preset','ultrafast','-crf','21','-c:a','copy','-movflags','+faststart',str(FINAL/'mobile.mp4')])
    d=dict(revision='daily-doom-alert-v2',title=PLAN['title'],description=DESC,frames=frames,durationSeconds=frames/60,width=1080,height=1920,fps=60,files=files,actualCompleteHumanListening=False,humanFinalReview='pending',platformActions=False)
    ed.save(FINAL/'delivery.json',d);(FINAL/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['name']+'\n' for r in files),encoding='ascii')
    cues=ed.srtread(FINAL/'captions.ko.srt')
    body=''.join(f'<p><button data-s="{a}">{int(a)//60}:{int(a)%60:02}</button> {html.escape(s.replace(chr(10)," "))}</p>' for a,b,s in cues)
    page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(PLAN['title'])+'</title><style>body{max-width:860px;margin:2rem auto;padding:0 1rem;background:#0b1515;color:white;font:18px/1.6 Malgun Gothic,sans-serif}h1{font-size:1.4rem;color:#ffd366}video{display:block;width:min(100%,375px);margin:1rem auto}a,button{color:#81dcc0}button{background:#193330;border:1px solid #45675d;cursor:pointer}pre{white-space:pre-wrap;font:inherit}</style><h1>'+html.escape(PLAN['title'])+'</h1><video controls playsinline preload="metadata" src="captioned.mp4"></video><p>'+ ' · '.join(f'<a href="{f}">{s}</a>' for f,s in zip(ed.FILES,['무자막 영상','전체 자막 영상','한국어 SRT','English SRT']))+'</p><h2>대본</h2>'+body+'<details><summary>제목·설명·SHA256</summary><pre>'+html.escape(DESC)+'\n\n'+files[1]['sha256']+'</pre></details><script>const v=document.querySelector("video");document.querySelectorAll("button").forEach(b=>b.onclick=()=>{v.currentTime=Number(b.dataset.s);v.play()})</script></html>'
    (FINAL/'index.html').write_text(page,encoding='utf8');print(d['frames'],d['durationSeconds'],files[1]['sha256'],flush=True)
if __name__=='__main__':
    sources=prepare_frames()
    while not (ROOT/'shared/output/shorts-doom-noise-alert/voice-v1/addition.wav').is_file():time.sleep(3)
    records,frames=sequence_audio();render(records,frames);deliver(records,frames)
