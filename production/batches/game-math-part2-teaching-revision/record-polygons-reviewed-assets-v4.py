"""Save explicit review evidence; preserve raw ASR and foreign image entries."""
from pathlib import Path
from datetime import datetime
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/game-math-part2-teaching-revision'
R=B/'cross-game-review-20261011'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now().astimezone().isoformat()
slug='game-math-polygon-partition-v2';P=ROOT/'projects'/slug
raw=read(ROOT/f'shared/output/{slug}/mixed-asr-v4/all-scenes.json')
t=read(P/'production/timeline.json');m=read(P/'project.json')
assert raw['complete'] and len(raw['scenes'])==len(t['scenes'])==24
assert raw['sha256']==sha(ROOT/m['paths']['videoClean'])
assert raw['timelineSha256']==sha(P/'production/timeline.json')
assert [s['scene'] for s in raw['scenes']]==[s['id'] for s in t['scenes']]
review={'recordedAt':now,'slug':slug,'method':'Direct complete expected-versus-unprompted recognized text comparison for all24 current final AAC scene intervals. Preserve raw words/timestamps; recognition is not human listening.','source':raw['source'],'sha256':raw['sha256'],'captionedSha256':sha(ROOT/m['paths']['videoBurnedCaptions']),'timelineSha256':raw['timelineSha256'],'rawEvidence':f'shared/output/{slug}/mixed-asr-v4/all-scenes.json','completeScenesDirectlyRead':[s['scene'] for s in raw['scenes']],'completeSceneCount':24,'mathematicalMeaningReviewPassed':True,'checks':['Convex n-2 fan condition retained; six vertices gives four triangles.','Concave arbitrary fan can fail despite signed area7; anchor and geometry conditions retained.','First ear area2; following ears1.5 and1.5, final triangle2; total7.','Validity precedes quality; union preserves original region and empty notch.','Summary retains G(4/3,1), I(1,1), O(2,1.5), r1 and R2.5.','Shapez processing differs from triangulating all original area; belts are routes rather than polygon boundaries.','All narrated endings captured; no expected script supplied to recognizer.'],'recognitionNotes':[{'scene':'19','note':'Repeated final instruction appears with overlapping/backtracking word timestamps39.7–46.66 then40.0–46.58 in experimental chunked ASR; does not establish a repeated waveform. Preserve raw evidence and original PCM.'},{'scene':'QB12','note':'ASR reads 벨트 as 델트 in isolated and final intervals. This is an unresolved human pronunciation check, not an automatically rewritten transcript or mathematical error.'},{'scene':'17','note':'ASR homophones 내/네 and 일/엘 are recorded as recognition uncertainty; adjacent worked examples preserve explicit four-triangle and L-shape results.'}],'humanListening':'pending','automaticAudioApproval':False,'rightsApproval':False}
write(R/f'{slug}-mixed-audio-review-v4.json',review)
registry=read(ROOT/'shared/git-essential-images.json');ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8')
for slug,expected,reason in [('game-math-polygon-centers-v2','6558ce248da5465c8905bb9e93145e3860d307916b3d54e979bdfda910f3cbff','Directly reviewed independent centers lecture thumbnail: original cats, yellow header, purpose-selected center dots, red circumcenter on hypotenuse; illustrative geometry.'),('game-math-polygon-partition-v2','5984ec04d1bba36ae080bf1c23ca74b658193d34037a0ff5e57efbe448509c59','Directly reviewed independent partition lecture thumbnail: original cats, yellow header, exactly four triangles preserving the L-shaped empty notch.')]:
    path=f'projects/{slug}/publishing/thumbnail-v2.png';assert sha(ROOT/path)==expected
    gen=read(ROOT/f'projects/{slug}/publishing/thumbnail-generation-v2.json');assert gen['review']['status']=='directly-reviewed'
    gen.update(sha256=expected,reviewedAt=now);write(ROOT/f'projects/{slug}/publishing/thumbnail-generation-v2.json',gen)
    existing=[x for x in registry['entries'] if x['path']==path]
    if existing:assert len(existing)==1 and existing[0]['sha256']==expected
    else:registry['entries'].append({'path':path,'purpose':'delivery-thumbnail','reason':reason,'sha256':expected,'reviewedAt':now,'project':slug})
    exception='!'+path
    if exception not in text.splitlines():text+='\n'+exception+'\n'
write(ROOT/'shared/git-essential-images.json',registry);ignore.write_text(text,encoding='utf8')
print('Saved current24-scene partition ASR meaning review and two exact essential thumbnail registrations; human listening/platform work remains pending.')
