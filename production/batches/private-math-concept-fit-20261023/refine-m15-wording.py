"""Preserve all finished takes; replace two visual nouns/actions after closer source review."""
from common import *
import shutil
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';A=P/'production/local/concept-fit-v2/audio';authorized('M15')
assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Wait for the finite voice job; never interrupt it'
delta=read(H/'source-wording-correction.json');receipt=read(A/'paragraph-takes.json');old=read(H/'voice-plan.json')
assert receipt['takeCount']==14 and receipt['identitySha256']==old['identitySha256']
history=H/'before-source-wording-correction';history.mkdir(exist_ok=False)
for path in [H/'voice-plan.json',B/'m15-narration-edits.json',A/'paragraph-takes.json']:
 shutil.copy2(path,history/path.name)
ed=read(B/'m15-narration-edits.json')
for key,pair in delta['changes'].items():
 sid,line=key.split('.L');ed['edits'][sid][str(int(line))]=pair
save(B/'m15-narration-edits.json',ed)
for lang in ['ko','en']:
 path=P/f'script/concept-fit-v2/narration.{lang}.json';shutil.copy2(path,history/path.name);path.unlink()
(H/'voice-plan.json').unlink()
script=B/'prepare-m15-voice.py';script.write_text(script.read_text(encoding='utf8').replace('손전등과 굽은 바위 표면','전방 조명과 굽은 바위 표면'),encoding='utf8')
run(['C:/Python/python.exe','-X','utf8',script]);new=read(H/'voice-plan.json');new['resources']=old['resources'];new['resourceReason']=old['resourceReason'];save(H/'voice-plan.json',new)
discarded=[];retained=[]
for take in receipt['takes']:
 if take['id'] in delta['changes']:
  path=R/take['file'];destination=A/'takes-before-source-wording-correction'/path.name;destination.parent.mkdir(exist_ok=True);assert not destination.exists();path.rename(destination);discarded.append(dict(**take,archivedPath=rel(destination)))
 else:retained.append(take)
assert len(retained)==12
receipt.update(identitySha256=new['identitySha256'],takes=retained,takeCount=12,status='partial');save(A/'paragraph-takes.json',receipt)
delta.update(pendingAfterCurrentVoiceJob=False,appliedAt=now(),oldVoiceIdentity=old['identitySha256'],newVoiceIdentity=new['identitySha256'],retainedTakes=12,replacedTakes=discarded,actualListening=False);save(H/'source-wording-correction.json',delta)
print('Twelve takes retained unchanged; only two corrected paragraphs pending synthesis')
