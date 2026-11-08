from pathlib import Path
import json,shutil,datetime,hashlib
P=Path(__file__).resolve().parents[1];L=P/'production/local'
current=json.loads((L/'timeline.json').read_text('utf-8'))
assert (L/'captions.json').exists()
alignment=json.loads((L/'alignment-review.json').read_text('utf-8'))
assert alignment['asrSha256']==hashlib.file_digest((L/'qa/narration.timestamps.json').open('rb'),'sha256').hexdigest()
old=json.loads((L/'before-scene15-repair/timeline.json').read_text('utf-8'))
preserved=[]
for a,b in zip(old['scenes'],current['scenes']):
 assert a['id']==b['id']
 if a['id']!='15':
  assert a['sourceSha256']==b['sourceSha256'] and a['frames']==b['frames']
  preserved.append(a['id'])
record={'repairedParagraph':'15','firstTwoTakesOmittedOpeningSentence':True,'replacementOpening':'이제 완성한 캐릭터 옆에 배경을 놓아 보겠습니다.','unchangedTakeIds':preserved,'currentDuration':current['duration'],'reason':'Retain the background transition meaning, rewrite its opening to obtain a complete Qwen take. No unrelated TTS regeneration.'}
(P/'production/paragraph15-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
B=L/'visual/preflight-revisions'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');B.mkdir(parents=True)
for id in ['15','20','27','28']:
 for suffix in ['.mp4','.mp4.json']:
  f=L/'visual'/('scene-'+id+suffix)
  assert f.resolve().is_relative_to(L.resolve())
  shutil.move(f,B/f.name)
print(B)
