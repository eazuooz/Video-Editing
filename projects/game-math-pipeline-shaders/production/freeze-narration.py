"""Freeze reviewed M23 wording; picture corrections leave narration unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
assert c['productionAllowedNow'] and P.name in c['projectSlugs']
i=read(P/'planning/script-integration.json');review=i['readThrough'];scripts={l:read(P/f'script/narration.{l}.json') for l in ('ko','en')}
for lang in scripts:assert sha(P/f'script/narration.{lang}.json')==review[lang+'Sha256']
assert review['allBeatsRead'] and review['sourceOrderPreserved']
b=read(P/'planning/scene-bindings.json');p=read(P/'planning/production-plan.json')
assert len(scripts['ko']['scenes'])==len(scripts['en']['scenes'])==len(b['scenes'])==68
assert b['pendingImplementationBeatCount']==0 and p['sourceFinal']
assert [s['id'] for s in scripts['ko']['scenes']]==[s['id'] for s in b['scenes']]
for source in read(P/'planning/footage-audit.json')['sources']:
 assert source['classification']=='independent-gameplay' and min(source['decodedSize'])>=1080
 assert source['recordingPermission'] and (source.get('publisherRights') or source.get('rights')) and (R/source['file']).is_file()
for game in p['nativeGameCueBindings']:
 assert game['playbackRate']==1 and not game['freezePadding'] and not game['loop']
 assert game['nativeDecodeEvidence']['decodeExitCode']==0
assert read(P/'production/unity-staging/compile-check.json')['csharpCompilation']['exitCode']==0
runtime=read(P/'production/unity-staging/local-preflight-v1/progress.json')
assert runtime['status']=='images-ready-for-internal-visual-QA' and len(runtime['completed'])==21
for lang,script in scripts.items():
 script.update(status='frozen-for-approved-voice-production',isFinalNarration=True,actualDurationSeconds=None);save(P/f'script/narration.{lang}.json',script)
 review[lang+'Sha256']=sha(P/f'script/narration.{lang}.json')
review.update(productionDecisionAt=datetime.now(timezone.utc).isoformat(),ttsAuthorizedToStart=True,productionReadiness='Source and unchanged bilingual text checked. V1 pictures inspected; targeted source-order/material/label repairs awaiting V3. No final sound/picture pass claimed.')
i.update(narrationFinal=True,sceneBindingsFinal=True,remaining=['V3 targeted visual checks','Actual PCM/word alignment/native gameplay annotations','Integrated moving/audio/mobile QA']);save(P/'planning/script-integration.json',i)
b['sourceNarrationSha256']=review['koSha256'];save(P/'planning/scene-bindings.json',b)
p.update(narrationFinal=True,sceneBindingsFinal=True,stage='approved-voice-production-ready',productionReadinessMeaning='Source/unchanged narration/design bindings complete; actual final audio and visual review pending.')
p['scriptReadthrough'].update(koSha256=review['koSha256'],enSha256=review['enSha256']);save(P/'planning/production-plan.json',p)
project=read(P/'project.json');project['status']='narration-ready';save(P/'project.json',project)
print('68 unchanged bilingual paragraphs frozen; final sound/picture review pending.')
