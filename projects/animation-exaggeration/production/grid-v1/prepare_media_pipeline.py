"""Reuse A01's verified cut/still compositor for explicitly authorized A02."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
R=H.parents[3]
SOURCE=R/'projects/animation-assigning/production/grid-v1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    for name in ['video_pipeline.py','render_still.py','prepare_timing_plan.py']:
        src=SOURCE/name;dest=H/name
        assert not dest.exists(),('Preserve existing implementation',name)
        value=src.read_text(encoding='utf-8-sig').replace('animation-assigning','animation-exaggeration').replace('A01','A02')
        dest.write_text(value,encoding='utf-8')
        rows.append({'source':src.relative_to(R).as_posix(),'sourceSha256':digest(src),
                     'target':dest.relative_to(R).as_posix(),'targetSha256':digest(dest),
                     'changes':'Episode/slug scope only; separate A02 ratio record remains mandatory.'})
    aliases=R/'projects/animation-exaggeration/script/grid-v1/caption-aliases.json'
    assert not aliases.exists()
    aliases.write_text(json.dumps({'110cm':'백십센티미터','100cm':'백센티미터','10cm':'십센티미터','0cm':'영센티미터'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'media-pipeline-provenance.json').write_text(json.dumps({'files':rows,'jobsStarted':False,
        'alignmentOnlyNumerals':{'path':aliases.relative_to(R).as_posix(),'sha256':digest(aliases)},
        'audioAndCanonicalScriptsModified':False},indent=2)+'\n',encoding='utf-8')
    print('Prepared A02 compositor and alignment-only numeral aliases; no media job started.')
if __name__=='__main__':main()
