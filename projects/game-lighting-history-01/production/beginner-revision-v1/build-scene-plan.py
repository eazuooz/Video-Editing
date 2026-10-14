"""Bind existing spatial/math demonstrations to directly reviewed sentence edges."""
import pathlib,json,math,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (H/'measured-scene-plan.json').exists(),'Inspect the current locked scene plan rather than overwriting it'
 a=rd(O/'voice-alignment-proposal.json');review=rd(H/'voice-direct-review.json')
 assert review['all52WholeTextsDirectlyCompared'] and review['contentCoverageApproved']
 assert review['alignmentSha256']==sha(O/'voice-alignment-proposal.json') and review['allSentenceBoundariesDirectlyReviewed']
 assert not a['issues'],a['issues']
 rows={r['key']:r for r in rd(H/'changes.json')['rows']};speech={r['key']:r for r in a['rows']};design=rd(H/'semantic-motion-design.json')
 baseline=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json')
 explanationKeys={v['key'] for v in baseline['voice'] if any(n['role']=='explanation' and max(v['startFrame'],n['startFrame'])<min(v['startFrame']+v['samples']/400,n['endFrame']) for n in baseline['nodes'])}
 result=[];actualOnly=[]
 for d in design['rows']:
  key=d['key'];s=speech[key];assert sha(R/s['audioPath'])==s['audioSha256']
  if key not in explanationKeys:
   actualOnly.append(dict(key=key,reason='Narration remains over independently obtained native footage; do not render an unused explanation scene.'))
   continue
  begin,end=d['actionSentenceSpan'];assert 0<=begin<=end<len(s['sentences']),key
  frames=max(math.ceil(s['samples']/400),math.ceil(rows[key]['baselineSpeechSeconds']*60))
  start=max(0,round(s['sentences'][begin]['seconds'][0]*60));finish=min(frames-1,round(s['sentences'][end]['seconds'][1]*60));assert finish>start
  stages=[0]
  if key.startswith('09b-'):
   # Visible surface, stored input, and subsequent lighting are introduced
   # at actual sentence starts, not equal thirds of the scene duration.
   indices=d['stageSentenceIndices']
   assert len(indices)==3 and indices==sorted(indices) and indices[-1]<len(s['sentences']),key
   stages=[round(s['sentences'][i]['seconds'][0]*60) if i else 0 for i in indices]
  cues=[dict(text=c['text'],startFrame=round(c['seconds'][0]*60),endFrame=round(c['seconds'][1]*60)) for c in s['koCues']]
  result.append(dict(key=key,renderer=d['renderer'],frames=frames,audioSamples=s['samples'],audioSha256=s['audioSha256'],actionStartFrame=start,actionEndFrame=finish,stageFrames=stages if key.startswith('09b-') else None,previewCues=cues,semanticSentenceSpan=[begin,end],implementationNote=rows[key]['sceneDesign']['implementationKind'],allMovingPixelsReviewed=False))
 out=dict(schemaVersion=1,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scenes=result,actualOnlyNarration=actualOnly,currentVoiceReviewed=True,sentenceBoundariesDirectlyReviewed=True,voiceReviewSha256=sha(H/'voice-direct-review.json'),alignmentSha256=sha(O/'voice-alignment-proposal.json'),designSha256=sha(H/'semantic-motion-design.json'),finalEditTimingApproved=False,finalOutputApproved=False)
 (H/'measured-scene-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(scenes=len(result),frames=sum(x['frames'] for x in result),finalEditTimingApproved=False)))
if __name__=='__main__':main()
