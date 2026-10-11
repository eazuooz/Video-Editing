"""Record native comparison decisions; shorten distracting Noita boundaries."""
from pathlib import Path
import copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
data=read(R/'polygon-cross-game-content-v4.json')
s=next(s for s in data['scenes'] if s['id']=='QG08')
s['intervals'][0]=[453,467];s['maximumSeconds']=28;s['sourceSegments'][0].update({'in':453,'maxSeconds':14})
write(R/'polygon-cross-game-content-v4.json',data)
decisions={
 'noita-center-gap':{'chosen':[453,467],'rejected':[[451,453],[467,469]],'reason':'Character moving beside an exposed right ledge. Intro fight particles and later explosion excluded. Distinguishes reference point and physical edge; lower/right empty gap remains visible.','before':'Character approaches a ledge beside a rock opening.','action':'Character descends/moves through the adjacent space.','after':'Empty passage remains separate from solid rock.','camera':'Vertical 2D scroll; track terrain with native observations; hide obstruction/cuts.','densePagesSeen':4},
 'noita-center-return':{'chosen':[788,802],'reason':'Down/up navigation demonstrates that a concave opening is traversable; one continuous source, no loop. Actor combat is separate from the boundary claim.','before':'Character above the notch.','action':'Descends then returns alongside the same opening.','after':'The passage stays empty and the character can pass.','camera':'Scrolling reference frame; right-rock edge clear at794–798.','densePagesSeen':3},
 'dorf-placement':{'chosen':[],'rejected':[[0,14.8]],'reason':'Intro is scenic montage, insufficient mathematical action. Placement15–17 too short for this new voice.'},
 'dorf-connected-edge':{'chosen':[],'rejected':[[82,89.5]],'reason':'Readable placement, but already the second original clip in this episode; prefer a fresh segment.'},
 'dorf-convex-versus-union':{'chosen':[[90,107],[116,123]],'rejected':[[107,116]],'reason':'Actual tile placement and separate undo expose outline change. Train/boat cinematic excluded. Different regional cuts announced as independent examples; no identical before/after claim across a cut.','before':'Empty grid slot beside placed hexagons.','action':'Tile placed, or previously placed tile undone in a separate shot.','after':'Combined land outline differs; individual tile and union differ.','camera':'Top oblique game view; border changes need tracked distinct cut observations; no engine geometry inferred.','densePagesSeen':6},
 'shapez-square-cut':{'chosen':'Pending final cut alignment and semantic color review','rejected':[[39.5,41.1],[41.3,43]],'reason':'Throughput counter/paint montage precedes very brief square cutting43–44.4; these cannot be labeled cutting. New factory prerequisite and processing-versus-partition comparison do not by themselves approve this shot.','densePagesSeen':2}
}
write(R/'polygon-native-candidate-decisions-v4.json',{'createdAt':datetime.datetime.now().astimezone().isoformat(),'normalSpeedProofs':['first-candidate-native-proof.json','noita-candidate-native-proof.json'],'decisions':decisions,'finalPixelsApproved':False})
history=read(ROOT/'shared/output/gpu-handoff/1478780c-5a58-4a90-a058-37d998f9feff.json')
assert history['ttsExitCode']==0 and history['state']=='research_resume_verified'
assert history['resumedQueue']['command']==history['queueOwner']['command'] and history['resumedQueue']['cwd']==history['queueOwner']['cwd']
write(R/'polygons-v4-gpu-handoff-result.json',{'token':history['token'],'evidence':'shared/output/gpu-handoff/'+history['token']+'.json','ttsExitCode':0,'state':history['state'],'resumedStatus':history['resumedStatus'],'sameCommandAndWorkingDirectory':True,'researchStatusAtVerification':'waiting_for_resources for another task; subsequent foreign handoff kept separate','optimizerRngResumeClaimed':False})
print('Selected/rejected intervals and completed cooperative GPU restoration recorded.')
