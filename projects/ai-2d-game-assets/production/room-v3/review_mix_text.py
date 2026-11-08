"""Prepare complete ASR comparison evidence; never infer listening from it."""
from pathlib import Path
import json,difflib,re,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');Q=O/'qa';Q.mkdir(exist_ok=True)
plan=json.loads((H/'revision-plan.json').read_text('utf8'))['scenes'];tm=json.loads((L/'timeline.json').read_text('utf8'))['scenes'];chunks=[];rows=[]
def norm(v):return re.sub(r'[^가-힣A-Za-z0-9]','',v).lower()
for row in tm:
 data=json.loads((L/'asr-mix'/f"{row['id']}.json").read_text('utf8'));source=next(x for x in plan if x['id']==row['id']);a=norm(source['ko']);b=norm(data['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
 diffs=[{'operation':op,'expected':a[x:y],'recognized':b[u:v]} for op,x,y,u,v in m.get_opcodes() if op!='equal']
 rows.append({'id':row['id'],'expected':source['ko'],'recognized':data['text'],'sequenceRatio':m.ratio(),'differences':diffs,'audioSha256':data['audio_sha256'],'semanticReview':'pending direct text read'})
 for w in data.get('chunks',[]):
  if None in w['timestamp']:continue
  chunks.append({'text':w['text'],'timestamp':[row['start']+v for v in w['timestamp']]})
(Q/'mix.timestamps.json').write_text(json.dumps({'chunks':chunks,'source':'independent actual encoded mix per complete paragraph, no prompt'},ensure_ascii=False,indent=2),'utf8')
(H/'mix-asr-review.json').write_text(json.dumps({'mixSha256':hashlib.file_digest((O/'final-mix.m4a').open('rb'),'sha256').hexdigest(),'wholeNarratedContent':True,'humanListening':False,'status':'comparison-ready-for-semantic-review','paragraphs':rows},ensure_ascii=False,indent=2),'utf8')
print('Prepared',len(rows),'paragraph comparisons and',len(chunks),'global word timestamps')
