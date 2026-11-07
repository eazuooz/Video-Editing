"""Selected06.02 finite software compositor. Default never launches a process.

Only a hash-bound real103PCM/96logical-ASR/mix/MC timeline may be explicitly sampled or
encoded. Reuses frozen style/stream primitives in a private module; old episodes
and user applications are never changed or terminated.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,shutil,subprocess,time,uuid,sys
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw,ImageColor

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/shorts-leveldesign-06-02';SLUG=PROJECT.name
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')/SLUG
FPS=60;SIZE=(1080,1920);PANEL=[48,410,880,495];LOWER=[48,992,880,495];CAT_BOUNDS=[416,973,936,1680]
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0);CONTROLLER=None
STREAM_SHA='9e3ea1f564269d027111356bbecf762673114a0b4acb2c034121d18fea5138c2'
ENCODER_SHA='1a82e5676058835bcdf752706d96888deb1b6d393a06ec53efe86a3c189bd372'
CAPTION_SHA='fec20b03156cff68fa80d5d2be56a0407634fcf3287e516bb70ff3ffa8413769'
AUDIO_SHA='a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da'
AUDIO_VERIFY_SHA='db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4'
CLOCK_SHA='2a9335486c16f341c7d7fc22f5b6b5f1e32970e83f543699455943ccb93e1e48'
RESOURCE_SHA='886912ceea03da6a297a76d263b0e15f96850562e2648c3c7093eb1f59e880a7'
MC_RUNNER_SHA='e7328ef4dafd2249e41938f46bca75d0a00650fc174727111b6c7b56da3a3f98'
class Pending(RuntimeError):pass
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def bound(r):
 if not isinstance(r,dict)or not r.get('path')or sha(r['path'])!=r.get('sha256'):raise Pending('Actual source/input changed '+str(r))
 return Path(r['path']).resolve()
def save(p,x):
 p=Path(p);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(p)
def primitives():
 p=HERE/'render-zen-view-film.py'
 if sha(p)!=STREAM_SHA:raise Pending('Audit changed verified style/stream primitive before use')
 m=module('prospect_private_verified_style_stream',p);m.fresh_authorization=fresh_authorization;return m
def fresh_authorization():
 c=read(ROOT/'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106'];b=read(HERE/'batch.json');checkpoint=read(HERE/'checkpoint.json')
 if c['status']in('paused','stopped','cancelled','canceled')or not c['automaticAdvanceWithinExactList']or c['automaticAdvanceOutsideList']or not b['localFinalReviewOnly']or len(b['projects'])!=111 or checkpoint.get('currentTopicId')!='06.02'or not any(p['topicId']=='06.02'and p['slug']==SLUG for p in b['projects']):raise Pending('Exactselected111 current06.02 local boundary inactive')
 return dict(localFinalReviewOnly=True,controlSHA256=sha(ROOT/'shared/publishing/video-production-control.json'))
def overlap(a,b):return max(a[0],b[0])<min(a[0]+a[2],b[2])and max(a[1],b[1])<min(a[1]+a[3],b[3])
def fit(crop,box):
 x1,y1,x2,y2=crop;x,y,w,h=box
 if not 0<=x1<x2<=1920 or not 0<=y1<y2<=1080:raise Pending('Invalid actual source crop')
 scale=min(w/(x2-x1),h/(y2-y1),1.);return dict(crop=list(crop),scale=scale,x=x+(w-(x2-x1)*scale)/2,y=y+(h-(y2-y1)*scale)/2,width=(x2-x1)*scale,height=(y2-y1)*scale)
def point(viewport,transform):return(transform['x']+(viewport['x']*1920-transform['crop'][0])*transform['scale'],transform['y']+((1-viewport['y'])*1080-transform['crop'][1])*transform['scale'])

def section_badge_layout(panel,transform,font):
 """A compact section tag belongs to the actual observer image, not its header."""
 if panel['camera']!='observer':return None
 text='설명용 단면';size=32;margin=12;w=math.ceil(font.getlength(text))+24;h=48
 if transform['width']<w+2*margin or transform['height']<h+2*margin:raise Pending('Actual observer image has no readable section-badge slot')
 x=math.floor(transform['x']+transform['width']-margin-w);y=math.ceil(transform['y']+margin)
 return dict(text=text,fontSize=size,rectXYWH=[x,y,w,h],textXY=[x+w/2,y+h/2],color='#e8cf83',placement='inside actual fitted/cropped observer image top-right')
def visible_depth(viewport,near=.04,far=80):return near<viewport['z']<far and 0<=viewport['x']<=1 and 0<=viewport['y']<=1

def source_pins(source,panel=None):
 """Every non-image input actually consumed by a source must be proof-bound."""
 result=[]
 for key in('evidence','modeProof','frameHashManifest','sampledVisualReview','registryProof','ptsProof'):
  if isinstance(source.get(key),dict):result.append(source[key])
 result+=source.get('files',[])
 if panel and panel['sourceRef']in('main','close'):
  result+=list(source['modes'][panel['mode']].values())
 return result

def sidecar(source,panel,name):
 expected=(Path(panel['modeFolder'])/name).resolve()
 rows=source['modes'][panel['mode']].values()if panel['sourceRef']in('main','close')else source['files']
 found=[r for r in rows if Path(r['path']).resolve()==expected]
 if len(found)!=1:raise Pending('Actual mode sidecar has no unique source pin: '+str(expected))
 return bound(found[0])

class NativeFrameProofs:
 def __init__(self):self.manifests={}
 def verify(self,source,path):
  record=source['frameHashManifest'];mp=Path(record['path']).resolve()
  if str(mp)not in self.manifests:
   bound(record)
   value=read(mp);expected=source.get('captureFingerprint',source.get('fingerprint'))
   if value.get('captureFingerprint',value.get('fingerprint'))!=expected:raise Pending('Native image manifest belongs to another capture')
   rows=value.get('frames',[]);index={}
   for row in rows:
    rel=row['path'].replace('\\','/');target=(mp.parent/rel).resolve()
    if target in index or not target.is_relative_to(mp.parent)or Path(rel).is_absolute():raise Pending('Duplicate/escaping native JPEG path')
    index[target]=row
   self.manifests[str(mp)]=index
  p=Path(path).resolve();row=self.manifests[str(mp)].get(p)
  if row is None or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise Pending('Actual native JPEG differs from its immutable capture proof')
  return dict(path=str(p),sha256=row['sha256'],bytes=row['bytes'])
def source_frame(section,frame,panel):
 if section.get('rate')==1:return section['sourceStartFrame']+frame-section['startFrame']
 return panel['sourceFrame']if panel.get('sourceFrame')is not None else section['sourceStartFrame']
def section_at(t,frame):
 for s in t['sections']:
  if s['startFrame']<=frame<s['endFrameExclusive']:return s
 raise Pending('Frame outside actualpicture clock')
def destinations(panels):
 n=len(panels)
 if n==1:return[[0,500,1080,850]]if panels[0].get('cropXYXY')else[PANEL]
 if n==2:return[PANEL,LOWER]
 if n==3:return[[200,410,576,324],[200,774,576,324],[200,1138,576,324]]
 if n==4:return[[48,410,428,241],[500,410,428,241],[48,800,428,241],[500,800,428,241]]
 raise Pending('Readable selectedlayout supports1..4realpanels only')
def validate_structure(t):
 if t.get('schemaVersion')!='06-02-final-timeline-v2'or t.get('topicId')!='06.02'or t.get('format')!=dict(width=1080,height=1920,fps=60):raise Pending('Exact06portrait60fps contract required')
 if t.get('logicalSentenceGroupCount')!=96 or t.get('physicalVoiceUnitCount')!=103 or t.get('noNativeDuplicationForPhysicalParts')is not True or len(t.get('physicalVoiceComponents',[]))!=103:raise Pending('Exact103physical/96logical clock separation required')
 cursor=0;games=[]
 for s in t['sections']:
  a,b=s['startFrame'],s['endFrameExclusive']
  if type(a)is not int or type(b)is not int or a!=cursor or b<=a:raise Pending('Noncontiguous actualinteger pictureclock')
  cursor=b
  if s['kind']=='mc':
   if s['frameCount']!=b-a or s['rate']!=1:raise Pending('MC frameclock must remain1x exact')
  else:
   if not 1<=len(s['panels'])<=4:raise Pending('Unbounded nativepanelcount')
   if s.get('rate')==1 and s['frameCount']!=b-a:raise Pending('Native/game1x sourcecount differs')
   if s.get('rate')is None and(not s.get('holdReason')or s['frameCount']!=1):raise Pending('Unexplained frozen source is padding')
   for p in s['panels']:
    if p.get('cropXYXY')and p['sourceRef']!='c-refuge':raise Pending('Only explicitlyreviewed ownrefuge observer crop permitted')
    if p.get('cropXYXY')and p['camera']!='observer':raise Pending('Player/actualgame/closeup fullnativeaspect preserved')
    limit=600 if p['sourceRef']in('main','close')else t['sourceRegistry'][p['sourceRef']].get('frames',100000)
    for f in(source_frame(s,a,p),source_frame(s,b-1,p)):
     if type(f)is not int or not 0<=f<limit:raise Pending('Missing/out-of-range actualsource sample')
   if s['kind']=='gameplay':games.append((s['paragraph'],s['sentenceIndexZeroBased'],s['panels'][0]['sourceRef'],s['sourceStartFrame'],s['frameCount']))
 if cursor!=t['totalFrames']:raise Pending('FinalPCMceil pictureframe uncovered')
 if t.get('appliedPictureOverrideIds'):
  if [g[2]for g in games]!=['D','M','H']:raise Pending('Context overrides must retain exactly3 meaningfully taught games once')
  for p,j,ref,first,count in games:
   a,b=[round(v*60)for v in t['sourceRegistry'][ref]['selectedRange']]
   if not a<=first<first+count<=b:
    section=next(s for s in t['sections']if s['kind']=='gameplay'and s['panels'][0]['sourceRef']==ref);extra=section['panels'][0].get('additionalSourceWindow')
    if not extra or not extra['frameRange'][0]<=first<first+count<=extra['frameRange'][1]:raise Pending('Context override game cut escapes selected observed source window')
 elif games!=[(1,0,'D',360,360),(19,0,'M',600,480),(23,3,'H',1140,480)]:raise Pending('Actual3games must play onlyselectedwindows once1x')
 for cue in t.get('catCues',[]):
  if cue['pose']not in('puzzled','realize','relief')or not 0<=cue['startFrame']<cue['endFrameExclusive']<=cursor:raise Pending('Onlyapprovedcatposes/exactcues allowed')
  for s in t['sections']:
   if max(s['startFrame'],cue['startFrame'])>=min(s['endFrameExclusive'],cue['endFrameExclusive']):continue
   if s['kind']=='mc':
    raise Pending('Dense P04/P25 relationship maps keep cat OFF')
   elif len(s['panels'])!=1 or s['panels'][0].get('cropXYXY'):raise Pending('AB/dual/grid/largefocus nativecat OFF perapprovedproof')
 return dict(totalFrames=cursor,sections=len(t['sections']),actualGameClips=len(games))
def caption_srt(cap,cues,language):
 """V3 forwards V2.old: use the exact frozen SRT writer used by V3 itself."""
 return cap.old.base.srt(cues,language)

def verify_inputs(t):
 result=validate_structure(t)
 if t.get('status')!='actual-asr-aligned':raise Pending('Actualselected ASRaligned timeline required')
 inputs=t.get('inputs',[])
 for q in inputs:bound(q)
 roles={r['role']:r for r in inputs}
 if len(roles)!=len(inputs):raise Pending('Duplicate timeline input roles')
 required={'narration':PROJECT/'narration-expanded-draft-v4.json','selection':PROJECT/'native-teaching-selection-v3.json','physical-component-plan':PROJECT/'voice-semantic-components-v3.json','as-built-decisions':PROJECT/'film-asbuilt-decisions-v2.json','body-labels':PROJECT/'body-point-label-layout-v2.json','renderer':Path(__file__),'timeline-helper':HERE/'build-prospect-refuge-film-timeline-v2.py','style':ROOT/'projects/shorts-leveldesign-03-02/visual-layout-v1.json','style-helper':ROOT/'projects/shorts-leveldesign-03-02/production/composite-native-frame.py'}
 for role,path in required.items():
  if role not in roles or Path(roles[role]['path']).resolve()!=path.resolve():raise Pending('Missing exactselected '+role)
 for role in('caption-timing','caption-helper','audio-build','audio-helper','mix-clock-proof','mix-clock-helper','annotation-plan','style','style-helper','stream-helper','encoder-helper','resource-helper'):
  if role not in roles:raise Pending('Missingactualbinding '+role)
 exact_helpers={'caption-helper':(HERE/'build-prospect-refuge-caption-timing-v3.py',CAPTION_SHA),'audio-helper':(HERE/'verified-prospect-refuge-audio-build-v3.py',AUDIO_VERIFY_SHA),'audio-producer-helper':(HERE/'prepare-prospect-refuge-audio-v2.py',AUDIO_SHA),'stream-helper':(HERE/'render-zen-view-film.py',STREAM_SHA),'encoder-helper':(HERE/'render-first-film.py',ENCODER_SHA),'resource-helper':(HERE/'run-prospect-refuge-corrections-native.py',RESOURCE_SHA),'mc-recipe-helper':(HERE/'run-prospect-refuge-diagrams-v3.py',MC_RUNNER_SHA)}
 for role,(path,digest)in exact_helpers.items():
  if role not in roles or Path(roles[role]['path']).resolve()!=path.resolve()or roles[role]['sha256']!=digest:raise Pending('Unexpected trusted helper '+role)
 if Path(roles['mix-clock-helper']['path']).resolve()!=(HERE/'verify-prospect-refuge-mix-clock.py').resolve()or roles['mix-clock-helper']['sha256']!=CLOCK_SHA:raise Pending('Unexpected raw-to-mix sample clock verifier')
 selection=read(required['selection'])
 if t['sourceRegistry']!=selection['sourceRegistry']or t['bodyPointLabelLayout']!=read(required['body-labels']):raise Pending('Timeline substituted actualsource or measured bodylayout')
 cap=module('prospect_renderer_caption_verify',bound(roles['caption-helper']));verified=cap.verify_existing(bound(roles['caption-timing']));timing=verified['timing']
 if timing['totalFrames']!=t['totalFrames']or timing['captions']!=t['captions']:raise Pending('Film/captions differfromactualcurrentASR')
 if t['physicalVoiceComponents']!=timing.get('physicalComponents')or t.get('audioClock')!=timing.get('audioClock'):raise Pending('Film changed immutable raw103component/caption sample clock')
 annotations=read(bound(roles['annotation-plan']))
 if t['annotationPlan']!=annotations:raise Pending('Annotation plan changed')
 timeline=module('prospect_fresh_timeline_contract',HERE/'build-prospect-refuge-film-timeline-v2.py')
 guides=timeline.verify_annotations(annotations,selection,timing,cap)
 if guides!=t.get('guideCues'):raise Pending('Guides differ from actual spoken-word anchors')
 if timeline.manual_game_guides(annotations,selection)!=t.get('manualGameGuides'):raise Pending('Manual gameplay coverage differs from reviewed source plan')
 mc={}
 for s in t['sections']:
  if s['kind']=='mc':
   mc[s['paragraph']]=timeline.verify_mc_manifest(bound(s['mcManifest']),bound(roles['caption-timing']))
 decisions=read(bound(roles['as-built-decisions']))
 for q in decisions['inputs']:bound(q)
 if t['asBuiltDecisions']!={k:v for k,v in roles['as-built-decisions'].items()if k!='role'}:raise Pending('Closinghero decision pin differs')
 overrides=None
 if t.get('pictureOverrides'):
  if roles.get('picture-overrides')!={**t['pictureOverrides'],'role':'picture-overrides'}:raise Pending('Picture override file pin differs')
  overrides=timeline.prepare_picture_overrides(bound(t['pictureOverrides']),selection,timing,bound(roles['caption-timing']))
 fresh=timeline.plan(selection,timing,mc,decisions,overrides)
 for key in('sections','catCues','sentenceClocks','paragraphs','appliedPictureOverrideIds','physicalVoiceComponents','audioClock','logicalSentenceGroupCount','physicalVoiceUnitCount','noNativeDuplicationForPhysicalParts'):
  if t[key]!=fresh[key]:raise Pending('Timeline routing differs from actual selectedsource/PCM clock: '+key)
 audio=module('prospect_renderer_audio_verify',bound(roles['audio-helper']));mix=audio.verified_audio_build(bound(roles['audio-build']))
 if'audioBuild'in mix:mix=mix['audioBuild']
 if t['audio']['voice']!=verified['voice']['aggregateWav']or t['audio']['mix']!=mix['mixWav']or mix['rawVoiceFingerprint']!=verified['voice']['fingerprint']:raise Pending('Differentvoice/mixclock')
 clock=module('prospect_renderer_mix_clock_verify',bound(roles['mix-clock-helper']));proof=clock.verify_existing(bound(roles['mix-clock-proof']),bound(roles['caption-timing']),bound(roles['audio-build']));proof_pin={k:v for k,v in roles['mix-clock-proof'].items()if k!='role'}
 if t.get('rawMixClockProof')!=proof_pin or t['audio'].get('sampleClockAcceptance')!=timeline.clock_acceptance(proof,timing,verified['voice'],mix,proof_pin):raise Pending('Film lacks exact separate raw-to-mix sample clock acceptance')
 import soundfile as sf
 for name in('voice','mix'):
  item=t['audio'][name];info=sf.info(bound(item))
  if(info.samplerate,info.channels,info.frames)!=(item['sampleRate'],item['channels'],item['frames']):raise Pending('Actualaudio sample properties changed')
 if t['totalFrames']!=math.ceil(t['audio']['mix']['frames']*60/t['audio']['mix']['sampleRate']):raise Pending('Audio tail padded/truncated')
 for lang in('ko','en'):
  srt=bound(t['subtitles'][lang]);expected=Path(roles['caption-timing']['path']).parent/f'captions.{lang}.srt'
  if srt!=expected.resolve()or srt.read_text(encoding='utf8')!=caption_srt(cap,timing['captions'][lang],lang):raise Pending('SRT differs from actual exact authored timed captions')
 for s in t['sections']:
  if s['kind']=='mc':
   if s.get('catPolicy')!='off-dense-relationship-map':raise Pending('Dense map mascot policy changed')
   m=read(bound(s['mcManifest']));bound(m['output'])
   if not m['complete']or m['topicId']!='06.02'or s['sourceSHA256']!=m['output']['sha256']:raise Pending('Unrendered/stale MC')
   for q in m['inputPins']:bound(q)
  else:
   for p in s['panels']:
    source=t['sourceRegistry'][p['sourceRef']]
    for q in source_pins(source,p):bound(q)
    if source['sourceKind']=='independent-gameplay':bound(source['media'])
    elif p['sourceRef'].startswith('c-'):
     bound(source['modeProof']);bound(source['frameHashManifest'])
    elif p['sourceRef']in('main','close'):bound(source['frameHashManifest'])
    else:
     bound(source['frameHashManifest'])
 result['actualListening']=False;return result

LABELS={'player-head':'머리 높이','body-head':'머리 높이','player-torso':'몸통 높이','body-torso':'몸통 높이','body-hips':'골반 높이','player-ground':'플레이어 자리','player-camera-eye':'카메라 눈','main-player-camera-eye':'시연 카메라 눈','enemy-eye':'상대 눈','different-direction-outlook-target':'바깥 표적','Declared threat on other side-eye':'바깥 위협','window-opening-center':'창','public-area-point':'아래 공용 영역','public-atrium':'아트리움','enclosed-loft':'위층 방','actual-roof-surface':'옥상','Actual continuous roof ramp-top':'경사로 끝','hearth-center':'화로','interior-ceiling-underside-above-player':'실내 천장 밑면','interior-ceiling-floor-below-player':'낮아진 바닥','interior-ceiling-front-edge-center':'실내 천장','interior-ceiling-front-left':'천장 가장자리','interior-ceiling-front-right':'천장 가장자리','original-exterior-overhang-center':'바깥 처마','lowered-arrival':'낮은 입구','Lowered entry ramp-top':'입구 경사로','entry-point':'출발 입구','goal-point':'다음 입구','orange-next-refuge':'주황 입구','hidden-item-center':'찾을 아이템','item-look-target':'아이템','flying-enemy-center':'비행 적','Shielded burst-firing enemy-eye':'방패 적','Large open-room enemy-eye':'보스','own-object-moving-tool':'물체 이동 도구','Own movable board-top-center':'옮길 판','Second already placed board-top-center':'다음 판','next-pallet-top':'팔레트','rock--4-top':'출발 돌','rock-4-top':'도착 돌','Opposing open position-eye':'마주 보는 자리','Same body left boundary':'왼쪽 경계','Same body right boundary':'오른쪽 경계','Public circulation personA-eye':'공용 공간 사람 A','Public circulation personB-eye':'공용 공간 사람 B','Scripted crossing guardA-eye':'경비 A','Scripted crossing guardB-eye':'경비 B','first-cover-top':'낮은 엄폐 윗면','first-cover-bottom':'낮은 엄폐 아랫면','second-cover-top':'다음 엄폐 윗면','second-cover-bottom':'다음 엄폐 아랫면'}
for i in range(1,5):LABELS[f'column-{i}-top']='기둥 윗면'
for i in range(4):LABELS[f'moving-facade-panel-{i}']='외벽'
for i in range(2):LABELS[f'moving-partition-{i}']='내부 칸막이'
for body in('head','torso','hips'):
 LABELS[f'ray-{body}-actual-hit-end']='직선 끝';LABELS[f'enemy-ray-{body}-actual-end']='직선 끝'

def guide_visible(anchor,panel,frame,plan,guide_kind=None,held_source=False):
 prefix=panel['camera']
 vp=anchor.get(prefix+'Viewport')
 if not vp or not visible_depth(vp)or anchor.get(prefix+'InFrustum')is False or anchor.get('active')is False:return False
 policies=[x for x in plan.get('nativeGuidePolicies',[])if x['sourceRef']==panel['sourceRef']and x['camera']==prefix and x['anchorId']==anchor['id']and x.get('mode',panel['mode'])==panel['mode']]
 if not policies:return False # Frustum alone never fabricates visibility.
 for policy in policies:
  if policy.get('allowedGuideKinds')and guide_kind not in policy['allowedGuideKinds']:continue
  if policy.get('requiresMeaningfulHeldSourceFrame')and not held_source:continue
  if policy.get('sourceFrameRange')and not policy['sourceFrameRange'][0]<=frame<policy['sourceFrameRange'][1]:continue
  if policy['method']=='reviewed-frame-set':
   if frame in policy['visibleFrames']:return True
   continue
  if policy['method']!='recorded-camera-ray':raise Pending('Unknown guide visibility method')
  ray=anchor.get(prefix+'CameraRay')
  if ray is None:raise Pending('Actual camera-ray proof is absent')
  if not ray['blocked']:return True
  # Physical target/self hits remain raw facts. A separate reviewed section
  # policy may authorize only a section/height illustration, never visibility.
  d=math.sqrt(sum((ray['actualEndpoint'][k]-ray['desiredEndpoint'][k])**2 for k in'xyz'))
  if ray['hitCollider']in policy.get('targetSurfaceColliders',[])and d<=policy.get('targetSurfaceTolerance',0):return True
 return False

def closeup_guide_anchors(data):
 result=[]
 for source in data['anchors']:
  a=copy.deepcopy(source);a['closeupViewport']=a['viewport'];a['closeupInFrustum']=a['inFrustum'];a['closeupCameraRay']=dict(origin=data['position'],desiredEndpoint=a['world'],actualEndpoint=a['actualCameraRayEndpoint'],blocked=a['environmentBlocked'],hitCollider=a['hitCollider']);result.append(a)
 return result

def manual_regions(rows,source_ref,frame):
 result=[]
 for row in rows:
  if row['sourceRef']!=source_ref:continue
  coverage=row['reviewedTemporalCoverage'];a,b=coverage['sourceFrameRange']
  if not a<=frame<b or any(x<=frame<y for x,y in coverage.get('visibilityOffRanges',[])):continue
  for mark in row['marks']:
   keys=mark['keyframes'];exact=next((q for q in keys if q['frame']==frame),None)
   if exact:
    if exact.get('visible')is True:result.append(dict(mark,bboxXYXY=exact['bboxXYXY'],sourceFrame=frame,exactInspectedKeyframe=True))
    continue
   pair=next(((x,y)for x,y in zip(keys,keys[1:])if x['frame']<frame<y['frame']),None)
   if not pair or not all(q.get('visible')is True for q in pair):continue
   left,right=pair;alpha=(frame-left['frame'])/(right['frame']-left['frame']);box=[x+(y-x)*alpha for x,y in zip(left['bboxXYXY'],right['bboxXYXY'])]
   result.append(dict(mark,bboxXYXY=box,sourceFrame=frame,exactInspectedKeyframe=False,boundedBetweenInspectedFrames=[left['frame'],right['frame']],manualEditorialRegion=True,continuousTrackerVerified=False))
 return result

def manual_label_style(mark):
 return dict(anchor=tuple(mark.get('labelDisplayAnchor',[488,970])),fontSize=mark.get('labelFontPx',40),color=mark.get('color','#73c7c2'),stroke=mark.get('strokeWidthOutputPixels',8))

def verify_native60_source_pts(pts,first,count):
 if type(first)is not int or type(count)is not int or count<1 or first<0 or first+count>len(pts)or any(abs(pts[i]-i/60)>0.000002 for i in range(first,first+count)):raise Pending('Selected source cut does not contain exact native60fps decoded frames; never duplicate/drop/retime')

class FrameRouter:
 def __init__(self,t,work,ffmpeg,ffprobe,stream):
  self.t=t;self.work=Path(work);self.ffmpeg=ffmpeg;self.ffprobe=ffprobe;self.stream=stream;self.style=stream.style_adapter();self.data={};self.decoders={};self.pts={};self.decoder_count=0;self.native_proofs=NativeFrameProofs();self.additional_proofs={}
 def text(self,im,text,xy,size=36,color='#f5f5f5'):
  self.style.text(ImageDraw.Draw(im),text,xy,size,ImageColor.getrgb(color))
 def base(self):
  im=Image.new('RGB',SIZE,'black');title=' '.join(w for w in self.t['titleKo'].split()if not w.startswith('#'));lines=[];line=''
  for ch in title:
   if self.style.font(62).getlength(line+ch)>880:lines.append(line.strip());line=ch
   else:line+=ch
  if line:lines.append(line.strip())
  if len(lines)>2:raise Pending('Actualclaim heading needs readable two-line editorial version')
  for i,line in enumerate(lines):self.text(im,line,(488,130+i*88),62,'#e8cf83'if i else'#f5f5f5')
  return im
 def frame_data(self,p,frame):
  key=p['modeFolder']
  if key not in self.data:
   source=self.t['sourceRegistry'][p['sourceRef']];self.data[key]={'states':[json.loads(x)for x in sidecar(source,p,'states.jsonl').read_text(encoding='utf8').splitlines()],'anchors':[json.loads(x)for x in sidecar(source,p,'projected-anchors.jsonl').read_text(encoding='utf8').splitlines()]}
  if self.data[key]['states'][frame]['frame']!=frame or self.data[key]['anchors'][frame]['frame']!=frame:raise Pending('Actual native sidecar frame order changed')
  return self.data[key]['states'][frame],self.data[key]['anchors'][frame]
 def source_image(self,s,p,frame):
  f=source_frame(s,frame,p)
  if s['kind']not in('gameplay','gameplay-freeze'):
   path=Path(p['modeFolder'])/p['camera']/f'{f:04}.jpg'
   proof=self.native_proofs.verify(self.t['sourceRegistry'][p['sourceRef']],path)
   with Image.open(path)as x:x.load();im=x.convert('RGB')
   if im.size!=(1920,1080):raise Pending('Nativeactualframe notFHD')
   return im,dict(proof,frame=f)
  key=s['id'];source=self.t['sourceRegistry'][p['sourceRef']];path=source['media']['path']
  if key not in self.decoders:
   if path not in self.pts:self.pts[path]=self.stream.probe_pts(path,(1920,1080),self.ffprobe)
   count=1 if s['kind']=='gameplay-freeze'else s['frameCount'];self.decoder_count+=1
   verify_native60_source_pts(self.pts[path],s['sourceStartFrame'],count)
   self.decoders[key]=self.stream.StreamDecoder(path,(1920,1080),self.pts[path],s['sourceStartFrame']/60,count,self.ffmpeg,self.work/f'actualgame-{self.decoder_count:03}.log')
  image,pts=self.decoders[key].at(f/60);extra=p.get('additionalSourceWindow');matched=False
  if extra:
   record=extra['record'];name=record['path']
   if name not in self.additional_proofs:self.additional_proofs[name]=read(bound(record))
   exact=[r for r in self.additional_proofs[name]['sourceFramePtsProofs']if r['sourceFrame']==f]
   if exact:
    rgb=hashlib.sha256(image.tobytes()).hexdigest()
    if any(r['rgbSHA256']!=rgb for r in exact):raise Pending('Additional inspected source keyframe differs from actual decoded RGB')
    matched=True
  return image,dict(path=path,sha256=source['media']['sha256'],actualSourcePTS=pts,frame=f,additionalInspectedRgbKeyMatched=matched)
 def body_labels(self,im,p,frame,anchors,state,transform,dest):
  b=self.t['bodyPointLabelLayout'];templates=[q for sample in b['samples']for q in sample['panels']if q['mode']==p['mode']and q['destinationXYWH']==dest]
  if not templates:raise Pending('BodylayoutV2 has no measuredslot forselectedpanel; do not invent readablelayout')
  template=next((q for q in templates if q['sourceFrame']==frame),templates[-1]);byid={a['id']:a for a in anchors};rays={r['id']:r for r in state['bodyRays']};d=ImageDraw.Draw(im);out=[]
  for mark in template['points']:
   a=byid[mark['id']];vp=a['viewport'];camray=a
   if not a['inFrustum']or not visible_depth(vp):continue
   if a['environmentBlocked']:
    # Bodydiagnostic point may be actor-occluded, but not hidden behind a
    # different environmental wall from this explanatory camera.
    continue
   xy=point(vp,transform);ray=rays[mark['id'].removeprefix('body-')];role='blocked'if ray['blocked']else'seen'if ray['seen']else'outside';color=b['palette'][role];status={'blocked':'직선 막힘','seen':'적 시야 안','outside':'직선 통과'}[role];x,y,w,h=mark['labelXYWH'];line=[(x+w,y+h/2),(min(x+w+60,xy[0]-20),y+h/2),xy]
   d.line(line,fill=color,width=8);d.ellipse((xy[0]-12,xy[1]-12,xy[0]+12,xy[1]+12),outline=color,width=7);d.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='black',outline=color,width=3);self.text(im,mark['literalLabel'],(x+w/2,y+27),46);self.text(im,status,(x+w/2,y+72),36,color);out.append(dict(id=a['id'],point=xy,status=status,actualNativeRay=ray,declaredRootHeightNotAnatomicalJoint=True))
  self.text(im,'몸의 세 높이로 시야를 검사',(488,944),38,'#b8b8b8');return out
 def guides(self,im,p,frame,anchors,transform,output_frame,held_source=False):
  byid={a['id']:a for a in anchors};d=ImageDraw.Draw(im);out=[]
  cues=[r for r in self.t.get('guideCues',[])if r['sourceRef']==p['sourceRef']and r['startFrame']<=output_frame<r['endFrameExclusive']and r.get('camera',p['camera'])==p['camera']and r.get('mode',p['mode'])==p['mode']]
  for cue in cues:
   points=[]
   for aid in cue['anchorIds']:
    if aid not in byid:raise Pending('Spoken target anchor missing from actual trace: '+aid)
    a=byid[aid]
    if not guide_visible(a,p,frame,self.t['annotationPlan'],cue['kind'],held_source):break
    xy=point(a[p['camera']+'Viewport'],transform)
    if not(transform['x']<=xy[0]<=transform['x']+transform['width']and transform['y']<=xy[1]<=transform['y']+transform['height']):break
    points.append(xy)
   if len(points)!=len(cue['anchorIds']):continue # Any occluded endpoint clears the whole semantic guide.
   color=cue.get('color','#73c7c2');kind=cue['kind'];box=cue.get('labelXYWH')
   if not box:raise Pending('Speech-bound guide needs a reviewed label slot')
   x,y,w,h=box;label=(x+w/2,y+h/2);text=cue.get('labelKo')or LABELS.get(cue['anchorIds'][0])
   if not text:raise Pending('No canonical plain-language label for actual guide')
   if kind in('native-ray','span-leader','height-leader'):
    if len(points)!=2:raise Pending('Ray/height leader requires two actual projected anchors')
    d.line(points,fill=color,width=7)
    for xx,yy in points:d.line([(xx-13,yy),(xx+13,yy)],fill=color,width=7)
   else:
    xx,yy=points[0];d.ellipse((xx-13,yy-13,xx+13,yy+13),outline=color,width=7)
   d.line([label,points[0]],fill=color,width=5);d.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='black',outline=color,width=2);self.text(im,text,label,cue.get('fontSize',40),color)
   if kind in('height-leader','section-label'):
    badge=section_badge_layout(p,transform,self.style.font(32))
    if badge:
     bx,by,bw,bh=badge['rectXYWH'];d.rounded_rectangle((bx,by,bx+bw,by+bh),radius=8,fill='black',outline=badge['color'],width=2);self.text(im,badge['text'],badge['textXY'],badge['fontSize'],badge['color'])
   out.append(dict(cueId=cue['id'],anchorIds=cue['anchorIds'],actualSourceFrame=frame,points=points,kind=kind,editorialGuide=True,wordBoundaryProof=cue['wordBoundaryProof']))
  return out
 def game_guides(self,im,p,frame,transform,picture):
  rows=[r for r in self.t['annotationPlan'].get('gameKeyframes',[])if r['sourceRef']==p['sourceRef']and r['sourceFrame']==frame];d=ImageDraw.Draw(im);out=[]
  for row in rows:
   if row.get('visible')is not True:continue
   if row['sourceMediaSHA256']!=p['sourceSHA256']or row['rgbSHA256']!=hashlib.sha256(picture.tobytes()).hexdigest():raise Pending('Gameplay mark RGB/frame provenance differs from actual decoded image')
   bound(row['actualSourceReview']);x1,y1,x2,y2=row['bboxXYXY'];a=point(dict(x=x1/1920,y=1-y1/1080),transform);b=point(dict(x=x2/1920,y=1-y2/1080),transform);d.rectangle((*a,*b),outline='#73c7c2',width=8);self.text(im,row['label'],(488,970),40,'#73c7c2');out.append(row)
  for source in self.t.get('manualGameGuides',[]):
   if source['sourceRef']!=p['sourceRef']:continue
   exact=next((q for q in source['reviewedTemporalCoverage']['inspectedKeyframes']if q['frame']==frame),None)
   if exact and exact['rgbSHA256']!=hashlib.sha256(picture.tobytes()).hexdigest():raise Pending('Actual decoded gameplay differs from inspected manual keyframe RGB')
  for row in manual_regions(self.t.get('manualGameGuides',[]),p['sourceRef'],frame):
   x1,y1,x2,y2=row['bboxXYXY'];a=point(dict(x=x1/1920,y=1-y1/1080),transform);b=point(dict(x=x2/1920,y=1-y2/1080),transform);style=manual_label_style(row);draw=d.ellipse if row['type']=='ellipse'else d.rectangle;draw((*a,*b),outline=style['color'],width=style['stroke']);self.text(im,row['label'],style['anchor'],style['fontSize'],style['color']);out.append(row)
  return out # Manual bounded keyframes remain editorial; not detector output or every-frame inspection.
 def compose(self,frame):
  s=section_at(self.t,frame);im=self.base();evidence=[]
  if s['kind']=='mc':
   key=s['id']
   if key not in self.decoders:
    pts=self.stream.probe_pts(s['sourcePath'],(1080,900),self.ffprobe);self.decoder_count+=1;self.decoders[key]=self.stream.StreamDecoder(s['sourcePath'],(1080,900),pts,s['sourceStartFrame']/60,s['frameCount'],self.ffmpeg,self.work/f'mc-{self.decoder_count:03}.log')
   picture,pts=self.decoders[key].at((s['sourceStartFrame']+frame-s['startFrame'])/60);x,y,w,h=s['destinationXYWH'];im.paste(picture.resize((w,h),Image.Resampling.LANCZOS),(x,y));evidence.append(dict(kind='actualMC',sourceSHA256=s['sourceSHA256'],actualSourcePTS=pts))
  else:
   for p,dest in zip(s['panels'],destinations(s['panels'])):
    picture,proof=self.source_image(s,p,frame);transition=s.get('transition')
    if transition:
     if transition['kind']!='same-position-crossfade'or transition['frameCount']!=s['endFrameExclusive']-s['startFrame']or p['sourceRef']!='close':raise Pending('Unsupported source transition')
     before,before_proof=self.source_image(s,transition['fromPanel'],frame);alpha=(frame-s['startFrame']+1)/transition['frameCount'];picture=Image.blend(before,picture,alpha);proof=dict(current=proof,previous=before_proof,alpha=alpha,explicitEditorialCrossfade=True,notMeasuredIntermediateState=True)
    crop=p.get('cropXYXY')or[0,0,1920,1080];tr=fit(crop,dest);image=picture.crop(crop).resize((round(tr['width']),round(tr['height'])),Image.Resampling.LANCZOS);im.paste(image,(round(tr['x']),round(tr['y'])));f=source_frame(s,frame,p)
    kind='실제 게임 화면'if s['kind'].startswith('gameplay')else'직접 만든 Unity 설명';self.text(im,kind,(488,dest[1]-34),32,'#73c7c2'if p['camera']=='observer'else'#f5f5f5')
    if p['sourceRef']=='close':
     state,data=self.frame_data(p,f)
     if transition:marks=[] # Blended pictures never masquerade as measured intermediate body states.
     elif s['paragraph']==5 and s['sentenceIndexZeroBased']==2:marks=self.guides(im,p,f,closeup_guide_anchors(data),tr,frame,s.get('rate')is None) # Three diagnostic heights are introduced in the next sentence.
     else:marks=self.body_labels(im,p,f,data['anchors'],state,tr,dest)
    elif s['kind'].startswith('gameplay'):marks=self.game_guides(im,p,f,tr,picture)
    else:
     state,data=self.frame_data(p,f);marks=self.guides(im,p,f,data['anchors'],tr,frame,s.get('rate')is None)
    evidence.append(dict(source=proof,sourceToPanelTransform=tr,guides=marks,sourceKind=p['sourceKind']))
    if p.get('mode')in('baseline','shifted'):
     mode='기본 엄폐 위치'if p['mode']=='baseline'else'옮긴 엄폐 위치';self.text(im,mode,(dest[0]+dest[2]-112,dest[1]-32),30,'#e8cf83')
   if s['paragraph']in(5,6):self.text(im,'몸·이동 명령·카메라 동일 · 두 번째 엄폐 위치만 변경',(488,320),30,'#e8cf83')
   if s.get('holdReason'):self.text(im,'설명을 위한 정지 화면',(488,1497),26,'#b8b8b8')
  term=s.get('term')
  if term:
   self.text(im,term['english']+' ('+term['korean']+')',(488,315),40,'#e8cf83')
   if frame-s['startFrame']<min(120,s['endFrameExclusive']-s['startFrame']):self.text(im,term['meaning'],(488,365),34)
  pose=None
  for cue in self.t['catCues']:
   if cue['startFrame']<=frame<cue['endFrameExclusive']:
    pose=cue['pose'];cat=im.copy();self.style._cat(cat,pose);alpha=min(1,(frame-cue['startFrame']+1)/cue['easeInFrames'],(cue['endFrameExclusive']-frame)/cue['easeOutFrames']);im=Image.blend(im,cat,alpha)
  clean=im;captioned=im.copy();cue=next((x for x in self.t['captions']['ko']if x['startFrame']<=frame<x['endFrameExclusive']),None)
  if cue:self.style._captions(captioned,tuple(cue['lines']),self.stream.emphasis(cue))
  return clean,captioned,dict(outputFrame=frame,sectionId=s['id'],sources=evidence,captionId=cue['id']if cue else None,catPose=pose)
 def close(self,failed=False):
  for decoder in self.decoders.values():decoder.close(failed=failed or decoder.index!=len(decoder.selected)-1)

def _render(path,attempt,sample_frame=None,controller=None):
 t=read(path);verify_inputs(t);stream=primitives();stream.CONTROLLER=controller
 if sha(HERE/'render-first-film.py')!=ENCODER_SHA:raise Pending('Changed verified encoder primitive')
 shared=module('prospect_verified_first_encoder',HERE/'render-first-film.py');ffmpeg,ffprobe=shared.binaries();work=attempt/'work';work.mkdir();router=FrameRouter(t,work,ffmpeg,ffprobe,stream);encoders=[];tsha=sha(path);(attempt/'timeline.input.json').write_bytes(Path(path).read_bytes())
 try:
  if sample_frame is not None:
   clean,captioned,e=router.compose(sample_frame)
   for name,pic in [('clean',clean),('captioned',captioned)]:pic.save(attempt/f'sample-{sample_frame:06d}.{name}.png');pic.resize((375,667),Image.Resampling.LANCZOS).save(attempt/f'sample-{sample_frame:06d}.{name}.375.png')
   save(attempt/'sample-evidence.json',e);router.close(True);return dict(status='sample-only',complete=False,actualMotionReviewed=False)
  audio=work/'audio.m4a';stream.run([ffmpeg,'-hide_banner','-nostdin','-i',t['audio']['mix']['path'],'-vn','-c:a','aac','-b:a','192k','-n',audio],work/'audio.log')
  for name in('clean','captioned'):encoders.append(stream.VideoEncoder(work/f'{name}.video.mp4',t['totalFrames'],ffmpeg,work/f'{name}.encode.log'))
  samples=[]
  for frame in range(t['totalFrames']):
   if frame%60==0:
    fresh_authorization()
    if sha(path)!=tsha:raise Pending('Timeline changed duringownedrender')
   clean,captioned,e=router.compose(frame);encoders[0].write(clean);encoders[1].write(captioned)
   if frame in{s['startFrame']for s in t['sections']}:samples.append(e)
  router.close();[x.close()for x in encoders];encoders=[];outputs={}
  for name in('clean','captioned'):
   p=attempt/f'{SLUG}.{name}.mp4';stream.run([ffmpeg,'-hide_banner','-nostdin','-i',work/f'{name}.video.mp4','-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-n',p],work/f'{name}.mux.log');outputs[name]=dict(path=str(p),sha256=sha(p))
  for lang in('ko','en'):
   src=bound(t['subtitles'][lang]);p=attempt/f'{SLUG}.{lang}.srt';p.write_bytes(src.read_bytes());outputs[lang]=dict(path=str(p),sha256=sha(p))
  verify_inputs(t);fresh_authorization();result=dict(schemaVersion='06-02-render-manifest-v2',topicId='06.02',complete=True,timeline=dict(path=str(path),sha256=tsha),format=t['format'],totalFrames=t['totalFrames'],outputs=outputs,inputs=t['inputs'],sectionStartSamples=samples,gpuEncoding=False,modelsStarted=False,actualEncodedMotionReviewed=False,actualListening=False,humanApproval=False,platformActions=[]);save(attempt/'render-manifest.json',result);return result
 except BaseException as error:
  router.close(True)
  for encoder in encoders:encoder.close(True)
  save(attempt/'failed.json',dict(complete=False,error=str(error),timelineSHA256=tsha));raise
 finally:stream.CONTROLLER=None

def execute(path,sample_frame=None):
 verify_inputs(read(path));fresh_authorization();resource_path=HERE/'run-prospect-refuge-corrections-native.py'
 if sha(resource_path)!=RESOURCE_SHA:raise Pending('Audit changed selectedresource primitive')
 resource=module('prospect_private_composite_resource',resource_path);rt=resource.core.runtime;rt.PROTOCOL='architectural111-06-02-composite-v1';rt.OWNER='architectural-111-06-02-composite'
 stream=primitives();worker=rt.SingleWorker(MEDIA.parent/'06-02-composite-worker.json').acquire();state=MEDIA.parent/'06-02-composite-progress.json';known=set();token=None;rec=None;controller=None;attempt=None
 try:
  previous=worker.previous or{};known=set(previous.get('recoverableLeaseTokens',[]))
  if previous.get('leaseToken'):known.add(previous['leaseToken'])
  worker.update(recoverableLeaseTokens=sorted(known))
  if rt.LEASE.exists():
   old=read(rt.LEASE)
   if stream.reclaimable_lease(old,known,rt):rt.archive(rt.LEASE,old['token'])
  reason=resource.core.busy_reason()
  if reason:return dict(status='resource-declined-no-process',reason=reason,exitCode=75)
  if shutil.disk_usage(MEDIA).free<4*1024**3:raise Pending('Preserve previousmedia;4GiBCreserve required')
  attempt=MEDIA/'render-attempts-v2'/(datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir(parents=True,exist_ok=False)
  token=uuid.uuid4().hex;rec=dict(protocol=rt.PROTOCOL,owner=rt.OWNER,token=token,**rt.identity(),child=None,children=[],phase='reserved',output=str(attempt),timelineSHA256=sha(path))
  try:
   with rt.LEASE.open('x',encoding='utf8')as f:json.dump(rec,f)
  except FileExistsError:token=None;return dict(status='resource-race-no-process',exitCode=75)
  known.add(token);worker.update(leaseToken=token,recoverableLeaseTokens=sorted(known));controller=stream.OwnedController(rt,worker,rec)
  if resource.core.busy_reason(token):raise Pending('Resource changedbeforelaunch')
  save(state,dict(rec,status='owned-software-compositing',complete=False,gpuEncoding=False,modelsStarted=False));result=_render(path,attempt,sample_frame,controller);save(state,dict(rec,status=result['status']if'status'in result else'encoded-local-review-pending',complete=bool(result.get('complete')),gpuEncoding=False,modelsStarted=False));return result
 except BaseException as error:
  if controller:controller.terminate_owned() # Only Popenhandles createdbythiscontroller.
  save(state,dict(protocol=rt.PROTOCOL,owner=rt.OWNER,status='failed-preserved',error=str(error),complete=False,output=str(attempt)if attempt else None));raise
 finally:
  live=bool(rec and(rt.alive(rec.get('child'))or stream.pending_child(rec,rt)))
  if token and not live and rt.LEASE.exists():
   current=read(rt.LEASE)
   if rt.ours(current)and current['token']==token:rt.LEASE.unlink()
  worker.close(remove=not live)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--timeline');p.add_argument('--execute',action='store_true');p.add_argument('--sample-frame',type=int);a=p.parse_args()
 if not a.timeline:print(json.dumps(dict(ready=False,pending='Actual hash-bound06timeline notavailable; no process',mediaStarted=False)));return
 if a.sample_frame is not None and not a.execute:raise Pending('Samples are rendering: require explicit --execute --sample-frame')
 try:
  if a.execute:result=execute(Path(a.timeline).resolve(),a.sample_frame)
  else:result=dict(ready=True,structure=verify_inputs(read(a.timeline)),mediaStarted=False)
 except(RuntimeError,AssertionError,FileNotFoundError,KeyError)as error:
  if a.execute:raise
  result=dict(ready=False,pending=str(error),mediaStarted=False)
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
