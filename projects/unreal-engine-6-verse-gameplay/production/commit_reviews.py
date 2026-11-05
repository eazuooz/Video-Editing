"""Commit only the two delivered review revisions and their rows with the repo's isolated-index writer."""
from pathlib import Path
import importlib.util, json, sys, re
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3]
engine_path=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
mod=importlib.util.spec_from_file_location('review_commit',engine_path)
engine=importlib.util.module_from_spec(mod);mod.loader.exec_module(engine)
C='shared/publishing/video-production-control.json'; W=engine.W; D=engine.D
B='production/batches/animation-18-20261031/'
CHECK=B+'checkpoint.json'; TABLE=B+'research/review-table.json'; HTML=B+'research/review-table.html'
engine.SHARED={C,W,D,CHECK,TABLE,HTML}
UE='unreal-engine-6-verse-gameplay';A02='animation-exaggeration';REV='fighters-v4-kula-lili'
def overlay(name,raw,spec):
    if name==CHECK:
        data=engine.load(raw)
        if data.get('currentEpisode')=='A02':
            for key,val in spec['animationCheckpoint'].items():
                if data.get(key)!=val:raw=engine.patch(raw,[key],val)
        return raw
    if name==TABLE:
        idx=next(i for i,row in enumerate(engine.load(raw)['rows']) if row['episode']=='A02')
        for key,value in spec['animationTableRow'].items():
            if engine.load(raw)['rows'][idx].get(key)!=value:raw=engine.patch(raw,['rows',idx,key],value)
        return raw
    if name==HTML:
        pattern=rb'<tr><td data-label="[^"]*">A02</td>.*?</tr>'
        assert len(re.findall(pattern,raw,flags=re.S))==1
        return re.sub(pattern,lambda _:spec['animationHtmlRow'].encode('utf-8'),raw,flags=re.S)
    if name==C:
        for key,value in spec['grants'].items():
            path=['scopedProductionAuthorizations',key]
            if engine.at(engine.load(raw),path)!=(True,value):raw=engine.patch(raw,path,value)
        return raw
    if name==W:
        rows=engine.load(raw)['rows']
        for row in spec['rows']:
            matches=[i for i,x in enumerate(rows) if x['id']==row['id']]
            if not matches:
                assert row['id']=='S-UE6'
                raw=engine.patch(raw,['rows','append'],row)
            else:
                idx=matches[0];assert len(matches)==1
                for key,value in row.items():
                    if key=='evidence' and row['id']=='A02':
                        for evidence in value:
                            if evidence not in engine.load(raw)['rows'][idx]['evidence']:
                                raw=engine.patch(raw,['rows',idx,'evidence','append'],evidence)
                    elif engine.load(raw)['rows'][idx].get(key)!=value:
                        raw=engine.patch(raw,['rows',idx,key],value)
            rows=engine.load(raw)['rows']
        return raw
    assert name==D
    bom=raw[:3] if raw.startswith(b'\xef\xbb\xbf') else b''
    lines=raw.decode('utf-8-sig').splitlines(keepends=True)
    for ident,value in spec['table'].items():
        ix=[i for i,s in enumerate(lines) if s.startswith('| '+ident+' | ')]
        if ix:
            assert len(ix)==1
            i=ix[0];tail=lines[i][len(lines[i].rstrip('\r\n')):];lines[i]=value+tail
        else:
            assert ident=='S-UE6'
            anchor=next(i for i,s in enumerate(lines) if s.startswith('| S03 | '))
            nl='\r\n' if lines[anchor].endswith('\r\n') else '\n'
            lines.insert(anchor+1,value+nl)
    return bom+''.join(lines).encode()
def validate(spec):
    assert spec['scope']=='ue6-and-a02-two-local-reviews'
    assert set(spec['table'])=={x['id'] for x in spec['rows']}=={'S-UE6','A02'}
    assert set(spec['grants'])=={UE,A02+'-'+REV}
    for name in spec['ownedPaths']:
        p=R/name
        assert p.is_file() and p.resolve().is_relative_to(R) and '/local/' not in name and '__pycache__' not in name
        assert name.startswith(('projects/'+UE+'/',f'projects/{A02}/script/{REV}/',f'projects/{A02}/production/{REV}/','GameAnimationSample/Content/YamyamA02/fighters_v4_motion18/')) or name==f'projects/{A02}/project.json'
        assert p.suffix.lower() in {'.py','.js','.cjs','.json','.txt','.md','.html','.umap','.uasset','.tsx','.ts','.cs','.gd','.tscn','.godot','.uid'} or p.name=='.gitignore'
    return sorted(set(spec['ownedPaths'])|engine.SHARED)
engine.overlay=overlay;engine.validate=validate
orig_git=engine.git
def literal_git(*args,**kwargs):
    return orig_git('-c','core.quotepath=false',*args,**kwargs)
engine.git=literal_git
if __name__=='__main__':engine.main()
