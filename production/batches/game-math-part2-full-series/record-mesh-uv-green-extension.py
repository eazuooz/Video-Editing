"""Use inspected additional moving gameplay for the measured lecture balance."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-mesh-uv'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
samplefile=R/'shared/output/game-math-part2-full-series/inspection/mesh-uv-green-room-extension/generated-samples.json'
sample=read(samplefile);sheets=sample['records'];assert len(sheets)==1 and len(sheets[0]['sampleTimes'])==11
assert sheets[0]['in']==260 and sheets[0]['out']==270
lessonfile=B/f'lessons/{slug}.json';cutsfile=R/f'projects/{slug}/sources/gameplay-cuts.json'
lesson=read(lessonfile);cuts=read(cutsfile)
scene=next(s for s in lesson['scenes'] if s['id']=='06');cut=next(c for c in cuts['cuts'] if c['scene']=='06')
assert scene['sourceId']=='wzQLP0Z3zII' and scene['sourceSegments'][0]['in']==200
assert scene['maxSeconds'] in [60,70] and len(scene['sourceSegments'])==1
for s in [scene,cut]:s['maxSeconds']=70;s['sourceSegments'][0]['maxSeconds']=70
write(lessonfile,lesson);write(cutsfile,cuts)
record={'status':'passed-direct-11-sample-source-extension-review','reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scene':'06','sourceId':scene['sourceId'],'sourceSha256':sample['sourceSha256'],'sheet':sheets[0]['sheet'],'sheetSha256':sha(R/sheets[0]['sheet']),'sampleTimes':sheets[0]['sampleTimes'],'directObservation':'All11samples260–269.9directly viewed. Camera and existing game characters continue moving within the green room;grid surfaces,curved green wall,circular fixtures,rock and cylindrical bases remain visible. No menu,chat overlay or scene change. The final grid is partly occluded by moving characters but the narrated surface/outline relationships remain visible.','sourceInterval':{'in':200,'out':270,'maximumSeconds':70,'speed':1},'priorInterval':{'in':200,'out':260},'nextEpisodeIntervalBegins':270,'reason':'Full original explanations are preserved. Use inspected real movement and short guided observation pauses to support measured actual40%/explanation60%;final measured allocation is still pending.','narrationOrWaveChanged':False,'repeatFreezeSlowdown':False,'finalCaptionedSubjectReview':'pending'}
write(R/f'projects/{slug}/production/green-room-extension.json',record)
print('Scene06inspected real-time capacity70s;futureUVinterval270preserved.')
