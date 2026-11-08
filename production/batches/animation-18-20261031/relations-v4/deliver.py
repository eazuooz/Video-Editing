"""Collect this finite revision only after current encoded visual verification."""
from pathlib import Path
import json,sys,subprocess,hashlib,datetime,html,re
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def rel(p):return p.absolute().relative_to(R.absolute()).as_posix()
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def stamp(s):return f'{int(s)//60}:{int(s)%60:02}'

def deliver(id):
 e=next(e for e in read(H/'planning/relations-plan.json')['episodes'] if e['id']==id);P=R/'projects'/e['slug'];O=P/'production/local/relations-v4';M=P/'production/relations-v4';M.mkdir(exist_ok=True)
 a=read(O/'assembly.json');q=read(O/'qa.json');reviews=read(L/'visual-review.json')
 if (L/'visual-review-rest.json').exists():reviews.update(read(L/'visual-review-rest.json'))
 visual=reviews[id]
 cap=next(f for f in q['files'] if f['kind']=='captioned.mp4')
 assert visual['status']=='sampled-current-encoded-visuals-reviewed' and visual['masterSha256']==cap['sha256'],id
 assert not any(o.get('result') in {'needs-fix','failed','blocked'} for o in visual.get('observations',[])),(id,'Unresolved visual review finding')
 assert q['status']=='technical-checks-passed-visual-review-pending'
 for f in q['files']:assert sha(R/f['path'])==f['sha256'],(id,f['kind'])
 p=read(P/'project.json');backup=M/'previous-project-manifest.json'
 if not backup.exists():save(backup,p)
 # The current editable transcript is recovered from the actual delivered cue text.
 for lang in ['ko','en']:
  f=R/next(f['path'] for f in q['files'] if f['kind']==lang+'.srt');blocks=re.split(r'\n\s*\n',f.read_text('utf-8-sig').strip());lines=[' '.join(b.splitlines()[2:]) for b in blocks]
  paragraphs=[];buf=[]
  for line in lines:
   buf.append(line)
   if re.search(r'[.!?][”"’\']?$',line):paragraphs.append(' '.join(buf));buf=[]
  if buf:paragraphs.append(' '.join(buf))
  save(M/('final.'+lang+'.json'),{'provenance':'Display transcript from preserved baseline and added narration; existing speech must be reused, not regenerated from captions.','scenes':[{'id':f'{i+1:03}','title':e['title'],'lines':[t]} for i,t in enumerate(paragraphs)]})
 paths=p.setdefault('paths',{});V=O/'rendered'
 for key,kind in [('videoClean','clean.mp4'),('videoBurnedCaptions','captioned.mp4'),('captionsKo','ko.srt'),('captionsEn','en.srt')]:paths[key]=rel(V/(e['slug']+'.'+kind))
 paths.update(audioMix=rel(O/'mix.wav'),timeline=rel(M/'edit-plan.json'),script=rel(M/'final.ko.json'),scriptKo=rel(M/'final.ko.json'),scriptEn=rel(M/'final.en.json'))
 if 'narration' in paths:paths['originalNarrationSource']=paths.pop('narration')
 paths['narrationAddition']=rel(H/'local/voice/chunks'/(id+'-scene.wav'))
 p.setdefault('titles',{})['ko']=a['title']
 p['publishReady']=False;p.setdefault('delivery',{}).update(status='four-outputs-pending',localStorageRoot=rel(O/'delivery'),captionedMasterSha256=cap['sha256'],revision='relations-v4',humanReview='pending')
 p['relationsRevision']={'version':'relations-v4','checkedAt':now(),'baselineManifest':rel(H.parent/'pacing-v3/review-manifest.json'),'previousManifest':rel(backup),'addedSpeechOnly':True,'audioReconstruction':'Preserved pacing-v3 mix + added paragraph + proven music-only observation relocation. No new isolated full narration stem was synthesized.','platformMutation':False}
 save(M/'edit-plan.json',a);save(P/'project.json',p)
 prior=P/'production/delivery-output.json';priorcopy=M/'previous-delivery-output.json'
 if prior.exists() and not priorcopy.exists():save(priorcopy,read(prior))
 subprocess.run(['node','scripts/collect-video-output.cjs',e['slug']],cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 collected=read(prior);files=[]
 for f in collected['files']:
  kind=f['name'][len(e['slug'])+1:];files.append({'kind':kind,'path':collected['directory']+'/'+f['name'],'sha256':f['sha256'],'bytes':f['bytes']})
 record={'id':id,'slug':e['slug'],'title':a['title'],'revision':'relations-v4','status':'local-review-ready','description':'관계도 설명 → 정상 속도 관찰 → 기존 느린 분석. 기존 본문 음성 보존.','durationSeconds':a['duration'],'frames':a['totalFrames'],'directory':collected['directory'],'files':files,'insertion':a['insertion'],'bodyRepairs':a.get('bodyRepairs',[]),'audioProof':a['audioProof'],'measuredScreenShare':a['measuredScreenShare'],'visualReview':visual,'technicalChecks':q['videoChecks'],'loudness':q['loudnessMeasuredOnly'],'humanViewed':False,'humanListened':False,'platformChanged':False,'checkedAt':now()}
 save(M/'checkpoint.json',record);save(M/'review.json',q)
 ledger=P/'production/review-ledger.json';j=read(ledger) if ledger.exists() else {};j['relationsV4Review']={'checkpoint':rel(M/'checkpoint.json'),'activeLocalRevision':'relations-v4','masterSha256':cap['sha256'],'status':'local-review-ready-human-review-pending','humanViewed':False,'humanListened':False};save(ledger,j)
 p=read(P/'project.json');p['delivery']['status']='four-outputs-complete';save(P/'project.json',p)
 print(id,'four outputs collected',flush=True)

def manifest():
 records=[]
 for e in read(H/'planning/relations-plan.json')['episodes']:
  p=R/'projects'/e['slug']/'production/relations-v4/checkpoint.json';assert p.exists(),e['id'];records.append(read(p))
 save(H/'review-manifest.json',{'createdAt':now(),'status':'18-local-reviews-ready','humanReviewPending':[r['id'] for r in records],'platformChanged':False,'records':records})
 rows=[]
 for r in records:
  id=r['id'];topic=html.escape(r['title']);a=r['insertion'];focus='관계도 '+stamp(a['pictureFrame']/60)+' · '+f"{a['duration']:.1f}초 추가 설명"
  if r['bodyRepairs']:focus+=' · 본문 도식 보완'
  rows.append(f'<tr><td>{id}</td><td><a href="/{id}/">{topic}</a><small>{focus} · <a href="/{id}/?t={a["pictureFrame"]/60:.3f}">관계도부터 보기</a></small></td><td>{stamp(r["durationSeconds"])}</td><td>검수 대기</td></tr>')
 page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>애니메이션18편 · 관계도 보강 검수</title><style>body{margin:0;background:#101713;color:#f0f2ed;font:17px/1.65 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:28px 20px}h1{color:#f2d787;font-size:30px}a{color:#a7dfbf}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:680px}th,td{text-align:left;padding:15px 12px;border-bottom:1px solid #3b4c40}th{color:#f2d787}small{display:block;color:#b7c6ba;margin-top:8px;font-size:14px}footer{margin-top:30px;color:#b7c6ba}</style><main><h1>애니메이션18편 · 관계도 보강 검수</h1><p>각 편의 개념 관계를 먼저 그림과 말로 풀고, 정상 속도 관찰과 기존 자세 분석으로 이어집니다. 원래 본문 음성·게임 예시·이전 완성본은 보존했습니다.</p><p>영상별 페이지에서 자막/무자막 MP4와 한·영 SRT를 확인할 수 있습니다. 이번 수정본은 로컬 검수용이며 기존 YouTube 공개·예약 상태는 변경하지 않았습니다.</p><div class="scroll"><table><thead><tr><th>편</th><th>주제 · 수정 위치</th><th>길이</th><th>상태</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><footer>1080p60, 전체 디코딩, 동일 AAC, 기존 본문 PCM 보존, 추가 음성의 전체 ASR 대조와 변경 화면·모바일 표본 확인을 수행했습니다. 실제 전체 시청·청취 및 최종 사용자 검수는 대기 상태입니다.</footer></main></html>'''
 (H/'review.html').write_text(page,'utf-8');print('18 local reviews indexed')
if __name__=='__main__':manifest() if sys.argv[1]=='manifest' else deliver(sys.argv[1])
