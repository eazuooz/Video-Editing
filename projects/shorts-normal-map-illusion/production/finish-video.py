"""Build and inspect one current Short; never replace successful encoded media."""
from pathlib import Path
import argparse, hashlib, json, subprocess, math
from PIL import Image, ImageDraw

P=Path(__file__).resolve().parents[1]
R=P.parents[1]
L=P/'production/local/final-v2'
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
    c=read(R/'shared/publishing/video-production-control.json')
    assert c.get('selectedShortVideo')==P.name
    assert c.get('shortsDirectSelection',{}).get('selectedRevision')=='normal-map-v2-grid-rgb-deadcells'
    assert c.get('shortsDirectSelection',{}).get('fullProductionAuthorized') is True
def ass_filter(): return 'ass='+str((A/'captions.ko.ass').relative_to(R)).replace('\\','/')
def pair(visual):
    guard(); c=read(P/'script/captions.json'); visual=Path(visual).resolve()
    L.mkdir(parents=True,exist_ok=True)
    assert visual.is_relative_to(R), 'Use an owned recorded render.'
    assert not (L/'clean.mp4').exists() and not (L/'captioned.mp4').exists()
    assert (A/'final-mix.m4a').exists() and (A/'captions.ko.ass').exists()
    run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(A/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(L/'clean.mp4')])
    run(['ffmpeg','-v','error','-n','-i',str(L/'clean.mp4'),'-vf',ass_filter(),'-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(L/'captioned.mp4')])
    save(L/'pair-build.json',dict(frames=c['frames'],durationSeconds=c['durationSeconds'],visual=sha(visual),audio=sha(A/'final-mix.m4a'),ass=sha(A/'captions.ko.ass'),clean=sha(L/'clean.mp4'),captioned=sha(L/'captioned.mp4'),speechSpeed=1))
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
    c=read(P/'script/captions.json'); timing=read(P/'production/visual-timing.json')
    out=L/'qa'; out.mkdir(exist_ok=True)
    points=[(q['start']+q['end'])/2 for q in c['cues']]
    for s in timing['sections']:
        points.extend([s['start'],s['start']+1/60,s['end']-1/60])
        if s.get('kind')!='game':
            points.extend(s['start']+u for u in [.4,.9,1.6,2.2,3.5] if s['start']+u<s['end'])
    points.extend([.1,c['durationSeconds']-.15])
    points=sorted(set(round(t,4) for t in points if 0<=t<c['durationSeconds']))
    rows=[]
    for i,t in enumerate(points):
        target=out/f'frame-{i:03}.jpg'
        if target.exists() and target.stat().st_size==0: target.unlink()
        if not target.exists(): run(['ffmpeg','-v','error','-n','-ss',str(max(0,t-.0001)),'-i',str(L/'captioned.mp4'),'-frames:v','1','-pix_fmt','yuvj420p','-threads','1','-q:v','2',str(target)])
        assert target.exists() and target.stat().st_size>0, 'Frame extraction did not produce an image: '+str(t)
        rows.append(dict(seconds=t,path=str(target.relative_to(R)).replace('\\','/')))
    for start in range(0,len(rows),12):
        sheet=Image.new('RGB',(1500,2100),'#202020'); draw=ImageDraw.Draw(sheet)
        for j,row in enumerate(rows[start:start+12]):
            im=Image.open(R/row['path']).convert('RGB'); im.thumbnail((375,666))
            x=j%4*375; y=j//4*700; sheet.paste(im,(x,y));draw.text((x+5,y+674),str(row['seconds'])+'s',fill='white')
        sheet.save(out/f'sheet-{start//12+1:02}.jpg',quality=92)
    save(out/'index.json',dict(rows=rows,captionMidpoints=len(c['cues']),scope='Everycue andcut before/after; implementedinput/contact/control motion samples; browserplayback separatelyrecorded.'))
    if not (L/'mobile-review.mp4').exists(): run(['ffmpeg','-v','error','-n','-i',str(L/'captioned.mp4'),'-vf','scale=374:666','-c:v','libx264','-threads','3','-preset','fast','-crf','22','-c:a','copy','-movflags','+faststart',str(L/'mobile-review.mp4')])
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['pair','integrity','qa']);parser.add_argument('--visual')
    args=parser.parse_args()
    if args.command=='pair':
        assert args.visual,'Pass the exact successful current visual render.'
        pair(args.visual)
    else: globals()[args.command]()
