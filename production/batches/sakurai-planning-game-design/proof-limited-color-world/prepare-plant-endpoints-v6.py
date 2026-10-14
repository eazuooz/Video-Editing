from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;out=P/'review-plant-endpoints-v6.py';assert not out.exists()
c=[dict(key='plant-contour-paint-only',source='chicory-b-roll-2',startFrame=4110,endFrameExclusive=4230,candidateSeconds=2,
 framingUpPixels=120,endpointsOnly=True,provisionalInsertion='07b-cues-to-check',
 caveat='Observe brush/branch outline appearance and short motion, not platform growth or climb.68.5–70.5 excludes earlier approach and GiftQ/letterbox from first excluded70.5. Sameframe-up120; final label names plant contours.',
 selected=False,sourceAdoptionApproved=False,finalCueUiApproved=False,startSeconds=68.5,endSeconds=70.5)]
s=(P/'review-extra-native-targets-v5.py').read_text('utf-8')
s=s.replace('extra-native-targets-execution-v5.json','plant-endpoints-execution-v6.json').replace('preflight/extra-native-targets-v5','preflight/plant-endpoints-v6')
a=s.index('cuts = ');b=s.index('protected_paths =',a);s=s[:a]+'cuts = '+repr(c)+"\nassert sum(c['candidateSeconds'] for c in cuts)==2\n"+s[b:]
s=s.replace('candidateSeconds=14.75,planCuts=cuts','candidateSeconds=2,planCuts=cuts')
s=s.replace("extra = read(P/'extra-native-action-execution-v4.json')","extra = read(P/'extra-native-action-execution-v4.json')\n    targets = read(P/'extra-native-targets-execution-v5.json')\n    assert read(P/'extra-native-target-direct-review-v5.json')['all12BoardsAnd57SamplesDirectlyRead']")
s=s.replace('for d in [prior,trimmed,extra]:','for d in [prior,trimmed,extra,targets]:')
s=s.replace("for oldc in extra['cuts']","for oldc in extra['cuts']+targets['cuts']")
s=s.replace("'new-extra-native-targets-'","'new-plant-endpoints-'")
out.write_text(s,'utf-8');compile(s,str(out),'exec')
print(json.dumps(dict(prepared=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),sourceActionMeasured=False)))
