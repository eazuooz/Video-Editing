"""Check the final files, including attached rays, changing shader input and inherited shots."""
import html,io,re,subprocess
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import numpy as np
from common import *
from assemble import CHANGED,paths
from teaching import BOARDS,EXTRA
from guides import STILLS,triangle,project,unit,vec,view,NCLR,LCLR,VCLR,RCLR
from samples import DEMOS
from symbol_pages import SCALARS
from unity_guides import NATIVE
from sequence import LESSONS
from review import grab,audio
QA=WORK/'final-qa'
def now():return datetime.now(timezone.utc).isoformat()
def player(t):
    out=OUT;slug=PROJECT.name
    links=[]
    for sid,title in [(42,'N · L · V · R과 두 구의 반짝임'),(12,'광택 지수와 하이라이트 폭'),(39,'정점 색의 비중과 표면점 P'),(16,'가운데 방향 H'),(48,'표면점 P와 광원 Q'),(56,'입체각 dω와 광원 면적'),(58,'거리 d와 남는 빛'),(64,'상자 위치와 텍스처 위치')]:
        r=next(x for x in t if x['sid']==sid and x['kind']=='explanation');at=r['start']/60
        links.append(f'<li><a data-t="{at:.3f}" href="{slug}.captioned.mp4#t={at:.3f}">{int(at)//60:02}:{int(at)%60:02} · {html.escape(title)}</a></li>')
    d=(t[-1]['start']+t[-1]['frames']+600)/60
    page=(V6/'index.html').read_text('utf-8')
    page=re.sub(r'<p>32분 10초.*?</p>',f'<p>{int(round(d))//60}분 {int(round(d))%60}초 · 1080p60 · 구의 표면 기호와 조명 비교</p>',page,count=1)
    page=re.sub(r'(<h2>설명 바로 보기</h2><ul>).*?(</ul>)',lambda m:m[1]+''.join(links)+m[2],page,flags=re.S)
    page=re.sub(r'<p id="latest-m21-[^"]+".*?</p>','',page,flags=re.S)
    page=page.replace(V6.name+'/index.html',OUT.name+'/index.html')
    (out/'index.html').write_text(page,'utf-8')
