"""Prepare downstream readers for corrected-runtime ASR; do not run media."""
from pathlib import Path
import py_compile,json
B=Path(__file__).resolve().parent
s=(B/'prepare-motion-current17-contexts-v3.py').read_text('utf-8')
s=s.replace('whole-asr-execution-v2','whole-asr-execution-v3').replace('whole-asr-v2/','whole-asr-v3/').replace('plan-proposed-v3.json','plan-proposed-v4.json')
p=B/'prepare-motion-current17-contexts-v4.py';assert not p.exists();p.write_text(s,'utf-8');py_compile.compile(str(p),doraise=True)
s=(B/'prepare-motion-current17-captions-v2.py').read_text('utf-8').replace('contexts-asr-v2/','contexts-asr-v3/')
p=B/'prepare-motion-current17-captions-v3.py';assert not p.exists();p.write_text(s,'utf-8');py_compile.compile(str(p),doraise=True)
print(json.dumps(dict(preparedOnly=True,contextBuilderVersion=4,captionBuilderVersion=3,allMediaRuns=0,allApprovals=False)))
