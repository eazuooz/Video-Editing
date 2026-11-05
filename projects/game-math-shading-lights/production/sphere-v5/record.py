"""Record only M21's completed local checks; never advance other episodes/platform state."""
import re
from pathlib import Path
from delivery import B,P,R,W,SL,DEST,D,Q,read,write,HERO,BAKE
from review import now
STATUS='1080p60 수정본 · 재질 구·광선·카메라·영문 기호 반영 · 전체 디코딩·브라우저 재생 검사 완료'
def run():
 report=read(B/'review-evidence.json');browser=read(W/'final-qa/browser-playback.json');files=report['technical']['files']
 out={k:v['path'] for k,v in files.items()};out['index']=str(DEST/'index.html')
 catalog=[];scenes={x['id']:x for x in read(P/'planning/scene-bindings.json')['scenes']};sources={x['id']:x for x in read(P/'planning/footage-audit.json')['sources']}
 for i,c in enumerate(Q['cuts']):
  sid=c['scene'];s=int(sid);orig=scenes[sid];receipt=read(D/f'{i:03}-{sid}.done.json');assert receipt['frames']==c['frames']
  row=dict(cut=i,beat=sid,article=orig['sourceParagraphs'],term=orig['cue']['termKorean'],startFrame=120+c['globalStartFrame'],frames=c['frames'])
  if c['kind']!='explanation':
   src=sources[c['sourceId']];row.update(renderer='retained independent gameplay',game=src['game'],url=src['recordingUrl'],nativeSeconds=[c['sourceIn'],c['sourceOut']],annotation=orig['actualGamePart']['annotationPlan']['target'])
  elif s in HERO:
   assert (W/'optical'/sid/'complete.json').is_file();row.update(renderer='optics.py',states=len(read(W/'optical'/sid/'complete.json')['keys']),unit='frame / 60 s',anchoredAt='sphere surface P')
  elif s==78:row.update(renderer='four-up closing; actual frames from 009/037/074/076')
  else:
   group='bake-jobs' if s in BAKE else 'fit-jobs' if s in [53,56,58] else 'native-jobs'
   job=read(W/group/(sid+'.json'));capture=read(Path(job['output'])/'capture-success.json')
   listing=(D/f'{i:03}-{sid}.ffconcat').read_text(encoding='utf-8');assert Path(job['output']).as_posix()+'/' in listing
   assert (W/'NativeProject'/capture['scene']).is_file() and capture['completed']==len(job['sampleFrames'])
   row.update(renderer='Unity URP '+group.split('-')[0],editableScene=capture['scene'],sampledStates=capture['completed'],build=capture['compiledFingerprint'])
   if s in BAKE and 'nativeBakeReused' in receipt:
    receipt.pop('nativeBakeReused');receipt['originalRoomReused']=False;write(D/f'{i:03}-{sid}.done.json',receipt)
  catalog.append(row)
 write(B/'scene-catalog.json',dict(basis='120-frame brand + original body + 600-frame invitation; edited shot frames count from beginning',editableProject=str(W/'NativeProject'),footageAudit='planning/footage-audit.json',cuts=catalog))
 report['reviewBrowser']=browser;report['framing']={'inspected':['053','056','058'],'result':'Reframed camera includes complete solar source, solid-angle footprint and attenuation diagram below title.'};write(B/'review-evidence.json',report)
 batch=R/'production/batches/game-math-remaining-20261104';wp=R/'shared/publishing/video-worklist.json'
 paths={'technicalQa':str(W/'final-qa/report.json'),'contentReview':str(W/'content-review.json'),'sphereEvidence':str(B/'review-evidence.json'),'sceneCatalog':str(B/'scene-catalog.json')}
 stamp=now()
 data=read(batch/'batch.json');item=next(r for r in data['items'] if r['id']=='M21');item.update(outputs=out,outputCandidatesAvailable=True,status='media-generated-internal-review-pending',humanReviewed=False,localReviewReady=False);item['evidence'].update(paths);write(batch/'batch.json',data)
 data=read(wp);r=next(x for x in data['rows'] if x['id']=='M21');r.update(productionStatus=STATUS,reviewStatus='연속 청취·사용자 시청 전',productionComplete=False,localMasterAvailable=True,notes='M21 v5 로컬 자막본과 일반본 재생 가능. 기존 79문단 음성과 게임 7컷 유지. 연속 청취·사용자 확인 전.');write(wp,data)
 cp=P/'production/checkpoint.json';j=read(cp);j.update(updatedAt=stamp,stage=STATUS,outputsReady=True,outputCandidates=out,localReviewReady=False,humanReview=False,nextAction='Review continuous listening and user feedback on v5; no platform mutation.');j['evidence'].update(paths);write(cp,j)
 ledger=P/'production/review-ledger.json';j=read(ledger);key='m21-sphere-v5';j['checks']=[x for x in j['checks'] if x.get('id')!=key]+[dict(id=key,at=stamp,masterSha256=files['captioned']['sha256'],evidence=paths,scope='Both full files decoded, original audio hash preserved, mobile/normal/sun/reflection movement and browser seeks checked. No claim of continuous listening.',humanReview=False)];j.update(updatedAt=stamp,humanReview={'status':'v5-local-preview-available-not-human-reviewed'});write(ledger,j)
 doc=R/'docs/VIDEO_WORKLIST.md';txt=doc.read_text(encoding='utf-8-sig');txt=re.sub(r'^\| M21 \|.*$',f"| M21 | 빛과 셰이딩 | ☐ {STATUS} | ☐ {r['reviewStatus']} | {r['platformStatus']} |",txt,flags=re.M);txt=re.sub(r'^\| M21 [^|]+ \|.*$',f"| M21 빛과 셰이딩 | {r['notes']} |",txt,flags=re.M);doc.write_text(txt,encoding='utf-8')
 doc=batch/'progress.md';txt=doc.read_text(encoding='utf-8');doc.write_text(re.sub(r'^\| M21 \|.*$',f'| M21 | 빛과 셰이딩 | {STATUS} | 연속 청취 남음 | [로컬 수정본 보기](http://127.0.0.1:9347/output/{DEST.name}/index.html) |',txt,flags=re.M),encoding='utf-8')
 hub=R/'output/game-math-remaining-20261104/index.html';txt=hub.read_text(encoding='utf-8');txt=re.sub(r'<tr><td>M21</td>.*?</tr>',f'<tr><td>M21</td><td>빛과 셰이딩<br><a href="../{DEST.name}/index.html">수정본 재생</a></td><td>{STATUS}</td><td>{r["reviewStatus"]}</td></tr>',txt,count=1);hub.write_text(txt,encoding='utf-8')
if __name__=='__main__':run()
