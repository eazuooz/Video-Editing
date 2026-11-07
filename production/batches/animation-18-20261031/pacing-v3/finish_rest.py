"""Collect verified local deliveries; selectively commit only this finite revision."""
from pathlib import Path
import json,sys,hashlib,datetime,html,importlib.util,contextlib,subprocess
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/pacing-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def clock(s):return f'{int(s)//60}:{int(s)%60:02}'
def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();records=[];fields={};reviewed=read(L/'visual-review.json');preservation=read(L/'preservation-audit.json')
 for old in read(B/'real-clips-v2/review-manifest.json')['records']:
  ep=old['id'];P=R/'projects'/old['slug'];F=P/'production/pacing-v3/edit-plan.json';plan=read(F);D=R/plan['outputDirectory'];f=D/'delivery-manifest.json';m=read(f)
  if ep!='A02':
   assert reviewed[ep]['status']=='sampled-changed-visuals-reviewed',ep
   assert reviewed[ep]['masterSha256']==next(x['sha256'] for x in m['files'] if x['kind']=='captioned.mp4'),(ep,'visual review hash differs')
   sampleFile=R/reviewed[ep]['sampleFile'];samples=read(sampleFile);samples.update(modelVisualInspection=reviewed[ep]['status'],reviewedMasterSha256=reviewed[ep]['masterSha256'],fullPlayback=False);save(sampleFile,samples)
   assert all(m['narrationAllSamplesPreserved'] for _ in [0])
   key=lambda e:{k:e[k] for k in ['key','pictureAt','audioAt','sourceSHA256','sourceStartFrame','sourceEndFrame','repeatCount','frames']}
   assert [key(e) for e in m['events']]==[key(e) for e in plan['events']],(ep,'rendered plan differs')
   assert m.get('packetProof') and len(set(m['identicalAAC'].values()))==1
   assert preservation[ep]['totalFrames']==round(m['durationSeconds']*60)
   assert all(x['allCueTextPreserved'] for x in preservation[ep]['languages'].values())
   assert preservation[ep]['languages']['ko']['allObservationInsertionsAfterCompleteSentence']
   audio=read(P/'production/local/pacing-v3/audio-proof.json');assert all(x.get('serializedPCMExactEquality') for x in audio['segments'])
   for x in m['files']:assert sha(R/x['path'])==x['sha256'],(ep,x['kind'])
   m.update(status='local-review-ready',humanViewed=False,wholeHumanListening=False,technicalChecks='Both full decodes, FHD60 frame counts and uniform packet timestamps; identical AAC; all baseline final-mix PCM samples retained exactly',visualReview=reviewed[ep],bilingualPreservation=preservation[ep],audioProofSHA256=sha(P/'production/local/pacing-v3/audio-proof.json'),measuredScreenShare=plan['measuredScreenShare'],planSHA256=sha(F),platformMutation=False)
   save(f,m);save(P/'production/pacing-v3/checkpoint.json',m)
   fields[ep]=dict(productionStatus=f'기본 속도 약3회 관찰 후 기존 분석 · {clock(m["durationSeconds"])}',reviewStatus='1080p60·전체 디코딩·PCM 보존·변경 화면 표본 확인 · 통합 사용자 검수 대기',executionStatus='페이싱 수정본 로컬 검수 준비',updatedAt=now,deliveryLedger=(P/'production/pacing-v3/checkpoint.json').relative_to(R).as_posix(),captionedMasterSha256=next(x['sha256'] for x in m['files'] if x['kind']=='captioned.mp4'))
  m['directory']=D.relative_to(R).as_posix();m['description']=f'기본 속도 관찰 {len(plan["events"])}개 구간 → 기존 느린 분석. 기존 설명·음성·배경음악 보존.'
  records.append(m)
 save(H/'review-manifest.json',dict(createdAt=now,status='18-local-reviews-ready-a02-scheduled',records=records,humanReviewPending=[x['id'] for x in records],platformReceipt='projects/animation-exaggeration/publishing/pacing-v3/upload.json'))
 if (L/'storage-relocation.json').exists():save(H/'storage-layout.json',dict(reason='Keep existing D-drive paths through directory junctions while retaining newly generated revision media on C; preserve all earlier baselines',relocations=read(L/'storage-relocation.json')))
 rows=[]
 for m in records:
  id=m['id'];topic=m['title'].split(' | ')[0];added=sum(e['frames'] for e in m['events'])/60
  focus=' · '.join(dict.fromkeys(e['reason'] for e in m['events'] if e['kind']=='explanation'))
  state='11/8 오전 8시 예약 완료 · 구본 비공개' if id=='A02' else '수정본 검수 대기'
  rows.append(f'<tr><td>{id}</td><td><a href="http://127.0.0.1:9277/{id}/">{html.escape(topic)}</a><small>{html.escape(focus)}</small></td><td>{clock(m["durationSeconds"])}</td><td>+{added:.1f}초</td><td>{state}</td></tr>')
 page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 · 애니메이션 통합 검수</title><style>body{margin:0;background:#101713;color:#f0f2ed;font:17px/1.65 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:28px 20px}h1{color:#f2d787;font-size:30px}a{color:#a7dfbf}p{max-width:980px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:760px}th,td{text-align:left;padding:15px 12px;border-bottom:1px solid #3b4c40;vertical-align:top}th{color:#f2d787}small{display:block;color:#b7c6ba;margin-top:8px;font-size:14px;max-width:580px}footer{margin-top:30px;color:#b7c6ba}</style><main><h1>애니메이션 18편 · 통합 검수</h1><p>핵심 동작을 기본 속도로 약 세 번 관찰한 뒤 기존 느린 구간·자세 분석으로 이어집니다. 원래 대본, 음성, 설명 순서와 영상은 보존했습니다.</p><p><a href="https://youtu.be/VW4Bj-qmIZg">A02 YouTube 수정본</a>은 2026년 11월 8일 오전 8시(한국시간) 예약 완료. 나머지 17편은 아래 로컬 수정본을 검수해 주세요. 각 영상 페이지에서 자막/무자막 MP4와 한·영 SRT를 받을 수 있습니다.</p><div class="scroll"><table><thead><tr><th>편</th><th>주제 · 관찰 포인트</th><th>길이</th><th>추가 관찰</th><th>상태</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><footer>공통 확인: 1920×1080 · 60fps, 두 MP4 전체 디코딩, 프레임 타이밍, 동일 AAC, 기존 음성 PCM 보존. 변경 구간의 화면·자막 표본을 확인했습니다. 실제 전체 시청·청취와 최종 사용자 검수는 대기 상태입니다. 다른 영상의 YouTube 공개 상태는 변경하지 않았습니다.</footer></main></html>'''
 (R/'output/animation-series-review/pacing-v3/index.html').write_text(page,'utf-8')
 save(H/'checkpoint.json',dict(stage='all18-local-reviews-ready-a02-replacement-complete',completed=[x['id'] for x in records],remainingProduction=[],humanReviewPending=[x['id'] for x in records],updatedAt=now,reviewManifest=(H/'review-manifest.json').relative_to(R).as_posix(),reviewUrl='http://127.0.0.1:9277/',platformAuthorizedEpisodes=['A02'],platformReceipt='projects/animation-exaggeration/publishing/pacing-v3/upload.json',automationStarted=False))
 # Preserve all other worktree/index bytes, including foreign staged changes.
 helper=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py';spec=importlib.util.spec_from_file_location('scoped',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json'
 control=read(R/C)['animationPacingRevision20261107'];control.update(other17LocalDeliveredAt=now,reviewManifest=(H/'review-manifest.json').relative_to(R).as_posix(),status='a02-scheduled-17-local-review-ready')
 def overlay(name,raw,spec):
  if name==C:return mod.patch(raw,['animationPacingRevision20261107'],control)
  if name==W:
   for ep,updates in fields.items():
    index=next(i for i,x in enumerate(mod.load(raw)['rows']) if x['id']==ep)
    for k,v in updates.items():raw=mod.patch(raw,['rows',index,k],v)
   return raw
  if name==D:
   lines=raw.decode('utf-8-sig').splitlines(keepends=True)
   for i,line in enumerate(lines):
    ep=next((ep for ep in fields if line.startswith('| '+ep+' | ')),None)
    if ep:
     end=line.rfind('|');before=line.rfind('|',0,end);lines[i]=line[:before+1]+' 페이싱 수정본 · 기본속도 관찰 후 분석 / 통합 검수 대기 |\n'
   return ''.join(lines).encode('utf-8')
  raise ValueError(name)
 mod.SHARED={W,D,C};mod.overlay=overlay
 for name in mod.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
 paths=[p.relative_to(R).as_posix() for p in H.iterdir() if p.is_file() and p.suffix in ('.py','.json','.cjs','.ps1')]
 for m in records:
  if m['id']=='A02':continue
  paths.extend(p.relative_to(R).as_posix() for p in (R/'projects'/m['slug']/'production/pacing-v3').glob('*.json'))
 paths+=['output/animation-series-review/pacing-v3/index.html'];paths=sorted(set(paths))
 def validate(spec):
  assert spec['ownedPaths']==paths and all((R/p).is_file() for p in paths)
  return paths+sorted(mod.SHARED)
 mod.validate=validate;specpath=L/'rest-commit-spec.json';save(specpath,dict(ownedPaths=paths));sys.argv=[str(helper),'--spec',str(specpath),'--execute','--push','--message','Add native-speed observation passes to remaining animation reviews']
 with (L/'rest-commit-result.json').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):mod.main()
 print(read(L/'rest-commit-result.json')['commit'])
if __name__=='__main__':main()
