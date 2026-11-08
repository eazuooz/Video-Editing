"""Record real component completion separately from full video completion."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
manifest=read(H/'renderer/integration-manifest.json');qa=read(H/'renderer/final-renderer-qa.json')
assert hashlib.sha256((H/'renderer/integration-manifest.json').read_bytes()).hexdigest()==qa['integrationManifestSHA256']
assert len(manifest['episodes'])==17 and manifest['A03Preserved']
rows=[r for e in manifest['episodes'] for r in e['rows']]
assert len(rows)==443 and all((R/r['output']).is_file() for r in rows)
facts={'explanationEpisodesReady':17,'explanationReplacementIntervals':443,'explanationMediaFrames':qa['totalFrames'],'explanationManifest':str((H/'renderer/integration-manifest.json').relative_to(R)).replace('\\','/'),'explanationManifestSha256':qa['integrationManifestSHA256'],'a15AddedFrames':230,'newFullMastersCompleted':0,'finalCombinedReviewReady':False,'finalFullVideoRenderRunningAtStatusCheck':False,'newFullRenderJobsStartedByThisScript':False,'remaining':['Source-matched KO/EN game-passage revisions, including KO/EN sentence alignment','Clean source and use-condition resolution for a subset of selected games','Changed passage TTS integration while preserving other PCM','Full picture/audio/caption assembly and final integrated review'],'scope':'Only approved17; A03 and all prior deliveries preserved; no platform mutation'}
cp=read(H/'checkpoint.json');cp.update(updatedAt=now,stage='explanations-ready-game-narration-final-integration-in-progress',componentProgress=facts,next='Finish source-verified KO/EN passage mapping and compatible assembly EDL, then changed TTS and final integration.',activeTasks=['source-verified-game-passage-merge','clean-source-and-use-condition-audit','final-assembly-pipeline']);cp['internalReview']['newMediaProductionStarted']=True;save(H/'checkpoint.json',cp)
spec=read(H/'active-commit-spec.json');control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];control.update(updatedAt=now,status=cp['stage'],componentProgress=facts);spec['control']=control
work=read(R/'shared/publishing/video-worklist.json')['rows'];spec['worklist']=[]
for ep in control['episodes']:
 row=next(x for x in work if x['id']==ep);revision=dict(row.get('contrastRevision',{}));revision.update(componentStatus=cp['stage'],explanationReady=True,finalMasterReady=False,progressCheckpoint=str((H/'checkpoint.json').relative_to(R)).replace('\\','/'))
 spec['worklist'].append({'id':ep,'set':{'executionStatus':cp['stage'],'contrastRevision':revision,'updatedAt':now}})
spec['markdownStatus']='설명 시연 수정 완료 · 새 게임/대본/음성 통합 진행 · 새 전체 검수본 준비 중'
spec['ownedPaths']=[str((H/n).relative_to(R)).replace('\\','/') for n in ['checkpoint.json','record-integration-progress.py']]
save(H/'integration-progress-commit-spec.json',spec)
print(json.dumps(facts,ensure_ascii=False,indent=2))
