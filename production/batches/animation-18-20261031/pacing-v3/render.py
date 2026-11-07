"""Lossless narration retiming, frame-exact picture inserts, caption retiming."""
from pathlib import Path
import json,re,sys,subprocess,hashlib,html,os
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'local/pacing-v3/python-deps'))
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
ENC=['-c:v','h264_nvenc','-preset','p4','-cq','18','-b:v','0','-bf','0','-g','120','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def run(args,log):
    with log.open('wb') as f:subprocess.run(['ffmpeg','-nostdin','-v','error','-y',*map(str,args)],stdout=f,stderr=f,check=True)
def esc(p):return str(p.resolve()).replace('\\','/').replace(':','\\:').replace("'","\\'")
def ts(t,srt=False):
    n=round(t*(1000 if srt else 100));unit=1000 if srt else 100;sec,ms=divmod(n,unit);h,sec=divmod(sec,3600);m,s=divmod(sec,60)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}' if srt else f'{h}:{m:02d}:{s:02d}.{ms:02d}'
def seconds(s):
    h,m,v=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(v)
def shifted(t,events,end=False,ass=False):
    def at(e):return round(e['audioAt']/60,2) if ass else e['audioAt']/60
    return t+sum(e['frames']/60 for e in events if (at(e)<t-.0001 if end else at(e)<=t+.0001))
