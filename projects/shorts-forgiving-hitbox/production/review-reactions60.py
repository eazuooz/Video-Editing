"""Visual-only review. Exact reference music remains unresolved, so do not publish."""
from pathlib import Path
import importlib.util, json, hashlib, sys
from PIL import Image, ImageDraw

spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('finish-fairness60.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
R,P=f.R,f.P
L=P/'production/local/fairness-60s-reactions-v1'
VERSION=sys.argv[2] if len(sys.argv)>2 else 'v3'
assert VERSION in ('v1','v2','v3')
V=R/f'shared/output/motion-canvas/shorts-forgiving-hitbox-reactions60-full-{VERSION}.mp4'
OLD=P/'production/local/fairness-60s'

def build():
    assert V.exists()
    out=L/f'visual-review-{VERSION}.captioned.mp4'
    assert not out.exists(),'Preserve completed visual review'
    # Narration/effects only: never imply that unresolved reference music is matched.
    mix=OLD/'final-mix.m4a'  # Previously verified narration/effects-only AAC.
    ass=str((OLD/'captions.ko.ass').resolve()).replace('\\','/').replace(':','\\:')
    f.run([f.FF,'-v','error','-n','-i',str(V),'-i',str(mix),
           '-map','0:v:0','-map','1:a:0','-vf',f"ass=filename='{ass}'",'-t','60',
           '-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p',
           '-r','60','-fps_mode','cfr','-c:a','copy','-movflags','+faststart',str(out)])
    f.save(L/f'visual-review-{VERSION}.json',dict(role='Visual review only, not publishing master',
           captionedPath=out.relative_to(R).as_posix(),sha256=f.sha(out),
           music='No BGM in this visual review; exact reference track still unidentified',
           narrationAndEffectsPcmUnchanged=True,audioPayloadCopiedFrom=mix.relative_to(R).as_posix(),
           publishReady=False,seconds=60,format=[1080,1920,60]))

def qa():
    out=L/f'visual-review-{VERSION}.captioned.mp4';q=L/f'qa-{VERSION}';q.mkdir(exist_ok=True)
    assert not (q/'technical.json').exists(),'Reuse successful output inspection'
    meta=json.loads(f.run([f.FP,'-v','error','-show_streams','-of','json',str(out)]).stdout)
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',3600)
    assert float(v['duration'])==60
    def packets(path):
        return json.loads(f.run([f.FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
                    '-show_entries','packet=data_hash','-of','json',str(path)]).stdout)['packets']
    assert packets(out)==packets(OLD/'final-mix.m4a')
    f.run([f.FF,'-v','error','-n','-i',str(out),'-map','0:v:0','-f','framehash',str(q/'visual-review.framehash'),
           '-map','0:a:0','-c:a','pcm_f32le',str(q/'visual-review-decoded.wav')])
    rows=[s for s in (q/'visual-review.framehash').read_text().splitlines() if not s.startswith('#')]
    assert len(rows)==3600 and [int(s.split(',')[2]) for s in rows]==list(range(3600))
    cues=f.read(P/'script/fairness-60s/captions.json')['cues']
    times={round((c['start']+c['end'])/2,3) for c in cues}
    times.update(round(s['start']+.08,3) for s in f.read(OLD/'visual-timing.json')['sections'])
    for a,b in [(1.05,2.55),(4.97,6.70),(40.28,41.92),(58.37,59.65)]:
        times.update([round(a-.02,3),round(a+.06,3),round(a+.24,3),round((a+b)/2,3),round(b-.06,3),round(b+.02,3)])
    times.update([17.08,17.4,18.1,20.60,29.28,29.73,30.18,31.7,35.02,36.02,36.15,36.85,36.90,42.20,59.80])
    samples=[]
    for i,t in enumerate(sorted(times)):
        target=q/f'sample-{i:03}.png'
        f.run([f.FF,'-v','error','-n','-ss',str(t),'-i',str(out),'-frames:v','1',str(target)])
        Image.open(target).convert('RGB').resize((375,667),Image.Resampling.LANCZOS).save(q/f'mobile-{i:03}.jpg',quality=94)
        samples.append(dict(index=i,seconds=t,native=target.name,mobile=f'mobile-{i:03}.jpg'))
    for first in range(0,len(samples),12):
        sheet=Image.new('RGB',(1125,2776),'#242424');draw=ImageDraw.Draw(sheet)
        for j,s in enumerate(samples[first:first+12]):
            x=(j%3)*375;y=(j//3)*694
            sheet.paste(Image.open(q/s['mobile']),(x,y+27));draw.text((x+8,y+5),f"{s['index']:03} | {s['seconds']:.3f}s",fill='white')
        sheet.save(q/f'contact-{first//12+1:02}.jpg',quality=94)
    f.save(q/'samples.json',samples)
    f.save(q/'technical.json',dict(role='Visual-only revision review; reference music unresolved',
           sha256=f.sha(out),fullDecode=True,frames=3600,uniformPts=True,seconds=60,
           format=[1080,1920,60],captionTimingUnchanged=True,aacPayloadUnchanged=True,sampleCount=len(samples),
           humanListening='not asserted',publishReady=False))
    print(json.dumps(dict(samples=len(samples),qa=str(q))))

if __name__=='__main__':globals()[sys.argv[1]]()
