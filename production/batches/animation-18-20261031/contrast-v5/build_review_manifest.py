"""Publish a local review inventory only when all17 exact outputs exist."""
from pathlib import Path
import hashlib,json,html
H=Path(__file__).resolve().parent;R=H.parents[3];OUT=Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];ids=c['episodes'];assert len(ids)==17 and 'A03'not in ids
 summaries={e['id']:e for e in read(H/'footage/source-summary.json')['records']};records=[]
 actual={e['episode']:e for e in read(H/'footage/final-picture-adoption.json')['episodeGames']}
 audio={e['id']:e for e in read(H/'local/final-audio/audio-preparation.json')['episodes']}
 for ep in ids:
  d=read(OUT/ep/'delivery.json');assert d['localFinalFilesReady']and not d['humanReviewed']
  assert {f['kind']for f in d['files']}=={'captioned.mp4','clean.mp4','ko.srt','en.srt'}
  for f in d['files']:assert sha(f['path'])==f['sha256'],(ep,f['kind'])
  master=next(f for f in d['files'] if f['kind']=='captioned.mp4')
  visual_path=H/'visual-qa'/f'{ep}.json'
  visual=read(visual_path)
  assert visual['status']=='sampled-encoded-visual-qa-passed',(ep,'visual QA pending')
  assert visual['proof']['masterSha256']==master['sha256'],(ep,'stale visual QA')
  expected_readbacks=sum(len(group['placements']) for group in audio[ep]['groups'])
  readback_summary={'checkedPassages':expected_readbacks,'transcriptionDifferences':[]}
  if expected_readbacks:
   encoded_audio=read(H/'local/asr-final-aac/episodes'/f'{ep}.json')
   assert encoded_audio['proof']['masterSha256']==master['sha256'],(ep,'stale encoded audio readback')
   assert encoded_audio['allChangedPassagesReadBack'] and len(encoded_audio['entries'])==expected_readbacks
   readback_summary['transcriptionDifferences']=[
    {'sentenceId':entry['sentenceId'],'expected':entry['expected'],'recognized':entry['recognized'],
     'seconds':entry['startSample']/entry['sampleRate']}
    for entry in encoded_audio['entries'] if not entry['comparison']['acceptedSemanticReadback']
   ]
  d['sampledVisualReview']={'path':str(visual_path),'sha256':sha(visual_path)}
  d['encodedAudioReadback']=readback_summary
  d['pictureMetrics']=read(H/'picture-metrics'/f'{ep}.json')
  captionReview=read(H/'local/final-audio'/ep/'captions/review.json');assert not captionReview['fallbackPassages']
  d['gameExamples']=[q['gameAndEdition']for q in actual[ep]['meaningfullyShownUniqueGames']]
  integration=H/'renderer/integration-caption-safe.json'
  if not integration.exists():integration=H/'renderer/integration-manifest.json'
  edl=read(H/'local/explanation-assembly'/ep/'edl.json');assert edl['integrationManifestSHA256']==sha(integration)
  correction=H/'visual-corrections'/(ep+'.json')
  if correction.exists():assert (edl.get('visualCorrection')or{}).get('sha256')==sha(correction),'Latest visual correction missing'
  inter=next(e for e in read(integration)['episodes']if e['id']==ep)
  for g in audio[ep]['groups']:
   assert g.get('technicalMixVerified'),(ep,g['id'],'speech verification pending')
   row=next(r for r in edl['audioEdl']if r.get('id')in[g['id'],g['id']+'-audio'])
   assert row['sourceSha256']==g['sourceSha256']==sha(R/g['source']),(ep,g['id'],'stale mix')
   for q in g.get('inputChecks',[]):assert sha(R/q['path'])==q['sha256'],'Changed take after mix'
  signature=read(H/'local/final-encode'/ep/'signature.json')
  assert signature['assSha256']==sha(H/'local/final-audio'/ep/'captions/captions.provisional.ko.ass')
  assert signature['mixSha256']==d['technicalQa']['audioInput']['sha256']==sha(d['technicalQa']['audioInput']['source'])
  def mapped(frame):
   for p in edl['pictureEdl']:
    if p['oldStartFrame']<=frame<p['oldEndFrame']:
     return(p['outputStartFrame']+min(frame-p['oldStartFrame'],p['frames']-1))/60
   raise ValueError(frame)
  points=[{'label':'게임 예시와 도입','seconds':2}]
  if inter.get('preservedRelationRegions'):
   q=inter['preservedRelationRegions'][0];points.append({'label':'핵심 관계도','seconds':mapped(q['outputStartFrame'])})
  demo=next((q for q in inter['rows']if q.get('mode')=='analysis'),None)
  if demo:points.append({'label':'비교 시연','seconds':mapped(demo['relationFrameStart'])})
  for difference in readback_summary['transcriptionDifferences']:
   points.append({'label':'발음 확인','seconds':difference['seconds']})
  d['reviewPoints']=points;d['sourceSummary']=str(H/'footage/source-summary.json');records.append(d)
 preserved=next(e for e in read(H.parent/'relations-v4/review-manifest.json')['records']if e['id']=='A03')
 for f in preserved['files']:
  if f['kind']=='captioned.mp4':assert sha(R/f['path'])==f['sha256']
 manifest={'schemaVersion':1,'revision':'contrast-v5','scope':ids,'records':records,'preservedA03':preserved,'humanReviewed':False,'humanListened':False,'platformChanged':False,'url':'http://127.0.0.1:9294/','outputFolder':str(OUT),'sourcePublicationConditionsRemain':True}
 save(H/'review-manifest.json',manifest);save(OUT/'review-manifest.json',manifest)
 style='<style>body{background:#090e0b;color:#f2f3ed;font:18px/1.6 system-ui;margin:30px auto;padding:0 20px;max-width:1120px}h1{color:#f2d787}a{color:#a7dfbf}section{padding:20px 0;border-top:1px solid #354b3d}video{width:100%;background:#000}nav{display:flex;flex-wrap:wrap;gap:18px}</style>'
 def page(title,body):return '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title>'+style+'<h1>'+html.escape(title)+'</h1>'+body+'</html>'
 cards=[]
 for d in records:
  ep=d['id'];slug=d['slug'];title=ep+' · '+d['title'];links='<nav>'+''.join('<a href="'+slug+'.'+k+'">'+name+'</a>'for k,name in [('captioned.mp4','자막 영상'),('clean.mp4','무자막 영상'),('ko.srt','한국어 자막'),('en.srt','영어 자막')])+'</nav>'
  (OUT/ep/'index.html').write_text(page(title,'<nav><a href="../index.html">전체 목록</a></nav><video controls playsinline preload="metadata" src="'+slug+'.captioned.mp4"></video>'+links),encoding='utf8')
  cards.append('<section><h2><a href="'+ep+'/index.html">'+html.escape(title)+'</a></h2><p>'+html.escape(' · '.join(d['gameExamples']))+'</p><small>1080p60 · 사용자 검수 대기</small></section>')
 (OUT/'index.html').write_text(page('애니메이션 17편 통합 검수','<p>각 편의 전체 자막 영상·무자막 영상·한영 자막을 모았습니다.</p>'+''.join(cards)),encoding='utf8')
 print(json.dumps({'episodes':len(records),'files':sum(len(e['files'])for e in records),'url':manifest['url']},ensure_ascii=False))
if __name__=='__main__':main()
