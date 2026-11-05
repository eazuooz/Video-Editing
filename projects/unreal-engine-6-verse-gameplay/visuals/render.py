"""Render the editable teaching pictures in Qt's CPU raster engine at 60 fps.

The image list holds a picture through the time its narration needs it. All
moving points are sampled at the actual 60 Hz timeline and never optical-flowed.
"""
import argparse, bisect, hashlib, json, math, os, subprocess, sys, tempfile
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QFontDatabase, QImage, QPainter
from PIL import Image, ImageDraw
from scenes import draw
from stage import WIDTH,HEIGHT,ASSETS,TUTORIAL
P=Path(__file__).resolve().parents[1]
L=P/'production/local/v1'
WORK=L/'visuals'
WORK.mkdir(parents=True,exist_ok=True)
FPS=60

# Fractions of the spoken sentence over which geometry changes. Remaining
# frames keep the settled state for the explanation. The renderer still samples
# per-frame when more than one independently moving element is present.
MOTION={1:{0:1/2.8,1:1/2.8,2:1/1.8,3:1/1.5},2:{1:1},3:{3:1/3,4:1/3},4:{1:.5,2:.5,3:.5},5:{3:1/3,4:1/2,5:1},6:{1:1/2.4},7:{2:1/2.6},8:{1:1/2.6,3:1/3},9:{0:1},10:{1:.5,5:.5},11:{3:.4,4:.4},12:{0:1/2.3,3:1/2.4}}

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8<<20),b''):h.update(chunk)
    return h.hexdigest()
def jsonfile(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha_json(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def times(scene,t):
    s=scene['sentences'];i=max(0,bisect.bisect_right([r['start'] for r in s],t)-1)
    return i,min(1,max(0,(t-s[i]['start'])/max(.001,s[i]['end']-s[i]['start'])))
def picture(index,i,p,t):
    image=QImage(WIDTH,HEIGHT,QImage.Format.Format_RGB32)
    painter=QPainter(image)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        draw(painter,index-1,i,p,t)
    finally:painter.end()
    return image
def quote(p):return "file '"+p.resolve().as_posix().replace("'","'\\''")+"'"
def ffmpeg(args):
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
def probe(p):
    row=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
     'stream=width,height,nb_frames,avg_frame_rate,start_time,duration','-of','json',str(p)]))['streams'][0]
    assert (row['width'],row['height'],row['avg_frame_rate'])==(1920,1080,'60/1'),row
    return row
def cut(scene):
    index=int(scene['id']);out=WORK/f'scene-{index:02}.mp4';receipt=out.with_suffix('.json')
    sources=[Path(__file__),Path(__file__).with_name('stage.py'),Path(__file__).with_name('scenes.py')]
    sig=sha_json([scene,[digest(p) for p in sources]])
    if receipt.exists() and out.is_file() and jsonfile(receipt)['inputs']==sig and int(probe(out)['nb_frames'])==scene['frames']:
        return jsonfile(receipt)
    with tempfile.TemporaryDirectory(dir=WORK,prefix=f's{index:02}-') as tmp:
        temp=Path(tmp);shots=[];last=None
        for frame in range(scene['frames']):
            t=frame/FPS;i,progress=times(scene,t)
            limit=MOTION.get(index,{}).get(i,0)
            # Every visible degree of movement keeps its original 60 Hz sample.
            p=min(limit,progress) if limit else 0
            key=(i,min(p,limit))
            if key!=last:
                im=picture(index,i,p,t)
                path=temp/f'{frame:06}.png'
                if not im.save(str(path),'PNG',93):raise OSError(path)
                shots.append([path,0]);last=key
            shots[-1][1]+=1
        concat=temp/'frames.ffconcat'
        lines=['ffconcat version 1.0']
        for path,count in shots:lines.extend([quote(path),'option framerate 60',f'duration {count/FPS:.12f}'])
        lines.extend([quote(shots[-1][0]),'option framerate 60'])
        concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        ffmpeg(['-f','concat','-safe','0','-i',concat,'-vf','fps=60,setsar=1,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-frames:v',scene['frames'],'-an',
                '-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000',out])
        info=probe(out);assert int(info['nb_frames'])==scene['frames'],(scene['id'],info['nb_frames'],scene['frames'])
        report={'id':scene['id'],'inputs':sig,'frames':scene['frames'],'distinctRenderedStates':len(shots),'sha256':digest(out)}
        save(receipt,report);print(f"Rendered scene {index:02}: {scene['frames']} frames, {len(shots)} timed pictures",flush=True)
        return report

