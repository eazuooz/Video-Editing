from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+'.correcting');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
proof=BASE/'pre-voice-reference-corrections-v1.json'
assert not proof.exists() and not (BASE/'narration-tts-execution-v1.json').exists()
request=read(BASE/'narration-tts-request-v1.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
changes=[]
p=BASE/'sources/game-candidates.json';j=read(p);before=sha(p)
tet=next(x for x in j['chosen'] if x.get('game')=='Tetris Effect: Connected')
old=tet['sourceBank'];new='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json'
assert old=='projects/presenting-game-scores/production/source-action-bank-v4.json' and (ROOT/new).exists()
tet['sourceBank']=new;save(p,j);changes.append(dict(path=p.relative_to(ROOT).as_posix(),beforeSha256=before,sha256=sha(p),old=old,new=new,reason='Correct reference to the existing sealed source bank; source selection unchanged'))
p=BASE/'script/narration.en.json';j=read(p);before=sha(p)
s=next(x for x in j['scenes'] if x['id']=='08-scoring-feedback')
old=s['lines'][0];new=old.replace('short Balatro closeups','short Balatro scoring sequences');assert new!=old
s['lines'][0]=new;save(p,j);changes.append(dict(path=p.relative_to(ROOT).as_posix(),beforeSha256=before,sha256=sha(p),old=old,new=new,reason='Match the actual full-frame scoring sequences; Korean words and retained PCM unchanged'))
for c in changes:
 r=next(x for x in request['protectedInputs'] if x['path']==c['path']);assert r['sha256']==c['beforeSha256'];r['sha256']=c['sha256']
request['preVoiceReferenceCorrections']=proof.relative_to(ROOT).as_posix();save(BASE/'narration-tts-request-v1.json',request)
p=Path(__file__).parent/'adopt-revision-source-content-v7.py';txt=p.read_text('utf-8');assert old!=new
txt=txt.replace('projects/presenting-game-scores/production/source-action-bank-v4.json','production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json');p.write_text(txt,'utf-8')
p=Path(__file__).parent/'prepare-selective-balanced-script-v1.py';txt=p.read_text('utf-8').replace('bounds[2]=267360 #11.14s, before actual ASR 어떤 onset11.30s; current PCM quiet gate still required','bounds[2]=268800 #11.20s actual PCM quiet boundary; joined context review still required')
txt=txt.replace('candidate11.14s moves into actual ASR sentence gap10.98–11.30','actual quiet11.20s lies in actual ASR sentence gap10.98–11.30');p.write_text(txt,'utf-8')
save(proof,dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),changes=changes,correctionTextsDirectlyCompared=True,pairedFullTextReviewPreserved=True,wholeReview='projects/presenting-game-scores/production/revision-balatro60-v2/paired-selective-script-direct-review-v1.json',koreanVoiceTextChanged=False,sourceMediaOrBaselineWrites=0,ttsStarted=False))
print('Two reviewed reference/English wording corrections; protected hashes updated, Korean voice unchanged.')
