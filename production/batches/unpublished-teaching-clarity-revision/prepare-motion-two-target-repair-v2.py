from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
MC=ROOT/'motion-canvas/src/projects/motion-sickness-games/teaching-clarity-v1'
old=MC/'goal-cues-explanation.tsx';new=MC/'goal-cues-explanation-v4.tsx'
assert not new.exists()
content=old.read_text('utf-8').replace('[-100, 55], .9','[-100, 45], .86').replace('[-430, 224]','[-430, 205]').replace('y={235}','y={210}').replace('y={295}','y={270}').replace('y={350}','y={320}')
assert content!=old.read_text('utf-8');new.write_text(content,'utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[{'id':'02','source':(MC/'scene02-explanation-v2.tsx').relative_to(ROOT).as_posix(),'frames':2338},
 {'id':'06b','source':new.relative_to(ROOT).as_posix(),'frames':403}]
for x in sources:x['sha256']=sha(ROOT/x['source'])
plan={'schemaVersion':1,'status':'prepared-two-target-repair-only','sourceHeldReview':'final-pixel-direct-review-v1.json','sources':sources,
 'originalDepthSourcePreservedSha256':sha(ROOT/'motion-canvas/src/projects/motion-sickness-games/depth-explanations-v1.tsx'),
 'originalGoalV3SourcePreservedSha256':sha(old),'framesOrAudioOrCaptionsChanged':False,
 'scene02':'Early body comparison stays; before paragraph4 right transitions to extra camera shake, left remains necessary viewpoint rotation. Body is never shaken.',
 'scene06b':'Reduce projection and raise floor label/footer/disclaimer; fixed 960,970 caption remains.',
 'newTts':0,'newAsr':0,'finalPixelsApproved':False,'humanListeningApproved':False}
p=R/'targeted-visual-repair-plan-v2.json';assert not p.exists();p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'targetFrames':[2338,403],'baselineSourcesUnmodified':True}))
