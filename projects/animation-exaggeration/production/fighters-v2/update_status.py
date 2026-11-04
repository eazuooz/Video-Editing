"""Update only A02 delivery, its batch row and exact shared status fields."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, re, html, hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];P=H.parents[1]
B=R/'production/batches/animation-18-20261031';D=P/'production/local/fighters-v2/delivery/output/animation-exaggeration'
W='shared/publishing/video-worklist.json';MD='docs/VIDEO_WORKLIST.md'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def artifact(p):return {'path':rel(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def main():
 stamp=datetime.now(timezone.utc).isoformat();m=read(D/'delivery-manifest.json');ledger=read(H/'local-delivery-ledger.json')
 assert m['verification']['structuralFinalPair']=='pass' and not ledger['humanFinalReview']
 digest=m['captionedMasterSha256'];project=read(P/'project.json')
 if project['revision']!='fighters-v2':
  project.setdefault('preservedDeliveries',[]).append({'revision':project['revision'],'delivery':project['delivery']})
 project.update(revision='fighters-v2',status='local-delivery-user-review-pending',updatedAt=stamp,publishReady=False)
 project['delivery']={'status':'four-outputs-complete','directory':rel(D),'manifest':rel(D/'delivery-manifest.json'),'captionedMasterSha256':digest}
 project['voice'].update(additionalGeneration=artifact(H/'voice-generation-record.json'),finalEncodedAudioReview=artifact(H/'final-audio-asr-review.json'),status='original-preserved-plus-three-sample-b-additions',newGenerationNeeded=False)
 project['editing'].update(measuredBodyGameplayShare=m['gameplayShare'],measuredBodyExplanationShare=1-m['gameplayShare'],ratioChoiceRecord=rel(H/'authorization.json'),scenePlan=rel(H/'edit-plan.json'))
 project['review'].update(actualUserViewed=False,currentRevisionHumanReview=False)
 save(P/'project.json',project)
 batch=read(B/'checkpoint.json')
 batch.update(currentEpisode='A02',updatedAt=stamp,currentWork=['A02 fighters-v2 completed: KOF XV and Guilty Gear Strive examples; four local outputs; user review pending.','A03-A18 status is unchanged by this selected revision.'],nextAction='Review the exact A02 fighters-v2 captioned master. No platform mutation is authorized by this revision.')
 batch['costlyJobSummary'].update(ttsGenerations=3,currentJob='A02 fighters-v2 local delivery complete; no running production job',sourceAsr='A02 fighters-v2 full AAC text reviewed; actual human listening remains pending')
 save(B/'checkpoint.json',batch)
 report=read(B/'research/review-table.json');row=next(x for x in report['rows'] if x['episode']=='A02')
 row['script'].update(path=rel(P/'script/fighters-v2/narration.ko.json'),displayKo='기존 14문단 보존 + 게임 설명 3문단 · 한영 자막 132개',timingLocked=True)
 row['voice'].update(status='final-asr-reviewed-human-listening-pending',displayKo='샘플 B 보강 · 최종 음성 텍스트·연속성 확인 · 청취 검수 대기',evidence=artifact(H/'final-audio-asr-review.json'),humanListening=False)
 row['video'].update(status='local-four-output-review-delivery-ready',displayKo='격투게임 보강 검수본 · 6분 4초 · 1080p 60fps',completedReviewMaster=True,technicalQaComplete=True,sampledEncodedPixelsReviewed=True,finalAudioVisualQaComplete=False,humanFinalReviewRecorded=False,uploadAuthorizedByBatch=False,qaScopeKo='41컷·132개 자막 표본 검사 및 연속 음성 검사 완료. 실제 게임 60% · 사용자 시청·청취 대기.')
 host='http://127.0.0.1:9238/@fs/D:/Github/VideoEditing/'
 row['delivery']={'directory':rel(D),'indexUrl':host+rel(D/'index.html'),'captionedUrl':host+rel(D/'animation-exaggeration.captioned.mp4'),'manifestUrl':host+rel(D/'delivery-manifest.json'),'captionedMasterSha256':digest,'manifest':artifact(D/'delivery-manifest.json'),'fourOutputs':m['files'],'userFinalReview':False,'uploadsPerformed':False}
 row['nextActionKo']='격투게임 예시 보강본 전체 시청·청취 및 사용자 검수'
 row['evidenceSnapshot']={'checkedAt':stamp,'delivery':artifact(D/'delivery-manifest.json'),'pixels':artifact(H/'final-pixel-review.json'),'basis':'A02 revision only; no completion inferred for other episodes.'}
 report['updatedAtKst']=datetime.now().astimezone().isoformat();report['validation'].update(a02Paragraphs=17,a02PairedUnits=132)
 save(B/'research/review-table.json',report)
 page=(B/'research/review-table.html').read_text(encoding='utf-8');esc=html.escape
 video=esc(row['video']['displayKo'])+f'<small><a href="{esc(row["delivery"]["indexUrl"])}">영상·자막 보기</a> · <a href="{esc(row["delivery"]["captionedUrl"])}">전체 영상</a></small>'
 replacement='<tr><td data-label="편">A02</td>'+f'<td data-label="제목 / 원제"><strong>{esc(row["titleKo"])}</strong><small><a href="{esc(row["sourceUrl"])}">{esc(row["sourceTitleEn"])}</a></small></td>'+f'<td data-label="원본 검토">{esc(row["research"]["displayKo"])}</td>'+f'<td data-label="대본">{esc(row["script"]["displayKo"])}</td>'+f'<td data-label="음성">{esc(row["voice"]["displayKo"])}</td>'+f'<td data-label="영상·최종 검수">{video}<small>{esc(row["video"]["qaScopeKo"])}</small></td></tr>'
 page,count=re.subn(r'<tr><td data-label="편">A02</td>.*?</tr>',lambda _:replacement,page,count=1,flags=re.S);assert count==1
 (B/'research/review-table.html').write_text(page,encoding='utf-8')
 originals=[json.loads(subprocess.check_output(['git','show',ref+':'+W],cwd=R)) for ref in ['HEAD','']]+[read(R/W)]
 fields={'productionComplete':True,'productionStatus':'격투게임 예시 보강 검수본 · 1080p60 · 6분4초 · 실제60:설명40','reviewStarted':True,'reviewStatus':'41컷·132개 자막·음성 텍스트 검사 완료 · 사용자 시청·청취 대기','executionStatus':'A02 보강본 로컬 검수 대기 · 업로드 미승인','localMasterAvailable':True,'deliveryLedger':rel(H/'local-delivery-ledger.json'),'captionedMasterSha256':digest,'updatedAt':stamp}
 changes=[]
 for k,v in fields.items():
  expected=[]
  for old in originals:
   r=next(x for x in old['rows'] if x['id']=='A02');value={'exists':k in r,'value':r.get(k)}
   if value not in expected:expected.append(value)
  changes.append({'field':k,'value':v,'expected':expected})
 line=next(x for x in (R/MD).read_text(encoding='utf-8-sig').splitlines() if x.startswith('| A02 | '))
 replacement=line[:line.rfind('|',0,line.rfind('|'))+1]+' 격투게임 예시 보강 · 6분4초·1080p60 · 사용자 검수 대기 |'
 owned=[p for base in [H,P/'script/fighters-v2'] for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (p.suffix in {'.py','.json','.md','.html','.cjs'} or p.name in {'narration.spoken-ko.txt','additional-narration.ko.txt'}) and p.name not in {'delivery-commit-plan.json'}]
 owned += [P/'project.json',B/'checkpoint.json',B/'research/review-table.json',B/'research/review-table.html']
 md_variants=[line]
 for ref in ['HEAD','']:
  prior=subprocess.check_output(['git','show',ref+':'+MD],cwd=R).decode('utf-8-sig')
  old_line=next(x for x in prior.splitlines() if x.startswith('| A02 | '))
  if old_line not in md_variants:md_variants.append(old_line)
 spec={'scope':'animation-A02-fighters-v2-delivery','rows':[{'id':'A02','changes':changes,'appendEvidence':[rel(H/'local-delivery-ledger.json'),rel(H/'source-review.json')]}],'markdownRows':[{'id':'A02','expected':line,'expectedVariants':md_variants,'value':replacement}],'seriesStatus':read(R/W)['animationSeriesPlan']['status'],'ownedPaths':sorted({rel(p) for p in owned})}
 save(H/'delivery-commit-plan.json',spec)
 print(json.dumps({'updated':'A02 only','ownedFiles':len(spec['ownedPaths']),'sha256':digest},ensure_ascii=False))
if __name__=='__main__':main()
