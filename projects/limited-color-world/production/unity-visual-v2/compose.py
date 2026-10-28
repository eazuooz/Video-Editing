"""D25/D26 visual-only pair assembly. Never changes speech, source cuts or originals.

Run one explicit stage for one slug. `prepare` only validates inputs and remuxes
replacement video headers; expensive render/verify are deliberately separate.
"""
import argparse
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
MEDIA=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
SLUGS={'limited-color-world','computer-controlled-players'}

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def stamp():return datetime.now(timezone.utc).isoformat()
def ff(args,log):
    with Path(log).open('w',encoding='utf-8') as f:
        p=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-nostdin','-v','warning','-n','-filter_threads','1','-filter_complex_threads','1',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if p.returncode:raise RuntimeError(Path(log).read_text('utf-8',errors='replace')[-4000:])
def probe(p):return json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def video(p,count):
    vs=[s for s in probe(p)['streams'] if s['codec_type']=='video'];assert len(vs)==1
    s=vs[0]
    assert (s['width'],s['height'],Fraction(s['avg_frame_rate']),int(s['nb_frames']))==(1920,1080,Fraction(60),count),(p,s)
    return s
def audio_hash(p):
    return subprocess.check_output([shutil.which('ffmpeg'),'-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def video_hash(p):
    return subprocess.check_output([shutil.which('ffmpeg'),'-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def pts_scan(p,frames):
    proc=subprocess.Popen([shutil.which('ffprobe'),'-v','error','-threads','3','-err_detect','explode','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    last=-1;count=0;error=0
    for row in proc.stdout:
        value=row.split(',')[0].strip()
        if not value:continue
        try:t=float(value)
        except ValueError:continue
        assert t>last,(p,t,last);error=max(error,abs(t-count/60));last=t;count+=1
    err=proc.stderr.read();code=proc.wait()
    assert code==0 and not err.strip(),err
    assert count==frames and error<1e-5,(count,frames,error)
    return {'frames':count,'lastPts':last,'maxGridErrorSeconds':error,'fullVideoDecoded':True}

def context(args):
    assert args.slug in SLUGS
    project=ROOT/'projects'/args.slug
    plan=read(project/'production/batch-v1/edit-plan.json')
    visual=read(project/'production/unity-visual-v2/visual-plan.json')
    control=read(ROOT/'shared/publishing/video-production-control.json')
    authorization=control['finiteBatchAuthorizations']['design-25-30-unity-v2-20261028']
    assert args.slug in authorization['slugs'] and authorization['localProductionAuthorized'] is True
    assert visual['preservation']['newTts'] is False and visual['preservation']['cutClocks'] is True
    assert sha(ROOT/visual['baseEditPlan']['path'])==visual['baseEditPlan']['sha256']
    frozen={f['key']:f for f in visual['frozenInputs']}
    for f in frozen.values():assert sha(ROOT/f['path'])==f['sha256'],f['path']
    out=MEDIA/args.slug/('composite-'+args.version)
    assert out.resolve().is_relative_to(MEDIA.resolve())
    out.mkdir(parents=True,exist_ok=True)
    captures=Path(args.capture_root or (MEDIA/args.slug/'render'/args.capture_version))
    expected=MEDIA/args.slug/'render'
    assert captures.resolve().is_relative_to(expected.resolve())
    return project,plan,visual,frozen,out,captures

def prepare(args):
    project,plan,visual,frozen,out,captures=context(args)
    replacements={c['id']:c for c in visual['cuts'] if c['operation']=='replace-explanation-visual'}
    old=ROOT/plan['outputDir'];entries=[]
    canonical=old/'pair-join'
    brand=canonical/'branding-timescale60000.mp4';member=canonical/'membership-timescale60000.mp4'
    video(brand,120);video(member,600)
    entries.append({'id':'branding','path':str(brand),'frames':120,'sha256':sha(brand),'operation':'preserved'})
    for cut in plan['cuts']:
        if cut['id'] in replacements:
            folder=captures/cut['id'];native=read(folder/'render-success.json');request=read(folder/'request.json')
            assert native['status']=='complete' and native['slug']==args.slug and native['cutId']==cut['id']
            assert native['frames']==cut['frames'] and native['completed']==cut['frames']
            assert native['compiledSourceFingerprint']==request['expectedFingerprint']
            job={k:request[k] for k in ['slug','cutId','frames','stageClass']}
            current=hashlib.sha256(b''.join((ROOT/p).read_bytes() for p in request['sourceFiles'])+json.dumps(job,sort_keys=True).encode()).hexdigest()
            assert current==request['inputHash'],'Capture does not match current frozen source: '+cut['id']
            src=folder/'unity.mp4';meta=video(src,cut['frames']);src_hash=sha(src)
            target=out/(cut['id']+'-timescale60000.mp4');receipt=target.with_suffix('.json')
            if target.exists():
                old_r=read(receipt);assert old_r['sourceSha256']==src_hash and old_r['outputSha256']==sha(target)
            else:
                ff(['-i',src,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','60000','-movflags','+faststart',target],out/(cut['id']+'-remux.log'))
                assert video_hash(src)==video_hash(target)
                write(receipt,{'source':str(src),'sourceSha256':src_hash,'outputSha256':sha(target),'compressedVideoIdentical':True})
            video(target,cut['frames']);p=target;op='unity-explanation-replacement'
        else:
            p=old/(cut['id']+'.mp4');meta=video(p,cut['frames'])
            receipt=read(old/(cut['id']+'-render.json'))
            assert receipt['signature']['cut']==cut
            assert receipt['outputSha256']==sha(p)
            op='preserved-independent-gameplay' if cut['kind']=='independent-gameplay' else 'preserved-factual-explanation-screen'
        assert Fraction(video(p,cut['frames'])['time_base'])==Fraction(1,60000)
        entry={'id':cut['id'],'scene':cut['scene'],'path':str(p),'frames':cut['frames'],'sha256':sha(p),'operation':op,'startFrame':cut['startFrame'],'endFrame':cut['endFrame']}
        if cut['id'] in replacements:entry['nativeCapture']={'requestSha256':sha(folder/'request.json'),'successSha256':sha(folder/'render-success.json'),'inputHash':request['inputHash'],'compiledSourceFingerprint':native['compiledSourceFingerprint'],'scene':native['scene']}
        entries.append(entry)
    entries.append({'id':'membership','path':str(member),'frames':600,'sha256':sha(member),'operation':'preserved'})
    assert sum(e['frames'] for e in entries)==plan['totalFrames']
    concat=out/'concat.txt';concat.write_text('\n'.join("file '"+Path(e['path']).as_posix().replace("'","'\\''")+"'" for e in entries)+'\n','utf-8')
    master=ROOT/frozen['videoBurnedCaptions']['path'];aac_hash=audio_hash(master)
    receipt={'status':'prepared','slug':args.slug,'revision':'unity-visual-v2','preparedAt':stamp(),'entries':entries,'totalFrames':plan['totalFrames'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'ratioPreserved':True,'oldCaptionedMaster':str(master),'oldMasterSha256':frozen['videoBurnedCaptions']['sha256'],'audioPacketsSha256':aac_hash,'captionsAss':str(ROOT/plan['captionsAss']),'captionsAssSha256':sha(ROOT/plan['captionsAss']),'frozenInputs':visual['frozenInputs'],'concatSha256':sha(concat),'newTts':False,'userWholeReviewOfNewVersion':False,'captureRoot':str(captures)}
    write(out/'preparation.json',receipt);print(json.dumps({'prepared':args.slug,'unityCuts':len(replacements),'out':str(out)}),flush=True)

def render(args):
    project,plan,visual,frozen,out,captures=context(args)
    r=read(out/'preparation.json');assert r['status']=='prepared'
    for e in r['entries']:assert sha(e['path'])==e['sha256']
    assert sha(out/'concat.txt')==r['concatSha256'] and sha(r['captionsAss'])==r['captionsAssSha256']
    outputs={k:out/(args.slug+'.'+k+'.mp4') for k in ['clean','captioned']}
    if all(p.exists() for p in outputs.values()) and (out/'pair-build.json').exists():
        prior=read(out/'pair-build.json')
        assert prior['preparationSha256']==sha(out/'preparation.json')
        for k,p in outputs.items():assert prior['outputs'][k]['sha256']==sha(p)
        print('Identical completed pair reused');return
    for p in outputs.values():assert not p.exists(),p
    # Copy the original complete continuous AAC stream from the reviewed master.
    # setpts forces the original 60fps clock across heterogeneous cut headers.
    ass=r['captionsAss'].replace('\\','/').replace(':','\\:').replace("'","\\'")
    graph="[0:v]setpts=N/(60*TB),settb=1/60000,setsar=1,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,split=2[clean][cap];[cap]ass='"+ass+"'[captioned]"
    cmd=['-f','concat','-safe','0','-reinit_filter','0','-i',out/'concat.txt','-i',r['oldCaptionedMaster'],'-filter_complex',graph]
    for kind,p in outputs.items():cmd+=['-map','['+kind+']','-map','1:a:0','-frames:v',str(plan['totalFrames']),'-t',f"{plan['totalFrames']/60:.9f}",'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-fps_mode','passthrough','-c:a','copy','-movflags','+faststart',p]
    ff(cmd,out/'pair-encode.log')
    result={}
    for k,p in outputs.items():
        meta=video(p,plan['totalFrames']);ah=audio_hash(p);assert ah==r['audioPacketsSha256']
        result[k]={'path':str(p),'sha256':sha(p),'audioPacketsSha256':ah,'video':meta}
    write(out/'pair-build.json',{'status':'encoded-awaiting-visual-QA','preparationSha256':sha(out/'preparation.json'),'outputs':result,'exactOriginalAacCopied':True,'newSpeechOrMix':False})
    print('Pair encoded with exact original AAC',flush=True)

def verify(args):
    project,plan,visual,frozen,out,captures=context(args)
    r=read(out/'preparation.json');pairs=read(out/'pair-build.json');result={}
    for kind,p in pairs['outputs'].items():
        file=Path(p['path']);assert sha(file)==p['sha256'];video(file,plan['totalFrames'])
        ah=audio_hash(file);assert ah==r['audioPacketsSha256']
        pts=pts_scan(file,plan['totalFrames'])
        ff(['-xerror','-err_detect','explode','-i',file,'-map','0:a:0','-vn','-f','null','-'],out/(kind+'-audio-decode.log'))
        meta=probe(file);aud=[s for s in meta['streams'] if s['codec_type']=='audio'];assert len(aud)==1 and aud[0]['codec_name']=='aac' and aud[0]['sample_rate']=='48000'
        assert abs(float(meta['format']['duration'])-plan['totalFrames']/60)<1/60
        result[kind]={'path':str(file),'sha256':p['sha256'],'pts':pts,'audioPacketsSha256':ah,'fullAudioVideoDecode':'pass','video':p['video']}
    for lang,key in [('ko','captionsKo'),('en','captionsEn')]:
        src=ROOT/frozen[key]['path'];dst=out/(args.slug+'.'+lang+'.srt')
        if dst.exists():assert sha(dst)==sha(src)
        else:shutil.copyfile(src,dst)
    write(out/'structural-verification.json',{'status':'pass','outputs':result,'originalAacIdentical':True,'originalCaptionsIdentical':True,'totalFrames':plan['totalFrames'],'durationSeconds':plan['totalFrames']/60,'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'unchangedSourceReviewReusable':True,'finalVisualQa':'pending','humanNewVersionReview':'pending'})
    print('Two full decodes, exact source AAC and paired SRT passed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','verify']);p.add_argument('--slug',required=True,choices=sorted(SLUGS));p.add_argument('--version',default='v1');p.add_argument('--capture-version',default='v1');p.add_argument('--capture-root');args=p.parse_args()
    assert args.version.replace('-','').isalnum() and args.capture_version.replace('-','').isalnum()
    globals()[args.stage](args)
