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
    save(L/'render-plan-used.json',p)
    D=R/p['outputDirectory'];D.mkdir(parents=True,exist_ok=True);events=p['events'];base=p['baseline'];parts=L/'parts';parts.mkdir(exist_ok=True)
    # The explicit finite scope is checked before every costly encode.
    control=read(R/'shared/publishing/video-production-control.json')
    assert ep in control['animationPacingRevision20261107']['episodes']
    baseline=R/next(f['path'] for f in base['files'] if f['kind']=='clean.mp4')
    assert sha(baseline)==next(f['sha256'] for f in base['files'] if f['kind']=='clean.mp4')
    reusePicture=None
    if p.get('reuseExistingPictureForSentenceBoundaryFix') and (D/'delivery-manifest.json').exists():
        old=read(D/'delivery-manifest.json');keys=['key','pictureAt','sourceSHA256','sourceStartFrame','sourceEndFrame','repeatCount','frames']
        signature=lambda ev:[{k:e[k] for k in keys} for e in ev]
        if old['baseline']==base['captionedSha256'] and signature(old['events'])==signature(events) and round(old['durationSeconds']*60)==p['totalFrames']:
            previous=next(x for x in old['files'] if x['kind']=='clean.mp4')
            assert sha(R/previous['path'])==previous['sha256']
            previous['videoPacketSHA256']=subprocess.check_output(['ffmpeg','-v','error','-i',str(R/previous['path']),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
            reusePicture=previous
    def segment(source,start,n,dest,label=None):
        if reusePicture:return
        if dest.exists():
            v=next(s for s in probe(dest)['streams'] if s['codec_type']=='video')
            if int(v.get('nb_frames',0))==n:return
        vf='settb=1/60,setpts=N'
        if label:
            txt=dest.with_suffix('.txt');txt.write_text(label,'utf-8')
            vf+=f",drawbox=x=58:y=878:w=1804:h=42:color=0x101713:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':textfile='{esc(txt)}':fontsize=31:fontcolor=0xF2D787:x=(w-text_w)/2:y=884"
        run(['-threads','6','-filter_threads','4','-ss',start/60,'-i',source,'-vf',vf,'-frames:v',n,'-an',*ENC,dest],dest.with_suffix('.log'))
    sequence=[];cursor=0
    for i,e in enumerate(events):
        assert e['pictureAt']>=cursor
        if e['pictureAt']>cursor:
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
    if reusePicture:run(['-i',R/reusePicture['path'],'-map','0:v:0','-c','copy','-an','-video_track_timescale','60000',picture],L/'picture.log')
    else:run(['-f','concat','-safe','0','-i',concat,'-map','0:v','-c','copy','-an','-video_track_timescale','60000',picture],L/'picture.log')
    # New observation time gets a music bed, not repeated or stretched speech.
    voice,sr=sf.read(R/p['audioStem'],dtype='float32',always_2d=True);assert sr==48000
    assert abs(len(voice)-p['baselineFrames']*800)<=800
    voice=np.pad(voice,((0,max(0,p['baselineFrames']*800-len(voice))),(0,0)))[:p['baselineFrames']*800]
    output=np.zeros((p['totalFrames']*800,2),np.float32);cursor=0;previous=0;proof=[];insertions=[]
    for e in sorted(events,key=lambda x:x['audioAt']):
        end=round(e['audioAt']*800);n=end-previous;output[cursor:cursor+n]=voice[previous:end]
        proof.append(dict(oldStartSample=previous,oldEndSample=end,newStartSample=cursor,exactEquality=bool(np.array_equal(output[cursor:cursor+n],voice[previous:end]))))
        insertions.append((cursor+n,e['frames']*800,end,e))
        cursor+=n+e['frames']*800;previous=end
    output[cursor:]=voice[previous:];proof.append(dict(oldStartSample=previous,oldEndSample=len(voice),newStartSample=cursor,exactEquality=bool(np.array_equal(output[cursor:],voice[previous:]))))
    if p.get('audioMode')=='preserve-final-mix':
        music,msr=sf.read(R/p['music'],dtype='float32',always_2d=True);assert msr==sr
        bridges=[];continuous=[]
        for start,n,old,e in insertions:
            if continuous and continuous[-1][0]+continuous[-1][1]==start and continuous[-1][2]==old:
                prev=continuous.pop();continuous.append((prev[0],prev[1]+n,old,{**prev[3],'key':prev[3]['key']+' + '+e['key']}))
            else:continuous.append((start,n,old,e))
        for start,n,old,e in continuous:
            # A phase-return bridge keeps the original mastered mix bit-identical on
            # both sides. Only the new observation interval receives new music.
            at=round(e.get('musicAt',e['audioAt'])*800)%len(music)
            left=music[(at+np.arange(n))%len(music)].copy()
            right=music[(at-n+np.arange(n))%len(music)]
            w=np.clip((np.arange(n)/max(1,n-1)-.35)/.30,0,1)[:,None]
            bridge=left*(1-w)+right*w
            # Original music normalization is already in this stem. Derive final
            # master attenuation from a voice-free part of the unchanged ending.
            if ep!='A01':
                tail=min(len(voice),len(music));lo=max(0,tail-8*sr);hi=max(lo+1,tail-2*sr)
                denom=float(np.sum(music[lo:hi]**2));gain=float(np.sum(voice[lo:hi]*music[lo:hi])/max(1e-9,denom));gain=float(np.clip(gain,0.1,1.0))
            else:gain=.6 if ep=='A01' else 1.0
            bridge*=gain
            edge=min(480,n//4);weight=np.linspace(0,1,edge,dtype=np.float32)[:,None]
            if start:bridge[:edge]=bridge[:edge]*weight+output[start-1]*(1-weight)
            if start+n<len(output):bridge[-edge:]=bridge[-edge:]*(1-weight)+output[start+n]*weight
            output[start:start+n]=bridge
            bridges.append(dict(key=e['key'],startSample=start,samples=n,musicGain=gain,edgeFadeMs=10,reason='User-requested complete native-speed observation before analysis'))
        for q in proof:
            n=q['oldEndSample']-q['oldStartSample'];q['exactEquality']=bool(np.array_equal(output[q['newStartSample']:q['newStartSample']+n],voice[q['oldStartSample']:q['oldEndSample']]))
        assert all(q['exactEquality'] for q in proof)
        gain=1.0
    else:
        sf.write(L/'narration.wav',output,sr,subtype='PCM_24')
        decoded=L/'music.wav';run(['-stream_loop','-1','-i',R/p['music'],'-t',p['totalFrames']/60,'-ar',48000,'-ac',2,'-c:a','pcm_s24le',decoded],L/'music.log')
        music,_=sf.read(decoded,dtype='float32',always_2d=True);music=music[:len(output)]
        if len(music)<len(output):music=np.pad(music,((0,len(output)-len(music)),(0,0)))
        music*=10**(-28/20)/max(1e-9,float(np.sqrt(np.mean(music**2))))
        fade=np.minimum(np.arange(len(music))/48000,(len(music)-1-np.arange(len(music)))/96000).clip(0,1);music*=fade[:,None]
        gain=p['masterGain'];output=(output+music)*gain;bridges=[]
    sf.write(L/'mix.wav',output,sr,subtype='PCM_24')
    if p.get('audioMode')=='preserve-final-mix':
        with sf.SoundFile(L/'mix.wav') as check:
            for q in proof:
                check.seek(q['newStartSample']);n=q['oldEndSample']-q['oldStartSample']
                restored=check.read(n,dtype='float32',always_2d=True)
                q['serializedPCMExactEquality']=bool(np.array_equal(restored,voice[q['oldStartSample']:q['oldEndSample']]))
        assert all(q['serializedPCMExactEquality'] for q in proof)
    save(L/'audio-proof.json',dict(narrationRetimedWithoutResynthesis=True,preservationMode=p.get('audioMode','narration-stem'),originalNarrationSHA256=sha(R/p['audioStem']),segments=proof,gain=gain,samplePeak=float(np.max(abs(output))),bgmSHA256=sha(R/p['music']),insertedMusicBridges=bridges,fullListeningPerformed=False))
    run(['-i',L/'mix.wav','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',L/'pair-audio.m4a'],L/'audio.log')
    for lang in ['ko','en']:
        src=R/next(f['path'] for f in base['files'] if f['kind']==lang+'.srt');out=[]
        for block in re.split(r'\n\s*\n',src.read_text('utf-8-sig').strip()):
            lines=block.splitlines();a,b=map(seconds,lines[1].split(' --> '));assert not any(a+.00001<e['audioAt']/60<b-.00001 for e in events),(ep,a,b,'speech cue split')
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
    run(['-threads','6','-filter_threads','4','-i',picture,'-i',L/'pair-audio.m4a','-vf',f"ass='{esc(L/'captions.ass')}'",'-map','0:v','-map','1:a','-frames:v',p['totalFrames'],*ENC,'-c:a','copy','-movflags','+faststart',cap],L/'captioned.log')
    files=[]
    packetProof={};audioPacketHashes={}
    for kind in ['clean.mp4','captioned.mp4','ko.srt','en.srt']:
        f=D/f'{slug}.{kind}';files.append(dict(kind=kind,path=f.relative_to(R).as_posix(),sha256=sha(f),bytes=f.stat().st_size))
        if kind.endswith('mp4'):
            v=next(s for s in probe(f)['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',p['totalFrames'])
            run(['-threads','6','-i',f,'-map','0:v','-map','0:a','-f','null','-'],L/(kind+'.decode.log'))
            pts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts,dts,duration','-of','csv=p=0',str(f)]).decode().strip().splitlines()
            for i,line in enumerate(pts):
                x=list(map(int,line.split(',')[:3]));assert x==[i*1000,i*1000,1000],(ep,kind,i,x)
            assert len(pts)==p['totalFrames'];packetProof[kind]={'packets':len(pts),'allPTSAndDTSUniform60fps':True}
            ah=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip();audioPacketHashes[kind]=ah
    assert len(set(audioPacketHashes.values()))==1
    if reusePicture:
        videoHash=subprocess.check_output(['ffmpeg','-v','error','-i',str(clean),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
        assert videoHash==reusePicture['videoPacketSHA256']
    run(['-loglevel','info','-i',clean,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],L/'loudness.log')
    meter=(L/'loudness.log').read_text('utf-8',errors='replace');loudness=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1])
    manifest=dict(id=ep,slug=slug,title=p['title'],revision='pacing-v3',status='encoded-technical-check-passed-visual-review-pending',durationSeconds=p['totalFrames']/60,files=files,baseline=base['captionedSha256'],events=events,narrationAllSamplesPreserved=all(x['exactEquality'] for x in proof),packetProof=packetProof,identicalAAC=audioPacketHashes,loudnessMeasuredWithoutChangingAudio=loudness,humanViewed=False)
    if reusePicture:manifest['pictureReusedFrom']=reusePicture
    save(D/'delivery-manifest.json',manifest);save(P/'production/pacing-v3/checkpoint.json',manifest)
    (D/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#101713;color:#eee;font:18px/1.6 sans-serif;margin:24px}video{width:100%;max-height:76vh}a{color:#add9bd}</style><h1>'+html.escape(ep+' '+p['title'])+'</h1><p>기본 속도 3회 관찰 → 기존 구간·자세 분석. 최종 검수 대기.</p><video controls playsinline src="'+slug+'.captioned.mp4"></video><p>'+''.join('<a href="'+slug+'.'+k+'">'+k+'</a>　' for k in ['captioned.mp4','clean.mp4','ko.srt','en.srt'])+'</p>','utf-8')
    print(ep,'DELIVERY',str(D),'seconds',p['totalFrames']/60,flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
