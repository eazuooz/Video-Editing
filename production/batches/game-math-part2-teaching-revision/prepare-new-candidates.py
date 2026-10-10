from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';SRC=O/'sources/_dw9jjRpanA.mp4';D=O/'new-source-candidates';D.mkdir(exist_ok=True)
windows=[('E',24,56,'비행체 날개와 화면 기준'),('F',80,121,'링을 향한 비행체 자세'),('G',130,196,'자전거의 몸과 바퀴'),('H',308,350,'눈길 자전거의 기울기'),('I',350,405,'공중에서 몸·바퀴의 자세'),('J',407,440,'반대 기울기와 방향 전환'),('K',558,620,'다른 라이더와 물체 가림'),('L',623,700,'다른 자전거의 회전과 점프')]
records=[];sheet=Image.new('RGB',(1600,len(windows)*245),'white');draw=ImageDraw.Draw(sheet)
for row,(key,a,b,title) in enumerate(windows):
 p=D/f'{key}.mp4'
 if not p.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(a),'-i',str(SRC),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 for j,t in enumerate([0,(b-a)/3,(b-a)*2/3,b-a-.15]):
  f=D/f'{key}-{j}.png';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=400:225',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  sheet.paste(Image.open(f),(j*400,row*245));draw.text((j*400+5,row*245+228),f'{key} / original {a+t:.2f}s',fill='black')
 records.append({'candidate':key,'in':a,'out':b,'viewerFocus':title,'sourceId':'_dw9jjRpanA','playedAndSelected':False})
html='<!doctype html><meta charset="utf-8"><title>새 게임 자료 후보 비교</title><style>body{background:#222;color:white;font:20px sans-serif}article{margin:30px}video{width:960px;max-width:95vw}</style><h1>새 기록의 실제 동작 비교 · 쿼터니언 보충용</h1>'
for key,a,b,title in windows:html+=f'<article><h2>{key}: {a}–{b}초 · {title}</h2><button onclick="document.getElementById(\'{key}\').play()">{key} 재생</button><video id="{key}" controls muted preload="metadata" src="{key}.mp4"></video></article>'
(D/'index.html').write_text(html,encoding='utf8');sheet.save(D/'comparison.jpg');(D/'candidates.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidates':len(records),'capacitySeconds':sum(x['out']-x['in'] for x in records),'allNeedPlaybackSelection':True}))
