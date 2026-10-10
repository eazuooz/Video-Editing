"""Current captioned pixels for every cue plus native whole-episode playback."""
from pathlib import Path
import json,hashlib,subprocess,sys,shutil,math,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];assert slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']
P=ROOT/'projects'/slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));src=ROOT/m['paths']['videoBurnedCaptions'];sha=hashlib.sha256(src.read_bytes()).hexdigest()
D=ROOT/f'shared/output/{slug}/caption-review';D.mkdir(parents=True,exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
def extract(item):
 i,c=item;at=(c['start']+c['end'])/2;raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(at),'-i',str(src),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
 assert len(raw)==1920*1080*3
 im=Image.frombytes('RGB',(1920,1080),raw);im.save(D/f'cue-{i+1:03}.jpg',quality=94)
 return i,c,at,im.crop((0,860,1920,1080)).resize((960,110))
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for i,c,at,im in pool.map(extract,enumerate(t['koCaptions'])):rows.append((i,c,at,im))
for start in range(0,len(rows),24):
 sheet=Image.new('RGB',(1920,1680),'#eef0ef');draw=ImageDraw.Draw(sheet)
 for j,(i,c,at,im) in enumerate(rows[start:start+24]):
  x=j%2*960;y=j//2*140;sheet.paste(im,(x,y+26));draw.text((x+6,y),f'Cue{i+1:03} scene{c["scene"]} at{at:.3f}s',font=font,fill='black')
 sheet.save(D/f'strips-{start//24+1:02}.jpg',quality=95)
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':sha,'cueCount':len(rows),'allCuePixelsExtracted':True,'directReviewPassed':False,'humanListeningComplete':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
O=ROOT/'shared/output/game-math-part2-teaching-revision';target=O/(slug+'.captioned.mp4')
if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=sha:shutil.copy2(src,target)
(O/(slug+'-review.html')).write_text('''<!doctype html><meta charset="utf-8"><title>평면·삼각형 좌표 최종 강의 연속 검수</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:10px}</style><h1>최종 한국어 자막 강의 · 원래 속도 전체 재생</h1><p>'''+slug+' SHA256 '+sha+'''</p><button id="play">전체 강의 재생</button><video controls id="v" src="'''+target.name+'?sha='+sha+'''"></video><p id="now"></p><pre id="proof"></pre><script>const v=document.querySelector('video');document.querySelector('#play').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.play()};v.ontimeupdate=()=>document.querySelector('#now').textContent=v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3);v.onended=()=>document.querySelector('#proof').textContent=JSON.stringify({sha256:"'''+sha+'''",seconds:v.duration,rate:v.playbackRate,ended:v.ended},null,2);</script>''',encoding='utf8')
print(json.dumps({'allCuePixels':len(rows),'currentVideoSha256':sha,'wholePlaybackPage':slug+'-review.html','pixelApproval':False}))
