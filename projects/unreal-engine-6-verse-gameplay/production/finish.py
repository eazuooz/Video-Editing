"""Pair the measured picture and a single AAC stream and verify both encoded masters."""
from pathlib import Path
from fractions import Fraction
import json, hashlib, shutil, subprocess, math, sys, time
from PIL import Image,ImageDraw
import numpy as np
from edition import BASE, EXTENDED, LOCAL
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=LOCAL
B=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def hashfile(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def run(args,name):
    log=L/(name+'.log')
    with log.open('wb') as f:
        rc=subprocess.call(['ffmpeg','-y','-nostdin','-hide_banner',*map(str,args)],cwd=R,stdout=f,stderr=f)
    if rc:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-2200:])
def video(path,n):
    streams=probe(path)['streams'];v=next(s for s in streams if s['codec_type']=='video')
    assert (v['width'],v['height'],Fraction(v['avg_frame_rate']),int(v['nb_frames']))==(1920,1080,60,n),(path,v)
def audio_encode(plan):
    run(['-loglevel','warning','-i',L/'final-mix.wav','-t',str(plan['totalFrames']/60),'-ac','2','-ar','48000','-c:a','aac','-b:a','192k',L/'audio.m4a'],'aac')
def pair(plan):
    body_parts=[(BASE/'body.mp4',plan.get('baseBodyFrames',plan['bodyFrames']))]
    if EXTENDED:
        until=time.monotonic()+600
        while time.monotonic()<until:
            receipt=L/'visuals/comparison-render.json'
            if receipt.exists():
                entry=read(receipt)
                if entry['timeline']==hashfile(L/'timeline.json') and entry['frames']==plan['extraBodyFrames']:
                    assert entry['sha256']==hashfile(L/'body-extra.mp4')
                    break
            time.sleep(3)
        else:raise TimeoutError('Awaiting comparison image receipt bound to the final Qwen timeline')
        body_parts.append((L/'body-extra.mp4',plan['extraBodyFrames']))
    assert sum(n for _,n in body_parts)==plan['bodyFrames']
    parts=[(B/'branding.mp4',120),*body_parts,(B/'membership.mp4',600)]
    paths=[p for p,_ in parts]
    for p,n in parts:video(p,n)
    n=plan['totalFrames'];g=[]
    for i in range(len(parts)):g.append(f'[{i}:v]setsar=1,format=yuv420p,settb=1/60,setpts=N[v{i}]')
    labels=''.join(f'[v{i}]' for i in range(len(parts)))
    g+=[labels+f'concat=n={len(parts)}:v=1:a=0,settb=1/60,setpts=N,split=2[clean][c]',"[c]ass="+(L/'captions.ko.ass').relative_to(R).as_posix()+"[cc]"]
    args=['-loglevel','warning','-filter_complex_threads','2']
    for p in paths:args+=['-threads','2','-i',p]
    args+=['-i',L/'audio.m4a','-filter_complex',';'.join(g)]
    for tag,output in [('clean','clean.mp4'),('cc','captioned.mp4')]:
        args+=['-map',f'[{tag}]','-map',f'{len(parts)}:a:0','-r','60','-frames:v',str(n),'-t',str(n/60),'-c:v','libx264','-threads','5','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-colorspace','bt709','-color_trc','bt709','-video_track_timescale','60000','-c:a','copy','-movflags','+faststart',L/output]
    run(args,'pair')

def stream_hash(path,selector):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map',selector,
        '-c','copy','-f','hash','-hash','sha256','-']).decode().strip()