def media(t):
    duration=t[-1]['start']+t[-1]['frames']+600
    mixhash=audio(VOICE/'pair.m4a');results={}
    for kind in ['clean','captioned']:
        p=OUT/(PROJECT.name+'.'+kind+'.mp4');video,sound=v6.original.probe(p)['streams']
        assert (video['width'],video['height'],video['codec_name'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'h264','60/1',duration)
        assert abs(float(video['duration'])-float(sound['duration']))<.04 and audio(p)==mixhash
        pkts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','csv=p=0',str(p)])
        ticks=sorted(int(l.split(b',')[0]) for l in pkts.splitlines() if l.strip());assert len(ticks)==duration and ticks[0]==0 and all(abs(b-a-1500)<=1 for a,b in zip(ticks,ticks[1:]))
        subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-threads','3','-i',str(p),'-map','0:v','-map','0:a','-f','null','NUL'],check=True)
        results[kind]=dict(path=str(p),sha256=sha(p),frames=duration,seconds=duration/60,fullDecode=True,audioHash=mixhash)
    for lang in ['ko','en']:
        p=OUT/(PROJECT.name+'.'+lang+'.srt');rows=v6.original.CAP.read_srt(p);assert len(rows)>550 and rows[-1]['end']<duration/60
        results[lang]=dict(path=str(p),sha256=sha(p),cues=len(rows))
    return results
def proof(t):
    cap=OUT/(PROJECT.name+'.captioned.mp4');audit=[];samples=[]
    for r in t:
        s=r['sid'];key=f'{r["i"]:03}-{s:03}';actual=r['kind']=='actual-gameplay';changed=s in CHANGED and not actual
        row=dict(scene=s,kind=r['kind'],start=r['start']/60,frames=r['frames'],revised=changed,speech=r['newSpeech'])
        if actual:row['disposition']='original independent recording and game UI'
        elif not changed:row['disposition']='existing conceptual picture; no arithmetic example'
        else:
            rec=read(WORK/'edit'/(key+'.json'));assert rec['frames']==r['frames']
            k=min(r['frames']-2,round(.76*r['frames']));f=(r['start']+k+.15)/60;frame=grab(cap,f,1920)
            state=max(v for v in rec['states'] if v<=k);layer=Image.open(WORK/'plates'/f'{s:03}'/f'{state:06}.png').convert('RGBA')
            if s in BOARDS:
                exp=np.array(layer.crop((1014,181,1880,265)));mask=(exp[:,:,3]>246)&(exp[:,:,0]>190)&(exp[:,:,1]>145)&(exp[:,:,2]<165)
                pix=np.array(frame.crop((1014,181,1880,265))).astype(float);assert mask.sum()>120 and np.median(abs(exp[:,:,:3][mask]-pix[mask]))<20,(s,'purpose')
                roi=(1016,280,1870,402);exp=np.array(layer.crop(roi));mask=(exp[:,:,3]>246)&(exp[:,:,0]>190)&(exp[:,:,1]>180)&(exp[:,:,2]>167)
                pix=np.array(frame.crop(roi)).astype(float);assert mask.sum()>120 and np.median(abs(exp[:,:,:3][mask]-pix[mask]))<20,(s,'general formula')
                row.update(purpose=BOARDS[s].purpose,formula=BOARDS[s].formula,symbols=BOARDS[s].definitions)
            if s in DEMOS:
                guide=WORK/'demos'/f'{s:03}-guided.mp4';data=read(guide.with_suffix('.json'));lo,hi=data['linearRampFrames'];values=[]
                for phase in (.12,.50,.88):
                    j=round(lo+(hi-lo)*phase);clock=(r['start']+j+.15)/60
                    crop=np.asarray(grab(cap,clock,1920).crop((78,290,930,770)),dtype=float)
                    ref=np.asarray(grab(guide,(j+.15)/60,852),dtype=float)
                    mae=np.mean(abs(ref-crop));assert mae<5.5,(s,'shader mismatch',mae)
                    x=int((.12+.76*(j-lo)/(hi-lo))*852);y=round(.954*480)
                    patch=crop[y-3:y+4,x-3:x+4];assert patch[:,:,0].mean()>175 and patch[:,:,0].mean()>patch[:,:,2].mean()+35,(s,'slider')
                    values.append(dict(frame=j,x=x,mae=round(float(mae),3),image=crop))
                motion=np.mean(abs(values[-1]['image'][35:415]-values[0]['image'][35:415]))
                assert motion>.85,(s,'no motion in surface region',motion)
                if s in (12,42):
                    probe=triangle(s).mean(axis=0);normal=unit(probe);px=project(s,probe,1 if s==42 else 0)
                    scale=166 if s==42 else 208;verified={}
                    for v in values:
                        u=(v['frame']-lo)/(hi-lo);light=vec(s,u);reflection=2*np.dot(normal,light)*normal-light
                        for key,direction,color in [('N',normal,NCLR),('L',light,LCLR),('V',view,VCLR),('R',reflection,RCLR)]:
                            ideal=np.array([int(color[i:i+2],16) for i in [1,3,5]])
                            for fraction in [.32,.48,.62,.77]:
                                x,y=np.rint(px+scale*fraction*np.array([direction[0],-direction[1]])).astype(int)
                                crop=v['image'][y-5:y+6,x-5:x+6]
                                if np.min(np.max(abs(crop-ideal),axis=2))<64:
                                    verified[key]=verified.get(key,0)+1;break
                    assert all(verified.get(k,0)>=1 for k in 'NLVR'),(s,verified)
                    row['observedProjectedVectors']=verified
                for v in values:v.pop('image')
                row.update(shader=DEMOS[s][0],shaderChecks=values,visibleSurfaceChange=float(motion))
            row['disposition']='symbolic relation / labeled surface, geometry, stored color or observed shader response'
            if s in {1,5,6,9,10,11,12,15,16,20,22,30,35,36,39,40,41,42,44,46,48,53,54,55,56,58,61,62,64,70,72,73,77}:
                samples.append((s,frame.resize((375,211),Image.Resampling.LANCZOS)))
        if not changed:
            raw=V6WORK/'edit'/(key+'.mp4');assert paths(r)[0].resolve()==raw.resolve()
        audit.append(row)
    for page,k in enumerate(range(0,len(samples),12)):
        group=samples[k:k+12];sheet=Image.new('RGB',(1125,((len(group)+2)//3)*235),'#111716');d=ImageDraw.Draw(sheet)
        for i,(s,im) in enumerate(group):
            x=i%3*375;y=i//3*235;sheet.paste(im,(x,y));d.text((x+8,y+213),f'M21 / {s:03}',fill='white')
        sheet.save(QA/f'mobile-{page}.jpg',quality=95)
    return audit
def run():
    t=read(WORK/'timeline.json');QA.mkdir(exist_ok=True)
    files=media(t);audit=proof(t);player(t)
    write(QA/'report.json',dict(checkedAt=now(),files=files,reviewedCuts=audit,all85Cuts=len(audit)==85,symbolicBoards=len(BOARDS),changedExplanations=sum(r['revised'] for r in audit),untouchedGameplay=sum(r['kind']=='actual-gameplay' for r in audit),shaderScenes=sorted(DEMOS),matchedNativeGuides=sorted(NATIVE),staticSurfaceDiagrams=sorted(STILLS),voice=[dict(id=k,similarity=read(VOICE/f'{k:03}-alignment.json')['similarity']) for k in LESSONS],humanReview=False))
    import playerqa
    start=next(r['start']/60 for r in t if r['sid']==42)
    playerqa.run_review(OUT,WORK,PROJECT.name,start,files['captioned']['seconds'])
if __name__=='__main__':run()
