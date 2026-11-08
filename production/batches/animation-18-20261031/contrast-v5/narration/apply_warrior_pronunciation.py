"""Canonical Roman I display with a separate spoken-number alias."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;p=H/'source-verified-revisions.json';d=json.loads(p.read_text('utf8'))
c=next(c for e in d['episodes']if e['id']=='A08'for c in e['changes']if c['id']=='001')
assert c['ko']=='링 피트 어드벤처의 전사 자세 I를 보세요.'
c['spokenKo']='링 피트 어드벤처의 전사 자세 원을 보세요.'
c['pronunciationCorrection']={'display':'Warrior I Pose / 전사 자세 I','spokenNumber':'원','reason':'I identifies the first pose, not the English letter eye. Display and English wording are preserved.','priorTake':'Preserved but not adopted as final.'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
