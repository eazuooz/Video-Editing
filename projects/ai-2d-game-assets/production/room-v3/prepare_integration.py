"""Create v3 integration scripts without overwriting v2 render/audio outputs."""
from pathlib import Path
H=Path(__file__).resolve().parent;H2=H.parent/'room-v2'
for name in ['build_timing.py','build_captions.py','caption_layout.cjs','assemble.py','technical_qa.py','deliver.py','serve-review.cjs','render-scenes.cjs']:
 s=(H2/name).read_text('utf8').replace('production/local/room-v2','production/local/room-v3').replace('ai-2d-room-v2/video','ai-2d-room-v3/video').replace('ai-2d-game-assets.room-v2.','ai-2d-game-assets.room-v3.')
 if name=='caption_layout.cjs':s=s.replace('../local/room-v2','../local/room-v3')
 if name=='build_timing.py':
  s=s.replace("f=(L/'voice/chunks'/f'{ident}-scene.wav') if ident.startswith('R') else Path(next(x['source'] for x in original['scenes'] if x['id']==ident))", "f=(L/'voice/chunks'/f'{ident}-scene.wav') if (L/'voice/chunks'/f'{ident}-scene.wav').exists() else (P/'production/local/room-v2/voice/chunks'/f'{ident}-scene.wav') if ident.startswith('R') else Path(next(x['source'] for x in original['scenes'] if x['id']==ident))")
 if name=='build_captions.py':
  s=s.replace("parts=json.loads((H/'caption-clauses.json').read_text('utf8'))['scenes']", "parts=json.loads((H/'caption-clauses.json').read_text('utf8'))['scenes']; oldparts=json.loads((H.parent/'room-v2/caption-clauses.json').read_text('utf8'))['scenes']; parts += [p for p in oldparts if p['id'] not in {r['id'] for r in parts}]")
  s=s.replace("if not ident.startswith('R'):","if ident.isdigit():")
  s=s.replace("asr=json.loads((L/'asr'/f'{ident}.json').read_text('utf8'))", "asrfile=L/'asr'/f'{ident}.json'; asrfile=asrfile if asrfile.exists() else P/'production/local/room-v2/asr'/f'{ident}.json'; asr=json.loads(asrfile.read_text('utf8'))")
  s=s.replace("(L/'asr'/f'{ident}.json').open('rb')", "asrfile.open('rb')")
 if name=='assemble.py':s=s.replace("row['id'].startswith('R')", "not row['id'].isdigit()")
 if name=='technical_qa.py':s=s.replace('==46','==51').replace("'sceneCount':46", "'sceneCount':51").replace("'newPcmScenes':16", "'newPcmScenes':21").replace("row['id'].startswith('R')", "not row['id'].isdigit()")
 if name=='deliver.py':s=s.replace('46','51').replace('room-v2','room-v3')
 if name=='serve-review.cjs':s=s.replace('room-v2','room-v3')
 if name=='render-scenes.cjs':
  s=s.replace("s.id.startsWith('R')", "!/^\\d+$/.test(s.id)")
  s=s.replace("require('./game-runtime.cjs')", "require('../room-v2/game-runtime.cjs')")
  # These are unchanged actual tool inputs, deliberately reused in v3.
  for sub in ['pixeloe/comparison.png','forge-walk/atlas.png','codixel/reading-ruler.png','codixel/reading-owners.png','forge-walk/frames/frame-']:
   s=s.replace('production/local/room-v3/'+sub,'production/local/room-v2/'+sub)
  s=s.replace("['횃불','비','눈']", "['불꽃','비','눈']")
 (H/name).write_text(s,'utf8')
print('Prepared isolated v3 integration scripts.')
