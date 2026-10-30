"""Exact A01/A02 state overlays with foreign staging and shared bytes preserved."""
from pathlib import Path
import importlib.util, json, sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
module=importlib.util.spec_from_file_location('delivery_tx',ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
engine=importlib.util.module_from_spec(module);module.loader.exec_module(engine)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md'
engine.SHARED={W,D}
ALLOWED={'slug','plannedSlug','productionComplete','productionStatus','reviewStarted','reviewStatus',
         'executionStatus','localMasterAvailable','deliveryLedger','captionedMasterSha256','updatedAt'}
def overlay(name,raw,spec):
    if name==W:
        for item in spec['rows']:
            rows=engine.load(raw)['rows'];indices=[i for i,r in enumerate(rows) if r['id']==item['id']]
            assert len(indices)==1;n=indices[0]
            for c in item['changes']:
                k=c['field'];assert k in ALLOWED
                row=engine.load(raw)['rows'][n];present=k in row;current=row.get(k)
                assert {'exists':present,'value':current} in c['expected'] or (present and current==c['value']),('Concurrent selected row',item['id'],k)
                raw=engine.patch(raw,['rows',n,k],c['value'])
            evidence=engine.load(raw)['rows'][n]['evidence']
            for link in item['appendEvidence']:
                assert link.startswith('projects/animation-') and link.endswith('.json')
                if link not in evidence:evidence.append(link)
            raw=engine.patch(raw,['rows',n,'evidence'],evidence)
        raw=engine.patch(raw,['animationSeriesPlan','status'],spec['seriesStatus'])
        return raw
    if name==D:
        text=raw.decode('utf-8-sig');bom=b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
        for item in spec['markdownRows']:
            lines=text.splitlines(keepends=True)
            matches=[l for l in lines if l.startswith('| '+item['id']+' | ')]
            assert len(matches)==1;line=matches[0]
            assert line.rstrip('\r\n') in [item['expected'],item['value']]
            ending=line[len(line.rstrip('\r\n')):]
            text=''.join(item['value']+ending if l==line else l for l in lines)
        return bom+text.encode('utf-8')
    raise AssertionError(name)
def validate(spec):
    assert spec['scope']=='animation-A01-A02-delivery-status'
    assert {x['id'] for x in spec['rows']}=={'A01','A02'}
    paths=spec['ownedPaths'];assert len(paths)==len(set(paths))
    prefixes=['projects/animation-assigning/','projects/animation-exaggeration/','production/batches/animation-18-20261031/']
    for name in paths:
        p=ROOT/name
        assert any(name.startswith(x) for x in prefixes) and '/local/' not in name
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file() and p.suffix in {'.py','.json'}
    return sorted(paths)+sorted(engine.SHARED)
engine.overlay=overlay;engine.validate=validate
if __name__=='__main__':engine.main()
