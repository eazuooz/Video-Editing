import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent; R=H.parents[3]
file=R/'projects/game-math-euler-axis-angle/script/revision-v8-orientation-matrix/narration.en.json'
receipt=json.loads((H/'caption-en-edits.json').read_text(encoding='utf8'))
current=file.read_bytes()
if hashlib.sha256(current).hexdigest()==receipt['sourceEnSha256Before']:
 print('Original English already restored')
else:
 assert hashlib.sha256(current).hexdigest()==receipt['sourceEnSha256After'],'No unrelated source edits may be overwritten'
 d=json.loads(current)
 for change in receipt['changes']:
  sid,line=change['paragraphId'].split('.L');line=int(line)-1
  s=next(s for s in d['scenes'] if s['id']==sid)
  assert s['paragraphs'][line]==change['after'];s['paragraphs'][line]=change['before']
 serialized=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 candidates=[serialized.encode('utf8'),serialized.replace('\n','\r\n').encode('utf8')]
 restored=next((x for x in candidates if hashlib.sha256(x).hexdigest()==receipt['sourceEnSha256Before']),None)
 assert restored is not None,'Must restore exact approved bytes including original Windows line endings'
 file.write_bytes(restored)
 receipt['sourceRestoredExactSha256']=hashlib.sha256(restored).hexdigest()
 receipt['scopeCorrection']='Source restored byte-for-byte. Rewordings below are permitted only in caption-specific data, not narration.en.json.'
 (H/'caption-en-edits.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(receipt['sourceRestoredExactSha256'])
