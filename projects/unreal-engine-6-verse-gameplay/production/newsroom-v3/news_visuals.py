"""Cut first-party native-speed camera/editor recordings on actual spoken clauses."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,subprocess,hashlib
from concurrent.futures import ThreadPoolExecutor
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
L=P/'production/local/newsroom-v3';D=L/'sources';V=L/'visuals';V.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(p)]))['streams'][0]
def font(n,b=False,jp=False):return ImageFont.truetype('C:/Windows/Fonts/'+('msgothic.ttc' if jp else 'malgunbd.ttf' if b else 'malgun.ttf'),n)
labels={'bp-preview':'블루프린트  /  에픽 공식 작업 시연','chicago':'2026.06  /  시카고 State of Unreal','graph':'UEFN  /  에픽 씬 그래프 시연','mcp':'2026.06  /  시카고 UE 5.8 시연'}
# A press excerpt uses publisher/date and brief sourced lines, separately from archival film.
# No unlicensed press photographs, reference videos, square-as-FHD exports or sourced sound enter the cuts.
records={
 'june':('EPIC GAMES     2026.06.22','6월 로드맵','기존 구조와 새 구조의 전환 기간','The road to Unreal Engine 6',['UE5와 UEFN의 개발 흐름을 통합','새 게임플레이 언어 Verse'], 'unrealengine.com  /  News'),
 'tokyo':('GAME MAKERS     2026.11.03','도쿄 현장 보도','UE6 초기부터 블루프린트 제거 계획','UE6は最初からBP廃止へ方針転換',['액터   /   블루프린트','C++ 게임플레이 프레임워크'], 'gamemakers.jp  /  Unreal Fest Tokyo 2026'),
 'deadline':('GAME MAKERS     2026.11.03','도쿄 기자회견','얼리 액세스 목표','2027년 말',['공개 일정은 에픽이 발표한 목표','게임플레이 코드의 전환을 예고'], 'gamemakers.jp  /  現地取材'),
 'productivity':('GAME MAKERS     2026.11.03','에픽의 사내 사례','일부 작업에서 관찰한 생산성','1.5배 – 4배',['프로그래밍 · 오류 추적 · 레벨 설계','에픽 발표 수치'], 'gamemakers.jp  /  Tokyo keynote'),
 'preview':('UNREAL ENGINE     2026.11.03','언리얼 엔진 5.9','프리뷰 공개 예고','11월 3일 발표 → 그다음 주',['UE5.9  /  프리뷰 예고','UE6  /  2027년 말 얼리 액세스 목표'], 'Unreal Engine  /  발표 시점 기준'),
 'godot':('GODOT ENGINE     LICENSE','고도 엔진','상업용 게임도 무료','MIT License',['엔진 사용료  0원','매출 로열티  0원'], 'godotengine.org  /  License'),
 'notice':('GODOT ENGINE     LICENSE','배포 조건','저작권·라이선스 표기를 포함','MIT License',['Godot Engine contributors','엔진에 포함된 제3자 라이선스도 확인'], 'godotengine.org  /  License'),
 'unity':('UNITY     EDITOR SOFTWARE TERMS','유니티 퍼스널','최근 12개월 재정 규모','20만 달러 이하',['자체 게임 개발사 기준','매출과 투자금 합계'], 'unity.com  /  Editor Software Terms'),
 'pro':('UNITY     PRICING IN 2026','유니티 프로','미국 연간 선결제','$2,310/yr per seat',['개발자 한 자리당 연간 2,310달러','2026년 미국 고지 가격 기준'], 'unity.com  /  Pricing updates'),
 'royalty':('EPIC GAMES     LICENSING','언리얼 일반 게임 계약','제품 누적 총매출 기준','첫 100만 달러 면제',['초과분의 5%','스팀 판매 · 표준 로열티 가정'], 'unrealengine.com  /  Licensing'),
 'cost':('ENGINE LICENSING     2026.11.05','스팀 게임 매출 예시','첫 분기 총매출 120만 달러','20만 달러 × 5% = 1만 달러',['고도   엔진 로열티 0원','유니티 프로   개발자 좌석 단위'], '스토어 수수료·세금 별도  /  일반 게임 계약 예시')
}
def text(draw,xy,s,n,col,b=False,jp=False):
 f=font(n,b,jp);draw.text(xy,s,font=f,fill=col,anchor='lt');return draw.textlength(s,font=f)
def news_page(key):
 title,subject,heading,big,notes,footer=records[key]
 im=Image.new('RGB',(1920,1080),'#121713');d=ImageDraw.Draw(im)
 d.rectangle((68,70,1852,858),fill='#f1f0e8');text(d,(125,116),title,33,'#375247',True)
 d.line((124,179,1790,179),fill='#677b70',width=3)
 text(d,(125,235),subject,48,'#31473b',True);text(d,(122,319),heading,69,'#152119',True)
 if key in ('godot','notice'):
  e=Image.open(D/'godot-editor.webp').convert('RGB');e.thumbnail((789,405),Image.Resampling.LANCZOS);im.paste(e,(1010,430))
  text(d,(125,442),big,69,'#122219',True)
  for i,line in enumerate(notes):text(d,(128,580+i*65),line,36,'#266446',True)
 elif key=='tokyo':
  text(d,(127,465),big,52,'#16251b',jp=True)
  for i,line in enumerate(notes):text(d,(128,594+i*55),line,35,'#266446',True)
 else:
  n=66 if len(big)<22 else 56
  text(d,(125,460),big,n,'#17261c',True)
  for i,line in enumerate(notes):text(d,(128,601+i*56),line,36,'#256445',True)
 d.line((124,758,1790,758),fill='#9faa9e',width=2);text(d,(129,782),footer,27,'#405449',jp='現' in footer)
 f=V/(key+'.png');im.save(f);return f
def bug(key):
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im);s=labels[key]
 ww=math.ceil(d.textlength(s,font=font(37,True)))
 d.rectangle((54,43,54+ww+47,115), fill=(9,17,14,225));d.rectangle((54,43,63,115), fill='#fae26d')
 text(d,(79,58),s,37,'#fafaf5',True)
 f=V/(key+'-label.png');im.save(f);return f
# Backgrounds are separately identified archival pictures. Keep dates of the
# reported fact and the demonstration separate even when shown side by side.
wire_pictures={'june':('chicago',134),'productivity':('mcp',235),'preview':('mcp',365),'royalty':('mcp',407),'cost':('mcp',335)}
def wire_strip(key):
 _,subject,heading,big,notes,footer=records[key]
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
 d.rectangle((56,585,1324,849),fill=(10,22,18,235))
 d.rectangle((56,585,66,849),fill='#f5d76b')
 text(d,(94,615),subject+'  /  '+footer.split('  /')[0],32,'#d6ddce',True)
 text(d,(91,676),heading,47,'#fafaf5',True)
 summary=big if key not in ('june','productivity') else ('6월 22일 에픽 로드맵' if key=='june' else '1.5배 – 4배   /   도쿄에서 발표한 사내 수치')
 text(d,(94,760),summary,43,'#f5dc83',True)
 f=V/(key+'-strip.png');im.save(f)
# Each tuple is a zero-based caption clause at which to cut, a source, and its independently inspected in-point.
SHOTS={
 '01':[(0,'bp-preview',18.9),(1,'bp-preview',25.4),(2,'bp-preview',3.7),(3,'chicago',52),(4,'chicago',396)],
 '02':[(0,'chicago',19),(1,'chicago',67),(2,'chicago',116),(3,'june',0),(5,'tokyo',0)],
 '03':[(0,'tokyo',0),(3,'mcp',446),(4,'mcp',343),(5,'deadline',0)],
 '04':[(0,'graph',650),(1,'graph',697),(2,'graph',755),(3,'graph',792),(4,'chicago',348)],
 '05':[(0,'mcp',151),(1,'mcp',159),(2,'mcp',166),(4,'mcp',189),(5,'productivity',0)],
 '06':[(0,'chicago',406),(1,'mcp',381),(2,'mcp',493),(3,'preview',0),(5,'chicago',235)],
 '07':[(0,'godot',0),(3,'notice',0),(4,'unity',0),(7,'pro',0)],
 '08':[(0,'mcp',356),(1,'royalty',0),(2,'cost',0),(4,'pro',0),(5,'chicago',92),(6,'mcp',372),(7,'graph',840)]
}
def encode(entry):
 seq,key,point,count=entry
 target=V/f'cut-{seq:02}.mp4';args=['ffmpeg','-v','error','-y','-nostdin','-filter_complex_threads','2']
 if key in labels or key in wire_pictures:
  film,point=wire_pictures.get(key,(key,point))
  s=D/(film+'.mp4');meta=probe(s)
  assert meta['width']==1920 and meta['height']==1080 and point+count/60<=float(meta['duration'])
  args+=['-ss',str(point),'-threads','2','-i',str(s),'-i',str(V/(film+'-label.png'))]
  graph='[0:v]fps=60,setsar=1[v];[v][1:v]overlay=0:0'
  if key in wire_pictures:
   args+=['-i',str(V/(key+'-strip.png'))];graph+='[identified];[identified][2:v]overlay=0:0'
  args+=['-filter_complex',graph+',format=yuv420p[out]','-map','[out]']
 else:
  args+=['-loop','1','-framerate','60','-i',str(V/(key+'.png')),'-vf','setsar=1,format=yuv420p']
 args+=['-an','-frames:v',str(count),'-c:v','h264_nvenc','-preset','p4','-rc','vbr','-cq','18','-b:v','0','-bf','0','-g','120','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(target)]
 subprocess.run(args,check=True)
 assert int(probe(target)['nb_frames'])==count,(entry,probe(target).get('nb_frames'))
 return target
def main():
 plan=read(L/'timeline.json');assert len(plan['sealedPrimaryTakes'])==8
 grant=read(R/'shared/publishing/video-production-control.json')['scopedProductionAuthorizations'][P.name]
 assert grant['renderAuthorized']
 for k in records:news_page(k)
 for k in labels:bug(k)
 for k in wire_pictures:wire_strip(k)
 edits=[];ledger=[]
 for scene in plan['scenes']:
  shots=SHOTS[scene['id']];n=scene['frames']
  cuts=[0]+[round(scene['clauses'][i]['start']*60) for i,_,_ in shots[1:]]+[n]
  for (clause,key,src),a,b in zip(shots,cuts,cuts[1:]):
   assert b>a
   entry=(len(edits)+1,key,src,b-a);edits.append(entry)
   film,tc=wire_pictures.get(key,(key,src))
   kind='official-recording-with-report' if key in wire_pictures else 'official-recording' if key in labels else 'editorial-source-excerpt'
   ledger.append(dict(scene=scene['id'],startFrame=120+scene['startFrame']+a,frames=b-a,clause=clause,source=film,inSeconds=tc,report=key if key in records else None,classification=kind))
 assert sum(e[-1] for e in edits)==plan['bodyFrames']
 with ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(encode,edits))
 txt=V/'concat.txt';txt.write_text(''.join("file '"+f.name+"'\n" for f in files),encoding='ascii')
 subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(txt),'-map','0:v','-c','copy',str(L/'body.mp4')],check=True)
 assert int(probe(L/'body.mp4')['nb_frames'])==plan['bodyFrames']
 (L/'news-cut-ledger.json').write_text(json.dumps({'timelineSha256':sha(L/'timeline.json'),'bodyFrames':plan['bodyFrames'],'sourceFilmFrames':sum(e['frames'] for e in ledger if e['source'] in labels),'cuts':ledger,'sources':{k:{'sha256':sha(D/(k+'.mp4')),'width':probe(D/(k+'.mp4'))['width'],'height':probe(D/(k+'.mp4'))['height'],'url':read(D/(k+'.info.json'))['webpage_url']} for k in labels}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
