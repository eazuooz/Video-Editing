"""Explicit sentence-group alignment after reading KO and EN side by side.

Pair (k,e) consumes k Korean sentences and e English sentences. Grouping joins
only corresponding meanings; actual start/end still come from spoken word ASR.
No narration or translation file is rewritten by this script.
"""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parents[1]
ONE=(1,1)
GROUPS={
0:[(2,1),ONE,ONE],1:[ONE]*4,2:[(2,1),ONE,ONE],3:[ONE,ONE,(2,1),ONE,ONE],4:[ONE]*4,
5:[ONE,(1,2),ONE,ONE,ONE],6:[ONE]*4,7:[ONE]*4+[(2,1),ONE],8:[ONE]*3+[(2,1),ONE],
9:[ONE,(2,1),(2,2),ONE],10:[(2,1),ONE,(2,1),ONE],11:[ONE]*3+[(2,2)],12:[(2,1)]+[ONE]*3,
13:[ONE]*3+[(2,1)],14:[ONE,(2,1),(2,1),ONE,ONE],15:[ONE]*3+[(2,1),ONE],
16:[ONE]*4,17:[(2,1)]+[ONE]*3,18:[ONE]*4+[(2,1)],19:[ONE,ONE,(2,1),ONE,(2,1)],
20:[(2,1)]+[ONE]*3,21:[(2,2),ONE,(2,1)],22:[(2,1)]+[ONE]*3,23:[ONE]*4,24:[ONE]*4,
25:[(3,1),(2,1),ONE],26:[ONE,ONE,(2,1),ONE],27:[ONE,ONE,(2,1),ONE,(2,1)],
28:[ONE,(2,1),ONE,ONE],29:[ONE]*4,30:[ONE,(2,1),ONE,ONE],31:[ONE,(2,1),ONE,ONE,ONE],
32:[ONE]*4,33:[(2,2),ONE,ONE],34:[ONE]*3+[(2,1)],35:[ONE]*3+[(2,1),ONE],
36:[ONE,ONE,(2,1),(2,1)],37:[ONE,(2,1),ONE,ONE],38:[ONE,ONE,(2,1)],39:[(3,1),ONE,ONE],
40:[ONE,ONE,(2,1),ONE],41:[(2,1),ONE,(2,1)],42:[(2,1),ONE,(2,1),ONE],43:[ONE]*4,
44:[(2,1)]+[ONE]*3,45:[ONE,(2,1),(2,1),ONE],46:[ONE]*4,47:[ONE]*4,
48:[(2,1)]+[ONE]*3,49:[ONE,ONE,(2,1),(2,1),ONE],50:[(2,1)]+[ONE]*3,51:[ONE]*4,
52:[ONE,ONE,(2,1),ONE,ONE],53:[(2,1)]+[ONE]*3,54:[ONE]*5,55:[ONE]*4,56:[ONE]*4,
57:[(2,1),ONE,ONE],58:[(3,1),ONE,ONE],59:[ONE,ONE,(2,1),ONE],60:[ONE]*6,
61:[(2,1),ONE,ONE],62:[(3,2),ONE],63:[ONE]*3,
64:[(2,1)]+[ONE]*3,65:[(2,1)]+[ONE]*3,66:[ONE,ONE,(2,1)],67:[(2,1),(2,1),ONE],
68:[(2,2),(2,1),ONE],69:[(2,1),ONE,ONE],70:[ONE,ONE,(2,1)],71:[ONE,ONE,(3,2)],
72:[ONE,(2,1),(2,2)],73:[ONE]*3,74:[(2,1),ONE,(2,1)],75:[ONE,ONE,(2,1),ONE],
76:[(2,1),ONE,ONE],77:[ONE,ONE,(2,1),ONE],78:[ONE,(2,1),ONE],
}
def main():
    kp=P/'script/narration.ko.json';ep=P/'script/narration.en.json'
    ko=json.loads(kp.read_text(encoding='utf-8'));en=json.loads(ep.read_text(encoding='utf-8'));rows=[]
    for k,e in zip(ko['scenes'],en['scenes']):
        sid=k['id'];a=[m.group().strip() for m in re.finditer(r'.+?(?:[.!?](?=\s|$)|$)',k['lines'][0]) if m.group().strip()];b=[v.strip() for v in re.split(r'(?<=[.!?])\s+',e['lines'][0]) if v.strip()]
        if int(sid) not in GROUPS:continue
        groups=GROUPS[int(sid)];assert sum(x for x,y in groups)==len(a),(sid,'KO',groups,len(a));assert sum(y for x,y in groups)==len(b),(sid,'EN',groups,len(b))
        ki=ei=0;out=[]
        for kn,en_ in groups:
            out.append({'koStart':ki,'koCount':kn,'enStart':ei,'enCount':en_,'ko':' '.join(a[ki:ki+kn]),'en':' '.join(b[ei:ei+en_])});ki+=kn;ei+=en_
        rows.append({'id':sid,'groups':out})
    record={'status':'complete-semantic-map' if len(rows)==len(ko['scenes']) else 'partial-do-not-render','koSha256':hashlib.sha256(kp.read_bytes()).hexdigest(),'enSha256':hashlib.sha256(ep.read_bytes()).hexdigest(),'basis':'Direct side-by-side sentence meaning review. Actual-word timing required next. English subdivisions use reading-length allocation within each corresponding group.','scenes':rows,'humanListening':False}
    (P/'planning/bilingual-caption-map.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'{len(rows)}/{len(ko["scenes"])} sentence groups reviewed')
if __name__=='__main__':main()
