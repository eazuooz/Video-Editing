from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
prior=read(BASE/'dante-native-direct-review-v1.json')
rows=[(34,44,44.084,None,'Cast toward targets with swirled effects and gold pillars; transit and camera reposition must be trimmed.'),
 (70,78,78.244,'dante-crop70-78-end.png','Cyan projectile lines from caster toward a target near the gold wall.'),
 (109,117,117.238,'dante-crop109-117-end.png','Floating blue orb and beam-like effects toward visible targets.'),
 (221,228,228.166,'dante-crop221-228-end.png','Raised glowing blue spherical spell centered near the caster.'),
 (258,268,268.147,'dante-crop258-268-end.png','Crossing Dark Verse projectile lines toward targets near the doorway.'),
 (431,440,440.032,'dante-crop431-440-end.png','Aiming/casting toward visible targets at a stone doorway.')]
record={'schemaVersion':1,'reviewedAt':now,'sourceVideo':'vy_vtGx8vq8','sourceSha256':prior['sourceSha256'],
 'sourceOffsetSeconds':2530,'nativeReview':'projects/player-customization/production/dante-native-direct-review-v1.json',
 'method':'Actual bounded CUA playback and returned endpoint pixels, plus prior direct full125 native samples/32boards. Browser overshoot is preserved; exact final native-frame edges remain pending.',
 'crop':{'x':634,'y':150,'width':1152,'height':648,'presenterExcluded':True,'abilityHudExcluded':True,
  'captionPrototypeEnabled':True,'limitation':'Cropped shot supports caster/effect/target spatial relationships; no cropped-out HUD numbers, named verse order or timer claims.'},
 'observations':[],'allFinalNativeBoundariesReviewed':False,'finalCaptionPixelsReviewed':False,'sourceAudioUsed':False,'gameplayQuotaApproved':False}
for a,b,end,p,finding in rows:
 r={'requestedLocalSeconds':[a,b],'observedEndSeconds':end,'finding':finding,'directBoundedPlaybackObserved':True}
 if p:
  path=ROOT/'shared/output/player-customization/preflight'/p;assert path.exists()
  r['endpointEvidence']={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
 record['observations'].append(r)
save(BASE/'dante-continuous-crop-review-v1.json',record)
gp=ROOT/'projects/player-customization/sources/game-candidates.json';g=read(gp)
candidate=g['candidates'][0]
candidate['additionalOfficialSourcesNativeReview']='projects/player-customization/production/dante-native-direct-review-v1.json'
candidate['additionalOfficialSourcesContinuousReview']='projects/player-customization/production/dante-continuous-crop-review-v1.json'
candidate['additionalOfficialSourceSelectionStatus']='source-inspected-before-independent-observation-guide-authoring; exact final intervals/crops remain pending'
save(gp,g)
print(json.dumps({'directBoundedWindows':6,'savedEndpointEvidence':5,'nativeReviewPreserved':True,'finalApproval':False}))
