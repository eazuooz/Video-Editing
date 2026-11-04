"""Freeze the internally read source-faithful script for the approved voice.

This is readiness for production, not approval of any audio or finished video.
The final comparison is a declared dependency on the body renders themselves.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
assert control['productionAllowedNow'] and P.name in control['projectSlugs']
review=read(P/'planning/readthrough-review.json')
scripts={l:read(P/f'script/narration.{l}.json') for l in ('ko','en')}
for l in scripts:
    assert sha(P/f'script/narration.{l}.json')==review['textHashes'][l], 'Re-read changed narration first'
assert len(scripts['ko']['scenes'])==len(scripts['en']['scenes'])==79
bindings=read(P/'planning/scene-bindings.json');scenes=bindings['scenes']
assert [s['id'] for s in scenes]==[s['id'] for s in scripts['ko']['scenes']]
footage=read(P/'planning/footage-audit.json');sources={s['id']:s for s in footage['sources']}
selected=[s['actualGamePart'] for s in scenes if 'actualGamePart' in s]
assert len(selected)==7
for segment in selected:
    source=sources[segment['sourceId']]
    assert source['decodedSize'][0]>=1920 and source['decodedSize'][1]>=1080
    assert source['classification'] in ('independent-gameplay','independent-gameplay-menu-operation'), source['id']
    assert (R/source['file']).is_file(), source['file']
    assert source['recordingPermission'] and source['rights'] and segment['claimLimits']
    assert segment['duration']>0 and segment['speed']==1 and not segment['loop'] and not segment['freezePadding']
assert read(P/'production/unity-staging/compile-check.json')['exitCode']==0
for version in ('v2','v3'):
    status=read(P/f'production/unity-staging/local-preflight-{version}/progress.json')
    assert status['status']=='images-ready-for-internal-visual-QA' and not status['failed']
plan=read(P/'planning/production-plan.json');assert plan['sourceFinal']
plan['narrationFinal']=True
plan['sceneBindingsFinal']=True
plan['productionReadinessMeaning']='All 79 source paragraphs and seven inspected native-game roles bound; implementation exists. Actual PCM timing, final visual/audio QA and human review remain pending.'
plan['finalComparisonDependency']={
    'scene':'078','renderer':'advanced:final-grid',
    'fromFinishedBodyScenes':['001','037','074','076'],
    'labels':['표면 한 점의 반사','물체 전체의 셰이딩','고정된 배치의 베이크','움직이는 물체의 조명'],
    'requirements':['Extract genuine FHD frames after body render','SHA256 and same-project paths required by renderer','Keep source-kind labels and measured crop/aspect','Final comparison must not use placeholders or claim commercial game internals']}
scenes[-1]['remainingImplementation']=None
scenes[-1]['renderDependencies']=plan['finalComparisonDependency']
bindings['pendingImplementationBeatCount']=0
bindings['status']='production-design-frozen-actual-audio-timing-and-final-QA-pending'
stamp=datetime.now(timezone.utc).isoformat()
for language,script in scripts.items():
    script['status']='frozen-for-approved-voice-production'
    script['isFinalNarration']=True
    script['actualDurationSeconds']=None
    save(P/f'script/narration.{language}.json',script)
review['textHashes']={l:sha(P/f'script/narration.{l}.json') for l in scripts}
review['ttsAuthorizedToStart']=True
review['productionDecisionAt']=stamp
review['decision']='Use existing approved Qwen voice; no extra sample approval. Text unchanged; only production metadata finalized.'
bindings['sourceNarrationSha256']=review['textHashes']['ko']
save(P/'planning/readthrough-review.json',review)
save(P/'planning/scene-bindings.json',bindings)
save(P/'planning/production-plan.json',plan)
footage['status']='Five selected games, seven concept-matched native intervals; final sound and moving composite QA pending'
for source in footage['sources']:
    if source['id']=='X9UdRR_4Rog':
        source['selection']='Selected Forzavista camera movement: body paint highlight moves as the view changes. Independent native game menu-operation recording, not a rendered teaching demo.'
footage['selection']={'gameCount':5,'nativeIntervals':7,'selectedSegmentIds':[s['id'] for s in selected],'noFixedLectureShare':True}
footage['rules']['nintendoTarget']={'meaningfullyTaughtNintendoGames':1,'meaningfullyTaughtTotalGames':5,'fraction':'1/5','basis':'Nintendo Tears of the Kingdom official product verified; non-reference math lecture uses the smallest sufficient concept-matched set, no unrelated quota padding.'}
save(P/'planning/footage-audit.json',footage)
project=read(P/'project.json');project['status']='narration-ready'
project['tts']=read(P/'production/tts-manifest.json')['tts']
project['paths']['ttsManifest']='projects/game-math-shading-lights/production/tts-manifest.json'
save(P/'project.json',project)
print('79 source-faithful bilingual paragraphs frozen; next: approved voice. No audio or final-video approval claimed.')
