"""Candidate cut review at native speed with unchanged baseline narration.

Do not write production clips or mark source cuts approved here.
"""
import datetime,sys
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
source=read(B/'uncle-fhd-scene-candidates.json')['source']
src=R/source['path'];assert sha(src)==source['sha256']
cases={'M09':('02',[(402,1260),(374,480),(431,300),(342,660)]),
       'M11':('08',[(342,720),(366,840),(402,1680)]),
       'M12':('14',[(406,960),(342,840),(366,840),(422,809)])}
if sys.argv[1:]:cases={k:v for k,v in cases.items() if k in sys.argv[1:]}
records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
for ident,(sid,cuts) in cases.items():
 e=Episode(ident);e.authorized();slot=next(s for s in e.T['scenes'] if s['id']==sid)
 assert sum(n for _,n in cuts)==slot['frames']
 for j,(a,n) in enumerate(cuts):
  for z,m in cuts[j+1:]:assert a+n/60<=z or z+m/60<=a,'No repeated source frames within one scene'
 revision='v3' if ident=='M09' else 'v2'
 manifest=e.H/f'uncle-cut-review-{revision}.json'
 out=e.O/f'uncle-cut-review-{revision}';out.mkdir(exist_ok=True);parts=[];offset=0;segments=[]
 previous=read(manifest) if manifest.exists() else None
 for j,(start,frames) in enumerate(cuts):
  p=out/f'part-{j}.mp4'
  cached=previous and previous['source']['sha256']==source['sha256'] and j<len(previous['segments']) and previous['segments'][j]['in']==start and previous['segments'][j]['frames']==frames and p.exists()
  if not cached:e.ff(['-ss',start,'-i',src,'-frames:v',frames,'-an',*ENC,p],'uncle-cut-review.log')
  e.verify(p,frames);parts.append(p);segments.append({'in':start,'frames':frames,'sourceFile':rel(src),'localStart':offset});offset+=frames/60
 listing=out/'parts.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
 raw=out/'raw.mp4';e.ff(['-f','concat','-safe','0','-i',listing,'-c','copy',raw],'uncle-cut-review.log');e.verify(raw,slot['frames'])
 dst=out/'captioned.mp4'
 vf=f'scale=1600:900,pad=1920:1080:160:0:black,settb=1/60,setpts=PTS+{slot["start"]}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS'
 e.ff(['-i',raw,'-ss',slot['start'],'-i',e.O/'baseline-audio.m4a','-map','0:v','-map','1:a','-vf',vf,'-frames:v',slot['frames'],'-t',slot['seconds'],'-c:a','aac','-b:a','160k',*ENC,dst],'uncle-cut-review.log',e.O);e.verify(dst,slot['frames'])
 framesdir=out/'frames';framesdir.mkdir(exist_ok=True)
 e.ff(['-i',dst,'-vf','fps=1,scale=640:360:flags=lanczos','-q:v',2,framesdir/'%04d.jpg'],'uncle-cut-review.log')
 tiles=[];samples=[]
 for i,p in enumerate(sorted(framesdir.glob('*.jpg'))):
  t=i+.5;tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((6,4),f'{ident} {sid} +{t:.1f}s',font=font,fill='white');tiles.append(tile);samples.append({'localTimeApprox':t,'path':rel(p),'sha256':sha(p)})
 sheets=[]
 for i in range(0,len(tiles),9):
  sheet=Image.new('RGB',(1920,1170),'#222222')
  for j,tile in enumerate(tiles[i:i+9]):sheet.paste(tile,(j%3*640,j//3*390))
  p=out/f'sheet-{i//9+1:02d}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
 (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#151515;color:white;font:18px system-ui}video{width:min(96vw,1280px)}</style><p>대체 장면과 기존 대사 대응 검수 · 완성본 아님</p><video controls src="captioned.mp4"></video>',encoding='utf8')
 record={'episode':ident,'scene':sid,'status':'candidate-await-direct-source-and-speech-inspection','originalTimelineSha256':sha(e.P/'production/timeline.json'),'source':source,'segments':segments,'frames':slot['frames'],'rawClip':rel(raw),'rawClipSha256':sha(raw),'preview':rel(dst),'previewSha256':sha(dst),'samples':samples,'sheets':sheets,'internalCutsChanged':True,'originalSceneOrderAndDurationPreserved':True,'reason':'Omit observed fall/reset and unrelated tutorial banner ranges; retain native-speed grapple/triangular-glyph approach and landing at the existing speech clock. Internal source excerpts may change within the same immutable scene slot.','fullMasterReady':False}
 save(manifest,record);records.append(rel(manifest))
 print(ident,'candidate preview encoded, awaiting direct review',flush=True)
save(B/'uncle-cut-review-v2-job.json',{'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'finished-await-direct-review','records':records,'fullMasterReady':False})
