"""Record a short inspected passage following the yellow opening, without reuse."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-mesh-uv'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sample=read(R/'shared/output/game-math-part2-full-series/inspection/mesh-uv-yellow-extension/generated-samples.json');sheet=sample['records'][0]
assert len(sample['records'])==1 and sheet['in']==706 and sheet['out']==710 and len(sheet['sampleTimes'])==5
lf=B/f'lessons/{slug}.json';cf=R/f'projects/{slug}/sources/gameplay-cuts.json';lesson=read(lf);cuts=read(cf)
s=next(x for x in lesson['scenes'] if x['id']=='15');c=next(x for x in cuts['cuts'] if x['scene']=='15')
assert s['sourceId']=='wzQLP0Z3zII' and s['sourceSegments'][0]['in']==640 and s['maxSeconds'] in [66,68]
for x in [s,c]:x['maxSeconds']=68;x['sourceSegments'][0]['maxSeconds']=68
write(lf,lesson);write(cf,cuts)
write(R/f'projects/{slug}/production/yellow-opening-extension.json',{'status':'passed-direct-five-source-sample-review','reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scene':'15','sourceId':s['sourceId'],'sourceSha256':sample['sourceSha256'],'sheet':sheet['sheet'],'sheetSha256':sha(R/sheet['sheet']),'sampleTimes':sheet['sampleTimes'],'directObservation':'All five samples706,707,708,709,709.9 directly viewed. Real camera and characters pass through the yellow opening;yellow flat walls and rounded opening remain visible before moving toward the beach. No menu. Only706–708 additional seconds are selected;later beach709–710 is excluded. Small existing blue gear UI at706 does not replace the visible game action.','priorInterval':{'in':640,'out':706},'sourceInterval':{'in':640,'out':708,'maximumSeconds':68,'speed':1},'oldRenderingEpisodeBeginsAt':716,'narrationOrWaveChanged':False,'repeatFreezeSlowdown':False,'finalCaptionedSubjectReview':'pending','reason':'Keep the complete distinct top-normal/side-normal explanation; a short new actual traversal supports measured40:60 without relaxing quiet-seam limits.'})
print('Scene15 maximum inspected interval640–708; no old716+ footage reused.')
