"""Record only directly inspected selected source samples; final episode stays pending."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def write(p,v):
 assert not p.exists(),str(p)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
sets=[]
for version,limit in [(136,lambda f:f<1926),(139,lambda f:f>=1100),(143,lambda f:True)]:
 p=ROOT/f'production/research/game-lighting-history/local/guided-source-qa-v{version}/execution.json'
 j=read(p);boards=[b for b in j['boards'] if any(limit(f) for f in b['frames'])]
 for b in boards:
  assert sha(ROOT/b['path'])==b['sha256']
 sets.append({'extraction':ref(p),'selectedBoards':[{**b,'directlyViewed':True,'selectedFrames':[f for f in b['frames'] if limit(f)]} for b in boards], 'selectedImages':[{'path':x['path'],'sha256':x['sha256'],'frame':x['frame'],'source':x['source'],'directlyViewed':True} for x in j['items'] if limit(x['frame'])]})
value={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'Five selected black projected explanation sources only; v135 appearance first1926, v138 retained focus1100–3280, v142 repaired focus0–1100', 'sampleSets':sets,'observations':['Projected top/side faces and occlusion retained, red observation arrows reveal in narration order.','v140 raised the yellow transition label above the reference-position plate; all v143 clean and captioned boards directly read with clearance.','All selected Korean cue samples retain960,970 square white boxes and forest offset shadow; no detected diagram/caption overlap.','Adjacent centisecond subtitle boundaries can retain a prior cue for one frame; no zero-frame boundary claim.'], 'selectedSourceSamplePixelsAccepted':True,'allSourceMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','newGitImages':0}
write(P/'guided-selected-source-sample-review-v144.json',value)
p=read(P/'selected-part3-source-plan-v141.json')
row=next(x for x in p['rows'] if x['id']=='hogwarts-courtyard-ui')
row['proposedCuts']=[{'inFrame':9660,'outFrame':10610,'nativeSeconds':[161,176+50/60]}]
row['rejectedNativeStart']={'seconds':160,'reason':'CUA normal-speed first frame directly showed a presenter/game cross-dissolve; native161 is clear gameplay.'}
p['preparedAt']=datetime.now(timezone.utc).isoformat();p['prior']=ref(P/'selected-part3-source-plan-v141.json');p['sourcePixelReview']=ref(P/'guided-selected-source-sample-review-v144.json')
p['status']='Court transition removed; exact allocation and full PCM preserved; final episode pixels and mixed audio pending'
write(P/'selected-part3-source-plan-v144.json',p)
rows=[{'id':'appearance-selected','path':'production/research/game-lighting-history/local/episode04-guided-source-review-v135/guided-source.captioned.mp4','ranges':[[0,1926/60]],'ko':'선택한 두 설명: 네 게임 비교 전제 → 설정과 프레임 검사 연결'}, {'id':'focus-retained-selected','path':'production/research/game-lighting-history/local/episode04-guided-source-review-v138/guided-source.captioned.mp4','ranges':[[1100/60,3280/60]],'ko':'선택한 두 설명: 관찰 조건 → 프레임 검사'}, {'id':'focus-label-current','path':'production/research/game-lighting-history/local/episode04-guided-source-review-v142/guided-source.captioned.mp4','ranges':[[0,1100/60]],'ko':'교정한 거리 영역과 기준 위치의 이름표 간격'}]
html=(ROOT/'production/research/game-lighting-history/local/selected-part3-native-review-v141.html').read_text('utf-8')
a=html.index('<script>const rows=');z=html.index(';const pick=',a)
html=html[:a]+'<script>const rows='+json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')+html[z:]
write(ROOT/'production/research/game-lighting-history/local/selected-guided-motion-review-v144.html',html)
print(json.dumps({'selectedBoards':sum(len(x['selectedBoards']) for x in sets),'finalApproved':False,'bodyFrames':p['part3']['bodyFrames']}))
