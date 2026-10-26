"""Build and inspect one current Short; never replace successful encoded media."""
from pathlib import Path
import argparse, hashlib, json, subprocess, math
from PIL import Image, ImageDraw
from audio_revision import MEDIA_ROOT, VOICE, REVISION, media_reference, media_allowed, assert_no_game_apps, LEASE

P=Path(__file__).resolve().parents[1]
R=P.parents[1]
L=P/json.loads((P/'project.json').read_text(encoding='utf8')).get('currentFinalDirectory','production/local/final-reviewed')
A=P/'production/local/audio-v2'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
def run(args):
    result=subprocess.run(args,cwd=R,capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace')[-5000:])
    return result.stdout
def guard():
    from audio_revision import guard as current_guard
    control=current_guard()
    assert_no_game_apps()
    if LEASE.exists(): raise RuntimeError('Foreign GPU/costly lease preserved; defer final encode.')
    if not L.resolve().is_relative_to((MEDIA_ROOT/'local').resolve()):
        raise RuntimeError('Final outputs must stay inside this finite selected project C: local directory.')
    return control

def ass_filter(): return 'ass='+str((A/'captions.ko.ass').relative_to(R)).replace('\\','/')
def verify_pair_inputs(visual, captions, header):
    """Read-only acceptance of the current frame timeline before encoding."""
    if captions.get('fps')!=60 or captions.get('frames',0)<=0:
        raise RuntimeError('Require the actual current 60fps caption timeline.')
    if abs(captions['durationSeconds']-captions['frames']/60)>1e-7:
        raise RuntimeError('Caption duration and exact frame count differ.')
    timing=read(P/'production/visual-timing.json')
    local_timing=read(P/'production/local/visual-timing.json')
    if timing!=local_timing or timing.get('revision')!=REVISION or timing.get('previewOnly') is not False:
        raise RuntimeError('Use the same actual production timing for MC and the audio mix.')
    if timing.get('frames')!=captions['frames']:
        raise RuntimeError('Visual/caption frame counts differ.')
    digest=sha(VOICE)
    config=read(P/'production/visual-config.json')
    rendered=read(P/'production/local'/(visual.stem+'-render.json'))
    if (rendered.get('revision')!=REVISION or rendered.get('fullCurrentTimeline') is not True
            or rendered.get('outputSha256')!=sha(visual)
            or rendered.get('configSha256')!=sha(P/'production/visual-config.json')
            or rendered.get('inputHashes')!=config.get('inputs') or config.get('inputsReady') is not True):
        raise RuntimeError('Use this exact complete MC render and current accepted input hashes.')
    header_receipt=read(P/'production/local/header-build.json')
    if header_receipt.get('sha256')!=sha(header) or header_receipt.get('text')!=config.get('head'):
        raise RuntimeError('Fixed header differs from its current title recipe.')
    if captions.get('timingInputs',{}).get('voiceSha256')!=digest:
        raise RuntimeError('Captions do not belong to the current complete narration PCM.')
    audio=read(A/'audio-build.json')
    if audio.get('recipe',{}).get('voice',{}).get('sha256')!=digest:
        raise RuntimeError('Mixed voice differs from the current caption PCM.')
    if audio.get('artifacts',{}).get('final-mix.m4a',{}).get('sha256')!=sha(A/'final-mix.m4a'):
        raise RuntimeError('Final mix differs from its recorded successful build.')
    with Image.open(header) as image:
        if image.size!=(1080,440):
            raise RuntimeError('Fixed header must be exactly 1080x440 and leave dynamic labels below it.')
    info=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(visual)]))
    video=next(s for s in info['streams'] if s['codec_type']=='video')
    if (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))!=(1080,1920,'60/1',captions['frames']):
        raise RuntimeError('Require the complete exact current 1080x1920/60 visual master.')
    used={s['source'] for s in timing['nativeSegments']}
    if not used:
        raise RuntimeError('Selected finite Short requires its independently viewed real-game footage.')
    for key in used:
        source=timing['sources'][key];path=R/source['path']
        if not media_allowed(path) or not path.is_file() or source.get('sourceSHA256')!=sha(path):
            raise RuntimeError('Selected game source path/hash changed: '+key)
        probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
        stream=next(s for s in probe['streams'] if s['codec_type']=='video')
        if stream['width']<1920 or stream['height']<1080:
            raise RuntimeError('Selected source is not native FHD or higher: '+key)
        limit=float(probe['format']['duration'])
        for section in timing['nativeSegments']:
            if section.get('kind')!='game' or section['source']!=key:continue
            if float(section.get('rate',1))!=1:
                raise RuntimeError('Preserve native gameplay speed.')
            start=float(section['sourceStart']);end=float(section['sourceEnd'])
            if not 0<=start<end<=limit+1/60:
                raise RuntimeError('Selected gameplay interval exceeds the actual source.')
    return {'voiceSha256':digest,'visualSha256':sha(visual),'headerSha256':sha(header),'sourceIds':sorted(used)}

