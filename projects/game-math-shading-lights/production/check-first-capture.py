"""Inspect the first exact production clip with its real final caption timings."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,uuid,time
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];R=P.parents[1]
spec=importlib.util.spec_from_file_location('edit',P/'production/compose-lecture.py');E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
W=P/'production/local/encoder-sample-v1';Q=P/'production/local/render-v2';q=E.read(Q/'queue.json');job=E.read(Path(q['jobs'][0]));video=Path(job['output'])/'unity.mp4'
assert E.G.verify(job,Path(job['output']))
scene=next(s for s in E.read(q['wordAlignment'])['scenes'] if s['id']=='001');offset=scene['startFrame']/60+2
lease=E.LEASE;token=str(uuid.uuid4());started=time.monotonic()
while True:
    E.G.authorized();reason=E.G.idle_reason()
    E.save(W/'caption-sample-progress.json',{'status':'waiting-for-scoped-resources','reason':reason,'pid':os.getpid()})
    if reason is None:
        try:
            with lease.open('x',encoding='utf-8') as f:json.dump({'owner':P.name+'-encoder-sample-qa','id':token,'pid':os.getpid()},f)
        except FileExistsError:pass
        else:break
    if time.monotonic()-started>6*3600:raise RuntimeError('Bounded wait ended; other work preserved')
    time.sleep(20)
try:
    with (W/'decode.log').open('w') as f:subprocess.run([str(E.FF),'-v','error','-threads','2','-i',str(video),'-f','null','-'],stdout=f,stderr=f,check=True,creationflags=E.CREATE)
    frames=[0,480,960,1260];images=[]
    for frame in frames:
        out=W/f'caption-{frame:06}.png';images.append(out)
        if out.exists():continue
        vf=f'setpts=PTS+{offset}/TB,ass=captions.ko.ass,select=eq(n\\,{frame})'
        subprocess.run([str(E.FF),'-v','error','-threads','2','-i',str(video),'-vf',vf,'-fps_mode','passthrough','-frames:v','1','-n',str(out)],cwd=Q/'composite',check=True,creationflags=E.CREATE)
    contact=Image.new('RGB',(1000,616),'#252525');draw=ImageDraw.Draw(contact)
    mobile=Image.new('RGB',(750,460),'#252525')
    for i,p in enumerate(images):
        im=Image.open(p);draw.text(((i%2)*500+6,(i//2)*308+4),f'001 / {frames[i]/60:.1f}s',fill='white');contact.paste(im.resize((500,281)),((i%2)*500,(i//2)*308+24));mobile.paste(im.resize((375,211)),((i%2)*375,(i//2)*230+18))
    contact.save(W/'caption-contact.png');mobile.save(W/'caption-mobile.png')
    E.save(W/'encoder-qa.json',{'clip':str(video),'sha256':E.sha(video),'frames':job['frames'],'size':[1920,1080],'fps':'60/1','fullDecodePassed':True,'actualCaptionTimes':True,'sampleFrames':frames,'visualReviewed':False,'humanListening':False,'notFullLecture':True})
    E.save(W/'caption-sample-progress.json',{'status':'images-ready-for-internal-review','pid':os.getpid()})
finally:
    if lease.exists() and E.read(lease).get('id')==token:lease.unlink()
print('First production scene decoded; exact-timing caption images ready for visual review.')
