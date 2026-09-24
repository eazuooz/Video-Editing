"""Reproducible licensed B-roll assembly; source timecodes live in media-sources-v2.json."""
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PLAN=json.loads((BASE/'media-sources-v2.json').read_text(encoding='utf-8'))
OUT=ROOT/'motion-canvas/src/projects/game-dev-career/assets/examples-v2'
OUT.mkdir(parents=True,exist_ok=True)
def run(args):
    r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode: raise RuntimeError(r.stderr[-3000:])
    return r.stdout
reports=[]
for scene in PLAN['scenes']:
    if '--skip04' in sys.argv and scene['id']=='04':continue
    dst=OUT/(scene['id']+'.mp4')
    if dst.exists():
        print('Already prepared',dst.name,flush=True);continue
    args=['ffmpeg','-v','error','-n'];filters=[];labels=[]
    for i,cut in enumerate(scene['cuts']):
        source=PLAN['sources'][cut['source']]
        offset=cut['in']-source.get('fileStart',0)
        args+=['-ss',str(offset),'-t',str(cut['seconds']),'-i',str(ROOT/source['file'])]
        crop='crop='+cut['crop']+',' if cut.get('crop') else ''
        filters.append(f'[{i}:v]setpts=PTS-STARTPTS,{crop}scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps=30,trim=duration={cut["seconds"]}[v{i}]')
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,atrim=duration={cut["seconds"]}[a{i}]')
        labels.append(f'[v{i}][a{i}]')
    filters.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=1[v][a]')
    run(args+['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-t',str(scene['seconds']),'-c:v','libx264','-preset','fast','-crf','19','-g','30','-keyint_min','30','-sc_threshold','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',str(dst)])
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dst)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert abs(float(v['duration'])-scene['seconds'])<.04
    assert int(v['nb_frames'])==round(scene['seconds']*30)
    run(['ffmpeg','-v','error','-i',str(dst),'-f','null','-'])
    run(['ffmpeg','-v','error','-y','-i',str(dst),'-vf','fps=1/3,scale=480:-1,tile=4x2','-frames:v','1',str(BASE/'media-v2'/f'cut-{scene["id"]}.jpg')])
    reports.append({'scene':scene['id'],'file':str(dst.relative_to(ROOT)), 'frames':int(v['nb_frames']),'seconds':float(v['duration']),'audio':True,'fullDecode':True})
    print('PREPARED',scene['id'],scene['seconds'],flush=True)
# Include cached clips in the report too, so a resumed build does not lose QA rows.
reports=[]
for scene in PLAN['scenes']:
    dst=OUT/(scene['id']+'.mp4')
    if not dst.exists():continue
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dst)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==round(scene['seconds']*30)
    assert any(s['codec_type']=='audio' for s in info['streams'])
    run(['ffmpeg','-v','error','-i',str(dst),'-f','null','-'])
    reports.append({'scene':scene['id'],'file':str(dst.relative_to(ROOT)), 'frames':int(v['nb_frames']),'seconds':float(v['duration']),'audio':True,'fullDecode':True})
(BASE/'footage-build-v2.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
