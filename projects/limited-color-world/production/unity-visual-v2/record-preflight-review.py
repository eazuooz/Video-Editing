from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4]
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
for slug in ['limited-color-world','computer-controlled-players']:
 q=M/slug/'qa/preflight-v2';cuts=json.loads((q/'sheet-index.json').read_text('utf-8'))['cuts']
 files=[{'path':str(q/(c+'-375.jpg')),'sha256':hashlib.sha256((q/(c+'-375.jpg')).read_bytes()).hexdigest()} for c in cuts]
 result={
  'slug':slug,'stage':'native-preflight-v2','currentSourceApproval':False,
  'allCompletedCutTemporalSamplesDirectlyViewed':True,'cutIds':cuts,'samplesPerCut':7,
  'mobileWidths':[375],'boards':files,'nativeFullSizeDirectViews':(['cut004/frame-00333.png','cut015/frame-00145.png'] if slug=='limited-color-world' else []),
  'observations':[
   'Actual imported characters, forest and chest assets render with textures/materials and readable shapes.',
   'Colour/contrast/pattern examples visually change the narrated property; generic blocks are the actual named teaching object, not substitutes for people.',
   'Fixed caption area below892px remains clear in preflight sample views.',
   'Runtime build was stale: D26cut009 screenshot/animationreceipt still contains old 방어/FightM_Hit_A while disk code says 반응/Fight_Punch_A. Parent requested explicit refresh/compile-finished before v3 all23cuts.',
   'D25cut030 treetops overlap subtitle; removed redundant subtitle in source.',
   'D26cut017 arbitrary chest standing for action selection replaced with actual miniature opponent performing an attack in the same process region.'
  ],
  'next':'Inspect current-compiled v3 native captures; no current-source final QA or render approval inferred from stalev2 pixels.',
  'humanFullListeningOrViewingClaimed':False,
 }
 (R/'projects'/slug/'production/unity-visual-v2/preflight-v2-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