def preview():
    thumb=Image.new('RGB',(1500,4*302),'#1b2120');label=ImageDraw.Draw(thumb)
    for n in range(1,13):
        beat=[2,3,4,4,5,1,3,3,2,5,3,3][n-1]
        im=picture(n,beat,.71,5)
        path=WORK/f'preview-{n:02}.png';im.save(str(path))
        img=Image.open(path);img.thumbnail((500,282));x=(n-1)%3*500;y=(n-1)//3*302;thumb.paste(img,(x,y));label.text((x+9,y+282),f'{n:02}', fill='white')
    thumb.save(WORK/'preview-contact.jpg',quality=92)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['sample','partial','full'])
    args=parser.parse_args()
    app=QGuiApplication(['ue6-visual-render','-platform','offscreen'])
    for filename in ('malgun.ttf','malgunbd.ttf','consola.ttf','consolab.ttf'):
        if QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+filename)<0:
            raise RuntimeError('Required font is unavailable: '+filename)
    assert {'Malgun Gothic','Consolas'} <= set(QFontDatabase.families())
    if args.stage=='sample':return preview()
    m=jsonfile(P/'project.json')
    root=P.parents[1];control=jsonfile(root/'shared/publishing/video-production-control.json')
    assert control['scopedProductionAuthorizations'][P.name]['renderAuthorized'] and m['revision']=='v1'
    timeline=L/('partial-timeline.json' if args.stage=='partial' else 'timeline.json')
    plan=jsonfile(timeline);rows=plan['scenes']
    assert plan['fps']==60
    receipts=[cut(scene) for scene in rows]
    if args.stage=='partial':return
    assert len(rows)==12 and sum(r['frames'] for r in receipts)==plan['bodyFrames']
    listing=WORK/'body.ffconcat';listing.write_text('ffconcat version 1.0\n'+'\n'.join(quote(WORK/f"scene-{int(r['id']):02}.mp4") for r in rows)+'\n',encoding='utf-8')
    # Matroska/MP4 container durations are often rounded to milliseconds. Supply
    # the measured frame durations for each cut so the concatenation stays CFR.
    listing.write_text('ffconcat version 1.0\n'+'\n'.join(quote(WORK/f"scene-{int(r['id']):02}.mp4")+'\nduration '+f"{r['frames']/60:.12f}" for r in rows)+'\n',encoding='utf-8')
    target=L/'body.mp4';ffmpeg(['-f','concat','-safe','0','-i',listing,'-map','0:v','-c:v','copy','-an','-video_track_timescale','60000','-movflags','+faststart',target])
    info=probe(target);assert int(info['nb_frames'])==plan['bodyFrames'],info
    # Source-dominant vs. diagram-dominant here are editing roles, not credited
    # commercial gameplay. All of the body is editorial explanation.
    docframes=sum(r['frames'] for r in rows if r['id'] in ('04','07'))
    s3=rows[2]
    docframes+=min(s3['frames'],round(s3['sentences'][3]['start']*FPS))
    save(WORK/'body-receipt.json',{'bodySha256':digest(target),'bodyFrames':plan['bodyFrames'],'timelineSha256':digest(timeline),
      'fps':60,'independentGameVideoFrames':0,'editorialBodyFrames':plan['bodyFrames'],'primaryDocumentOrCodeDominantFrames':docframes,
      'diagramDominantFrames':plan['bodyFrames']-docframes,'semanticSourceKinds':'Epic official stills, installed example images, installed header statements, editorial diagrams',
      'editor':'CPU Qt vector stage with native 60 Hz animations, scripted oblique door/hinge/parent transforms',
      'humanViewing':'pending','sceneReceipts':receipts,'probe':info})
    print('BODY READY',target,info,flush=True)
if __name__=='__main__':main()
