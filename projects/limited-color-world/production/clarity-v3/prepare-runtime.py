"""Prepare scoped source adapters only; never imports or executes media pipelines."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OLD=HERE.parent/'batch-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for name in ['audio_pipeline.py','caption_pipeline.py','video_pipeline.py']:
 p=OLD/name;text=p.read_text('utf-8-sig')
 if name=='audio_pipeline.py':
  text=text.replace('SCRIPT = PROJECT / "script" / REVISION','SCRIPT = Path(__file__).resolve().parent')
  start=text.index('def require_authorized(stage):');end=text.index('def current_local_output(value):',start)
  text=text[:start]+'''def require_authorized(stage):
    policy = read(ROOT / 'shared/publishing/video-production-control.json')
    approval = read(Path(__file__).resolve().parent / 'authorization.json')
    selected = policy.get('finiteBatchAuthorizations', {}).get('design-25-30-review-actions-20261029', {})
    if (SLUG,REVISION)!=("limited-color-world","clarity-v3"):
        raise ValueError('This adapter belongs only to selected D25 clarity-v3')
    if approval.get('fullProductionAuthorized') is not True or 'D25' not in selected.get('revisionEpisodeIds',[]):
        raise ValueError('Explicit D25 clarity revision required')
    if selected.get('automaticOutsideBatch') is not False or selected.get('nativeUiAndFocusChanges') is not False:
        raise ValueError('Preserve selected scope and no-UI boundary')
    if approval.get('voice',{}).get('approvedSample')!='B':
        raise ValueError('Approved own-voice Sample B required')
    return {'stage':stage,'project':SLUG,'revision':REVISION,
            'authorizationSha256':sha(Path(__file__).resolve().parent/'authorization.json'),
            'controlSha256':sha(ROOT/'shared/publishing/video-production-control.json'),
            'observedSharedSelection':policy.get('selectedVideo'),'controlSelectionChanged':False,
            'youtubeUploadPerformed':False}


''' + text[end:]
  text=text.replace("lease=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/heavy-job.lock.json')","lease=LOCAL/'voice/heavy-job.lock.json'")
 if name=='video_pipeline.py':
  old='''    target = plan.get("expectedGameplayShare", .6) * plan["bodyFrames"]
    if abs(gameplay - target) > plan.get("ratioToleranceFrames", 1):
        raise ValueError(f"Gameplay ratio outside one-frame tolerance: {gameplay}/{plan['bodyFrames']}")'''
  new='''    contract=plan.get("ratioDecision",{})
    if contract.get("policy")!="D25-clarity-v3-content-led-explanation-expansion" or not contract.get("reason"):
        raise ValueError("D25-only documented explanation expansion required")
    if gameplay<=0 or gameplay>=plan["bodyFrames"]:
        raise ValueError("Both actual observed game actions and substantive explanation required")'''
  assert old in text;text=text.replace(old,new)
 dest=HERE/name
 if dest.exists() and dest.read_text('utf-8')!=text:raise RuntimeError('Preserve edited runtime '+str(dest))
 dest.write_text(text,'utf-8');records.append({'copiedFrom':str(p.relative_to(ROOT)).replace('\\','/'),'sourceSha256':sha(p),'newFile':dest.name,'newSha256':sha(dest)})
(HERE/'runtime-provenance.json').write_text(json.dumps({'revision':'clarity-v3','files':records,'executionPerformed':False,'preservedGuards':['unchanged raw voice','unprompted ASR and complete-text comparison','word-anchored paired captions','no loops or speed changes','source FHD checks','continuous filter clock reinit_filter=0','same AAC in both masters','full frame/PTS/decode verification'],'changedScope':['D25 clarity-v3 authority','new local output root','own source script paths','own ASR lease','content-led measured ratio with written reason']},ensure_ascii=False,indent=2)+'\n','utf-8')
print('Scoped runtime authored; no media execution.')
