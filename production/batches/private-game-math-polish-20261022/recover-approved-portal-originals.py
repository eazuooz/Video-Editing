"""Recover only original Portal2 inputs expressly covered by the10-slot exception."""
import datetime
from polish_common import *

evidence=B/'portal-original-resolution-exception.json';approval=read(evidence)
receipts=read(B/'portal-original-recovery.json') if (B/'portal-original-recovery.json').exists() else {}
publisher=read(B/'publisher-source-restoration.json')
paths={path for episode in approval['episodes'].values() for slot in episode['scenes'].values() for path in slot['sourcePaths']}
for name in sorted(paths):
    owner=next((ident,sid) for ident,ep in approval['episodes'].items() for sid,s in ep['scenes'].items() if name in s['sourcePaths'])
    e=Episode(owner[0]);e.authorized();path=R/name
    assert approved_original_resolution(e,owner[1],path)
    previous=receipts.get(name,{})
    if previous.get('status')=='restored' and path.exists() and sha(path)==previous['sha256']:
        continue
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.stem=='yFRbGppLaUI':
        assert path.exists(),'Original selected YouTube source must be recovered separately with best available video.'
        metadata=path.with_suffix('.info.json');source_url='https://www.youtube.com/watch?v=yFRbGppLaUI'
    else:
        selected=publisher[name];source_url=selected['sourceUrl'];metadata=R/selected['metadata']
        streams=probe(source_url)['streams'];v=max((v for v in streams if v['codec_type']=='video'),key=lambda v:v['width']*v['height'])
        if not path.exists():
            e.ff(['-i',source_url,'-map',f'0:{v["index"]}','-an','-c:v','copy','-movflags','+faststart',path],f'portal-restore-{path.stem}.log')
    v=video(path);info=probe(path)
    receipts[name]={'status':'restored','sourceUrl':source_url,'metadata':rel(metadata),'metadataSha256':sha(metadata),
        'sha256':sha(path),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'duration':info['format']['duration'],
        'sourceNativeFhd':v['width']>=1920 and v['height']>=1080,'exceptionEvidence':rel(evidence),'exceptionSha256':sha(evidence),
        'rights':'Original selected Valve gameplay source and prior policy record retained; no source audio used.',
        'currentSourceCutReview':'pending','restoredAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save(B/'portal-original-recovery.json',receipts)
    print(path.stem,v['width'],v['height'],'original recovered; cut/track review pending',flush=True)
