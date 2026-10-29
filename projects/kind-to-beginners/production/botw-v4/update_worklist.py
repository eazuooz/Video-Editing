"""Update only D29 and its scoped authorization, preserving all other rows."""
from pathlib import Path
import argparse,copy,datetime,json,sys
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parents[1]
sys.path.insert(0,str(R/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import patch
def read(p):return json.loads(p.read_text('utf-8-sig'))
def rel(p):return p.relative_to(R).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def guarded_write(p,original,updated):
 assert p.read_bytes()==original,'Concurrent shared-file change; reread before updating '+str(p)
 p.write_bytes(updated)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--complete',action='store_true');a=ap.parse_args();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 auth=read(H/'authorization.json');w=R/'shared/publishing/video-worklist.json';raw=w.read_bytes();original_w=raw;data=json.loads(raw.decode('utf-8-sig'));i=next(i for i,r in enumerate(data['rows'])if r['id']=='D29');row=copy.deepcopy(data['rows'][i])
 row.update(activeRevision='botw-v4',productionComplete=bool(a.complete),humanApproval='pending-new-revision-review',platformStatus='미업로드 · 야숨 수정본 검수 대기',latestRulesPassed=None,updatedAt=now)
 revision=copy.deepcopy(row.get('revisionInProduction',{}))
 revision.update(revision='botw-v4',baseMasterSha256=auth['priorCaptionedSha256'],userEvidence=auth['userEvidence'],newReviewRequired=True,privateUploadAuthorized=False,plan=rel(H),updatedAt=now,status='local-review-ready'if a.complete else'production',humanWholeViewing='not separately asserted',captionedSha256=None,reviewEvidence=rel(H/'checkpoint.json'))
 row['revisionInProduction']=revision
 for p in [rel(H/'authorization.json'),rel(H/'checkpoint.json')]:
  if p not in row['evidence']:row['evidence'].append(p)
 if a.complete:
  review=read(H/'review-status.json');assert review['status']=='local-review-ready'
  prev=row.get('localReview');history=row.setdefault('localReviewHistory',[])
  if prev and prev.get('captionedSha256')!=review['captionedSha256'] and not any(x.get('captionedSha256')==prev.get('captionedSha256')for x in history):history.append(prev)
  d=review['directory'];slug=P.name
  row['localReview']={'status':'ready-for-human-local-review','index':d+'/index.html','captionedVideo':d+'/'+slug+'.captioned.mp4','cleanVideo':d+'/'+slug+'.clean.mp4',
    'captionsKo':d+'/'+slug+'.ko.srt','captionsEn':d+'/'+slug+'.en.srt','captionedSha256':review['captionedSha256'],'durationSeconds':review['durationSeconds'],
    'actualUserViewed':False,'humanWholeListening':'pending','updatedAt':now,'feedbackEvidence':rel(H/'authorization.json'),'reviewEvidence':rel(H/'review-status.json')}
  row.update(productionStatus='botw-v4 야숨 수정본 4종 완성 · 이전 버전 보존',reviewStatus='야숨 수정본 사용자 검수 대기',executionStatus='야숨 수정본 완성 · 사용자 검수까지',internalQaStatus='botw-v4 internal QA complete; user review pending',localMasterAvailable=True,notes='야숨으로 실제 사례·대본·Unity 설명·Sample B 음성·한영 자막 수정. 새 완성본 사용자 검수 대기; 이전 버전과 모든 업로드 상태 보존.')
  row['revisionInProduction'].update(captionedSha256=review['captionedSha256'],reviewEvidence=rel(H/'review-status.json'))
  if rel(H/'review-status.json')not in row['evidence']:row['evidence'].append(rel(H/'review-status.json'))
 else:
  row.update(productionStatus='botw-v4 야숨 수정 제작 중 · clarity-v3 보존',reviewStatus='야숨 수정본 제작 후 검수',executionStatus='29편 야숨 대본·Unity 설명 수정 중',internalQaStatus='new revision in production',notes='사용자 선택 야숨으로 교체 중. 기존 clarity-v3 완성본·기록 보존; 새 검수본 아직 미완성.')
  m=read(P/'project.json');m['pendingRevision']={'revision':'botw-v4','plan':rel(H/'production-plan.json'),'status':'production','boundary':'complete-local-review'};m['latestCheckpoint']=rel(H/'checkpoint.json');save(P/'project.json',m)
 for key,value in row.items():
  if data['rows'][i].get(key)!=value:raw=patch(raw,['rows',i,key],value)
 guarded_write(w,original_w,raw)
 d=R/'docs/VIDEO_WORKLIST.md';raw=d.read_bytes();txt=raw.decode('utf-8-sig');lines=txt.splitlines(keepends=True)
 for j,line in enumerate(lines):
  end='\r\n'if line.endswith('\r\n')else'\n';parts=line.rstrip('\r\n').split('|')
  if line.startswith('| D29 | '):
   parts[3]=' '+('☑ 'if a.complete else'◐ ')+row['productionStatus']+' ';parts[4]=' ☐ '+row['reviewStatus']+' ';parts[5]=' '+row['platformStatus']+' ';lines[j]='|'.join(parts)+end
  elif '| 게임디자인 | D29 'in line:
   parts[4]=' '+row['executionStatus']+' ';parts[5]=' ☐ '+row['reviewStatus']+' ';lines[j]='|'.join(parts)+end
 guarded_write(d,raw,(b'\xef\xbb\xbf'if raw.startswith(b'\xef\xbb\xbf')else b'')+''.join(lines).encode('utf8'))
 c=R/'shared/publishing/video-production-control.json';raw=c.read_bytes();original_c=raw;base=['finiteBatchAuthorizations','design-25-30-review-actions-20261029','selectedD29Revision'];raw=patch(raw,base+['status'],'local-review-ready'if a.complete else'production');guarded_write(c,original_c,raw)
 print('D29 worklist state updated; unrelated rows and publication states preserved.')
if __name__=='__main__':main()
