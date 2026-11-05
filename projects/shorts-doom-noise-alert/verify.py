"""Verify the final streams and the concrete one-flag experiment."""
from io import BytesIO
import json
import subprocess
from PIL import Image
from compose import FINAL,PROJECT,RAW,WORK,MEDIA,ROOT,MUSIC,ed

d=ed.read(FINAL/'delivery.json')
for r in d['files']:
    assert ed.sha(FINAL/r['name'])==r['sha256']
hashes=[]
for name in ('clean.mp4','captioned.mp4'):
    movie=FINAL/name;video,audio=ed.probe(movie)
    assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1080,1920,'60/1',d['frames'])
    assert abs(float(audio['duration'])-d['durationSeconds'])<.09
    ed.run(['ffmpeg','-v','error','-xerror','-threads','3','-i',str(movie),'-f','null','-'])
    hashes.append(subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-map','0:a','-c:a','copy','-f','hash','-hash','SHA256','-'],text=True).strip())
assert len(set(hashes))==1
for name in ('captions.ko.srt','captions.en.srt'):
    cs=ed.srtread(FINAL/name)
    assert cs and all(0<=a<b<=d['durationSeconds'] for a,b,_ in cs)
    assert all(a[1]<b[0]+.002 for a,b in zip(cs,cs[1:]))
rows=ed.read(WORK/'timing.json')
times=[.86,3.22,4.43,rows[1]['start']+4,rows[2]['start']+3.15,rows[3]['start']+1.3,rows[3]['start']+4.7,rows[4]['start']+6,rows[5]['start']+3,rows[6]['start']+1.45]
canvas=Image.new('RGB',(376*5,668*2))
for i,t in enumerate(times):
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-threads','2','-i',str(FINAL/'captioned.mp4'),'-frames:v','1','-vf','scale=376:668','-c:v','png','-f','image2pipe','-'])
    im=Image.open(BytesIO(raw));im.save(FINAL/f'sample-{i:02}.png');canvas.paste(im,(i%5*376,i//5*668))
canvas.save(FINAL/'mobile-sheet.jpg',quality=94)
evidence={}
for mode in ('one','two'):
    quiet=ed.read(RAW/f'test-{mode}-map01-quiet-fhd'/'states.json')
    shot=ed.read(RAW/f'test-{mode}-map01-shot-fhd'/'states.json')
    actor=next(k for k,v in quiet[0]['actors'].items() if v[0]=='DoomImp')
    still=quiet[0]['actors'][actor]
    assert all(f['actors'][actor]==still for f in quiet)
    movement=[f['tick'] for f in shot if f['actors'][actor]!=still]
    assert bool(movement)==(mode=='one')
    evidence[mode]=dict(player=shot[0]['player'],actorStart=still,firstObservedMoveTick=movement[0] if movement else None,shotStateSha=ed.sha(RAW/f'test-{mode}-map01-shot-fhd'/'states.json'))
assert evidence['one']['player']==evidence['two']['player'] and evidence['one']['actorStart']==evidence['two']['actorStart']
src=ed.read(PROJECT/'source-footage.json');assert all(s['width']==1920 and s['height']==1080 for s in src.values())
notice=FINAL/'Freedoom-COPYING.txt'
assert notice.exists()
ed.save(FINAL/'technical-review.json',dict(masterSha256=ed.sha(FINAL/'captioned.mp4'),fourOutputsVerified=True,decodedBoth=True,identicalAudioStream=True,audioStreamHash=hashes[0],subtitleTimesChecked=True,sampleTimes=times,gameplay=evidence,sourceFHD=True,
         sourceWadSha=ed.sha(MEDIA/'tools/vizdoom/freedoom2.wad'),musicSha=ed.sha(MUSIC),freedoomNoticeSHA256=ed.sha(notice),
         wholeHumanListening=False,fullRealtimeViewing=False,platformActions=False))
print('Verified',d['frames'],'frames; one/two boundary movement:',evidence)
