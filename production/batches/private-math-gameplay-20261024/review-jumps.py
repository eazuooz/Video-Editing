"""Add direct scene review controls without modifying any media."""
from pathlib import Path
import json,html
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
start='<!-- GAMEPLAY-JUMPS-START -->';end='<!-- GAMEPLAY-JUMPS-END -->'
for e in rd(B/'checkpoint.json')['entries']:
 h=R/'projects'/e['slug']/'production/gameplay-v3';index=R/'output'/f"{e['slug']}-gameplay-v3/index.html"
 if not index.exists() or not (h/'outputs.json').exists():continue
 p=B/f"{e['id'].lower()}-gameplay-plan.json";clips=[]
 if p.exists():
  plan=rd(p);receipts={x.get('key',x['scene']):x for x in rd(h/'patches.json')['patches']}
  for x in plan['patches']:
   k=x.get('key',x['scene']);clips.append((receipts[k]['start'],x['title'],plan['sources'][x['source']]['game']))
 else:
  timeline={s['id']:s for s in rd(R/'projects'/e['slug']/'production/concept-fit-v2/timeline.json')['scenes']}
  audit=next(a for a in rd(B/'edit-list-audit.json')['entries'] if a['id']==e['id'])
  clips=[(timeline[s['scene']]['start']+s['offset'],s['title'],'') for s in audit['shots']]
 buttons=[]
 for at,title,game in sorted(clips):
  timestamp=f'{int(at)//60:02}:{int(at)%60:02}'
  buttons.append(f'<button type="button" onclick="const v=document.querySelector(\'video\');v.currentTime={max(0,at-1):.3f};v.play()">{timestamp} · {html.escape(title)}'+(f' <small>({html.escape(game)})</small>' if game else '')+'</button>')
 section=start+'<section><h2>게임 예시 바로 보기</h2><p>버튼을 누르면 해당 예시 직전부터 재생됩니다. 실제 동작 뒤의 관찰 정지에서는 해설과 계산 모형이 계속 이어집니다.</p><style>section button{display:block;background:#16231d;color:#f5f5ef;border:1px solid #516958;padding:12px 16px;margin:8px 0;text-align:left;font:inherit;cursor:pointer;max-width:100%}section small{color:#a5b9ac}</style>'+''.join(buttons)+'</section>'+end
 text=index.read_text('utf8')
 if start in text:text=text.split(start,1)[0]+section+text.split(end,1)[1]
 else:text=text.replace('</html>',section+'</html>')
 index.write_text(text,encoding='utf8')
print('Local review scene buttons updated')
