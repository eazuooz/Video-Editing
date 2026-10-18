"""One selected speech-clarity correction; preserve all other paragraphs."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
assert not (R/'shared/output/GPU_HANDOFF.json').exists()
files={'ko':P/'script/revision-v2/narration.ko.json','en':P/'script/revision-v2/narration.en.json','lesson':P/'production/revision-v2/lesson.json'}
before={k:sha(v) for k,v in files.items()}
ko,en,lesson=(read(files[k]) for k in ['ko','en','lesson'])
changes=[
 ('03',0,
  '주변에 고정한 방향자를 월드 좌표계라고 부릅니다. 물체와 함께 도는 방향자는 로컬 좌표계, 또는 몸체 좌표계입니다.',
  'A frame fixed in the surroundings is the world frame. A frame that turns with the object is its local frame, also called its body frame.'),
 ('12',3,
  '이번에는 피치를 음의 구십 도로 바꿉니다. 이때는 헤딩과 뱅크를 더합니다. 헤딩 삼십 도에 뱅크 십 도를 더하면 사십 도가 됩니다. 따라서 헤딩 사십 도와 뱅크 영도로 적어도 같은 자세입니다.',
  'Now change pitch to negative ninety degrees. Heading and bank now add. Thirty degrees of heading plus ten degrees of bank makes forty degrees. Heading forty degrees and bank zero therefore represents the same orientation.'),
 ('15',3,
  '입력이 마이너스 파이일 때는 이 조건이 참이라 플러스 파이로 바뀝니다. 파이의 절반은 처음부터 정해 둔 범위에 들어 있습니다. 이때는 조건이 거짓이므로 입력값 그대로 남습니다.',
  'For an input of minus pi, the condition is true and the result becomes plus pi. Half of pi already lies within the chosen interval. The condition is false, so that input remains unchanged.')]
outline=P/'planning/outline.md';text=outline.read_text(encoding='utf8');records=[]
for sid,index,new_ko,new_en in changes:
 k=next(s for s in ko['scenes'] if s['id']==sid);e=next(s for s in en['scenes'] if s['id']==sid);l=next(s for s in lesson['scenes'] if s['id']==sid)
 old=k['lines'][index]
 assert old!=new_ko and old==l['ko'][index]
 assert text.count(old)==1,(sid,'outline paragraph count')
 records.append(dict(scene=sid,paragraph=index+1,oldKo=old,newKo=new_ko,oldEn=e['lines'][index],newEn=new_en))
 text=text.replace(old,new_ko);k['lines'][index]=new_ko;e['lines'][index]=new_en;l['ko'][index]=new_ko;l['en'][index]=new_en
assert sum(len(s['lines']) for s in ko['scenes'])==157
for key,value in [('ko',ko),('en',en),('lesson',lesson)]: save(files[key],value)
outline.write_text(text,encoding='utf8')
save(P/'production/revision-v2/clarity-retake-plan.json',dict(schemaVersion=1,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Repeated ambiguous speech/ASR contexts; choose clearer complete sentences without changing the lesson or calculations.',scenes=['03','12','15'],beforeHashes=before,afterHashes={k:sha(v) for k,v in files.items()},changes=records,unchangedScenePcm='Preserve all other 23 source chunks byte for byte; only selected three scene takes require new synthesis and current-hash ASR.',fullOriginalAsr='production/local/revision-v2/whole-voice-asr.log',independentContexts='production/local/revision-v2/ambiguity-review/results.json',humanListening='pending'))
print('Updated exactly three paired paragraphs; 26 scenes and 157 paired paragraphs retained.')
