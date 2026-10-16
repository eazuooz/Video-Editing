"""Reuse established checks with current paths and the combined sentence patch map."""
from pathlib import Path
import sys,json,argparse
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';D=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit/standalone-v3';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2'
a=argparse.ArgumentParser();a.add_argument('--check',choices=['integrity','asr','levels'],required=True);args=a.parse_args()
def reuse(file,replacements=()):
 p=D/file;s=p.read_text(encoding='utf8').replace("'production/local/reference-preserving-v2/edit'","'production/local/reference-preserving-v2/edit/standalone-v3'").replace("'projects/game-reward-planning/production/local/reference-preserving-v2/edit'","'projects/game-reward-planning/production/local/reference-preserving-v2/edit/standalone-v3'")
 for before,after in replacements:assert before in s;s=s.replace(before,after)
 exec(compile(s,str(p),'exec'),{'__file__':str(p)})
if args.check=='integrity':reuse('verify-output.py')
elif args.check=='asr':reuse('review-final-audio.py')
else:
 patches=json.loads((N/'leveled-patched/patch-map.json').read_text(encoding='utf8'));patches=[x for x in patches if x['id']!='frequent'];new=json.loads((O/'patch-evidence.json').read_text(encoding='utf8'))['patches']
 for x in patches:x['asrFile']=(N/'patches/asr'/f"{x['id']}.json").as_posix()
 for x in new:x['asrFile']=(N/'standalone-patches/asr'/f"{x['id']}.json").as_posix()
 (O/'combined-sentence-patches.json').write_text(json.dumps(patches+new,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 reuse('check-audio-levels.py',[("N/'leveled-patched/patch-map.json'","O/'combined-sentence-patches.json'"),("N/'patches/asr'/f\"{s['id']}.json\"","Path(s['asrFile'])"),('including3 replacement intervals','including6 replacement intervals')])
