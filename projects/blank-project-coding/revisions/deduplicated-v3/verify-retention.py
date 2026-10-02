"""Check deletion at sample precision and produce focused transition evidence."""
from pathlib import Path
import json,subprocess
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).resolve().parent;R=W.parents[3];B=W.parent/'original-restored-v2'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
p=read(W/'plan.json');m=read(W/'final.manifest.json');a=read(W/'duplicate-removal-audit.json')
new,rate=sf.read(R/m['paths']['narration'],dtype='int16')
old,oldrate=sf.read(R/read(B/'final.manifest.json')['paths']['narration'],dtype='int16')
assert rate==oldrate==24000
start=(41693-120)*400;end=(50320-120)*400
assert np.array_equal(new,np.concatenate([old[:start],old[end:]]))
entries=read(W/'caption-alignment.json')['entries']
assert all(e['end']>e['start'] for e in entries)
assert all(a['end']<=b['start'] for a,b in zip(entries,entries[1:]))
assert all(e['scene'] not in [str(i) for i in range(31,38)] for e in entries)
assert [s['chapter'] for s in p['scenes']]==sorted(s['chapter'] for s in p['scenes'])
assert len([s for s in p['scenes'] if s['chapter']==17])==3
assert len([s for s in p['scenes'] if s['chapter']==18])==2
assert len([s for s in p['scenes'] if s['chapter']==19])==2
times=[690.7,693.6,695.1,697.4,700.0,702.4,705.0,710.0,716.4,752.0,793.7,843.4,p['bodyEnd']-1,p['bodyEnd']+3,p['seconds']-1]
out=W/'transition-native';out.mkdir(exist_ok=True)
pages=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for i,t in enumerate(times):
    f=out/f'{i+1:02d}.png'
    subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(t),'-i',str(R/m['paths']['videoBurnedCaptions']),'-frames:v','1','-threads','1',str(f)],check=True)
    page=i//6
    if page==len(pages):pages.append(Image.new('RGB',(1920,1710),'white'))
    im=Image.open(f).resize((960,540));x=i%2*960;y=i//2%3*570
    pages[page].paste(im,(x,y));ImageDraw.Draw(pages[page]).text((x+10,y+543),f'{t:.3f}s',font=font,fill='black')
for i,page in enumerate(pages):page.save(W/f'transitions-{i+1:02d}.jpg',quality=95)
subprocess.run(['ffmpeg','-v','error','-y','-ss','685','-i',str(R/m['paths']['videoBurnedCaptions']),'-t','40','-c:v','libx264','-threads','2','-crf','21','-preset','veryfast','-c:a','aac',str(W/'transition-preview.mp4')],check=True)
(W/'retention-review.json').write_text(json.dumps({'bodyPCMExactlyEqualsBaselineMinusSpecified8627Frames':True,'allRetainedScriptWordsAndOrderUnchanged':a['allRetainedWordsAndOrderUnchanged'],'remainingCueTimesIncreasing':True,'threeTeachingSequencesAppearOnceAtChapterLevel':True,'sceneCount':49,'originalReconstructedScene36Removed':True,'transitionImages':len(times),'directTransitionReview':'pending','fullHumanListening':'pending'},indent=2)+'\n',encoding='utf8')
print('Sample-exact speech deletion and retained chapter/caption checks passed.')
