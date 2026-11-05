"""Update only the selected M21/M22 entries. An upload ID must come from Studio."""
from prepare import *
import argparse,re
def mark(stage,review=False):
 m21=P.with_name('game-math-shading-lights');receipt=m21/'publishing/youtube-upload-v7.json';r=read(receipt);sha21=r['video']['sha256']
 stamp=datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(R).as_posix()
 for name in ['checkpoint','review-ledger']:
  path=m21/f'production/{name}.json';j=read(path)
  j['reviewedVersion']={'sha256':sha21,'userApproved':True,'scope':'upload private M21 v7','message':'좋아~ 업로드 해줘~','fullContinuousListeningClaimed':False}
  if name=='checkpoint': j.update(humanReview=True,nextAction='Transfer this SHA256 to the intended Studio channel privately; verify real ID and privacy.',platformReceipt=rel(receipt))
  else:j['humanReview']={'status':'approved-v7-for-private-upload','masterSha256':sha21}
  save(path,j)
 cp=P/'production/checkpoint.json';j=read(cp);j.update(stage=stage,updatedAt=stamp,outputsReady=review,localReviewReady=review,humanReview=False)
 j['meaningGuides']=dict(source='10.8 / 10.9',voiceRevision='audio-v4',rules=['meaning-before-values-v1','surface-symbol-guides-v1'],revoiced=sorted(ROWS),unchanged=36-len(ROWS),editorSource=rel(P/'production/unity-staging/SkinNormalMeaningGuides.cs'),preview=rel(P/'production/unity-staging/local-preflight-meaning-v1'))
 j['nextAction']='Local user review only' if review else 'Finish selected source-synchronous Unity / audio alignment, encode and verify four outputs.'
 save(cp,j)
 ledger=P/'production/review-ledger.json';j=read(ledger);j['meaningGuides']=dict(stage=stage,at=stamp,userReviewed=False,localFinalReviewReady=review,source=rel(cp));save(ledger,j)
 w=R/'shared/publishing/video-worklist.json';j=read(w);rows={x['id']:x for x in j['rows']};a,b=rows['M21'],rows['M22']
 a.update(reviewStatus='v7 사용자 승인 · 비공개 업로드 요청',humanApproval='현재 v7 검수본 승인',platformStatus='미업로드 · Studio 파일 전송 대기',notes='승인 SHA256 '+sha21+' · 자막 포함 제작 마스터',localMasterAvailable=True)
 b.update(productionStatus=stage,reviewStatus='사용자 검수 대기' if review else '내부 제작 중',localMasterAvailable=review,productionComplete=review)
 save(w,j)
 doc=R/'docs/VIDEO_WORKLIST.md';s=doc.read_text('utf-8-sig')
 for v in [a,b]:
  def change(m):return f"| {v['id']} | {v['title']} | {v['productionStatus']} | {v['reviewStatus']} | {v['platformStatus']} |"
  s=re.sub(r'^\| '+v['id']+r' \|.*$',change,s,flags=re.M)
 doc.write_text(s,'utf8')
 bat=R/'production/batches/game-math-remaining-20261104';doc=bat/'progress.md';s=doc.read_text('utf-8-sig')
 for id,entry in [('M21','| M21 | 빛과 셰이딩 | v7 검수 완료 · YouTube 비공개 전송 대기 | 마스터 해시 대조 | 사용자 승인 |'),('M22',f'| M22 | 스키닝과 노멀 맵 | {stage} | '+('완성본 점검' if review else '내부 제작 중')+' | '+('검수 대기' if review else '완성본 대기')+' |')]:
  s=re.sub(r'^\| '+id+r' \|.*$',lambda _:entry,s,flags=re.M)
 doc.write_text(s,'utf8')
if __name__=='__main__':
 import sys
 mark(sys.argv[1], '--review-ready' in sys.argv)

