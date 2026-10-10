from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision'
D=O/'extra-source-candidates';D.mkdir(exist_ok=True);source=O/'sources/_dw9jjRpanA.mp4'
windows=[('M',7,24,'자전거 출발과 공중 동작'),('N',56,80,'자전거 자세와 도로 방향'),('O',278,296,'눈길 출발과 자세 변화'),('P',196,208,'경사로와 결승 접근')]
sheet=Image.new('RGB',(1600,4*245),'white');draw=ImageDraw.Draw(sheet)
html='<!doctype html><meta charset="utf-8"><title>추가 게임 동작 비교</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>중복 없는 추가 후보 구간</h1>'
records=[]
for row,(key,a,b,title) in enumerate(windows):
    p=D/f'{key}.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(a),'-i',str(source),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    for j,t in enumerate([0,(b-a)/3,(b-a)*2/3,b-a-.15]):
        f=D/f'{key}-{j}.png'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=400:225',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        sheet.paste(Image.open(f),(j*400,row*245));draw.text((j*400+5,row*245+228),f'{key} source {a+t:.2f}s',fill='black')
    html+=f'<h2>{key}: {a}–{b}초 · {title}</h2><button onclick="document.getElementById(\'{key}\').play()">{key} 재생</button><video id="{key}" controls muted src="{key}.mp4"></video>'
    records.append({'id':key,'in':a,'out':b,'title':title,'playedAndSelected':False})
(D/'index.html').write_text(html,encoding='utf8');sheet.save(D/'comparison.jpg');(D/'candidates.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'newCapacitySeconds':sum(b-a for _,a,b,_ in windows),'candidateCount':4,'allNeedPlaybackSelection':True}))
