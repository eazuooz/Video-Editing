"""Candidate same-game cuts; no adoption until narration/action and motion review."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
source=read(B/'fhd-candidate-acquisition.json')['5u3sUKuncSU'];meta=read(B/'fhd-candidate-catalog.json')['5u3sUKuncSU']
starts={'M09':{'02':[300,328],'05':[375,390],'LG02':[465,505],'LG03':[525,575],'08':[270]},'M11':{'08':[325]},'M12':{'14':[375]}}
records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for ident,slots in starts.items():
 e=Episode(ident);e.authorized()
 for sid,at in slots.items():
  s=next(s for s in e.T['scenes'] if s['id']==sid);assert len(s['cut']['segments'])==len(at)
  segments=[]
  for old,start in zip(s['cut']['segments'],at):
   assert start+old['frames']/60<=source['duration'];segments.append({'in':start,'frames':old['frames'],'sourceFile':source['path']})
  records.append({'episode':ident,'scene':sid,'originalTimelineSha256':sha(e.P/'production/timeline.json'),'segments':segments,'originalFrames':s['frames'],'narration':' '.join(x['text'] for x in s['captions']['ko']),'status':'candidate-not-approved','sourceCutPositionsPreserved':True})
save(B/'uncle-fhd-scene-candidates.json',{'status':'proposed-await-exact-motion-review','source':source,'permission':meta,'scenes':records,'excludedM10':'Wooden-column village not established in this recording. Do not substitute cliff bridges for the unchanged village narration.','sourceAudioUsed':False,'fullMasterApproval':False})
out=R/'shared/output/private-game-math-polish-20261022/fhd-candidates/uncle-triangle-cut-review';out.mkdir(exist_ok=True)
samples=[];tiles=[]
for r in records:
 if r['episode'] not in ['M11','M12']:continue
 seg=r['segments'][0];folder=out/r['episode'];folder.mkdir(exist_ok=True)
 e=Episode(r['episode']);e.ff(['-ss',seg['in'],'-i',R/source['path'],'-t',seg['frames']/60,'-vf','fps=1,scale=750:422','-threads','1',folder/'%04d.jpg'],'uncle-candidate-stills.log')
 for i,p in enumerate(sorted(folder.glob('*.jpg'))):
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(p).resize((375,211)),(0,29));ImageDraw.Draw(tile).text((4,2),f"{r['episode']} {r['scene']} src {seg['in']+i+.5:.1f}s",font=font,fill='white');tiles.append(tile)
  samples.append({'episode':r['episode'],'scene':r['scene'],'sourceSecondsApprox':seg['in']+i+.5,'path':rel(p),'sha256':sha(p)})
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//12+1:02d}.jpg',quality=94)
save(B/'uncle-triangle-cut-samples.json',{'status':'await-direct-inspection','planSha256':sha(B/'uncle-fhd-scene-candidates.json'),'samples':samples,'sheetCount':(len(tiles)+11)//12,'continuousPlaybackReviewed':False})
print(len(samples),'candidate states; no production-cut approval',flush=True)
