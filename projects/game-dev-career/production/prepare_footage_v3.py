"""Download and assemble the v3 all-new licensed role-overview footage."""
from pathlib import Path
import json, subprocess

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PLAN=json.loads((BASE/'media-sources-v3.json').read_text(encoding='utf-8'))
OUT=ROOT/'motion-canvas/src/projects/game-dev-career/assets/examples-v3'
RAW=BASE/'media-v3-raw'
CONTACT=BASE/'media-v3'
OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True);CONTACT.mkdir(parents=True,exist_ok=True)

def run(args, capture=True):
    result=subprocess.run(args,cwd=ROOT,capture_output=capture,text=True,encoding='utf-8',errors='replace')
    if result.returncode:
        message=(result.stderr or result.stdout or '')[-5000:]
        raise RuntimeError(message)
    return result.stdout if capture else ''

def has_audio(path):
    value=run(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=index','-of','csv=p=0',str(path)])
    return bool(value.strip())

# Compute the small source interval needed by every selected cut.  The raw cache is
# never committed and is deliberately separate from older project media.
needed={}
for scene in PLAN['scenes']:
    for cut in scene['cuts']:
        item=needed.setdefault(cut['source'],[]);item.append(cut)

for key,cuts in needed.items():
    source=PLAN['sources'][key];dst=ROOT/source['file']
    if dst.exists():
        print('RAW CACHED',key,flush=True);continue
    start=float(source['fileStart'])
    end=max(float(c['in'])+float(c['seconds']) for c in cuts)+2
    dst.parent.mkdir(parents=True,exist_ok=True)
    base_command=[
        str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-m','yt_dlp','--no-progress','--js-runtimes','node',
        '--download-sections',f'*{start}-{end}','--force-keyframes-at-cuts',
    ]
    output_args=['--merge-output-format','mp4','-o',str(dst),source['url']]
    selectors=[
        'bv*[height<=1080]+ba/b[height<=1080]',
        'bv*[height<=1080][protocol^=m3u8]+ba[protocol^=m3u8]/b[height<=1080]',
    ]
    print('DOWNLOAD',key,f'{start:.1f}-{end:.1f}',flush=True)
    last_error=None
    for selector in selectors:
        try:
            run(base_command+['-f',selector]+output_args,capture=True)
            last_error=None
            break
        except RuntimeError as exc:
            last_error=exc
            print('RETRY',key,'with alternate YouTube transport',flush=True)
    if last_error is not None:
        raise last_error
    if not dst.exists():raise FileNotFoundError(dst)

reports=[]
for scene in PLAN['scenes']:
    dst=OUT/(scene['id']+'.mp4')
    args=['ffmpeg','-v','error','-y'];filters=[];labels=[];input_index=0
    for i,cut in enumerate(scene['cuts']):
        source=PLAN['sources'][cut['source']];raw=ROOT/source['file'];offset=float(cut['in'])-float(source.get('fileStart',0))
        args+=['-ss',str(offset),'-t',str(cut['seconds']),'-i',str(raw)]
        filters.append(f'[{input_index}:v]setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30,trim=duration={cut["seconds"]}[v{i}]')
        if has_audio(raw):
            filters.append(f'[{input_index}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,atrim=duration={cut["seconds"]}[a{i}]')
        else:
            args+=['-f','lavfi','-t',str(cut['seconds']),'-i','anullsrc=r=48000:cl=stereo']
            filters.append(f'[{input_index+1}:a]asetpts=PTS-STARTPTS,atrim=duration={cut["seconds"]}[a{i}]')
            input_index+=1
        labels.append(f'[v{i}][a{i}]');input_index+=1
    filters.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=1[v][a]')
    run(args+['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-t',str(scene['seconds']),'-c:v','libx264','-preset','fast','-crf','19','-g','30','-keyint_min','30','-sc_threshold','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',str(dst)])
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dst)]));video=next(s for s in info['streams'] if s['codec_type']=='video')
    expected=round(float(scene['seconds'])*30)
    if int(video['nb_frames'])!=expected:raise RuntimeError(f'{scene["id"]}: {video["nb_frames"]} != {expected}')
    if not any(s['codec_type']=='audio' for s in info['streams']):raise RuntimeError(f'{scene["id"]}: audio stream missing')
    run(['ffmpeg','-v','error','-i',str(dst),'-f','null','-'])
    run(['ffmpeg','-v','error','-y','-i',str(dst),'-vf','fps=1/3,scale=480:-1,tile=4x2:padding=3:color=white','-frames:v','1',str(CONTACT/f'cut-{scene["id"]}.jpg')])
    reports.append({'scene':scene['id'],'file':str(dst.relative_to(ROOT)),'frames':int(video['nb_frames']),'seconds':float(video['duration']),'audio':True,'fullDecode':True})
    print('PREPARED',scene['id'],flush=True)

(BASE/'footage-build-v3.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ALL V3 FOOTAGE READY',flush=True)
