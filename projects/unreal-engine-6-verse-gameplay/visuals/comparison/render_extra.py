"""Render only the five newly narrated scenes. Originals 01–12 are read-only."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
V=HERE.parent
sys.path.insert(0,str(V))
import render as engine
from stage import BG
from pictures import comparison,MOTION
from PySide6.QtGui import QGuiApplication,QFontDatabase
from PIL import Image,ImageDraw
P=V.parent;ROOT=P.parents[1];L=P/'production/local/engine-comparison-v2';OUT=L/'visuals';OUT.mkdir(parents=True,exist_ok=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['sample','partial','full','watch'])
    args=parser.parse_args()
    app=QGuiApplication(['comparison','-platform','offscreen'])
    for name in ['malgun.ttf','malgunbd.ttf','consola.ttf','consolab.ttf']:
        assert QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+name)>=0
    engine.WORK=OUT;engine.draw=comparison;engine.MOTION=MOTION
    if args.stage=='sample':
        sheet=Image.new('RGB',(1200,5*366),'#121b19')
        for j,beats in enumerate([(2,4),(1,5),(0,4),(3,6),(1,4)]):
            for k,beat in enumerate(beats):
                im=engine.picture(13+j,beat,.71,5)
                png=OUT/f'preview-{13+j}-{beat}.png';im.save(str(png))
                with Image.open(png) as img:sheet.paste(img.resize((600,338),Image.Resampling.LANCZOS),(k*600,j*366))
            ImageDraw.Draw(sheet).text((7,j*366+340),f'scene {j+13}',fill='white')
        sheet.save(OUT/'comparison-preview.jpg',quality=92)
        return
    ctrl=engine.jsonfile(ROOT/'shared/publishing/video-production-control.json')
    assert any(a.get('revision')=='engine-comparison-v2' and a.get('renderAuthorized') for a in ctrl['scopedProductionAuthorizations'].values())
    sources=[HERE/'pictures.py',Path(__file__),HERE/'godot/Door.gd',HERE/'godot/Door.tscn',HERE/'unity/DoorSwitch.cs']
    version=engine.sha_json([engine.digest(f) for f in sources])
    while True:
        finally_ready=(L/'timeline.json').exists()
        tp=L/('timeline.json' if finally_ready else 'partial-timeline.json')
        if not tp.exists():
            if args.stage=='watch':time.sleep(4);continue
            raise FileNotFoundError(tp)
        plan=engine.jsonfile(tp)
        scenes=[s for s in plan['scenes'] if 13<=int(s['id'])<=17]
        for s in scenes:
            engine.cut(dict(s,comparisonSourceSignature=version))
        if finally_ready:break
        if args.stage=='partial':return
        if args.stage=='full':raise ValueError('Final timeline is required')
        time.sleep(4)
    assert [s['id'] for s in scenes]==['13','14','15','16','17']
    frames=sum(s['frames'] for s in scenes);assert scenes[0]['startFrame']==17724
    assert scenes[-1]['startFrame']+scenes[-1]['frames']==17724+frames
    ff=OUT/'list.ffconcat';ff.write_text('ffconcat version 1.0\n'+'\n'.join(engine.quote(OUT/f"scene-{s['id']}.mp4")+'\nduration '+f"{s['frames']/60:.12f}" for s in scenes)+'\n',encoding='utf-8')
    output=L/'body-extra.mp4'
    engine.ffmpeg(['-f','concat','-safe','0','-i',ff,'-map','0:v','-c:v','copy','-an','-video_track_timescale','60000','-movflags','+faststart',output])
    info=engine.probe(output);assert int(info['nb_frames'])==frames
    samples={}
    for s in scenes:
        offset=s['startFrame']-17724
        for j,q in enumerate(s['sentences']):samples[offset+round((q['start']+q['end'])*30)]=f"{s['id']}.{j+1}"
        samples[offset]=s['id']+' first';samples[offset+s['frames']-1]=s['id']+' last'
    seq=sorted(samples)
    expr='select='+'+'.join(f'eq(n\\,{f})' for f in seq)+',scale=375:211'
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(output),'-vf',expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
    import numpy as np
    rgb=np.frombuffer(data,np.uint8).reshape(-1,211,375,3);assert len(rgb)==len(seq) and rgb[:,177:].max()<=9
    for first in range(0,len(seq),12):
        contact=Image.new('RGB',(1125,952),'#182022');d=ImageDraw.Draw(contact)
        for j,n in enumerate(seq[first:first+12]):
            x=j%3*375;y=j//3*238;contact.paste(Image.fromarray(rgb[first+j]),(x,y));d.text((x+5,y+212),samples[n],fill='white')
        contact.save(OUT/f'final-{first//12+1}.jpg',quality=92)
    engine.save(OUT/'comparison-render.json',{'frames':frames,'startFrameInBody':17724,'probe':info,'sha256':engine.digest(output),'timeline':engine.digest(tp),'sourceSignature':version,'mobileEncodedFramesInspected':len(seq),'captionAreaMaxRGB':int(rgb[:,177:].max()),'upstreamOriginal':'v1/body.mp4 kept intact','sourceRoles':{'realGameVideo':0,'editorialExplanation':frames},'humanReview':False})
    print('EXTRA READY',frames,info['duration'],flush=True)
if __name__=='__main__':main()
