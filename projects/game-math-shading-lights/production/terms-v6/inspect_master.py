"""Verify both M21 masters, the rendered math glyphs, subtitle timing, source shots, and actual player."""
import html
import subprocess
from datetime import datetime, timezone
from PIL import Image,ImageDraw
import numpy as np
from build import original, EDIT, OUTPUT, WORK, SLUG, TABLE, V5
from layout import TITLES, PAIRS
from voice import write,read,VOICE
from review import grab,audio

QA=WORK/'final-qa'
def utc():return datetime.now(timezone.utc).isoformat()
def offset(sid,local=0):
    c=next(c for c in TABLE if c['kind']=='explanation' and int(c['scene'])==sid)
    return 2+c['globalStartFrame']/60+local-c['sourceIn']
CHAPTERS=[(9,8,'Reflection Vector (반사 벡터)'),(39,6,'Gouraud Shading (구로 셰이딩)'),
          (54,8.8,'Irradiance (복사조도)'),(55,12,'Radiance (복사휘도)'),
          (16,6,'Halfway Vector (하프웨이 벡터)'),(58,9,'Linear Attenuation (선형 감쇠)'),
          (72,13,'Directional Irradiance (방향별 복사조도)'),(3,7.15,'해에서 구로 들어오는 빛')]
def player():
    links=[]
    for sid,t,title in CHAPTERS:
        at=offset(sid,t);stamp=f'{int(at)//60:02}:{int(at)%60:02}'
        links.append(f'<li><a href="{SLUG}.captioned.mp4#t={at:.3f}" data-t="{at:.3f}">{stamp} · {html.escape(title)}</a></li>')
    url='http://127.0.0.1:9347/output/'+OUTPUT.name+'/index.html'
    page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>M21 · 빛과 셰이딩</title><style>body{max-width:1120px;margin:24px auto;background:#090b0e;color:#f6f5f1;padding:0 16px;font:18px/1.6 system-ui}h1{color:#ffd173}a{color:#89ded4}video{width:100%;display:block;background:black}nav a{display:inline-block;margin:.4em 1em .4em 0}li{margin:.35em 0}</style><main>
<a href="../game-math-remaining-20261104/index.html">게임수학 제작표</a><h1>M21 · 빛과 셰이딩</h1><p>32분 10초 · 1080p60 · 영어 용어와 수학식 수정본</p>
<video id="v" controls playsinline preload="metadata" src="__SL__.captioned.mp4"></video><nav><a href="__SL__.captioned.mp4">자막 영상</a><a href="__SL__.clean.mp4">무자막 영상</a><a href="__SL__.ko.srt">한국어 자막</a><a href="__SL__.en.srt">영어 자막</a></nav><h2>설명 바로 보기</h2><ul>__LINKS__</ul><p id="help" hidden>재생이 멈추면 <a href="__URL__">로컬 브라우저용 검수 페이지</a>를 열어 주세요.</p></main><script>
const video=document.getElementById('v'),help=document.getElementById('help');
function seekFragment(){if(/^#t=[0-9.]+$/.test(location.hash))video.currentTime=Number(location.hash.slice(3))}
video.readyState?seekFragment():video.addEventListener('loadedmetadata',seekFragment,{once:true});
window.addEventListener('hashchange',seekFragment);
for(const a of document.querySelectorAll('[data-t]'))a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();video.currentTime=Number(a.dataset.t);video.play().catch(err=>{if(err.name!=='AbortError')help.hidden=false})});
video.addEventListener('error',()=>help.hidden=false);if(location.protocol==='file:')help.hidden=false;
</script></html>'''.replace('__SL__',SLUG).replace('__LINKS__',''.join(links)).replace('__URL__',url)
    (OUTPUT/'index.html').write_text(page,'utf-8')
def encoded_overlays(cap):
    seen=[];sample_images=[];receipts=read(WORK/'layers.json')
    for c in TABLE:
        if c['kind']!='explanation':continue
        sid=int(c['scene']);r=next(x for x in receipts if x['scene']==c['scene'])
        start=int(c['globalStartFrame']);localframe=min(c['frames']-2,max(4,round(c['frames']*.74)))
        k=max(k for k in r['states'] if k<=localframe)
        target=Image.open(WORK/'layers'/c['scene']/f'{k:06}.png').convert('RGBA')
        f=(120+start+localframe)/60
        frame=grab(cap,f,1920)
        gold=np.array(target.crop((72,30,1320,126)));mask=(gold[:,:,3]>250)&(gold[:,:,0]>190)&(gold[:,:,1]>140)&(gold[:,:,2]<160)
        pix=np.array(frame.crop((72,30,1320,126))).astype(float)
        assert mask.sum()>130 and np.median(abs(pix[mask]-gold[:,:,:3][mask]))<15,(sid,'heading')
        item=dict(scene=c['scene'],heading=TITLES[sid],at=round(f,3),verifiedTitlePixels=int(mask.sum()))
        if sid in PAIRS:
            roi=(1010,324,1870,465)
            expected=np.array(target.crop(roi));mask=(expected[:,:,3]>250)&(expected[:,:,0]>190)&(expected[:,:,1]>190)&(expected[:,:,2]>180)
            actual=np.array(frame.crop(roi)).astype(float);assert mask.sum()>190 and np.median(abs(actual[mask]-expected[:,:,:3][mask]))<19,(sid,'typeset equation')
            codebox=(1010,558,1880,674);exp=np.array(target.crop(codebox));code_mask=(exp[:,:,3]>250)&(exp[:,:,0]>95)&(exp[:,:,1]>150)&(exp[:,:,2]>135)
            pix=np.array(frame.crop(codebox)).astype(float);assert code_mask.sum()>90 and np.median(abs(pix[code_mask]-exp[:,:,:3][code_mask]))<19,(sid,'code')
            item['formulaPixels']=int(mask.sum());item['codePixels']=int(code_mask.sum())
        if sid in {2,3,9,10,11,16,20,22,37,39,40,42,54,55,56,58,62,70,72,78}:
            img=frame.resize((375,211),Image.Resampling.LANCZOS);sample_images.append((sid,img))
        seen.append(item)
    sheet=Image.new('RGB',(1500,((len(sample_images)+3)//4)*234),'#141817');draw=ImageDraw.Draw(sheet)
    for i,(sid,img) in enumerate(sample_images):
        x=i%4*375;y=i//4*234;sheet.paste(img,(x,y));draw.text((x+3,y+211),f'M21 / {sid:03}',fill='white')
    sheet.save(QA/'mobile.jpg',quality=95);return seen
def verify():
    QA.mkdir(exist_ok=True);master_hash=audio(VOICE/'pair-audio.m4a')
    expected=original.Q['bodyFrames']+720;files={}
    for name in ['clean','captioned']:
        path=OUTPUT/(SLUG+'.'+name+'.mp4');v,a=original.probe(path)['streams'];assert(v['width'],v['height'],v['codec_name'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'h264','60/1',expected)
        assert abs(float(a['duration'])-float(v['duration']))<.04 and audio(path)==master_hash
        out=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','csv=p=0',str(path)])
        frames=sorted(int(s.split(b',')[0]) for s in out.splitlines() if s.strip());assert len(frames)==expected and frames[0]==0 and all(abs(y-x-1500)<=1 for x,y in zip(frames,frames[1:]))
        subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-threads','3','-i',str(path),'-map','0:v','-map','0:a','-f','null','NUL'],check=True)
        files[name]=dict(path=str(path),sha256=original.sha(path),frames=expected,duration=v['duration'],fullDecode=True,audioHash=master_hash)
    for lang,n in [('ko',715),('en',606)]:
        path=OUTPUT/(SLUG+'.'+lang+'.srt');rows=original.CAP.read_srt(path);assert len(rows)==n
        prev=original.CAP.read_srt(V5/path.name);shift=[r['id'] for r,o in zip(rows,prev) if r['start']!=o['start'] or r['end']!=o['end']]
        files[lang]=dict(path=str(path),sha256=original.sha(path),cues=n,adjustedTimes=shift)
    games=[read(EDIT/f'{i:03}-{c["scene"]}.json') for i,c in enumerate(TABLE) if c['kind']=='actual-gameplay']
    assert len(games)==7
    for i,c in enumerate(TABLE):
        if c['kind']=='actual-gameplay':
            n=f'{i:03}-{c["scene"]}';assert read(EDIT/(n+'.json'))['clean']==original.sha(original.D/(n+'.mp4'))
    examples=encoded_overlays(OUTPUT/(SLUG+'.captioned.mp4'));assert len(examples)==78
    pcm=read(VOICE/'pcm-integrity.json')
    assert len(pcm['changedSentenceIntervals'])==8 and pcm['maxExcessSeamStep']<.012
    report=dict(checkedAt=utc(),files=files,encodedHeadings=len(examples),equationAndCodePairs=sum('formulaPixels' in e for e in examples),samples=examples,pcmIntegrity=pcm,gameplayCutsReused=7,userReview=False,continuousListening=False)
    write(QA/'report.json',report);player()
    import playerqa
    playerqa.DEST=OUTPUT;playerqa.W=WORK;playerqa.run()
    return report
if __name__=='__main__': verify()
