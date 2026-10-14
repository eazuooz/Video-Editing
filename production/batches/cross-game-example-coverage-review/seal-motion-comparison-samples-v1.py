import json, hashlib, os
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path('D:/Github/Video-Editing'); R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((R/'narration-timed-comparisons-qa-v1.json').read_text(encoding='utf-8-sig'))
checks=q['boards']+q['samples'] if 'samples' in q else q['boards']+[s for b in q['boards'] for s in b['samples']]
seen={}
for x in checks:
 p=ROOT/x['path']; assert sha(p)==x['sha256'],p; seen[x['path']]=x['sha256']
out={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'qaEvidence':'narration-timed-comparisons-qa-v1.json','actualRenderSession':27660,'actualRenderExitCode':0,'actualRenderCompletion':'259ed5','actualQaCompletion':'0e812a','actualQaExitCode':0,'directlyReadBoards':13,'directlyReadEncodedSamples':50,'sha256RecheckedFiles':seen,'findings':{'07b-role':'All ten samples: fixed held cube versus turning projected room; moving red tool over stable left panel. Labels and reserved caption area clear.','07b-limit':'All ten samples: red connection revealed toward blue wall cue; caution appears after relation; projected front/top/side visible.','08b-intro':'All ten samples: projected floor and door; yellow selection marker advances after prerequisite introduction; labels remain above caption reserve.','08b-arrival':'All ten samples: yellow destination arrow progresses then room/cube changes to arrival; blue wall cue label fades in at later samples without overlap. Long yellow leader is explanatory geometry, not measured travel path.','08b-limit':'All ten samples: two separated projected examples; blue direction arrow and yellow object change late, distinguishing orientation observation from individual reaction.'},'sampledNarrationTimedMovingPixelReview':True,'allIntermediateFramesRead':False,'normalPlaybackReviewed':False,'humanListeningApproved':False,'finalCueApproval':False,'allFinalPixelsApproved':False,'localOnly':True}
(R/'narration-timed-comparisons-sampled-direct-review-v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=ROOT/'shared/assets/presenting-game-scores/raw'
ids=['07b-role','07b-limit','08b-intro','08b-arrival','08b-limit']
for i in ids:
 src=ROOT/f'shared/output/cross-game-example-coverage/motion/narration-timed-comparisons-v1/scene-{i}.mp4'; dst=raw/f'motion-comparison-{i}-v1.mp4'
 if dst.exists(): assert os.path.samefile(src,dst)
 else: os.link(src,dst)
src=ROOT/'shared/assets/game-footage/motion-sickness-games/PF5L_2g9UVQ.mp4';dst=raw/'motion-powerwash-additional-native-v1.mp4'
if dst.exists(): assert os.path.samefile(src,dst)
else: os.link(src,dst)
buttons=''.join(f'<button data-id="{i}" data-src="motion-comparison-{i}-v1.mp4" data-start="0">Prepare {i}</button>' for i in ids)
buttons+='<button data-id="PowerWash69-90.5" data-src="motion-powerwash-additional-native-v1.mp4" data-start="69" data-stop="90.5">Prepare PowerWash69-90.5</button><button data-id="PowerWash115-132" data-src="motion-powerwash-additional-native-v1.mp4" data-start="115" data-stop="132">Prepare PowerWash115-132</button>'
html='''<!doctype html><meta charset="utf-8"><title>Motion measured comparisons and unused native candidates</title><style>body{background:#111;color:#eee;font:17px sans-serif;margin:16px}video{width:min(100%,1100px);display:block}button{padding:10px;margin:4px}</style><h1>Measured explanation parts and unused native source candidates · silent1×</h1><p>Source planning and bounded motion review only. No final captions/audio/ratio approval.</p>'''+buttons+'''<button id="play">Play at1×</button><button id="pause">Pause</button><video id="v" muted controls preload="metadata"></video><pre id="state"></pre><script>const v=document.querySelector('#v'),s=document.querySelector('#state');let id='',start=0,stop=null;function report(){s.textContent=JSON.stringify({id,currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate,start,stop},null,2)}document.querySelectorAll('[data-src]').forEach(b=>b.onclick=()=>{v.pause();id=b.dataset.id;start=Number(b.dataset.start);stop=b.dataset.stop?Number(b.dataset.stop):null;v.src=b.dataset.src;v.playbackRate=1;v.muted=true;v.load();report()});v.onloadedmetadata=()=>{v.currentTime=start;report()};v.ontimeupdate=()=>{if(stop!==null&&v.currentTime>=stop){v.pause()}report()};v.onseeked=report;v.onplay=report;v.onpause=report;v.onended=report;document.querySelector('#play').onclick=()=>v.play();document.querySelector('#pause').onclick=()=>v.pause();</script>'''
(raw/'motion-comparison-native-review-v1.html').write_text(html,encoding='utf-8')
print(json.dumps({'sealedBoards':13,'sealedSamples':50,'uniqueHashChecks':len(seen),'hardlinks':6,'htmlPrepared':True}))
