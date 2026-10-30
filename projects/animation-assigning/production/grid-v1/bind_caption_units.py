"""Bind reviewed bilingual clauses to immutable current script inputs."""
from pathlib import Path
import hashlib
import json
import re

H=Path(__file__).resolve().parent
R=H.parents[3]
S=H.parents[1]/'script/grid-v1'
def read(p): return json.loads(p.read_text('utf-8-sig'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\s+','',s)

def main():
    source=S/'caption-units.json'
    reviewed=read(source)
    ko,en=read(S/'narration.ko.json'),read(S/'narration.en.json')
    assert reviewed['sourceKoSha256']==digest(S/'narration.ko.json')
    out={'slug':'animation-assigning','revision':'grid-v1',
         'status':'authored-paired-clauses-verified','timingLocked':False,
         'reviewedSource':{'path':source.relative_to(R).as_posix(),'sha256':digest(source)},
         'scriptInputs':[{'path':(S/n).relative_to(R).as_posix(),'sha256':digest(S/n),'bytes':(S/n).stat().st_size}
                         for n in ['narration.ko.json','narration.en.json','narration.spoken-ko.json']],
         'paragraphs':{}}
    for a,b in zip(ko['scenes'],en['scenes']):
        assert a['id']==b['id'] and len(a['lines'])==len(b['lines'])
        for i,(k,e) in enumerate(zip(a['lines'],b['lines'])):
            units=reviewed['byScene'][a['id']][str(i)]
            assert norm(''.join(u['ko'] for u in units))==norm(k)
            assert norm(''.join(u['en'] for u in units))==norm(e)
            out['paragraphs'][f"{a['id']}-p{i+1:02d}"]={
                'semanticPairingReviewed':True,
                'basis':'Complete KO/EN meaning and paired clause boundaries reviewed by playlist_title_audit; exact reconstruction validated. Actual audio/encoded timing pending.',
                'captionUnits':units}
    (H/'caption-units.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
    print(f"Bound {len(out['paragraphs'])} complete bilingual paragraphs")

if __name__=='__main__': main()
