"""Adapt candidate tooling for the reassigned targets; no completed worker runs."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
pairs=[('build-candidate-captions-v3.py','build-candidate-captions-v4.py'),
       ('prepare-candidate-caption-layout-v3.cjs','prepare-candidate-caption-layout-v4.cjs'),
       ('build-inspection-pcm-v3.py','build-inspection-pcm-v4.py'),
       ('compile-native-candidate-v3.cjs','compile-native-candidate-v4.cjs'),
       ('extract-guided-native-cue-trials-v3.py','extract-wall-guide-targets-v4.py')]
for a,z in pairs:
    path=BASE/z;assert not path.exists()
    text=(BASE/a).read_text('utf-8').replace('v3','v4')
    if z=='compile-native-candidate-v4.cjs':
        text=text.replace('measured-edit-v2/native-review-v1','measured-edit-v3/native-review-v3')
    if z=='build-inspection-pcm-v4.py':
        text=text.replace("BASE/'narration-guided60-index-v4.json'","BASE/'narration-guided60-index-v3.json'")
    if z=='extract-wall-guide-targets-v4.py':
        text=text.replace("(s['id'] in ['02','06','13','12'] or c.get('bankCutId')==28)","((s['id']=='02' and c['paragraph']==4) or (s['id']=='06' and c['paragraph']==2))")
        text=text.replace("if not p.get('guideId'):continue","if not (p.get('guideId')=='02-g1' or (s['id']=='06' and p['paragraph']==2)):continue")
        text=text.replace("a=max(0,a);z=min(p['pcmToSample']/24000,z)","a=max(p['pcmFromSample']/24000,a);z=min(p['pcmToSample']/24000,z)\n            if z<=a:continue")
        text=text.replace("p['outputSpeechFromSample']/24000+(a+z)/2","(p['outputSpeechFromSample']-p['pcmFromSample'])/24000+(a+z)/2")
        text=text.replace("p['guideId']","p.get('guideId') or ('06-p2' if s['id']=='06' else '02-p4')")
        text=text.replace('guided-cue-review-local-v4','wall-guide-target-local-v4')
        text=text.replace('extract-guided-native-cue-trials-v4.py','extract-wall-guide-targets-v4.py')
    path.write_text(text.rstrip()+'\n',encoding='utf-8')
print('Five v4 tools prepared; only six reassigned/adjacent targets will be extracted.')
