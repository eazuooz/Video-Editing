"""Publish selected A03 local review only, preserving every other manifest record."""
from pathlib import Path
import json,os,re,html,shutil,datetime,hashlib
from prepare import H,P,R,B,L,read,save,sha

def rel(p):return p.relative_to(R).as_posix()
def record_span(text,episode):
 m=re.search(r'\{\s*"id":\s*"'+episode+r'"',text);assert m
 obj,n=json.JSONDecoder().raw_decode(text[m.start():]);return m.start(),m.start()+n,obj

def main():
 c=read(R/'shared/publishing/video-production-control.json')['a03ContrastRevision20261108'];assert c['fullLocalRevisionAuthorized']
 plan=read(H/'edit-plan.json');q=read(L/'qa.json');review=read(H/'visual-review.json')
 assert review['masterSha256']==q['technicalChecks']['captioned.mp4']['sha256'] and review['status']=='sampled-current-encoded-visuals-reviewed'
 out=L/'delivery/output'/P.name;out.mkdir(parents=True,exist_ok=True);files=[]
 for kind in ['captioned.mp4','clean.mp4','ko.srt','en.srt']:
  source=Path(q['technicalChecks'][kind]['path']);dest=out/source.name
  if not dest.exists():os.link(source,dest)
  assert sha(dest)==q['technicalChecks'][kind]['sha256'];files.append({'kind':kind,'path':rel(dest),'sha256':sha(dest),'bytes':dest.stat().st_size})
 title=read(P/'project.json')['title'];master=next(x['sha256'] for x in files if x['kind']=='captioned.mp4')
 desc='네 단계 실제 자세를 한 화면에서 비교하고, 정상 속도 3회 뒤 관절 궤적·기준 자세를 겹친 느린 분석으로 확인합니다. 기존 음성·관계도·게임 예시는 유지했습니다.'
 links=' · '.join('<a href="'+html.escape(P.name+'.'+x['kind'])+'">'+label+'</a>' for x,label in zip(files,['자막 영상','무자막 영상','한국어 자막','영어 자막']))
 (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>A03 검수본</title><style>body{background:#111;color:#eee;font:18px/1.6 sans-serif;max-width:1200px;margin:auto;padding:20px}h1{color:#f2d787;font-size:27px}a{color:#77d7ca}video{width:100%}</style><h1>'+html.escape(title)+'</h1><p>'+desc+'</p><video controls playsinline preload="metadata" src="'+P.name+'.captioned.mp4"></video><p>'+links+'</p><p>1920×1080 · 60fps · 7분 27.63초. 전체 기술 디코딩과 변경 화면·375px 표본을 확인했습니다. 전체 인간 시청·청취 및 사용자 검수는 대기 중입니다.</p>','utf-8')
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
 project=read(P/'project.json');project.update(revision='contrast-v5',checkpoint=rel(H/'checkpoint.json'),status='local-review-delivered')
 project['delivery'].update(status='four-outputs-complete',localStorageRoot=rel(L/'delivery'),captionedMasterSha256=master,revision='contrast-v5',humanReview='pending')
 for key,kind in [('videoClean','clean.mp4'),('videoBurnedCaptions','captioned.mp4'),('captionsKo','ko.srt'),('captionsEn','en.srt')]:project['paths'][key]=next(x['path'] for x in files if x['kind']==kind)
 project['paths']['visualRevisionPlan']=rel(H/'edit-plan.json')
 project['editing']['measuredBodyGameplayShare']=plan['baseline']['measuredScreenShare']['actualGameplayShare']
 project['contrastRevision']={'version':'contrast-v5','checkedAt':now,'previousProject':rel(H/'previous-project.json'),'plan':rel(H/'edit-plan.json'),'visualReview':rel(H/'visual-review.json'),'technicalQA':rel(L/'qa.json'),'audioPacketBytesPreserved':True,'ttsRegenerated':False,'otherEpisodesRemade':False,'platformMutation':False}
 project['review'].update(humanFinalReviewCompleted=False,audioListeningCompleted=False,visualReviewCompleted=False,internalEncodedVisualSamplesReviewed=True)
 save(P/'project.json',project)
 ledger_path=P/'production/review-ledger.json'
 if not (H/'previous-review-ledger.json').exists():shutil.copy2(ledger_path,H/'previous-review-ledger.json')
 ledger=read(ledger_path);ledger.update(revision='contrast-v5',status='local-delivery-user-review-pending',checkedAt=now,directory=rel(out),captioned=next(x['path'] for x in files if x['kind']=='captioned.mp4'),captionedMasterSha256=master,durationSeconds=plan['duration'],frames=plan['totalFrames'],files=files,scenePlan=rel(H/'edit-plan.json'),technicalQA=q['technicalChecks'])
 ledger['currentVisualReview']={'path':rel(H/'visual-review.json'),'scope':'current encoded changed visual samples at 1080 and 375; not full watch','fullWatch':False,'fullListening':False}
 ledger['baselineReview']=rel(H/'previous-review-ledger.json');ledger['audioPreservation']={'aacPacketSha256':q['technicalChecks']['captioned.mp4']['aacPacketSha256'],'unchangedOriginalMixSha256':q['unchangedOriginalMixSha256'],'newTTS':False,'newASR':False};save(ledger_path,ledger)
 ledger['bilingualCues']=len(re.findall(r'^\d+\s*$',(out/(P.name+'.ko.srt')).read_text('utf-8-sig'),re.M))
 ledger['gameplayShare']=plan['baseline']['measuredScreenShare']['actualGameplayShare'];ledger['measuredScreenShare']=plan['baseline']['measuredScreenShare']
 if 'relationsV4Review' in ledger:ledger['relationsV4Review']['archivedBaseline']=True;ledger['relationsV4Review'].pop('activeLocalRevision',None)
 save(ledger_path,ledger)
 manifest=B/'relations-v4/review-manifest.json';text=manifest.read_bytes().decode('utf-8');before_sha=sha(manifest);a,z,old=record_span(text,'A03');before=read(manifest);new=dict(old);preserved=[]
 new.update(revision='contrast-v5',status='local-review-ready',description=desc,directory=rel(out),files=files)
 new.update(visualReview=review,technicalChecks=q['technicalChecks'],checkedAt=now)
 new['visualRevision']={'plan':rel(H/'edit-plan.json'),'review':rel(H/'visual-review.json'),'qa':rel(L/'qa.json'),'previousRevision':'relations-v4','sameAudio':True,'humanReview':False}
 # Replace only the A03 object, byte-preserving all surrounding foreign records.
 replacement=json.dumps(new,ensure_ascii=False,indent=2).replace('\n','\n    ')
 after_text=text[:a]+replacement+text[z:];after=json.loads(after_text)
 for item in before['records']:
  if item['id']=='A03':continue
  x,y,_=record_span(text,item['id']);u,v,_=record_span(after_text,item['id']);assert text[x:y]==after_text[u:v]
  preserved.append({'id':item['id'],'recordSha256BeforeAndAfter':hashlib.sha256(text[x:y].encode('utf-8')).hexdigest(),'deliveryFilesUnchanged':item['files']})
 assert [x for x in before['records'] if x['id']!='A03']==[x for x in after['records'] if x['id']!='A03']
 manifest.write_bytes(after_text.encode('utf-8'))
 page=B/'relations-v4/review.html';page_text=page.read_bytes().decode('utf-8');m=re.search(r'<tr><td>A03</td>.*?</tr>',page_text);assert m
 replacement=m.group().replace('36.1초 추가 설명 ·','36.1초 관계도 · 실제 4단계 자세·궤적 분석 개선 ·')
 page.write_bytes((page_text[:m.start()]+replacement+page_text[m.end():]).encode('utf-8'))
 save(H/'integration-proof.json',{'beforeManifestSha256':before_sha,'afterManifestSha256':sha(manifest),'onlyChangedRecord':'A03','preserved17Records':preserved,'htmlEdit':'A03 row only'})
 report={'revision':'contrast-v5','stage':'local-four-files-ready-user-review-pending','completedAt':now,'durationSeconds':plan['duration'],'frames':plan['totalFrames'],'directory':rel(out),'files':files,'captionedMasterSha256':master,'technicalQA':rel(L/'qa.json'),'visualReview':rel(H/'visual-review.json'),'baselinePreserved':True,'other17ManifestRecordBytesUnchanged':True,'audioPacketsAndBothSrtBytesUnchanged':True,'humanReview':False,'fullHumanWatch':False,'fullHumanListening':False,'platformMutation':False,'reviewUrl':'http://127.0.0.1:9284/A03/'}
 save(H/'checkpoint.json',report);save(H/'delivery.json',report)
 print(json.dumps({'directory':str(out),'masterSha256':master,'other17RecordsBytePreserved':True}))
if __name__=='__main__':main()
