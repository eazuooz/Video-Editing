"""Local review table and real encoded temporal evidence; no platform actions."""
import html,subprocess,math,sys
from prepare import *
from render import OUT,WORK,ff,video,read_srt
def duration(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def pages():
 OUT.mkdir(parents=True,exist_ok=True);table=[]
 plan=read(HERE/'plan.json');receipts=[]
 for e in plan['episodes']:
  rp=HERE/'deliveries'/(e['id']+'.json');d=read(rp) if rp.exists() else None
  state='사용자 검수 대기' if d and d.get('status')=='local-user-review-pending' else ('내부 검수 중' if d else '편집·렌더 대기')
  title=f'<a href="{e["id"]}/index.html">{html.escape(e["title"])}</a>' if d else html.escape(e['title'])
  table.append(f'<tr><td>{e["id"]}</td><td>{title}</td><td>{len(e["inserts"])}</td><td>{duration(d["duration"]) if d else "—"}</td><td>{state}</td></tr>')
  if not d:continue
  receipts.append(d);folder=OUT/e['id'];links='';points=[]
  for k,f in d['files'].items():links+=f'<a href="{pathlib.Path(f["path"]).relative_to(folder).as_posix()}">{k}</a> · '
  for s in d['inserts']:points.append(f'<tr><td><button onclick="go({s["startFrame"]/60:.3f})">{duration(s["startFrame"]/60)}</button></td><td>{html.escape(s["concept"])}</td><td>{html.escape(s["question"])}</td><td>{html.escape(read(HERE/"sources.json")[s["source"]]["game"])}</td><td>{s["frames"]/60:.1f}초</td></tr>')
  video_src=pathlib.Path(d['files']['captioned']['path']).relative_to(folder).as_posix()
  folder.joinpath('index.html').write_text(shell(e['title'],f'<p><a href="../index.html">전체 검수표</a></p><h1>{e["id"]} · {html.escape(e["title"])}</h1><p>기존 설명 유지 · 설명 후 실제 게임 관찰 {len(d["inserts"])}곳 · 1080p60 · {duration(d["duration"])}</p><video id="v" controls preload="metadata" src="{video_src}"></video><p>{links}</p><table><tr><th>예시 시작</th><th>앞서 설명한 개념</th><th>화면에서 볼 것</th><th>게임</th><th>길이</th></tr>{"".join(points)}</table><p>원본 강의의 설명·발화 순서는 보존했습니다. 표의 예시는 새로 연결한 관찰 구간입니다. 사용자 최종 시청·청취 검수는 대기 상태입니다.</p><script>function go(t){{v.currentTime=Math.max(0,t-4);v.play();}}</script>'),encoding='utf8')
 OUT.joinpath('index.html').write_text(shell('게임수학 · 개념 뒤 실제 게임 예시',f'<h1>개념 설명 → 실제 게임에서 확인하기</h1><p>M21–M33 · 기존 설명 보존 · 새 연결 해설과 실제 동작 예시 {sum(len(e["inserts"]) for e in plan["episodes"])}곳</p><p>각 편을 열면 새 예시의 시작 지점으로 바로 이동할 수 있습니다.</p><table><tr><th>번호</th><th>강의</th><th>새 관찰 구간</th><th>전체 길이</th><th>상태</th></tr>{"".join(table)}</table><p>렌더 완료 {len(receipts)}/13 · 각 행에 검수 상태를 표시했습니다.</p><p><a href="CREDITS.html">게임 녹화 출처·사용 정보</a></p>'),encoding='utf8')
 return receipts
def shell(title,body):return f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{margin:32px auto;padding:0 20px;max-width:1300px;background:#0b1016;color:#e9edf2;font:17px/1.7 system-ui}}h1{{color:#e9d087}}a{{color:#72d8cf}}video{{width:100%;max-height:75vh;background:black}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;border-bottom:1px solid #35404c;text-align:left}}button{{font:inherit;color:#080b10;background:#72d8cf;border:0;padding:5px 12px;cursor:pointer}}@media(max-width:600px){{body{{margin:15px auto;font-size:14px}}td,th{{padding:6px}}}}</style>{body}</html>'
def frames(ids):
 folder=WORK/'encoded-review';folder.mkdir(parents=True,exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 for e in read(HERE/'plan.json')['episodes']:
  if ids and e['id'] not in ids:continue
  rp=HERE/'deliveries'/(e['id']+'.json')
  if not rp.exists():continue
  d=read(rp);master=d['files']['captioned']['path'];samples=[]
  # Exact join context plus native early/middle/late action; no single still
  # counted as evidence that the recording actually moves.
  for s in d['inserts']:
   p=folder/s['key']/d['files']['captioned']['sha256'][:12];p.mkdir(parents=True,exist_ok=True);start=s['startFrame']/60;end=start+s['frames']/60
   times=[start-1,start+.5,start+min(4,s['frames']/60*.3),(start+end)/2,end-1,end+.5]
   board=Image.new('RGB',(1440,970),'#0b1016');draw=ImageDraw.Draw(board)
   for i,t in enumerate(times):
    target=p/f'{i:02}.png'
    if not target.exists():ff(['-threads','1','-ss',t,'-i',master,'-frames:v',1,'-threads','1',target],p,f'frame-{i}')
    im=Image.open(target);small=im.copy();small.thumbnail((720,405));x=i%2*720;y=i//2*322;small=im.resize((568,320));board.paste(small,(x,y));draw.text((x+572,y+12),f'{t:.1f}s',font=font,fill='white')
   board.save(folder/(s['key']+'.jpg'),quality=92);samples.append(dict(key=s['key'],times=times,sheet=str(folder/(s['key']+'.jpg')),masterSha256=d['files']['captioned']['sha256']))
   # Inspect the main observation at full resolution as well as the sheet.
   Image.open(p/'03.png').resize((375,211)).save(p/'mobile.png')
  save(folder/(e['id']+'.json'),dict(id=e['id'],status='actual-encoded-frame-review-pending',samples=samples,humanReviewed=False))
  print('Encoded review evidence',e['id'],flush=True)
if __name__=='__main__':
 if '--frames' in sys.argv:frames([a for a in sys.argv[1:] if a.startswith('M')])
 pages()
