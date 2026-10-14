"""Protect just two utterance onsets; the disposable prelude is not final script."""
from pathlib import Path
import json,psutil
ROOT=Path(__file__).resolve().parents[3]
e=json.loads((ROOT/'projects/game-lighting-history-04/production/part1-onset-replacement-asr-execution-v209.json').read_text('utf-8-sig'))
if e.get('exitCode')!=0 or len(e['completed'])!=5:raise RuntimeError('Five-window worker must finish')
i=e['actualIdentity']
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid'])
 if abs(p.create_time()-i['createTime'])<.001 and p.cmdline()==i['command']:raise RuntimeError('Exact old recognizer alive')
source=Path(__file__).with_name('render-part1-scoped-repair-v176.py').read_text('utf-8')
source=source.replace('part1-scoped-repair-tts-request-v176','part1-protected-onsets-tts-request-v211').replace('part1-scoped-repair-tts-execution-v176','part1-protected-onsets-tts-execution-v211').replace('episode04Part1ScopedTtsV176','episode04Part1ProtectedOnsetsV211').replace('.tts176.tmp','.tts211.tmp')
exec(compile(source,str(__file__),'exec'))
