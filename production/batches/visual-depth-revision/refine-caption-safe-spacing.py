from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
changes={'motion-sickness-games':('[0,70],.76','[0,40],.70'),'hierarchical-game-outlines':('[0,75],.70','[0,40],.62'),'game-reward-planning':('[0,65],.74','[0,30],.68'),'making-game-sequels':('[0,65],.76','[0,30],.68'),'familiar-game-rules':('[0,65],.76','[0,30],.68')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for slug,(old,new) in changes.items():
 p=ROOT/'motion-canvas/src/projects'/slug/'depth-explanations-v1.tsx';folder=ROOT/'projects'/slug/'production/visual-depth-v1';history=folder/'depth-explanations-caption-safe-v2.tsx'
 if history.exists():raise RuntimeError('Preserve earlier refinement')
 s=p.read_text('utf-8-sig')
 if s.count(old)!=1:raise RuntimeError('Exact project-local projection expected')
 history.write_bytes(p.read_bytes());p.write_text(s.replace(old,new),'utf-8')
 record=folder/'caption-safe-repair-request.json';r=json.loads(record.read_text('utf-8-sig'));r['spacingRefinement']=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Motion v2 captioned preflight directly read: secondary role labels need a visible gap below the projected floor. Remaining similar wide-base sources corrected preventively before rendering.',old=old,new=new,previousSource=history.relative_to(ROOT).as_posix(),previousSourceSha256=sha(history));r.update(sourceSha256=sha(p),revision='v3',preflightPixelsApproved=False,allFinalPixelsReviewed=False);record.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(slug+' v3 spacing prepared; no final approval')