def pair(visual):
    guard(); c=read(P/'script/captions.json'); visual=Path(visual).resolve()
    L.mkdir(parents=True,exist_ok=True)
    owned_media=Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-splatoon-ink-readability').resolve()
    assert visual.is_relative_to(R) or visual.is_relative_to(owned_media), 'Use an owned recorded render.'
    assert not (L/'clean.mp4').exists() and not (L/'captioned.mp4').exists()
    assert (A/'final-mix.m4a').exists() and (A/'captions.ko.ass').exists()
    header=P/'production/local/static-header-v1.png'
    assert header.exists(), 'Generate the inspected fixed brand heading first.'
    acceptance=verify_pair_inputs(visual,c,header)
    run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(A/'final-mix.m4a'),'-i',str(header),'-filter_complex','[0:v][2:v]overlay=0:0:format=auto[v]','-map','[v]','-map','1:a:0','-frames:v',str(c['frames']),'-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(L/'clean.mp4')])
    run(['ffmpeg','-v','error','-n','-i',str(L/'clean.mp4'),'-vf',ass_filter(),'-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(L/'captioned.mp4')])
    for language in ['ko','en']:
        source=A/f'captions.{language}.srt';target=L/source.name
        if target.exists() and sha(target)!=sha(source):
            raise RuntimeError('Preserve differing final subtitles: '+str(target))
        if not target.exists():
            with target.open('xb') as handle:handle.write(source.read_bytes())
        assert sha(target)==sha(source)
    save(L/'pair-build.json',dict(frames=c['frames'],durationSeconds=c['durationSeconds'],visual=sha(visual),audio=sha(A/'final-mix.m4a'),ass=sha(A/'captions.ko.ass'),clean=sha(L/'clean.mp4'),captioned=sha(L/'captioned.mp4'),captionsKo=sha(L/'captions.ko.srt'),captionsEn=sha(L/'captions.en.srt'),speechSpeed=1,inputAcceptance=acceptance))
def integrity():
    guard(); c=read(P/'script/captions.json'); reports=[]; audio_hashes=[]
    for name in ['clean','captioned']:
        file=L/(name+'.mp4')
        run(['ffmpeg','-v','error','-xerror','-i',str(file),'-f','null','-'])
        info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]))
        v=next(s for s in info['streams'] if s['codec_type']=='video')
        a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',c['frames'])
        pts=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(file)]))['frames']
        assert len(pts)==c['frames'] and all(abs(float(f['best_effort_timestamp_time'])-i/60)<2e-6 for i,f in enumerate(pts))
        raw=run(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c','copy','-f','adts','pipe:1'])
        audio_hashes.append(hashlib.sha256(raw).hexdigest())
        reports.append(dict(name=name,sha256=sha(file),bytes=file.stat().st_size,video=v,audio=a,decoded=True,ptsRegular60=True,frames=len(pts)))
    raw=run(['ffmpeg','-v','error','-i',str(A/'final-mix.m4a'),'-map','0:a:0','-c','copy','-f','adts','pipe:1'])
    assert audio_hashes[0]==audio_hashes[1]==hashlib.sha256(raw).hexdigest()
    assert all(0<=q['start']<q['end']<=c['durationSeconds'] for q in c['cues'])
    save(L/'integrity.json',dict(status='pass',outputs=reports,identicalAac=True,aacHash=audio_hashes[0],allCaptionTimesInsideVideo=True))
def qa():
    guard(); c=read(P/'script/captions.json'); timing=read(P/'production/visual-timing.json')
    master_hash=sha(L/'captioned.mp4')
    out=L/('qa-sequential-'+master_hash[:12]); out.mkdir(exist_ok=True)
    points=[(q['start']+q['end'])/2 for q in c['cues']]
    for s in timing['sections']:
        points.extend([s['start'],s['start']+1/60,s['end']-1/60])
        if s.get('kind')!='game':
            points.extend(s['start']+u for u in [.4,.9,1.6,2.2,3.5] if s['start']+u<s['end'])
    points.extend([.1,c['durationSeconds']-.15])
    selected=sorted(set(min(c['frames']-1,round(t*60)) for t in points if 0<=t<c['durationSeconds']))
    # Decode once from the beginning and select exact frames. Large contact-sheet
    # previews must be checked against native frames/crops before diagnosing a
    # visual defect; a displayed collage alone is not a changed master frame.
    if not (out/'frame-000.jpg').exists():
        def balanced(items):
            if len(items)==1:return items[0]
            m=len(items)//2
            return '('+balanced(items[:m])+'+'+balanced(items[m:])+')'
        expression=balanced(['eq(n\\,'+str(n)+')' for n in selected])
        run(['ffmpeg','-v','error','-n','-threads','3','-i',str(L/'captioned.mp4'),'-vf','select='+expression,'-fps_mode','vfr','-frames:v',str(len(selected)),'-start_number','0','-pix_fmt','yuvj420p','-threads','1','-q:v','2',str(out/'frame-%03d.jpg')])
    rows=[]
    for i,n in enumerate(selected):
        t=n/60
        target=out/f'frame-{i:03}.jpg'
        assert target.exists() and target.stat().st_size>0, 'Frame extraction did not produce an image: '+str(t)
        rows.append(dict(frame=n,seconds=t,path=media_reference(target)))
    for start in range(0,len(rows),12):
        sheet=Image.new('RGB',(1500,2100),'#202020'); draw=ImageDraw.Draw(sheet)
        for j,row in enumerate(rows[start:start+12]):
            im=Image.open(R/row['path']).convert('RGB'); im.thumbnail((375,666))
            x=j%4*375; y=j//4*700; sheet.paste(im,(x,y));draw.text((x+5,y+674),str(row['seconds'])+'s',fill='white')
        sheet.save(out/f'sheet-{start//12+1:02}.jpg',quality=92)
    save(out/'index.json',dict(masterSha256=master_hash,rows=rows,decode='single sequential pass; exact60fps frame selection',scope='All cue midpoints, every section join and sampled motion states at native and mobile size. Moving playback separately recorded.'))
    if not (L/'mobile-review.mp4').exists(): run(['ffmpeg','-v','error','-n','-i',str(L/'captioned.mp4'),'-vf','scale=374:666','-c:v','libx264','-threads','3','-preset','fast','-crf','22','-c:a','copy','-movflags','+faststart',str(L/'mobile-review.mp4')])
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['pair','integrity','qa']);parser.add_argument('--visual')
    args=parser.parse_args()
    if args.command=='pair':
        assert args.visual,'Pass the exact successful current visual render.'
        pair(args.visual)
    else: globals()[args.command]()
