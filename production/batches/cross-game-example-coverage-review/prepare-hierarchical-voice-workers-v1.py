"""Derive new H-owned wrappers from the inspected completed idle-lease workflow."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
old='projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
new='projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
def convert(text):
    text=text.replace(old,new).replace('game-math-orientation-matrices','hierarchical-game-outlines')
    names={
      'narration-cross-game-repair-execution-v1.json':'narration-additions-execution-v1.json',
      'narration-cross-game-repair-request-v1.json':'narration-additions-request-v1.json',
      'narration-cross-game-repair-session-v1.json':'narration-additions-session-v1.json',
      'narration-cross-game-repair-waiting-v1.json':'narration-additions-waiting-v1.json',
      'resource-before-cross-game-repair-voice-v1.json':'resource-before-additions-voice-v1.json',
      'cross-game-repair-owned-idle-guard-v1.json':'additions-owned-idle-guard-v1.json',
      'cross-game-repair-voice-closure-verification-v1.json':'additions-voice-closure-verification-v1.json',
      'narration-cross-game-repair-v1.log':'narration-additions-v1.log',
      'cross-game-plan-review-flag-transition-v1.json':'causal-paired-script-direct-review-v1.json',
      'render-orientation-cross-game-repair-v1.py':'render-hierarchical-additions-voice-v1.py',
      'currentOrientationReview':'currentHierarchicalReview'
    }
    for a,b in names.items():text=text.replace(a,b)
    text=text.replace("'--candidate-file','projects/hierarchical-game-outlines/revision-teaching-clarity-v1/duplicate-candidate-v1.json',",'')
    text=text.replace("request['total']==5 and request['paragraphs']==19","request['total']==4 and request['paragraphs']==18")
    text=text.replace('total=5','total=4').replace("state['total']==5","state['total']==4").replace("state['results'])==5","state['results'])==4")
    text=text.replace('original24PcmRegenerated=0,existing6PcmRegenerated=0','original12PcmRegenerated=0')
    text=text.replace('original24+6PCM','original12PCM').replace('original24+6additivePCM','original12PCM')
    text=text.replace('Original24+6PCM','Original12PCM').replace('Five items','Four items').replace('five-items','four-items')
    text=text.replace('five-item','four-item').replace('five-items','four-items').replace('5items/19pairedparagraphs','4items/18pairedparagraphs')
    text=text.replace('wholefive','wholefour').replace('whole5','whole4').replace('allfive','allfour').replace('19independent','18independent')
    text=text.replace('19 complete independent','18 complete independent').replace('Original24+6PCM unchanged;21r adoption remains false.','Original12PCM unchanged; final ratio/mix/annotation/captions remain pending.')
    return text
wrapper=convert((B/'render-orientation-cross-game-repair-v1.py').read_text('utf8'))
wrapper=wrapper.replace('Four additive scenes and one exact paragraph candidate; preserve original PCM.','Four additive scenes only; preserve original12PCM.')
wrapper=wrapper.replace("retry=read(R/'resource-before-additions-voice-v1.json')","retry=read(R/'resource-before-additions-voice-v1.json') if not args.dry_run else dict(protectedShaMatched=True)")
wrapper=wrapper.replace('ttsStarted=True,crossGameVoiceStarted=True,activeOwnedWorkers=1','ttsStarted=True,newTtsStarted=True,crossGameVoiceStarted=True,activeOwnedWorkers=1')
observer=convert((B/'observe-orientation-cross-game-voice-resource-v1.py').read_text('utf8'))
observer=observer.replace('narration-cross-game-repair-request-v1.json','narration-additions-request-v1.json')
observer=observer.replace("assert len(protected)==61","assert len(protected)==129")
observer=observer.replace("'extract-motion']","'extract-motion','render-hierarchical','review-hierarchical','extract-hierarchical','acquire-hierarchical','assemble-hierarchical']")
observer=observer.replace("statusSha256=sha(statusp),status=status","statusSha256=sha(statusp),status=status")
registration=convert((B/'register-orientation-cross-game-voice-v1.py').read_text('utf8'))
registration=registration.replace("'single-five-item-voice-running'","'single-four-item-voice-running'")
registration=registration.replace('crossGameVoiceStarted=True','crossGameVoiceStarted=True,newTtsStarted=True')
verifier=convert((B/'verify-orientation-cross-game-voice-exit-v1.py').read_text('utf8'))
verifier=verifier.replace('five-items-voice-closed','four-items-voice-closed')
prepared=[('render-hierarchical-additions-voice-v1.py',wrapper),('observe-hierarchical-additions-voice-resource-v1.py',observer),
          ('register-hierarchical-additions-voice-v1.py',registration),('verify-hierarchical-additions-voice-exit-v1.py',verifier)]
for name,src in prepared:
    assert not (B/name).exists(),name
    assert old not in src and 'render-orientation-cross-game-repair-v1.py' not in src
    compile(src,str(B/name),'exec')
for name,src in prepared:(B/name).write_text(src,'utf8')
print('Prepared4H-owned wrappers; idle20s/600s guards unchanged;129current-transition-safe inputs; model/request0.')
