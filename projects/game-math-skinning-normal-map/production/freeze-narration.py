"""Freeze unchanged, internally reviewed M22 narration for the approved voice."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
assert control['productionAllowedNow'] and P.name in control['projectSlugs']
integration=read(P/'planning/script-integration.json');review=integration['readThrough']
scripts={lang:read(P/f'script/narration.{lang}.json') for lang in ('ko','en')}
for lang in scripts:assert sha(P/f'script/narration.{lang}.json')==review[lang+'Sha256']
assert review['allBeatsRead'] and review['sourceOrderPreserved']
bindings=read(P/'planning/scene-bindings.json');plan=read(P/'planning/production-plan.json')
assert len(scripts['ko']['scenes'])==len(scripts['en']['scenes'])==len(bindings['scenes'])==36
assert bindings['pendingImplementationBeatCount']==0 and plan['sourceFinal']
assert [x['id'] for x in scripts['ko']['scenes']]==[x['id'] for x in bindings['scenes']]
footage=read(P/'planning/footage-audit.json')
for source in footage['sources']:
 assert source['classification']=='independent-gameplay'
 assert source['decodedSize'][0]>=1920 and source['decodedSize'][1]>=1080
 assert source['recordingPermission'] and source['publisherRights'] and (R/source['file']).is_file()
for game in plan['nativeGameCueBindings']:
 assert game['playbackRate']==1 and game['sourceOut']>game['sourceIn'] and not game['freezePadding'] and not game['loop']
 assert game['nativeDecodeEvidence']['decodeExitCode']==0
assert read(P/'production/unity-staging/compile-check.json')['csharpCompilation']['exitCode']==0
runtime=read(P/'production/unity-staging/local-preflight-v2/progress.json')
assert runtime['status']=='images-ready-for-internal-visual-QA' and len(runtime['completed'])==9
rig=read(P/'production/unity-staging/local-preflight-v2/rig-validation-receipt.json');assert rig['runtimeSkinningChecks']==15
stamp=datetime.now(timezone.utc).isoformat()
for lang,script in scripts.items():
 script.update(status='frozen-for-approved-voice-production',isFinalNarration=True,actualDurationSeconds=None)
 save(P/f'script/narration.{lang}.json',script)
 review[lang+'Sha256']=sha(P/f'script/narration.{lang}.json')
review.update(productionDecisionAt=stamp,ttsAuthorizedToStart=True,productionReadiness='Unchanged reviewed text and all36 scene roles; actual PCM and integrated audiovisual QA remain pending.')
integration.update(narrationFinal=True,sceneBindingsFinal=True)
integration['remaining']=['Targeted label/data-order V3 visual review','Actual PCM, bilingual timestamps, synchronized native footage and final moving/audio QA']
save(P/'planning/script-integration.json',integration)
bindings['sourceNarrationSha256']=review['koSha256'];save(P/'planning/scene-bindings.json',bindings)
plan.update(narrationFinal=True,sceneBindingsFinal=True,stage='approved-voice-production-ready',productionReadinessMeaning='Source/unchanged narration/design bindings complete. Targeted visual repairs do not change speech; no final media or human review claimed.')
plan['scriptReadthrough'].update(koSha256=review['koSha256'],enSha256=review['enSha256'])
save(P/'planning/production-plan.json',plan)
project=read(P/'project.json');project['status']='narration-ready';save(P/'project.json',project)
print('36 unchanged bilingual paragraphs frozen; approved Qwen voice authorized, actual sound/visual QA remains pending.')
