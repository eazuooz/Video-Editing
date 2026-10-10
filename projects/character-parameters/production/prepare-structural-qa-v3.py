"""Derive the same reviewed CPU-only QA worker for one repaired scene."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
text=(BASE/'extract-black-structural-qa-v2.py').read_text('utf-8-sig')
text=text.replace('structural-v2.mp4','structural-v3.mp4').replace("QA=OUT/'qa-v2'","QA=OUT/'qa-v3'").replace('qa-v2.json','qa-v3.json').replace('qa-v2.json','qa-v3.json').replace('execution-v2.json','execution-v3.json').replace('whole-decode-v2.log','whole-decode-v3.log').replace('extraction-v2.log','extraction-v3.log').replace(',3601)',',721)').replace('frames=3601','frames=721')
text=text.replace("['05-useful-strength','06-role-and-limitation','07-state-not-base','09-condition-and-time','11-cost-and-summary']","['09-condition-and-time']")
text=text.replace('for local in [a+30,a+step-18]:','for local in sorted(set([a+30,a+step-18]+(list(range(240,301,3)) if j==1 else []))):')
path=BASE/'extract-black-structural-qa-v3.py'
assert not path.exists(); path.write_text(text,'utf-8')
print('Prepared one-scene v3 QA with explicit samples through the repaired fade boundary; not executed.')
