"""Refresh the five restored compositions without modifying a running worker.

An available clip, a current composition, a rendered master and human approval
remain separate states. Supersedes the pre-exception missing-source inventory.
"""
import datetime
from polish_common import *

now=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows={}
for ident in ['M09','M10','M11','M12','M17']:
    e=Episode(ident);e.authorized()
    game=read(e.H/'gameplay-restoration.json')['scenes']
    composition=read(e.H/'composition-polish.json')
    all_scenes={s['id']:s for s in e.T['scenes']}
    expected_games={s['id'] for s in e.T['scenes'] if s['classification']!='explanation'}
    expected_explanations=set(all_scenes)-expected_games
    assert set(game)==expected_games
    exceptions=[]
    for sid,item in game.items():
        assert sha(R/item['path'])==item['sha256']
        e.verify(R/item['path'],all_scenes[sid]['frames'])
        if item.get('sourceKind')=='approved-original-resolution-exception':
            for source in item['sources']:
                assert approved_original_resolution(e,sid,R/source['source'])
            exceptions.append(sid)
    for sid in expected_explanations:
        item=composition['inputs'][sid]
        assert sha(R/item['path'])==item['sha256']
        e.verify(R/item['path'],all_scenes[sid]['frames'])
    current_plan=sha(R/composition['plan'])==composition['planSha256']
    current_ass=sha(R/composition['globalAss'])==composition['globalAssSha256']
    missing=sorted(set(all_scenes)-set(composition['inputs']))
    rows[ident]={
        'timelineSha256':sha(e.P/'production/timeline.json'),
        'availableGameClips':len(game),'availableExplanationClips':len(expected_explanations),
        'approvedOriginalResolutionScenes':sorted(exceptions),
        'composition':rel(e.H/'composition-polish.json'),
        'compositionSha256':sha(e.H/'composition-polish.json'),
        'registeredInputs':len(composition['inputs']),
        'currentPlanAndAss':current_plan and current_ass,
        'awaitingWorkerRegistration':missing,
        'currentCompositionComplete':not missing and current_plan and current_ass,
        'sourceBlocked':False,
        'finalMasterReview':'See current hash-bound technical-qa.json and visual-review.json; clip readiness is not master approval.',
        'humanReview':'pending'
    }
report={
    'checkedAt':now,'status':'all-source-clips-restored-worker-compositions-tracked-separately',
    'episodes':rows,'availableGameClips':sum(r['availableGameClips'] for r in rows.values()),
    'availableExplanationClips':sum(r['availableExplanationClips'] for r in rows.values()),
    'approvedOriginalResolutionSceneCount':sum(len(r['approvedOriginalResolutionScenes']) for r in rows.values()),
    'missingActualSourceClips':0,'newRender':False,'newTts':False,
    'scope':'File/hash/frame inventory plus exact exception scope; existing source and annotation review evidence reused. No new visual pass or human approval inferred.'
}
assert (report['availableGameClips'],report['availableExplanationClips'],report['approvedOriginalResolutionSceneCount'])==(34,66,10)
save(B/'composition-readiness.json',report)
cp=read(B/'checkpoint.json')
cp['compositionInputReadiness']={
    'report':rel(B/'composition-readiness.json'),'sha256':sha(B/'composition-readiness.json'),
    'allExplanationInputsRegistered':True,'registeredExplanationClips':66,
    'availableGameClips':34,'nativeFhdGameSlots':24,'approvedOriginalResolutionGameSlots':10,
    'missingActualSourceClips':0,
    'currentCompleteCompositions':[k for k,v in rows.items() if v['currentCompositionComplete']],
    'awaitingWorkerRegistration':{k:v['awaitingWorkerRegistration'] for k,v in rows.items() if v['awaitingWorkerRegistration']},
    'humanReview':'pending'
}
cp['updatedAt']=now;save(B/'checkpoint.json',cp)
w=read(R/'shared/publishing/video-worklist.json')
w['privateMathPolish']['compositionInputReadiness']=cp['compositionInputReadiness']
save(R/'shared/publishing/video-worklist.json',w)
print('Verified34 game clips (24 FHD +10 scoped exceptions) and66 explanation clips. Current compositions:',cp['compositionInputReadiness']['currentCompleteCompositions'])
