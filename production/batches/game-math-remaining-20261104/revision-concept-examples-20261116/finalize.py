"""Register only the verified finite M21–M33 local revision."""
import datetime,html,re
from html.parser import HTMLParser
from prepare import *
from review import OUT,pages,duration
KEY='conceptExamplesRevision20261116'
def block(path,text):
 start='<!-- MATH-CONCEPT-EXAMPLES-20261116-START -->';end='<!-- MATH-CONCEPT-EXAMPLES-20261116-END -->';current=path.read_text(encoding='utf-8-sig');new=start+'\n'+text.strip()+'\n'+end
 if start in current:current=current[:current.index(start)]+new+current[current.index(end)+len(end):]
 else:current=current.rstrip()+'\n\n'+new+'\n'
 path.write_text(current,encoding='utf8')
def main():
 plan=read(HERE/'plan.json');visual=read(HERE/'visual-review.json');assert visual['allFinalEncodedSamplesReviewed'] and len(visual['episodes'])==13
 cont=read(HERE/'continuity.json');assert len(cont['episodes'])==13
 visual_by={r['id']:r for r in visual['episodes']};cont_by={r['id']:r for r in cont['episodes']}
 voice=read(HERE/'voice.json');assert all(v['qualityPassed'] for v in voice['items'])
 alignment=read(HERE/'bridge-review.json');assert alignment['allSelectedNewBridgeTextReviewed']
 words=read(HERE/'alignment.json')['items'];voices={v['key']:v for v in voice['items']}
 assert read(HERE/'source-audio-residual-review.json')['reviewed']
 rows=[];preserved=[];episodes=[]
 for e in plan['episodes']:
  d=read(HERE/'deliveries'/(e['id']+'.json'))
  assert visual_by[e['id']]['masterSha256']==d['files']['captioned']['sha256'] and visual_by[e['id']]['passed']
  assert cont_by[e['id']]['masterSha256']==d['files']['clean']['sha256']
  assert len(d['inserts'])==len(e['inserts'])
  for current,encoded in zip(e['inserts'],d['inserts']):
   assert all(current[k]==encoded[k] for k in ('key','source','sourceIn','sourceOut','atFrame','ko','en')),('stale scene selection',e['id'],current['key'])
   k=current['key'];assert words[k]['rawAudioSha256']==voices[k]['rawSha256']==alignment['items'][k]['rawAudioSha256'] and words[k]['voiceSha256']==voices[k]['sha256']
  for kind,f in e['baselineFiles'].items():
   assert sha(f['path'])==f['sha256'],('accepted master changed',e['id'],kind);preserved.append(dict(id=e['id'],kind=kind,**f,unchanged=True))
  assert all(sha(x['path'])==x['sha256'] for x in d['files'].values())
  d.update(status='local-user-review-pending',technicalQa=True,encodedTemporalVisualQa=True,originalVoiceContentAndPacePreserved=True,newBridgeOnly=True,humanReviewed=False)
  save(HERE/'deliveries'/(e['id']+'.json'),d);episodes.append(d)
  rows.append(dict(id=e['id'],title=e['title'],status='내부 검수 완료 · 사용자 검수 대기',files=d['files'],newExamples=len(d['inserts']),addedSeconds=d['addedFrames']/60,technicalQa=True,visualQa=True,humanReviewed=False,reviewPage=str(OUT/e['id']/'index.html')))
  p=ROOT/'projects'/e['slug']/'production/review-ledger.json';j=read(p);j[KEY]=rows[-1];save(p,j)
 save(HERE/'baseline-preservation.json',dict(all52AcceptedFilesUnchanged=True,files=preserved))
 state=dict(scope=[e['id'] for e in episodes],status='all-thirteen-local-user-review-pending',encodedCount=13,localReadyCount=13,rows=rows,reviewHub=str(OUT/'index.html'),newExamples=sum(len(e['inserts']) for e in episodes),retainedNonduplicatedFollowingCases=sum(len(e.get('retainedExistingCases',[])) for e in plan['episodes']),humanReviewed=False,upload=False,platformChanged=False)
 p=ROOT/'shared/publishing/video-worklist.json';j=read(p);j['mathConceptExamples20261116']=state
 by={r['id']:r for r in rows}
 for r in j['rows']:
  if r['id'] in by:r[KEY]=by[r['id']]
 save(p,j)
 p=ROOT/'shared/publishing/video-production-control.json';j=read(p);child=j['explicitMathRemainingBatch20261104'][KEY];child.update(status=state['status'],encodedCount=13,localReadyCount=13,renderAuthorized=False,ttsAuthorized=False,costlyJobsClosed=True,reviewHub=state['reviewHub'],newExamples=state['newExamples'],humanReviewed=False);save(p,j)
 rules='''### 개념 설명 뒤 실제 게임 관찰 (2026-11-16)
핵심 개념의 설명과 계산이 끝나면 그 개념을 실제 움직임에서 확인하는 게임 예시로 연결한다. 짧은 자연스러운 전환 해설로 무엇을 볼지 먼저 짚고, 관찰할 대상·동작·결과가 실제 녹화에 있는지 시간 순서로 검수한다. 설명 뒤에 적합한 기존 사례가 이미 있으면 살려 쓰고, 바로 같은 동작을 복제해 붙이지 않는다. 설명용 모형의 공식·벡터를 게임 내부에서 측정한 값처럼 주장하지 않는다. 필요한 관찰 표식만 정확한 대상에 붙이고 원래 HUD·동작을 가리지 않는다. 정지·반복·배속으로 시간을 채우지 않으며, 실제 동작의 시작과 결과가 보이는 길이를 사용한다. 기존 승인된 설명·음성과 발화 순서는 보존하고 이번 요청에 필요한 연결 문장만 같은 승인 목소리로 추가한다. 추가 길이만큼 모든 후속 영상·한영 자막을 함께 옮기고, 연결부 음량·발음·프레임 시계·자막 동기를 실제 출력으로 검사한다. 강의용 별도 배경음악은 추가하지 않고 확보된 동일 녹화의 게임 원음을 기존 믹스 기준으로 유지한다. M21–M33 총13편은 로컬 내부 검수 후 사용자 검수 대기이며 업로드·예약·기존 게시물 변경 허가는 아니다.'''
 block(ROOT/'docs/VIDEO_WORKFLOW.md',rules)
 table=['### 게임수학 M21–M33 · 설명 뒤 실제 게임 예시 보충','',f'[전체 검수표]({OUT.as_posix()}/index.html) · 새 관찰 구간 {state["newExamples"]}곳. 적합한 기존 후속 사례 5곳은 중복 삽입 없이 보존.','', '| 번호 | 강의 | 새 예시 | 전체 길이 | 상태 |','|---|---|---:|---:|---|']
 for e,r in zip(episodes,rows):table.append(f'| {e["id"]} | [{e["title"]}]({OUT.as_posix()}/{e["id"]}/index.html) | {r["newExamples"]} | {duration(e["duration"])} | 사용자 검수 대기 |')
 block(ROOT/'docs/VIDEO_WORKLIST.md','\n'.join(table))
 save(HERE/'delivery.json',dict(**state,episodes=episodes,all52PreviousAcceptedFilesUnchanged=True,at=datetime.datetime.now().astimezone().isoformat()))
 save(HERE/'checkpoint.json',dict(status=state['status'],encodedCount=13,localReadyCount=13,reviewHub=state['reviewHub'],costlyJobsClosed=True,upload=False,humanReviewed=False))
 pages();(OUT/'CREDITS.html').write_text('<meta charset="utf-8"><pre style="white-space:pre-wrap">'+html.escape((HERE/'CREDITS.md').read_text(encoding='utf8'))+'</pre>',encoding='utf8')
 class Links(HTMLParser):
  def __init__(self):super().__init__();self.urls=[]
  def handle_starttag(self,tag,attrs):self.urls += [v for k,v in attrs if k in ('href','src') and v]
 checks=[]
 review_pages=[OUT/'index.html',OUT/'CREDITS.html',*[OUT/e['id']/'index.html' for e in episodes]]
 for page in review_pages:
  parser=Links();parser.feed(page.read_text(encoding='utf8'))
  for url in parser.urls:
   if url.startswith(('http:','https:','#','data:')):continue
   dest=(page.parent/url.split('#')[0]).resolve();assert dest.exists(),(page,url,dest);checks.append(dict(page=str(page),url=url,exists=True))
 save(HERE/'local-links.json',dict(status='passed',reviewPages=len(review_pages),checks=checks));print('Final local deliveries registered:',len(episodes),'episodes /',state['newExamples'],'new observations')
if __name__=='__main__':main()
