"""Same-source camera cut proposal; narration/lesson duration stay unchanged."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M17');e.authorized();slot=next(s for s in e.T['scenes'] if s['id']=='14')
src=R/slot['cut']['sourceFile'];v=video(src);assert v['height']>=1080
cuts=[(647,4800),(735,1356)];assert sum(n for _,n in cuts)==slot['frames']
out=e.O/'camera-cue-review-v2';out.mkdir(exist_ok=True);parts=[]
for i,(start,n) in enumerate(cuts):
 p=out/f'part-{i}.mp4';e.ff(['-ss',start,'-i',src,'-vf','scale=1920:1080:flags=lanczos,setsar=1','-frames:v',n,'-an',*ENC,p],'camera-cue-cut.log');e.verify(p,n);parts.append(p)
listing=out/'parts.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
raw=out/'raw.mp4';e.ff(['-f','concat','-safe','0','-i',listing,'-c','copy',raw],'camera-cue-cut.log');e.verify(raw,slot['frames'])
dst=out/'captioned.mp4';vf=f'scale=1600:900,pad=1920:1080:160:0:black,settb=1/60,setpts=PTS+{slot["start"]}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS'
e.ff(['-i',raw,'-ss',slot['start'],'-i',e.O/'baseline-audio.m4a','-map','0:v','-map','1:a','-vf',vf,'-frames:v',slot['frames'],'-t',slot['seconds'],'-c:a','aac','-b:a','160k',*ENC,dst],'camera-cue-cut.log',e.O);e.verify(dst,slot['frames'])
f=out/'frames';f.mkdir(exist_ok=True);e.ff(['-i',dst,'-vf','fps=1,scale=640:360:flags=lanczos','-q:v','2',f/'%04d.jpg'],'camera-cue-samples.log')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);tiles=[];records=[];sheets=[]
for i,p in enumerate(sorted(f.glob('*.jpg'))):
 t=i+.5;tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((6,4),f'M17 14 +{t:.1f}s',font=font,fill='white');tiles.append(tile);records.append({'localTimeApprox':t,'path':rel(p),'sha256':sha(p)})
for i in range(0,len(tiles),9):
 sheet=Image.new('RGB',(1920,1170),'#222222')
 for j,tile in enumerate(tiles[i:i+9]):sheet.paste(tile,(j%3*640,j//3*390))
 p=out/f'sheet-{i//9+1:02d}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#151515;color:white;font:18px system-ui}video{width:min(96vw,1280px)}</style><p>카메라 동작·기존 대사 대응 검수 · 완성본 아님</p><video controls id="v" src="captioned.mp4"></video><button onclick="v.currentTime=12;v.play()">회전 12초</button><button onclick="v.currentTime=79;v.play()">줌 79초</button>',encoding='utf8')
save(e.H/'camera-cue-review-v2.json',{'status':'candidate-await-direct-source-and-speech-inspection','episode':'M17','scene':'14','sourceFile':rel(src),'sourceSha256':sha(src),'segments':[{'in':a,'frames':n} for a,n in cuts],'frames':slot['frames'],'rawClip':rel(raw),'rawClipSha256':sha(raw),'preview':rel(dst),'previewSha256':sha(dst),'samples':records,'sheets':sheets,'timelineSha256':sha(e.P/'production/timeline.json'),'internalCutsChanged':True,'originalSceneOrderAndDurationPreserved':True,'sourceSpeed':1,'freezeOrLoop':False,'fullMasterReady':False})
print('M17 candidate102.6s encoded; direct cue review pending',flush=True)
