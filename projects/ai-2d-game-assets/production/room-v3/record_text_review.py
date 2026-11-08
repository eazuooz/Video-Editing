from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3'
p=H/'mix-asr-review.json';data=json.loads(p.read_text('utf8'))
for row in data['paragraphs']:
 if not row['id'].isdigit():row['semanticReview']='model read expected and current AAC recognition completely: no omitted claim, reversed negation, or changed numeric value'
data['addedParagraphReview']={'count':21,'method':'direct model reading of every expected/current-recognized paragraph; not a listening claim','omittedClaims':[],'changedNegations':[],'changedNumbers':[],'phoneticUncertainty':[{'id':'R04','term':'ChatGPT','observed':'채찌피티 / 챗집 PT','meaningPresent':True},{'id':'R21','term':'PixelOE','observed':'픽셀52','meaningPresent':True},{'id':'R22','term':'Agent Sprite Forge','observed':'에이전트 스프라이트 포즈','meaningPresent':True},{'id':'V31','term':'PixelOE / Nearest Neighbor (최근접 보간)','observed':'픽셀5위 / 최근접 보관','meaningPresent':True}],'contextCheck':'asr-context-review.json; complete-sentence checks do not resolve subjective pronunciation; canonical captions/headings retained','homophonesNotDefects':['R18 짚기/집기 and 받치고/바치고','V34 안의/안에','R24 옆의/옆에'],'newTtsNotTriggeredSolelyByAsrSpelling':True,'humanListening':False}
data['status']='added21 semantically reviewed; baseline30 independently reviewed in baseline-asr-review.json'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for name in ['revision-plan.json','narration-additions.ko-en.json','additional-narration-brief.json']:
 f=H/name;s=f.read_text('utf8').replace('Pixelbolt40x18ledger','Pixelbolt56x20ledger');f.write_text(s,'utf8')
f=H/'caption-clauses.json';c=json.loads(f.read_text('utf8'));c['review']['sourceSha256']=hashlib.sha256((H/'narration-additions.ko-en.json').read_bytes()).hexdigest();c['review']['metadataUpdateOnly']='V33 ledger screen-plan dimension corrected40x18→56x20; KO/EN text unchanged';f.write_text(json.dumps(c,ensure_ascii=False,indent=2),'utf8')
print('Recorded 21 complete semantic readbacks, precise spelling uncertainty, unchanged spoken content.')
