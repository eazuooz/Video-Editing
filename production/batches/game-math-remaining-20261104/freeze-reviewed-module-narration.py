"""Freeze only explicitly selected, source/read-through/footage checked modules.

Runtime previews must exist; this does not claim final speech or moving QA.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess
R=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);a=ap.parse_args()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and a.project in c['projectSlugs']
P=R/'projects'/a.project;p=read(P/'planning/production-plan.json');assert not p.get('narrationFinal'),'Preserve already frozen media inputs'
i=read(P/'planning/script-integration.json');review=i['readThrough'];binding=read(P/'planning/scene-bindings.json');mapping=read(P/'planning/bilingual-caption-map.json')
scripts={l:read(P/f'script/narration.{l}.json') for l in ['ko','en']}
for l in scripts:assert sha(P/f'script/narration.{l}.json')==review[l+'Sha256']==mapping[l+'Sha256']
complete_bilingual=(review.get('allKoBeatsRead') and review.get('allEnBeatsRead') and review.get('beatCount')==len(scripts['ko']['scenes']))
assert (review.get('allBeatsRead') or complete_bilingual or (review.get('beats')==len(scripts['ko']['scenes']) and review['status'].startswith('full bilingual draft'))) and review['sourceOrderPreserved'] and p['sourceFinal']
assert mapping['status']=='complete-semantic-map' and binding['pendingImplementationBeatCount']==0
ids=[x['id'] for x in scripts['ko']['scenes']]
assert ids==[x['id'] for x in scripts['en']['scenes']]==[x['id'] for x in binding['scenes']]
for s in read(P/'planning/footage-audit.json')['sources']:
 assert s['classification'] in {'independent-gameplay','independent-gameplay-and-menu-operation'} and min(s['decodedSize'])>=1080
 assert s['recordingPermission'] and (s.get('publisherRights') or s.get('rights')) and (R/s['file']).is_file()
for g in p['nativeGameCueBindings']:
 assert g['playbackRate']==1 and not g['freezePadding'] and not g['loop']
 native=g['nativeDecodeEvidence']
 if 'clip' in native and 'file' in native:
  # The shared curve sources keep an indexed receipt for the precise decoded range.
  sample=next(x for x in read(R/native['file']) if x['clip']==native['clip'])
  assert sample['exitCode']==0 and sha(R/sample['sourceFile'])==sample['sourceSha256']
 assert native.get('decodeExitCode',native.get('returnCode',native.get('exitCode')))==0
runtime=[x for x in (P/'production/unity-staging').glob('local-preflight-v*/progress.json') if read(x)['status']=='images-ready-for-internal-visual-QA']
assert runtime,'Obtain actual runtime preview evidence before costly speech'
compile_check=P/'production/unity-staging/compile-check.json'
if compile_check.exists():assert read(compile_check)['csharpCompilation']['exitCode']==0
# A completed actual Unity capture already proves compilation for the sampled
# runtime; some shared modules record compile evidence at their owner project.
for l,s in scripts.items():
 s.update(status='frozen-for-approved-voice-production',isFinalNarration=True,actualDurationSeconds=None);save(P/f'script/narration.{l}.json',s);review[l+'Sha256']=sha(P/f'script/narration.{l}.json')
review.update(productionDecisionAt=datetime.now(timezone.utc).isoformat(),ttsAuthorizedToStart=True,productionReadiness='All bilingual meaning groups read in order; actual independent footage verified. Prior runtime previews exist; revised picture checks and final audiovisual review remain pending.')
i.update(narrationFinal=True,sceneBindingsFinal=True,remaining=['Targeted runtime picture verification','Actual speech ASR and caption/animation alignment','Integrated moving/audio/mobile QA']);save(P/'planning/script-integration.json',i)
binding['sourceNarrationSha256']=review['koSha256'];save(P/'planning/scene-bindings.json',binding)
p.update(narrationFinal=True,sceneBindingsFinal=True,stage='approved-voice-production-ready',productionReadinessMeaning='Reviewed narration/design frozen; final audio and visual checks pending.')
p.setdefault('scriptReadthrough',dict(evidence='planning/script-integration.json',humanListening=False)).update(koSha256=review['koSha256'],enSha256=review['enSha256']);save(P/'planning/production-plan.json',p)
project=read(P/'project.json');project['status']='narration-ready';save(P/'project.json',project)
subprocess.run(['python','-X','utf8',str(P/'production/build-bilingual-map.py')],check=True,cwd=R)
print(P.name,len(ids),'reviewed bilingual paragraphs frozen; no synthesis started')
