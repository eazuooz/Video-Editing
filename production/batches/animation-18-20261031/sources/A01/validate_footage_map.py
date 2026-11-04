from pathlib import Path
import json
P=Path(__file__).resolve().parent
def r(n):return json.loads((P/n).read_text(encoding='utf-8'))
core=r('selected-footage.json')['sources'];extra=r('additional-selected-footage.json')['sources'];all_sources={**core,**extra}
mapped=r('paragraph-footage-map.json')
assert len(mapped['paragraphs'])==17
seen=[]
for p in mapped['paragraphs']:
 for c in p['candidates']:
  assert c['anchor'] in p['narration']
  source=all_sources[c['sourceKey']]
  assert Path(source['path']).exists()
  assert 0<=c['sourceStart']<c['sourceEnd']<=float(source['decoded']['format']['duration'])
  assert abs(sum(x['seconds'] for x in c['nativeShots'])-c['seconds'])<.001
  assert all(x['width']>=1920 and x['height']>=1080 for x in source['decoded']['streams'] if x['codec_type']=='video')
  if c['priority']=='primary':
   for old in seen:
    if old['sourceKey']==c['sourceKey']:
     assert min(old['sourceEnd'],c['sourceEnd'])-max(old['sourceStart'],c['sourceStart'])<=.000001,(old,c)
   seen.append(c)
out={'status':'pass','paragraphs':17,'sourceFilesPresent':True,'anchorsExactSubstrings':True,'decodedFhdAllMappedSources':True,'nativeShotSumsMatch':True,'primaryIntervalsNonOverlapping':True,'doesNotVerify':'Human realtime viewing, listening, licenses beyond source policy records, final narration alignment, exact footage ratio or complete absence of undetected same-background edits.'}
(P/'paragraph-map-validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
