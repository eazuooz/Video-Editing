"""Read every receipt property with exact common-text references; no mutation."""
from pathlib import Path
import json, hashlib, sys
ROOT=Path(__file__).resolve().parents[3]
base=json.loads((ROOT/'projects/game-math-camera-projection/publishing/youtube-upload.json').read_text('utf-8-sig'))
slug=sys.argv[1]
path=ROOT/'projects'/slug/'publishing/youtube-upload.json'
cur=json.loads(path.read_text('utf-8-sig'))
print('FILE',path.relative_to(ROOT).as_posix(),'SHA',hashlib.sha256(path.read_bytes()).hexdigest())
for key,value in cur.items():
    if key in ('metadata','englishMetadata'):
        language='ko' if key=='metadata' else 'en'
        body=cur.get('descriptionBody',{}).get(language)
        footer=base[key]['description'][len(base['descriptionBody'][language]):]
        result=dict(value)
        if body and value.get('description')==body+footer:
            result['description']='<exact descriptionBody below + exact camera-projection footer already read>'
        print(key,json.dumps(result,ensure_ascii=False))
    elif key=='platformEvidence':
        result=dict(value)
        proofs=result.pop('proofs',[])
        print(key,json.dumps(result,ensure_ascii=False),'proofs',len(proofs))
        for item in proofs:
            print('PROOF',item['path'],item['sha256'])
    elif value==base.get(key):
        print(key,'<exact camera-projection subtree already read>')
    else:
        print(key,json.dumps(value,ensure_ascii=False))
