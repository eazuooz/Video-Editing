"""Scoped A02 commit with exact shared row overlays and foreign staging preserved."""
from pathlib import Path
import importlib.util,sys
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;R=H.parents[3]
s=importlib.util.spec_from_file_location('animation_delivery',R/'production/batches/animation-18-20261031/commit_delivery_status.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
base_overlay=m.engine.overlay
def overlay(name,raw,spec):
 if name!=m.D:return base_overlay(name,raw,spec)
 text=raw.decode('utf-8-sig');bom=b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
 for item in spec['markdownRows']:
  lines=text.splitlines(keepends=True);matches=[line for line in lines if line.startswith('| A02 | ')]
  assert item['id']=='A02' and len(matches)==1
  line=matches[0];assert line.rstrip('\r\n') in item['expectedVariants']+[item['value']]
  ending=line[len(line.rstrip('\r\n')):]
  text=''.join(item['value']+ending if x==line else x for x in lines)
 return bom+text.encode('utf-8')
def validate(spec):
 assert spec['scope']=='animation-A02-fighters-v2-delivery'
 assert [x['id'] for x in spec['rows']]==['A02'] and [x['id'] for x in spec['markdownRows']]==['A02']
 paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
 prefixes=['projects/animation-exaggeration/production/fighters-v2/','projects/animation-exaggeration/script/fighters-v2/']
 exact={'projects/animation-exaggeration/project.json','production/batches/animation-18-20261031/checkpoint.json','production/batches/animation-18-20261031/research/review-table.json','production/batches/animation-18-20261031/research/review-table.html'}
 for name in paths:
  p=R/name
  assert any(name.startswith(x) for x in prefixes) or name in exact
  assert p.resolve().is_relative_to(R.resolve()) and p.is_file() and '/local/' not in name
  assert p.suffix in {'.py','.json','.md','.html','.cjs'} or p.name in {'narration.spoken-ko.txt','additional-narration.ko.txt'}
 return sorted(paths)+sorted(m.engine.SHARED)
m.engine.validate=validate;m.engine.overlay=overlay
if __name__=='__main__':m.engine.main()
