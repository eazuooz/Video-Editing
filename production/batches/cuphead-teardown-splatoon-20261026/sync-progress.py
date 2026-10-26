"""Refresh only this explicitly selected finite batch from existing evidence."""
from pathlib import Path
import json, hashlib, datetime

B = Path(__file__).resolve().parent
R = B.parents[2]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

batch=read(B/'batch.json'); cp=read(B/'checkpoint.json'); rows=[]
for item in batch['projects']:
    p=R/'projects'/item['slug']; local=p/'production/local'
    plan=read(p/'planning/production-plan.json')
    row=dict(slug=item['slug'],revision=item['revision'],checkpoint=f'projects/{item["slug"]}/production/checkpoint.json',
             scriptFinalized=plan.get('scriptFinalized',False),independentFootageViewed=plan.get('independentFootageViewed',False))
    review=p/'production/local-review.json'
    if review.exists() and read(review).get('status') == 'local-final-review-pending':
        d=read(review)
        for name,evidence in d['outputs'].items():
            file=Path(evidence['path'])
            assert file.is_file() and sha(file)==evidence['sha256'], 'Current review file changed: '+str(file)
        row.update(status='local-final-review-pending',finalOutputs=d['outputs'],humanReview=d['humanReview'],reviewRecord=str(review.relative_to(R)).replace('\\','/'))
    else:
        state='source-and-code-ready'
        audio=read(p/'project.json').get('audioRevision','audio-v1')
        voice=local/audio/'voice/narration.wav'
        if voice.exists(): state='voice-generated; alignment/render-QA pending'
        elif (local/audio/'tts-execution.partial.json').exists(): state='voice-in-progress; generated takes preserved'
        row.update(status=state,finalOutputs=None,humanReview='not-delivered')
    item['status']=row['status']; rows.append(row)
cp.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),projects=rows,
          localFinalCompleted=sum(x['finalOutputs'] is not None for x in rows),
          status='finite-four-production-in-progress; exact local review only',
          resourceState={'mediaRoot':batch['mediaRoot'],'appsTerminated':False,
                         'policy':'Recheck process/resource lease before each serial costly job; no current availability inferred from this summary.'},
          notDone=['Remaining project final outputs','Full actual listening/continuous playback and human final review'],
          next=['Finish the exact remaining selected projects serially, using unchanged successful PCM/captures.','Inspect actual outputs, update own records, selective commit and normal push.'])
if cp['localFinalCompleted']==len(rows):
    cp.update(status='four-local-final-versions-ready-for-human-review',
              notDone=['Full actual listening/continuous playback and human final review'],
              next=['Review the exact four local versions. No platform action is authorized by this delivery.'])
save(B/'batch.json',batch);save(B/'checkpoint.json',cp)
work=R/'shared/publishing/shorts-worklist.json'
doc=read(work)
def visit(node):
    if isinstance(node,dict):
        key=node.get('slug') or node.get('project')
        for row in rows:
            if key==row['slug']:
                node['productionStatus']=row['status']
                node['humanReview']=row['humanReview']
                node['batchCheckpoint']='production/batches/'+batch['id']+'/checkpoint.json'
        for value in node.values(): visit(value)
    elif isinstance(node,list):
        for value in node: visit(value)
visit(doc);save(work,doc)
print(json.dumps({'completeLocal':cp['localFinalCompleted'],'total':len(rows),'states':[(r['slug'],r['status']) for r in rows]},ensure_ascii=False))
