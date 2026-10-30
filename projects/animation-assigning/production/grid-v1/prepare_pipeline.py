"""Prepare the existing conservative media pipeline for A01, without running jobs."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
R=H.parents[3]
old=R/'projects/kind-to-beginners/production/botw-v4'
records=[]
for name in ['audio_pipeline.py','video_pipeline.py','caption_pipeline.py']:
 src=old/name;raw=src.read_text('utf8')
 raw=raw.replace('D29 BOTW','A01 animation').replace('for D22.','for A01.').replace('Wrong isolated D29 revision','Wrong isolated animation revision')
 if name=='audio_pipeline.py':
  raw=raw.replace("approval=read(Path(__file__).resolve().parent/'authorization.json')", "approval=read(Path(__file__).resolve().parent/'authorization.json')\n    batch=policy['finiteBatchAuthorizations']['animation-18-20261031']\n    if not batch.get('productionAuthorized') or 'A01' not in batch.get('episodeIds',[]):\n        raise ValueError('A01 batch authorization is not active')")
  raw=raw.replace("'controlSelectionChanged':False", "'controlSelectionChanged':False,'batchAuthorization':'animation-18-20261031'")
 dst=H/name
 assert not dst.exists(),'Preserve later pipeline changes: '+name
 dst.write_text(raw,encoding='utf8')
 records.append({'source':src.relative_to(R).as_posix(),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'newFile':dst.relative_to(R).as_posix(),'newSha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(H/'pipeline-provenance.json').write_text(json.dumps({'files':records,'jobsStarted':False,'scope':'A01 only; read helpers reused, foreign project files unchanged'},indent=2)+'\n',encoding='utf8')
print('Prepared three media pipeline modules; no jobs started')
