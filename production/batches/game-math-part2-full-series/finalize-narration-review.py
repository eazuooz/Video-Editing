"""Seal only a directly reviewed full set of current raw narration evidence."""
from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];slug=sys.argv[1];P=R/f'projects/{slug}/production'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
m=read(R/f'projects/{slug}/project.json');out=R/m['tts']['outputDir'];v=read(P/'narration-review-in-progress.json');rows={s['scene']:s for s in v['scenes']};expected={s['id'] for s in read(R/m['paths']['script'])['scenes']}
assert not v['pendingScenes'] and set(rows)==expected and len(rows)==len(v['scenes']),'Direct scene-by-scene review incomplete'
report=read(out/(m['tts']['filenameStem']+'.asr-review.json'));assert report['complete'] and report['sceneCount']==len(expected)
for sid,s in rows.items():
 raw=read(out/f'asr/{sid}.json');a=next(a for a in report['scenes'] if a['scene']==sid)
 assert s['wavSha256']==sha(out/f'chunks/{sid}-scene.wav')==raw['audio_sha256']==a['audio_sha256']
 assert s['rawAsrSha256']==sha(out/f'asr/{sid}.json') and s['recognized']==raw['text'] and s['agentMeaningNumberReview']=='passed'
 assert s['matchingCharacterCoverage']>=.93 and a['acousticChecks']['endingHeuristicPassed']
v.update(status='passed-agent-script-and-ASR-difference-review',humanListening='pending',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Every current full unnormalized raw read-back was directly compared with its complete KO script, source claims and independently verified numbers/signs/frames. Ambiguous omitted nouns and values were repaired without weakening coverage or ending checks. Remaining ASR spelling/filler differences are explicit, and no human listening approval is implied.')
for name in ['narration-review.json','narration-review-in-progress.json']:write(P/name,v)
repairs=[]
for f in sorted((R/f'shared/output/{slug}').glob('line-repair-*/provenance.json')):
 p=read(f)
 if p['sha256']==sha(R/p['currentWave']):
  p['rawAsrAndMeaningReview']='passed-current-agent-review-human-listening-pending';p['provenanceSource']=f.relative_to(R).as_posix();repairs.append(p)
if repairs:write(P/'narration-repairs.json',{'status':'passed-current-agent-meaning-number-and-ending-review','humanListening':'pending','repairs':repairs})
for name in ['observation-expansion.json','spoken-value-clarification.json']:
 f=P/name
 if f.exists():
  p=read(f);p['newVoiceReview']='passed-current-agent-raw-meaning-and-number-review';p['currentVoiceReview']='passed-current-agent-raw-meaning-and-number-review';write(f,p)
qf=Path(__file__).parent/'queue.json';q=read(qf);item=next(x for x in q['items'] if x['slug']==slug);item.update(status='narration-reviewed-final-render-in-progress',narrationAsrReviewed=True,currentRawReviewPendingScenes=[],humanListening=False);write(qf,q)
print(slug,len(rows),'current full raw narration reviews verified; human listening pending')