def remux(plan):
    """Retain the verified picture packets and replace only the music-balanced AAC."""
    assert EXTENDED and (L/'coda-music-balance.json').is_file()
    archive=L/'qa/pre-coda-balance'
    prior=read(L/'encoded-verification.json')
    music=stream_hash(L/'audio.m4a','0:a:0')
    checks={}
    for tag in ['clean','captioned']:
        earlier=L/f'{tag}.mp4';new=L/f'balanced-{tag}.mp4'
        assert prior['masters'][tag]['sha256']==hashfile(earlier)
        run(['-v','error','-i',earlier,'-i',L/'audio.m4a','-map','0:v:0','-map','1:a:0',
             '-c','copy','-movflags','+faststart',new],'remux-'+tag)
        video(new,plan['totalFrames'])
        assert stream_hash(new,'0:a:0')==music
        before=stream_hash(earlier,'0:v:0');assert stream_hash(new,'0:v:0')==before
        checks[tag]={'videoPacketPayloadHash':before,'audioPacketPayloadHash':music}
    shutil.copyfile(L/'encoded-verification.json',archive/'encoded-verification.json')
    for tag in ['clean','captioned']:(L/f'balanced-{tag}.mp4').replace(L/f'{tag}.mp4')
    (L/'final-remux.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
def verify(plan):
    size=plan['totalFrames']; checks={}; streams=[]
    for tag in ['clean','captioned']:
        p=L/f'{tag}.mp4';video(p,size);info=probe(p)
        a=next(x for x in info['streams'] if x['codec_type']=='audio');assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
        assert abs(float(a['duration'])-size/60)<.05
        # Decode each video and audio completely; fail on corrupt packets.
        run(['-v','error','-xerror','-threads','5','-i',p,'-map','0:v','-map','0:a','-f','null','-'],'decode-'+tag)
        ts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)]).splitlines()
        step=Fraction(1,60)/Fraction(next(s for s in info['streams'] if s['codec_type']=='video')['time_base'])
        assert sorted(int(x) for x in ts)==[int(k*step) for k in range(size)],tag
        a_hash=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a','-c:a','copy','-f','hash','-hash','sha256','-']).decode().strip();streams.append(a_hash)
        checks[tag]={'sha256':hashfile(p),'frames':size,'audio':a_hash,'fullDecode':'pass','pts':'complete CFR 60'}
    assert streams[0]==streams[1]
    run(['-i',L/'captioned.mp4','-vn','-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],'encoded-loudness')
    log=(L/'encoded-loudness.log').read_text(encoding='utf-8',errors='replace');stats=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    assert float(stats['input_tp'])<=-1.5,stats
    cues=read(L/'cue-review.json');times=[round((c['start']+c['end'])*30) for c in cues]
    Q=L/'qa';Q.mkdir(exist_ok=True)
    expressions=['eq(n\\,'+str(n)+')' for n in times]
    # FFmpeg rejects a left-associative expression roughly 100 levels deep.
    # A balanced tree selects the same exact frames in one decode pass.
    while len(expressions)>1:
        expressions=[f'({expressions[i]}+{expressions[i+1]})' if i+1<len(expressions)
                     else expressions[i] for i in range(0,len(expressions),2)]
    selection=expressions[0]
    run(['-v','error','-threads','4','-i',L/'captioned.mp4','-vf','select='+selection+',scale=960:540','-fps_mode','vfr','-q:v','3',Q/'cue-%03d.jpg'],'cue-pixels')
    files=sorted(Q.glob('cue-*.jpg'));assert len(files)==len(cues)
    for k,file in enumerate(files):
        img=Image.open(file);area=np.asarray(img)[448:529,70:900,:3]
        white=(area.min(axis=2)>225);assert white.sum()>1100,(k,file)
    for start in range(0,len(files),18):
        sheet=Image.new('RGB',(375*3, (211+22)*6),'#181b1a');d=ImageDraw.Draw(sheet)
        for j,file in enumerate(files[start:start+18]):
            im=Image.open(file).resize((375,211),Image.Resampling.LANCZOS);x=j%3*375;y=j//3*233
            sheet.paste(im,(x,y));d.text((x+6,y+212),f'{start+j+1:03}  {times[start+j]/60:.1f}s',fill='white')
        sheet.save(Q/f'mobile-{start//18+1}.jpg',quality=89)
    result={'masters':checks,'audioMeasurement':stats,'seconds':size/60,'allCuePixelSamples':len(cues),'visualHumanApproval':False,'wholeHumanListening':False}
    (L/'encoded-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    plan=read(L/'timeline.json')
    mode=sys.argv[1]
    assert read(R/'shared/publishing/video-production-control.json')['scopedProductionAuthorizations'][P.name]['renderAuthorized']
    {'audio':audio_encode,'pair':pair,'remux':remux,'verify':verify}[mode](plan)
