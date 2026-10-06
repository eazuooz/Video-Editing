"""Record actual permission and direct pixel review before dependent writing."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
vid='igcymdI4XYM';f=R/f'shared/output/game-math-part2-full-series/sources/{vid}.mp4'
meta=f.with_suffix('.info.json');proof=R/'shared/output/game-math-part2-full-series/preflight/noita-permission.ax.txt'
inspection=R/'shared/output/game-math-part2-full-series/inspection/geometry-noita-fine/generated-samples.json'
records=json.loads(inspection.read_text(encoding='utf8'))['records']
sources=json.loads((B/'footage-index.json').read_text(encoding='utf8'))
source={'id':vid,'game':'Noita','uploader':'NCR Gameplay','url':f'https://www.youtube.com/watch?v={vid}',
 'file':f.relative_to(R).as_posix(),'sha256':sha(f),'durationSeconds':1081.666667,'width':1920,'height':1080,'fps':60,
 'reviewedBeforeNarration':True,'recordingPermissionObserved':'Expanded native uploader description read2026-10-06: Free to use Gameplay Recorded on PC, for your videos. Recording permission only; game-IP public review pending. Not a named CC license.',
 'permissionProof':proof.relative_to(R).as_posix(),'permissionProofSha256':sha(proof),
 'licenseLabel':'uploader free-to-use permission','metadataProof':meta.relative_to(R).as_posix(),'metadataSha256':sha(meta),
 'sourceAudioUsed':False,'priorUse':'Noita was previously used in deconstruct-analyze-rebuild from different sources. This NCR recording and its chosen intervals were not used earlier. Chosen for directly visible notched terrain, ledges, water reference lines and airborne positions; not treated as a new game title.',
 'visibleAction':'Actual2D gameplay through layered, notched cave terrain. Characters fly between ledges, cross water reference heights and move among explicitly chosen visible landmarks. This does not reveal an internal mesh, plane collider or triangulation algorithm.',
 'inspection':'All3 coarse sheets and12 dense sheets directly viewed at3-second intervals plus end samples before dependent narration. Exclude inventory/tooltip intervals27–30,126–132,443–446,490–511,522–525,763–787,840–843,856–858; portals/fades63–81,168–178,899–919; strong damage obscuration45–49,754–762,821–825,995–1001,1013–1017,1022–1026; death/ending1060 onward. Approved intervals are bounded, not looped or slowed.',
 'inspectionSheets':[x['sheet'] for x in records],
 'inspectionEvidence':[{'path':x['sheet'],'sha256':sha(R/x['sheet'])} for x in records],
 'approvedIntervals':[[30,44],[49,63],[81,126],[132,168],[404,443],[446,490],[511,522],[525,558],[729,754],[787,821],[825,840],[843,856],[870,899],[951,995],[1001,1013],[1017,1022],[1026,1040]],
 'publicGameIpReview':'pending'}
sources[vid]=source;write(B/'footage-index.json',sources)
write(B/'research/geometry-noita-readiness.json',{'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directReviewComplete':True,'dependentNarrationWrittenBeforeInspection':False,'source':source,'limits':'Only bounded reviewed action intervals may be selected. Human full listening and public-IP review remain pending; contact sheets remain local and untracked.'})
print('Noita actual recording permission and all12 dense sheets recorded before dependent narration.')
