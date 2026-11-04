"""Bind actually inspected source tracks; final encoded/moving QA remains separate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone.utc).isoformat();candidate=B/'local/annotation-tracking-v2';old=B/'local/annotation-tracking-v1'
notes={
'M24-000':'Mario position followed across room toward pipe; grid is not treated as measured world metres.',
'M24-015':'Fixed HUD circle highlights native mph values43→94 during acceleration; no fabricated velocity measurement.',
'M24-032':'Link remains beside mast while raft/environment move; reference-frame example does not claim he walks across raft.',
'M25-000':'37 repaired temporal samples: complete visible car takeoff/descent/landing; no boundary-hide flicker after manual extents.',
'M25-018':'Mario sprite tracked through upward/downward jumps and scrolling stage; no measured acceleration imposed on game.',
'M25-021':'27 repaired temporal samples: skier remains inside body guide during two front flips and landings; skis may extend outside body extent. Landing slope is not an equal-height test.',
'M26-000':'Car remains focus through actual corner. Speed varies; not presented as measured uniform circular motion.',
'M26-011':'Observed upright sail after turn; earlier native rotation retained in full cut. Label corrected to the visible result.',
'M26-017':'Windmill hub and visible blades tracked; top blade can be outside source framing. No complete-circle measurement claimed.',
'M27-000':'Wheel support/contact state visible over rocks, including airborne intervals; no force magnitude or friction coefficient claimed.',
'M27-012':'Cannon vehicle followed before firing and through recoil/tip; also used for the distinct M30 translation/rotation claim.',
'M27-018':'Link followed leaving cliff and falling; clear before splash/occlusion.',
'M28-000':'Wheel/body relative movement on uneven ground. Trimmed at10.45 before later wheel target becomes ambiguous.',
'M28-001':'Chain Chomp follows visible pull/wind-up state; native release continues in full cut. Elastic analogy, not measured Hooke-law implementation.',
'M28-016':'Rider retained through turn while camera follows; no invented damping constant or internal camera algorithm.',
'M29-000':'29 longer approach samples viewed; guide follows recognizable rear of car, clears before actual camera cut. Label names movement, not whole-body detector.',
'M29-000-after':'11 post-impact samples: main deformed body followed; detached parts outside the guide intentionally remain visible.',
'M29-014':'Fixed hollow region highlights actual wall impact; wall then debris visible. Editorial region, not object detector or measured momentum.',
'M29-018':'14 open-contour samples viewed after removing lower arc; native pull/release instruction remains uncovered. Clear before release/dust.',
'M30-003':'Attached logs move together in Ultrahand, retained native shared assembly. Not a rigid-body solver measurement.',
'M30-027':'Wheel remains connected while chassis rolls over bumps; native deformable model is distinguished from ideal rigid-body illustration.',
'M31-000':'Train follows curved track; guide cleared before camera viewpoint change. No specific spline implementation claimed.',
'M31-005':'Native moving platform on fixed track; circle follows platform as camera scrolls. Rail shape and travel parameter are distinct.',
'M31-012':'Launch Star and Mario remain observable; guide clears before clipping. Full native flight follows in source cut, no editable-trajectory claim.',
'M31-027':'Rejected terrain-drifting automatic track. Mark center aim/endpoint region only with valid hologram; hide during invalid previews, including272.0–272.25 and272.56–273.36.',
'M33-008':'Fixed observed editor region: right-angle/diagonal track is changed to rounded corner. Native editing UI retained; not proof of internal Bezier/spline choice.'}
reviewed=[]
for path in sorted(candidate.glob('M*.json')):
 d=read(path)
 if 'id' not in d:continue
 sid=d['id'];assert sid in notes
 evidence=d['sheets'] if sid in {'M25-000','M25-021','M29-000','M29-000-after','M29-018','M31-027'} else read(old/(sid+'.json'))['sheets']
 if sid=='M29-018':evidence=[(candidate/'M29-open-contour.jpg').relative_to(R).as_posix()]
 # Border-only off-screen samples at the bottom of a fully visible car should
 # not blink for two frames. Shrink only that editorial extent to safe bounds.
 if sid=='M26-000':
  for k in d['keyframes']:
   x,y,w,h=k['bbox']
   if not k['visible'] and 5<=x and x+w<=1915 and 32<=y and y+h<1080:
    k['bbox'][3]=min(h,1068-y);k['visible']=True
  d['repair']+='; bottom-edge extent limited to1068 for two otherwise-valid frames'
 d['failedSamples']=sum(not k['visible'] for k in d['keyframes'])
 d['visualQa']=dict(status='temporal-samples-reviewed-final-encoded-pending',at=at,evidence=evidence,note=notes[sid],scope='Decoded source temporal samples; unchanged source positions reused exactly where noted. Final speech timing/caption/mobile/moving edit still pending.',humanFinalReview=False,continuousPlayback=False)
 reviewed.append(d)
for item in read(B/'batch.json')['items'][3:]:
 P=R/'projects'/item['slug'];dest=P/'production/local/annotation-reviewed-v1';dest.mkdir(parents=True,exist_ok=True);windows=[]
 for d in reviewed:
  uses=[u for u in d['uses'] if u['project']==item['slug']]
  if not uses:continue
  file=dest/(d['id']+'.json');assert not file.exists(),'Preserve existing reviewed track revision';save(file,d)
  window={k:d[k] for k in ['id','sourceId','sourceSha256','start','end','label','shape','coordinates','fps','method','visualQa','failedSamples']}
  window.update(trackFile=file.relative_to(R).as_posix(),sourceTrackSha256=sha(file),scenes=[u['scene'] for u in uses]);windows.append(window)
 plan=read(P/'planning/production-plan.json')
 for cue in plan['nativeGameCueBindings']:
  matches=[w for w in windows if w['sourceId']==cue['sourceId'] and w['sourceSha256']==cue['sourceSha256'] and cue['sceneId'] in w['scenes'] and min(w['end'],cue['sourceOut'])>max(w['start'],cue['sourceIn'])]
  assert matches,(item['id'],cue['sceneId'],'missing actual target')
  cue['annotationEvidence']={'file':'planning/game-annotation-tracks.json','windows':[w['id'] for w in matches],'sourceTemporalSamplesReviewed':True,'finalSpeechAndMotionReview':False}
 save(P/'planning/game-annotation-tracks.json',dict(status='sampled-source-tracks-reviewed-final-composite-pending',windows=windows,finalCompositeViewed=False,humanReview=False))
 save(P/'planning/production-plan.json',plan)
 print(item['id'],len(windows),'source guides bound; final encoded review pending')
source=B/'local/annotation-targets-v1/manifest.json';data=read(source)
for row in data['records']:row.update(viewed=True,reviewScope='Actual nine-frame native source board, not continuous playback',reviewedAt=at)
data['status']='all27-source-boards-inspected-targets-repaired';save(source,data)
save(candidate/'review-record.json',dict(at=at,status='26-source-guide-windows-reviewed-and-bound',windows=[dict(id=d['id'],evidence=d['visualQa']['evidence'],note=notes[d['id']]) for d in reviewed],sourceBoardCount=27,finalEncodedReview=False,humanReview=False))
