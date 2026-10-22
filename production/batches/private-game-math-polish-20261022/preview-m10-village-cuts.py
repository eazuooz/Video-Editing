"""Review a same-game FHD village proposal on the preserved narration clock."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M10');e.authorized();slot=next(s for s in e.T['scenes'] if s['id']=='19')
source=read(B/'fhd-candidate-acquisition.json')['oU__wsOyeiY'];src=R/source['path']
assert sha(src)==source['sha256'] and video(src)['height']>=1080
cuts=[(243,480),(235,420),(259,1080),(392,900),(281,901)]
assert sum(n for _,n in cuts)==slot['frames']
for i,(a,n) in enumerate(cuts):
 for z,k in cuts[i+1:]:assert a+n/60<=z or z+k/60<=a
out=e.O/'village-cue-review';out.mkdir(exist_ok=True);parts=[]
for i,(start,n) in enumerate(cuts):
 e.authorized();p=out/f'part-{i}.mp4'
 e.ff(['-ss',start,'-i',src,'-vf','scale=1920:1080:flags=lanczos,setsar=1','-frames:v',n,'-an',*ENC,p],'village-cue-cut.log')
 e.verify(p,n);parts.append(p)
listing=out/'parts.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
raw=out/'raw.mp4';e.ff(['-f','concat','-safe','0','-i',listing,'-c','copy',raw],'village-cue-cut.log');e.verify(raw,slot['frames'])
dst=out/'captioned.mp4';vf=f'scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1,settb=1/60,setpts=PTS+{slot["start"]}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS'
e.ff(['-i',raw,'-ss',slot['start'],'-i',e.O/'baseline-audio.m4a','-map','0:v','-map','1:a','-vf',vf,'-frames:v',slot['frames'],'-t',slot['seconds'],'-c:a','aac','-b:a','160k',*ENC,dst],'village-cue-cut.log',e.O);e.verify(dst,slot['frames'])
f=out/'frames';f.mkdir(exist_ok=True);e.ff(['-i',dst,'-vf','fps=1,scale=640:360:flags=lanczos','-q:v','2',f/'%04d.jpg'],'village-cue-samples.log')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);tiles=[];records=[];sheets=[]
for i,p in enumerate(sorted(f.glob('*.jpg'))):
 t=i+.5;tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((6,4),f'M10 19 +{t:.1f}s',font=font,fill='white');tiles.append(tile);records.append({'localTimeApprox':t,'path':rel(p),'sha256':sha(p)})
for i in range(0,len(tiles),9):
 sheet=Image.new('RGB',(1920,1170),'#222222')
 for j,tile in enumerate(tiles[i:i+9]):sheet.paste(tile,(j%3*640,j//3*390))
 p=out/f'sheet-{i//9+1:02d}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#151515;color:white;font:18px system-ui}video{width:min(96vw,1280px)}</style><p>마을 시점 변화·기존 대사 대응 검수 · 완성본 아님</p><video controls id="v" src="captioned.mp4"></video><button onclick="v.currentTime=0;v.play()">난간·기둥</button><button onclick="v.currentTime=8;v.play()">다른 각도</button><button onclick="v.currentTime=44;v.play()">기준축 구분</button>',encoding='utf8')
save(e.H/'village-cue-review.json',{'status':'candidate-await-direct-source-and-speech-inspection','episode':'M10','scene':'19','sourceFile':rel(src),'sourceSha256':sha(src),'segments':[{'in':a,'frames':n} for a,n in cuts],'frames':slot['frames'],'rawClip':rel(raw),'rawClipSha256':sha(raw),'preview':rel(dst),'previewSha256':sha(dst),'samples':records,'sheets':sheets,'timelineSha256':sha(e.P/'production/timeline.json'),'internalCutsChanged':True,'originalSceneOrderAndDurationPreserved':True,'sourceSpeed':1,'freezeOrLoop':False,'fullMasterReady':False})
print('M10 village candidate63.0167s encoded; direct review pending',flush=True)
