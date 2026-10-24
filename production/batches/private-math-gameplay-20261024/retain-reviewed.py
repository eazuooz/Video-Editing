"""Keep three already suitable, inspected deliveries byte-identical."""
from pathlib import Path
import json,hashlib,subprocess,datetime
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proof=rd(B/'playback-batch1.json')['results']
for e in rd(B/'edit-list-audit.json')['entries']:
 if e['id'] not in ['M03-original','M04','M05']:continue
 slug=e['slug'];old=R/'projects'/slug/'production/concept-fit-v2';h=old.parent/'gameplay-v3';o=rd(old/'outputs.json');qa=rd(old/'qa.json');T=rd(old/'timeline.json');tests=[]
 for f in o['outputs']:
  file=R/f['path'];assert hashlib.sha256(file.read_bytes()).hexdigest()==f['sha256']
  if file.suffix=='.mp4':
   q=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(file)]));v=next(x for x in q['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',T['frames'])
   previous=next(x for x in qa['technical'] if x['sha256']==f['sha256']);assert previous['decodeErrors']==0
   tests.append(dict(path=f['path'],sha256=f['sha256'],width=1920,height=1080,fps=60,frames=T['frames'],fullDecodeEvidence=str(old.relative_to(R)/'qa.json'),evidenceReusedOnIdenticalHash=True))
 cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'));assert cap['sha256']==proof[e['id']]['sha256']
 o.update(status='retained-after-current-gameplay-review',retainedByteIdentical=True,newRender=False,actualWholeListening=False,humanReview='pending');save(h/'outputs.json',o)
 save(h/'technical-qa.json',dict(episode=e['id'],checkedAt=datetime.datetime.now().astimezone().isoformat(),checks=tests,retainedByteIdentical=True,oldQa=str(old.relative_to(R)/'qa.json'),wholeAudioListening=False,humanReview='pending'))
 save(h/'retention-decision.json',dict(episode=e['id'],reason='Existing concept-matched object manipulation examples and guides remain useful at native speed; retain original cuts after current frame and normal-speed playback review. No unnecessary rerender.',playback='production/batches/private-math-gameplay-20261024/playback-batch1.json',frameEvidence=f'shared/output/private-math-gameplay-20261024/retention-review/{e["id"]}-0.jpg',shots=e['shots'],newTts=False,newRender=False))
 d=R/'output'/f'{slug}-gameplay-v3';d.mkdir(exist_ok=True);links={x['path'].rsplit('.',2)[-2]+'.'+x['path'].rsplit('.',1)[-1]:'../'+Path(x['path']).parent.name+'/'+Path(x['path']).name for x in o['outputs']}
 (d/'index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{{background:#101412;color:#eee;font:18px/1.7 system-ui;max-width:1100px;margin:30px auto;padding:20px}}video{{width:100%}}a{{color:#80d3a2}}h1{{color:#ffd773}}</style><h1>{e["title"]}</h1><p>기존 게임 장면과 기즈모를 재검수한 뒤 동일 파일을 보존했습니다. 전체 최종 청취 및 사용자 검수는 별도입니다.</p><video controls src="{links["captioned.mp4"]}"></video><p>'+ ' · '.join(f'<a href="{u}">{k}</a>' for k,u in links.items())+'</p><p><a href="../private-math-gameplay-20261024/index.html">전체 검수표</a></p>',encoding='utf8')
 print(e['id'],'retained hash verified',flush=True)
