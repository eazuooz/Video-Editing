"""One unchanged onset repair, only after the current single CPU worker exits."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
previous=json.loads((BASE/'part1-selected-actions-asr-execution-v182.json').read_text('utf-8-sig'))
if not previous.get('endedAt') or previous.get('exitCode')!=0 or len(previous.get('completed',[]))!=74:
 raise RuntimeError('The existing74-window recognizer has not completed; no GPU lease or TTS state was created')
import psutil
identity=previous['actualIdentity']
if psutil.pid_exists(identity['pid']):
 p=psutil.Process(identity['pid'])
 if abs(p.create_time()-identity['createTime'])<.001 and p.cmdline()==identity['command']:
  raise RuntimeError('The exact previous CPU worker is still alive; do not overlap jobs')
me=psutil.Process();allowed={p.pid for p in me.parents()}|{me.pid}
for p in psutil.process_iter(['pid','name','cmdline']):
 if p.pid in allowed:continue
 try:
  name=(p.info['name'] or '').lower();command=' '.join(p.info['cmdline'] or []).lower()
  if 'game-lighting-history' in command and ('ffmpeg' in name or any(x in command for x in ['review-part1-selected-actions-v182.py','render-part1-onset-repair-v196.py','render-part1-scoped-repair-v176.py'])):
   raise RuntimeError('Another owned heavy media worker is alive; do not overlap jobs')
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
request=json.loads((BASE/'part1-onset-repair-tts-request-v196.json').read_text('utf-8-sig'))
if request['repairIds']!=['runtime-texture-size'] or len(request['preservedTakes'])!=36:
 raise RuntimeError('One exact onset repair and36 preserved current takes required')
# Reuse the already observed PCM16 tail gate and exclusive handoff implementation.
source=(Path(__file__).with_name('render-part1-scoped-repair-v176.py')).read_text('utf-8')
source=source.replace('part1-scoped-repair-tts-request-v176','part1-onset-repair-tts-request-v196').replace('part1-scoped-repair-tts-execution-v176','part1-onset-repair-tts-execution-v196').replace('episode04Part1ScopedTtsV176','episode04Part1OnsetTtsV196').replace('.tts176.tmp','.tts196.tmp').replace('part1-scoped-repairs-','part1-onset-repair-')
exec(compile(source,str(__file__),'exec'))
