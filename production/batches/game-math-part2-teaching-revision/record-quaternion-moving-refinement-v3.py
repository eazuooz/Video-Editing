"""Preserve readback masters; reserve new paths for two observed pixel fixes."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reveals=read(R/'final-aac-annotation-reveal.json')
for ident,episode in [('QF10','foundations'),('QC10','calculations')]:
    path=ROOT/f'shared/output/game-math-quaternion-{episode}-v3/mixed-asr-v3/{ident}.json'
    raw=read(path)
    observed={color:next(w['timestamp'][0] for w in raw['words'] if term in w['text']) for color,term in [('red','빨간'),('blue','파란')]}
    assert abs(observed['red']-reveals[ident]['redAt'])<.04
    assert abs(observed['blue']-reveals[ident]['blueAt'])<.04
    reveals[ident].update(finalAacReadback={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'observedWordOnsets':observed},method='Complete final-AAC scene readback, without expected-text prompting, confirms the spoken color cues within 0.04s; no audio or caption changes.')
write(R/'final-aac-annotation-reveal.json',reveals)
for episode in ['foundations','calculations']:
    path=ROOT/f'projects/game-math-quaternion-{episode}-v3/project.json'
    m=read(path)
    current={k:m['paths'][k] for k in ['videoClean','videoBurnedCaptions']}
    if all('-refined-v2.mp4' in p for p in current.values()):continue
    assert all('-refined.mp4' in p and (ROOT/p).exists() for p in current.values())
    m['finalRender']['previousFirstRefinedMasterPaths']={k:{'path':p,'sha256':sha(ROOT/p)} for k,p in current.items()}
    for k,p in current.items():m['paths'][k]=p.replace('-refined.mp4','-refined-v2.mp4')
    m['finalRender']['movingReviewRefinement']={'trailCameraOrbitHideSeconds':[9.5,10],'reason':'Actual current moving pixels at9.667s showed interpolation crossing the changing camera direction; hide the projected guides until the10s observed anchor. Gameplay remains1x and continuous.','qc11CaptionClearance':'Raise only its two central summary labels by0.30drawing units; retain fixed narration captions.','audioChanges':False,'original80ClipsChanged':False,'finalMovingReviewComplete':False}
    write(path,m)
write(R/'camera-orbit-and-caption-refinement.json',{'reviewedContacts':['QF10-moving-04.jpg','QC11-moving-01.jpg'],'observedIssues':['QF10 at9.667s: projected nose guide crosses rapid camera orientation interpolation.','QC11: lower central gold summary is too close to two-line fixed narration box.'],'corrections':['Hide both aircraft guides9.5–10s, resume at observed10s anchor.','Raise QC11 central gold text0.30units.'],'existingAudioPreserved':True,'currentNewMasterReviewPending':True})
