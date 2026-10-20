"""Finite game-left inputs. Design is CPU/metadata only; media jobs are explicit.

No narration, approved script, timing, shared control or other video's files
are changed. Native clips are prepared only after the root audio-slot handoff.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, subprocess

H=Path(__file__).resolve().parent;R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v7-part1'
G=O/'gameplay';FPS=60

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def path(p):return Path(p)if Path(p).is_absolute()else R/p
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def timing():
    s=importlib.util.spec_from_file_location('v7_left_input_clock',H/'timing.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inputs():
    j=read(H/'game-inputs.json')
    assert sha(R/j['script'])==j['scriptSha256']
    assert len(j['sources'])==4 and len(j['livePhases'])==11
    return j
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def run(args,log):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('wb')as out:
        q=subprocess.run(args,cwd=R,stdout=out,stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if q.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3000:])

def design():
    """Make explicit reusable media specifications, without decoding/rendering."""
    j=inputs();catalog={}
    for sid,s in j['stills'].items():
        key=f'{s["sourceId"]}:{s["sourceFrame"]}'
        catalog[key]=dict(id=sid,kind='still',file=s['file'],sourceId=s['sourceId'],
            sourceFrame=s['sourceFrame'],sourceSha256=s['sourceSha256'],
            originalSource=s['sourcePath'],existing=True,sha256=s['sha256'],
            classification='gameplay-derived-analysis',dimensions=[1920,1080])
    clips={}
    for q in j['livePhases']:
        clips[q['id']]=dict(id=q['id'],kind='video',file=rel(G/'cuts'/(q['id']+'.mp4')),
            originalSource=q['sourcePath'],sourceId=q['sourceId'],sourceSha256=q['sourceSha256'],
            nativeSourceInFrame=q['sourceInFrame'],nativeSourceOutFrameExclusive=q['sourceOutFrameExclusive'],
            sourceFrames=q['nativeFrames'],dimensions=[1920,1080],fps=60,sourceSpeed=1,
            classification='independent-gameplay',sourceAudioOriginal=q['sourcePath'],
            sourceAudioAllowed=q['sourceAudioAllowed'],silent=q['silent'],prepared=False)
        for b in q['sourceBeats']:
            sf=b['freezeAfter']['sourceFrame'];key=f'{q["sourceId"]}:{sf}'
            if key not in catalog:
                catalog[key]=dict(id='exact-'+q['sourceId']+'-'+str(sf),kind='still',
                    file=rel(G/'exact-frames'/f'{q["sourceId"]}-{sf:07}.png'),
                    sourceId=q['sourceId'],sourceFrame=sf,sourceSha256=q['sourceSha256'],
                    originalSource=q['sourcePath'],existing=False,classification='gameplay-derived-analysis',
                    dimensions=[1920,1080],reason='Exact last native frame of the finite source beat; no silent wait/earlier-pose substitution')
    result=dict(schemaVersion=1,part=1,status='planned-inputs-not-rendered',
        inputs=dict(gameInputsSha256=sha(H/'game-inputs.json'),implementationSha256=sha(Path(__file__))),
        stills=catalog,clips=clips,rect=[40,250,896,504],sourceRaster=[1920,1080],
        sourceToCanvas=dict(scale=7/15,x=40,y=250),sourceCredits='description-only; originalwatermark preserved',
        audio='No addedBGM. Original audio comes from exact live source intervals only; frozen analysis is silent.',
        heavyMediaPrepared=False,sourceSeconds=sum(x['sourceFrames']for x in clips.values())/60)
    save(G/'left-asset-plan.json',result)
    return result

def source_check(asset):
    source=path(asset['originalSource']);assert source.exists()
    assert sha(source)==asset['sourceSha256'],'Changed source requires re-inspection'
    v=next(x for x in probe(source)['streams']if x['codec_type']=='video')
    assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')

def still_frame(asset):
    f=path(asset['file'])
    if f.exists():
        from PIL import Image
        assert Image.open(f).size==(1920,1080)
        if asset.get('sha256'):assert sha(f)==asset['sha256']
        return dict(asset,prepared=True,sha256=sha(f))
    sf=asset['sourceFrame'];sec,offset=divmod(sf,60)
    f.parent.mkdir(parents=True,exist_ok=True)
    run(['ffmpeg','-hide_banner','-nostdin','-n','-threads','1','-ss',str(sec),'-i',str(path(asset['originalSource'])),
         '-vf',f'select=eq(n\\,{offset})','-frames:v','1','-fps_mode','vfr',str(f)],f.with_suffix('.log'))
    from PIL import Image
    assert Image.open(f).size==(1920,1080)
    return dict(asset,prepared=True,sha256=sha(f),pixelReview='pending direct view of the newly extracted frame')

def prepare_stills():
    timing().authorized();a=design();checked=set();rows={}
    for key,x in a['stills'].items():
        if not path(x['file']).exists()and x['sourceId']not in checked:source_check(x);checked.add(x['sourceId'])
        rows[key]=still_frame(x)
    save(G/'left-prepared-stills.json',dict(schemaVersion=1,stills=rows,inputs=dict(assetPlanSha256=sha(G/'left-asset-plan.json'))))
    return rows

def check_clip(f,frames):
    v=next(x for x in probe(f)['streams']if x['codec_type']=='video')
    assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',frames),(str(f),v)
    return v

def prepare_live(handoff,codec='libx264'):
    assert handoff=='root-approved-after-audio','Wait for explicit root heavy-slot handoff; design does not authorize a media job.'
    timing().authorized();a=design();rows={};checked=set()
    for key,x in a['clips'].items():
        f=path(x['file']);receipt=f.with_suffix('.json')
        signature=dict(sourceSha256=x['sourceSha256'],nativeInFrame=x['nativeSourceInFrame'],
            nativeOutFrameExclusive=x['nativeSourceOutFrameExclusive'],implementationSha256=sha(Path(__file__)),codec=codec)
        if f.exists():
            assert receipt.exists()and read(receipt)['inputs']==signature,'Preserve differing existing clip'
            assert read(receipt)['sha256']==sha(f);check_clip(f,x['sourceFrames']);rows[key]=read(receipt);continue
        if x['sourceId']not in checked:source_check(x);checked.add(x['sourceId'])
        sf=x['nativeSourceInFrame'];sec,offset=divmod(sf,60);f.parent.mkdir(parents=True,exist_ok=True)
        # Integer input seek, followed by native decoded-frame selection. This
        # avoids fractional seek rounding and never seeks past the initial act.
        vf=f'trim=start_frame={offset}:end_frame={offset+x["sourceFrames"]},setpts=N/(60*TB),setsar=1'
        enc=['-c:v','libx264','-threads','3','-preset','veryfast','-crf','17']if codec=='libx264'else['-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0']
        run(['ffmpeg','-hide_banner','-nostdin','-n','-threads','2','-filter_threads','1','-ss',str(sec),
             '-i',str(path(x['originalSource'])),'-vf',vf,'-an','-frames:v',str(x['sourceFrames']),
             '-r','60','-fps_mode','passthrough',*enc,'-pix_fmt','yuv420p','-color_primaries','bt709',
             '-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-movflags','+faststart',str(f)],f.with_suffix('.encode.log'))
        v=check_clip(f,x['sourceFrames']);record=dict(x,prepared=True,sha256=sha(f),inputs=signature,probe=v,
            firstLastNativePixelReview='pending actual prepared first/last frame view; exact source bounds documented',
            fullMovingOutputReview='pending paired1920/375output')
        save(receipt,record);rows[key]=record
    save(G/'left-prepared-clips.json',dict(schemaVersion=1,clips=rows,inputs=dict(assetPlanSha256=sha(G/'left-asset-plan.json'))))
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--design',action='store_true');ap.add_argument('--prepare-stills',action='store_true')
    ap.add_argument('--prepare-live',action='store_true');ap.add_argument('--heavy-handoff');ap.add_argument('--codec',choices=['libx264','h264_nvenc'],default='libx264');a=ap.parse_args()
    if a.prepare_live:result=prepare_live(a.heavy_handoff,a.codec);print('Prepared finite native clips',len(result))
    elif a.prepare_stills:print('Prepared still references',len(prepare_stills()))
    elif a.design:
        j=design();print(json.dumps(dict(stills=len(j['stills']),clips=len(j['clips']),sourceSeconds=j['sourceSeconds'],heavyMediaPrepared=False)))
    else:ap.print_help()
if __name__=='__main__':main()