def main(planfile):
    p=read(planfile);ep=p['episode'];slug=p['slug'];P=R/'projects'/slug;L=P/'production/local/pacing-v3';L.mkdir(parents=True,exist_ok=True)
    D=R/p['outputDirectory'];D.mkdir(parents=True,exist_ok=True);events=p['events'];base=p['baseline'];parts=L/'parts';parts.mkdir(exist_ok=True)
    # The explicit finite scope is checked before every costly encode.
    control=read(R/'shared/publishing/video-production-control.json')
    assert ep in control['animationPacingRevision20261107']['episodes']
    baseline=R/next(f['path'] for f in base['files'] if f['kind']=='clean.mp4')
    assert sha(baseline)==next(f['sha256'] for f in base['files'] if f['kind']=='clean.mp4')
    def segment(source,start,n,dest,label=None):
        if dest.exists():
            v=next(s for s in probe(dest)['streams'] if s['codec_type']=='video')
            if int(v.get('nb_frames',0))==n:return
        vf='settb=1/60,setpts=N'
        if label:
            txt=dest.with_suffix('.txt');txt.write_text(label,'utf-8')
            vf+=f",drawbox=x=58:y=878:w=1804:h=42:color=0x101713:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':textfile='{esc(txt)}':fontsize=31:fontcolor=0xF2D787:x=(w-text_w)/2:y=884"
        run(['-threads','2','-filter_threads','2','-ss',start/60,'-i',source,'-vf',vf,'-frames:v',n,'-an',*ENC,dest],dest.with_suffix('.log'))
    sequence=[];cursor=0
    for i,e in enumerate(events):
        assert e['pictureAt']>=cursor
        dest=parts/f'base-{i:02d}.mp4';segment(baseline,cursor,e['pictureAt']-cursor,dest);sequence.append(dest)
        src=R/e['source'];assert sha(src)==e['sourceSHA256'];n=e['sourceEndFrame']-e['sourceStartFrame']
        for k in range(e['repeatCount']):
            num=k+2 if e.get('firstPassAlreadyInBaseline') else k+1
            label=f'기본 속도  ·  {num}/3    ─    전체 동작을 먼저 확인하세요'
            dest=parts/f'{i:02d}-{e["key"]}-{num}.mp4';segment(src,e['sourceStartFrame'],n,dest,label);sequence.append(dest)
        cursor=e['pictureAt'];print(ep,'picture',e['key'],'done',flush=True)
    dest=parts/'base-last.mp4';segment(baseline,cursor,p['baselineFrames']-cursor,dest);sequence.append(dest)
    concat=L/'picture-concat.txt';concat.write_text(''.join("file '"+str(x.resolve()).replace('\\','/')+"'\n" for x in sequence),'utf-8')
    picture=L/'picture.mp4'
    run(['-f','concat','-safe','0','-i',concat,'-map','0:v','-c','copy','-an','-video_track_timescale','60000',picture],L/'picture.log')
    # New observation time gets a music bed, not repeated or stretched speech.
    voice,sr=sf.read(R/p['audioStem'],dtype='float32',always_2d=True);assert sr==48000
    assert abs(len(voice)-p['baselineFrames']*800)<=800
    voice=np.pad(voice,((0,max(0,p['baselineFrames']*800-len(voice))),(0,0)))[:p['baselineFrames']*800]
    output=np.zeros((p['totalFrames']*800,2),np.float32);cursor=0;previous=0;proof=[]
    for e in sorted(events,key=lambda x:x['audioAt']):
        end=round(e['audioAt']*800);n=end-previous;output[cursor:cursor+n]=voice[previous:end]
        proof.append(dict(oldStartSample=previous,oldEndSample=end,newStartSample=cursor,exactEquality=bool(np.array_equal(output[cursor:cursor+n],voice[previous:end]))))
        cursor+=n+e['frames']*800;previous=end
    output[cursor:]=voice[previous:];proof.append(dict(oldStartSample=previous,oldEndSample=len(voice),newStartSample=cursor,exactEquality=bool(np.array_equal(output[cursor:],voice[previous:]))))
    sf.write(L/'narration.wav',output,sr,subtype='PCM_24')
    decoded=L/'music.wav';run(['-stream_loop','-1','-i',R/p['music'],'-t',p['totalFrames']/60,'-ar',48000,'-ac',2,'-c:a','pcm_s24le',decoded],L/'music.log')
    music,_=sf.read(decoded,dtype='float32',always_2d=True);music=music[:len(output)]
    if len(music)<len(output):music=np.pad(music,((0,len(output)-len(music)),(0,0)))
    music*=10**(-28/20)/max(1e-9,float(np.sqrt(np.mean(music**2))))
    fade=np.minimum(np.arange(len(music))/48000,(len(music)-1-np.arange(len(music)))/96000).clip(0,1);music*=fade[:,None]
    output=(output+music)*p['masterGain'];sf.write(L/'mix.wav',output,sr,subtype='PCM_24')
    save(L/'audio-proof.json',dict(narrationRetimedWithoutResynthesis=True,originalNarrationSHA256=sha(R/p['audioStem']),segments=proof,gain=p['masterGain'],samplePeak=float(np.max(abs(output))),bgmSHA256=sha(R/p['music']),fullListeningPerformed=False))
    run(['-i',L/'mix.wav','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',L/'pair-audio.m4a'],L/'audio.log')
    for lang in ['ko','en']:
        src=R/next(f['path'] for f in base['files'] if f['kind']==lang+'.srt');out=[]
        for block in re.split(r'\n\s*\n',src.read_text('utf-8-sig').strip()):
            lines=block.splitlines();a,b=map(seconds,lines[1].split(' --> '));assert not any(a<e['audioAt']/60<b for e in events),(ep,a,b,'speech cue split')
            lines[1]=ts(shifted(a,events),True)+' --> '+ts(shifted(b,events,end=True),True);out.append('\n'.join(lines))
        (D/f'{slug}.{lang}.srt').write_text('\n\n'.join(out)+'\n','utf-8')
    ass=[]
    for line in (R/p['captionAss']).read_text('utf-8-sig').splitlines():
        if line.startswith('Dialogue:'):
            x=line.split(',',9);a,b=seconds(x[1]),seconds(x[2]);x[1]=ts(shifted(a,events,ass=True));x[2]=ts(shifted(b,events,end=True,ass=True));line=','.join(x)
        ass.append(line)
    (L/'captions.ass').write_text('\n'.join(ass)+'\n','utf-8')
    clean=D/f'{slug}.clean.mp4';cap=D/f'{slug}.captioned.mp4'
    run(['-i',picture,'-i',L/'pair-audio.m4a','-map','0:v','-map','1:a','-c','copy','-movflags','+faststart',clean],L/'clean.log')
    run(['-threads','2','-filter_threads','2','-i',picture,'-i',L/'pair-audio.m4a','-vf',f"ass='{esc(L/'captions.ass')}'",'-map','0:v','-map','1:a','-frames:v',p['totalFrames'],*ENC,'-c:a','copy','-movflags','+faststart',cap],L/'captioned.log')
    files=[]
    for kind in ['clean.mp4','captioned.mp4','ko.srt','en.srt']:
        f=D/f'{slug}.{kind}';files.append(dict(kind=kind,path=f.relative_to(R).as_posix(),sha256=sha(f),bytes=f.stat().st_size))
        if kind.endswith('mp4'):
            v=next(s for s in probe(f)['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',p['totalFrames'])
            run(['-threads','2','-i',f,'-map','0:v','-map','0:a','-f','null','-'],L/(kind+'.decode.log'))
    manifest=dict(id=ep,slug=slug,title=p['title'],revision='pacing-v3',status='encoded-technical-check-passed-visual-review-pending',durationSeconds=p['totalFrames']/60,files=files,baseline=base['captionedSha256'],events=events,narrationAllSamplesPreserved=all(x['exactEquality'] for x in proof),humanViewed=False)
    save(D/'delivery-manifest.json',manifest);save(P/'production/pacing-v3/checkpoint.json',manifest)
    (D/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#101713;color:#eee;font:18px/1.6 sans-serif;margin:24px}video{width:100%;max-height:76vh}a{color:#add9bd}</style><h1>'+html.escape(ep+' '+p['title'])+'</h1><p>기본 속도 3회 관찰 → 기존 구간·자세 분석. 최종 검수 대기.</p><video controls playsinline src="'+slug+'.captioned.mp4"></video><p>'+''.join('<a href="'+slug+'.'+k+'">'+k+'</a>　' for k in ['captioned.mp4','clean.mp4','ko.srt','en.srt'])+'</p>','utf-8')
    print(ep,'DELIVERY',str(D),'seconds',p['totalFrames']/60,flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
