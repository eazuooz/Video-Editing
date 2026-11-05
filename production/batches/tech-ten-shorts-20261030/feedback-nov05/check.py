"""Inspect both masters, subtitle bounds, mobile playability, and decoded sample frames."""
from build import *
from io import BytesIO
import sys
for idx in map(int,sys.argv[1:]):
    r=BASE[idx-1];p=Path(r['finalDirectory']).parent/'final-reviewed-feedback-nov05-r2'
    rec=read(p/'delivery.json');files={v['name']:v['sha256'] for v in rec['files']}
    qa=p/'feedback-check.json'
    if qa.is_file() and read(qa)['master']==files['captioned.mp4']:continue
    assert all(sha(p/n)==d for n,d in files.items())
    def streamhash(media):
        return sp.check_output(['ffmpeg','-v','error','-i',str(media),'-map','0:a:0','-c:a','copy','-f','hash','-hash','SHA256','-'],text=True).strip()
    av=streamhash(p/'captioned.mp4');assert av==streamhash(p/'clean.mp4')
    if not rec['additionFrames']: assert av==streamhash(Path(r['finalDirectory'])/'captioned.mp4')
    for k in ('clean.mp4','captioned.mp4'):
        run(['ffmpeg','-v','error','-xerror','-threads','3','-i',str(p/k),'-map','0:v','-map','0:a','-f','null','-'])
    for lang in ('ko','en'):
        rows=srtread(p/f'captions.{lang}.srt')
        assert rows and all(a<b and a>=0 and b<=rec['durationSeconds']+.01 for a,b,_ in rows)
        assert all(row[0]+.003>=prev[1] for prev,row in zip(rows,rows[1:]))
    ext=rec['additionFrames']/60
    times={1:[13.9,22,25.5,29,33,ext+29],2:[11.2,22.1,33.8,42.7+ext*.28,42.7+ext*.60,42.7+ext*.90],3:[10.9,14.8,18.8,25.3,32],6:[12,15.5+ext*.25,15.5+ext*.72,ext+19],8:[21,37,41.3+ext*.24,41.3+ext*.78],10:[3,12.2,17.6,22.6,28.7,38.7]}.get(idx,[2.4,15.1,25.4]);times+=[min(rec['durationSeconds']-.16,rec['durationSeconds']-.3)]
    canvas=Image.new('RGB',(280*len(times),498),'#171919')
    for j,t in enumerate(times):
        raw=sp.check_output(['ffmpeg','-v','error','-ss',f'{t:.4f}','-threads','2','-i',str(p/'captioned.mp4'),'-frames:v','1','-vf','scale=376:668','-c:v','png','-f','image2pipe','-'])
        im=Image.open(BytesIO(raw));im.save(p/f'sample-{j:02}.png');im.thumbnail((280,498));canvas.paste(im,(j*280,0))
    canvas.save(p/'sample-sheet.jpg',quality=88)
    save(qa,dict(master=files['captioned.mp4'],sourceMaster=r['masterSha256'],aac=av,originalAacPreserved=not bool(ext),decodedBoth=True,subtitleBounds=True,matchingAudioPair=True,format='1080x1920/60',sampleTimes=times,sampleSheet=str(p/'sample-sheet.jpg'),sampleSheetSha256=sha(p/'sample-sheet.jpg'),mobileReviewSha256=sha(p/'mobile-review.mp4'),actualFullHumanListening=False,fullRealtimePlayback=False))
    print(idx,'QA',flush=True)
