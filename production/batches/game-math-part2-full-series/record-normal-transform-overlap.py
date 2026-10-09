"""Keep actual native/whole-script comparisons while the preceding episode renders."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proofroot=R/'shared/output/game-math-part2-full-series/normal-transform-preflight'
uv=proofroot/'studio-current-uv-title.ax.txt';normal=proofroot/'studio-current-normal-title.ax.txt'
assert '-3NQEd_8mWg' in uv.read_text(encoding='utf8') and '일치하는 동영상이 없습니다.' in normal.read_text(encoding='utf8')
legacy=read(B/'preflight/mesh-uv-content-duplicate-review.json')['legacy']
comparisons={
 'game-math-mesh-uv':'All16 full current paragraphs reviewed. Storage,normal construction,interpolation,sharp edges and weights finish here; inverse-transpose is only the next-episode promise. Keep the original algorithm complete.',
 'game-math-projection-depth':'Complete prior script reviewed. Perspective-correct interpolation is a named prerequisite; do not repeat its complete w/depth derivation. New numerical failure wraps UV endpoints before interpolating,which is a different question.',
 'game-lighting-history-02':'Entire scene11m directly read:normal mapping changes lighting direction,parallax changes lookup,displacement changes geometry and SSS changes transport position. Does not derive inverse-transpose or floor-repeat lookup after UV interpolation.',
 'game-lighting-history-03':'Entire scene16ab directly read:mesh shaders,VRS,virtual texture residency and sampler feedback have distinct budgets. Does not teach per-surface mapping coordinates or normal/tangent perpendicularity.',
 'yamyam-dx12-texture-views':'Full scenes03–05 directly read:CPU upload,state transitions,resource/view/descriptor identity and b0/t0/s0 binding. The sampler sentence is a prerequisite,not a derivation of UV interpolation/address ordering or inverse-transpose.'
}
record={'status':'content-and-native-overlap-preparation-current-episode-not-yet-delivered','preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'game-math-normal-transform-uv','candidateSha256':sha(B/'candidates/game-math-normal-transform-uv.json'),'lessonSha256':sha(B/'lessons/game-math-normal-transform-uv.json'),'inventoryCount':len(read(R/'production/preflight/game-math-normal-transform-uv.json')['existingProjects']),'nativeProofs':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in [uv,normal]],'legacy':legacy,'comparisons':[{'slug':slug,'scriptSha256':sha(R/f'projects/{slug}/script/narration.ko.json'),'reason':note} for slug,note in comparisons.items()],'question':'Preserve transformed tangent-normal perpendicularity and sample the mapped image only after interpolating unmodified UV coordinates.','newWorkedValues':['diag(2,1): naive dot3 versus inverse-transpose dot0','repeat(-0.75)=0.25 using floor(-0.75)=-1','UV0→2 retains two tiles; wrapping endpoints first collapses both to0'],'officialCurrentPreflightCheck':'pending-after-current-episode-private-and-Git-delivery','newProjectCreated':False,'ttsStarted':False,'preserveOlderUploads':True}
(B/'preflight/normal-transform-uv-content-review-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('51-project inventory and actual nativeUV/normal search preparation saved; creation/TTS remain sequential.')
