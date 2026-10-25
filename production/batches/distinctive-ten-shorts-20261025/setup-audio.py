"""Adapt the inspected local Short audio tools to this finite batch, without jobs."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
base=R/'projects/shorts-portal-seamless-traversal/production'
batch=json.loads((B/'batch.json').read_text(encoding='utf8'))
auth="control.get('scopedBatchAuthorizations',{}).get('explicit-ten-distinctive-shorts-20261025',{})"
guard='''def guard():
    control=read(R/'shared/publishing/video-production-control.json')
    auth=control.get('scopedBatchAuthorizations',{}).get('explicit-ten-distinctive-shorts-20261025',{})
    project=read(P/'project.json')
    if auth.get('status')!='active' or P.name not in auth.get('slugs',[]) or not auth.get('fullProductionAuthorized') or project.get('currentRevision')!=REVISION:
        raise RuntimeError('Explicit ten-Short scope changed; preserve work.')
    plan=read(P/'planning/production-plan.json')
    if not plan.get('independentFootageViewed') or not plan.get('scriptFinalized'):
        raise RuntimeError('Source and script review remain incomplete.')
    return control
'''
for row in batch['projects']:
    p=R/'projects'/row['slug']/'production';p.mkdir(parents=True,exist_ok=True)
    ar=(base/'audio_revision.py').read_text(encoding='utf8')
    ar=ar[:ar.index('def guard():')]+guard
    ar=ar.replace("REVISION = 'portal-camera-guides-v3'","REVISION = 'distinctive-ten-v1'")
    ar=ar.replace('Finite audio paths and authorization for the selected Interior Mapping revision.','Finite audio paths and authorization for the selected ten-Short batch.')
    (p/'audio_revision.py').write_text(ar,encoding='utf8')
    for name in ['render-voice.py','assemble-paragraphs.py','transcribe.py','time-captions.py','finish-audio.py','finish-video.py']:
        code=(base/name).read_text(encoding='utf8').replace('shorts-portal-seamless-traversal',row['slug'])
        code=code.replace("control.get('portalTraversalShortsAuthorization',{})",auth)
        (p/name).write_text(code,encoding='utf8')
    manifest=json.loads((base/'tts-manifest.json').read_text(encoding='utf8'))
    manifest['slug']=row['slug'];manifest['revision']='distinctive-ten-v1'
    manifest['paths']['script']=f"projects/{row['slug']}/script/narration.spoken.ko.json"
    manifest['tts']['outputDir']=f"projects/{row['slug']}/production/local/audio-v1/voice"
    manifest['tts']['gpuProfileReason']='Only after user game exits; no CPU fallback or live-game GPU occupancy inferred.'
    (p/'tts-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Prepared ten finite audio pipelines; no TTS or render started.')
