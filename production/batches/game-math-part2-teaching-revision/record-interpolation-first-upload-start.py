"""Persist an actual Studio ID before transfer completion; never claim delivery."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'projects/game-math-interpolation-paths-v2/publishing/youtube-upload.json'
d=json.loads(p.read_text(encoding='utf8'))
assert d.get('videoId') in [None,'_SzbJR4R6OI']
d['videoId']='_SzbJR4R6OI';d['videoUrl']='https://youtu.be/_SzbJR4R6OI'
d['uploadStartedAt']=datetime.datetime.now().astimezone().isoformat()
d['status']='actual Studio transfer started; settings and processing incomplete'
d['uploadDialogObserved']='4% upload; metadata/thumbnail/PART2/Korean/Education/not-for-kids/paid-no/AI-yes saved; ads enabled and self-assessment none submitted'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
