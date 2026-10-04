"""Persist direct review of local source sheets; no raster or media delivery."""
import hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[4]
def read(p): return json.loads(p.read_text('utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
comparison=read(BASE/'additional-cross-source-comparison.json')
findings=[
 ('Pepper cave','Different yellow vertical bends and trajectory from DRILL brown low cave; fresh visible action.'),
 ('Pepper column','Yellow vertical column and rope platform differ from z4 water column/bulb; fresh visible action.'),
 ('Pepper water','Dark reeds and metal water vehicle attack differ from z4 tropical wooden platform; fresh action, short duration held.'),
 ('Pepper cauldron','Similar object, different positions/path; not proof of identical files. Short segment conservatively held.'),
 ('Pepper mech','Shared green roof setting but different positions/destruction; short segment held.'),
 ('Plucky elevator','Industrial art overlaps, but vertical pink-panel lift differs from flat spike-floor action; fresh action.'),
 ('Plucky city portal','Same central town area with different portal/camera; held pending exact sequence overlap review.'),
 ('Plucky mug','Orange fireballs/red costume differ from Rocket purple mug entry; short segment held.'),
 ('Plucky castle','Upper castle-wall climbing differs from WFI portal at castle base; short segment held.'),
 ('Plucky rocket','Blue day/CD/red costume flight differs from green night spool flight; short segment held.'),
 ('Plucky flags','Same puzzle area, different order/camera; held pending exact sequence overlap review.'),
 ('Plucky accordion','Horizontal texture/position and red costume differ from Jd vertical orange/Pink-costume path; short segment held.')]
sheets=[]
for s in comparison['sheets']:
    p=ROOT/s['path'];assert sha(p)==s['sha256']
    sheets.append({'path':s['path'],'sha256':s['sha256'],'directlyRead':True,'pairs':len(s['rows'])})
save(BASE/'direct-additional-cross-source-review.json',{'schemaVersion':1,'reviewedAt':now(),
 'method':'All9 sheets/36 paired native samples directly read at three anchors per case. Native PTS retained. Similar art or a numeric distance alone is not a duplicate verdict.',
 'sheets':sheets,'cases':[{'case':k,'directObservation':v} for k,v in findings],
 'all9SheetsDirectlyRead':True,'approvedIntervals':[],'approvedActualSeconds':0,'finalCaptionApproval':False,'newGitImages':0})
discovery=read(BASE/'discovery-plucky-mine.json');native=read(BASE/'native-review-plucky-mine.json')
source=native['sources'][0]
all_sheets=discovery['sources'][0]['sheets']+source['actionSheets']+source['boundarySheets']
assert len(all_sheets)==31
proof_sheets=[]
for entry in all_sheets:
    p=entry['path'] if isinstance(entry,dict) else entry
    digest=sha(ROOT/p)
    if isinstance(entry,dict): assert digest==entry['sha256']
    proof_sheets.append({'path':p,'sha256':digest,'directlyRead':True})
observations=[
 {'rangeSeconds':[0,3.5],'observation':'Virtual book cover/opening and brief standing; ESRB badge through early combat. Exclude cover/idle and start gameplay after badge.'},
 {'rangeSeconds':[3.5,21.3],'observation':'Runs, strikes purple enemy, dodges/attacks charging horned enemy. At21.48/21.50/21.52 transition to NPC dialogue is already blended; end conservatively before it.'},
 {'rangeSeconds':[22,31.5],'observation':'NPC dialogue and standing; excluded.'},
 {'rangeSeconds':[31.5,42.5],'observation':'Approaches green opening, leaves printed2D surface for virtual3D desk/book, then walks along the virtual book. Later camera pullback/idle/page turn excluded.'},
 {'rangeSeconds':[52.5,64.5],'observation':'Enters dark printed surface; spotlight platform traversal, approaches and strikes enemy, moves down to page opening. Page flip around65 excluded.'},
 {'rangeSeconds':[66,80.7],'observation':'NPC dialogue/pan to chest and brief standing excluded.'},
 {'rangeSeconds':[80.7,90.5],'observation':'Runs to opening, leaves printed surface for virtual desk and walks across translucent mine drawing. Yellow key visible; do not infer input mapping.'},
 {'rangeSeconds':[93,98.5],'observation':'Virtual book tilts left and yellow key moves left across drawing; book returns flat. No claim this solves the later blue chest.'},
 {'rangeSeconds':[100,108.9],'observation':'Virtual character runs and enters opening, then2D mine attack. Transition observed in same continuous region; no universal rule inferred.'},
 {'rangeSeconds':[110,127],'observation':'Dialogue, key carried toward blue chest, prolonged idle facing closed chest; no opening observed. Exclude this candidate rather than implying success.'},
 {'rangeSeconds':[132.2,146.6],'observation':'Leaves opening, walks in virtual desk/book space, book tilts right and yellow key moves right; book returns flat.'},
 {'rangeSeconds':[147,165.5],'observation':'Traverses drawing and enters opening, fights several enemies and rocks; red chest opens and a card graphic appears. Do not infer full-game victory/required input.'},
 {'rangeSeconds':[168,191.5],'observation':'Dialogue, town and ending title outside approved candidate windows. Do not count them or write new claims without native review.'}]
review={'schemaVersion':1,'reviewedAt':now(),'sourceVideoId':'CJ0_Xh59b98','sourceSha256':source['sourceSha256'],
 'nativeFrameRate':'60000/1001','nativeFps':source['nativeFps'],'all31SheetsDirectlyRead':True,
 'discoveryFrames':len(discovery['sources'][0]['actualPtsSeconds']),'nativeActionFrames':len(source['actionSamples']),
 'boundaryTriplets':len(source['candidateBoundaryFrames']),'sheets':proof_sheets,'observations':observations,
 'boundaryLimit':'The12 triplets mostly inspect proposed window edges, not every later selected cut. Final encoded boundaries and all subtitle cues require separate inspection.',
 'screenLimit':'Printed narrative text near bottom and key/character/opening positions need final framing review under fixed960,970 captions; captions must not move.',
 'virtualDeskIsInGame':True,'physicalHandsOrPapercraftUsed':False,'sourceAudioUsed':False,'selfCreatedGameExamples':0,
 'approvedFinalIntervals':[],'approvedActualSeconds':0,'finalBodyRatioApproved':False,'finalCaptionApproval':False,'newGitImages':0}
save(BASE/'direct-plucky-mine-review.json',review)
discovery.update(status='closed-all12-discovery-sheets-directly-read',directReview='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/direct-plucky-mine-review.json')
discovery['sources'][0]['nativeFps']=source['nativeFps'];discovery['sources'][0]['nativeFrameRate']='60000/1001'
save(BASE/'discovery-plucky-mine.json',discovery)
native.update(status='closed-all19-native-sheets-directly-read-planning-selection',directReview=discovery['directReview']);save(BASE/'native-review-plucky-mine.json',native)
old=read(BASE/'source-action-bank-v2.json')
bank=json.loads(json.dumps(old));bank['previousBank']='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/source-action-bank-v2.json'
windows=[(3.5,8,'2D run and first enemy strikes'),(8,16,'Horned enemy approach, dodges and strikes'),(16,21.3,'Continued2D combat before dialogue dissolve'),
 (31.5,36.2,'Approach opening and2D-to-3D departure'),(36.2,42.5,'Virtual desk/book traversal'),(52.5,58.6,'Enter dark printed surface and traverse platform'),
 (58.6,64.5,'Spotlit enemy strikes and traversal'),(80.7,83.9,'Opening departure to virtual desk'),(84,90.5,'Traverse translucent mine drawing'),
 (93,98.5,'Book tilt left and key moving left'),(100,108.9,'Approach/enter opening then2D mine attack'),
 (132.2,138.2,'Opening departure, traversal and start of book tilt'),(138.2,146.6,'Book tilt right and key moving right'),
 (147,153.3,'Traverse virtual book and enter opening'),(153.3,165.5,'2D combat, red chest and card graphic')]
new=[]
fps=60000/1001
for lo,hi,action in windows:
    start=math.ceil(lo*fps);end=math.floor(hi*fps)
    c={'id':f'action-{len(bank["clips"])+len(new)+1:02}', 'sourceVideoId':'CJ0_Xh59b98','sourceUrl':'https://www.youtube.com/watch?v=CJ0_Xh59b98',
      'sourceSha256':source['sourceSha256'],'nativeFrameRate':'60000/1001','nativeFps':fps,
      'startFrame':start,'endFrameExclusive':end,'inSeconds':start/fps,'outSeconds':end/fps,'seconds':(end-start)/fps,
      'visibleAction':action,'planningClaim':'Name/genre alone does not explain surface, visible verb and observed condition.',
      'viewerFocus':'Character, printed surface/virtual desk, opening and key positions; separate observed movement from proposed rule.',
      'diagramConnection':'Surface → verb → visible change; observed fact versus undecided question',
      'insertionPoint':'Related additive example between existing explanations; exact placement/narration still pending',
      'caution':'No button/universal rule/automatic victory inferred. Avoid dialogue, idle and dissolve; printed bottom text needs framing review.',
      'status':'native-reviewed-unique-planning-candidate-not-final-timeline','finalCaptionFramingApproved':False,
      'directReview':discovery['directReview']}
    new.append(c)
for a,b in zip(new,new[1:]): assert a['endFrameExclusive']<=b['startFrame']
bank['clips']+=new;bank.update(createdAt=now(),status='95-conservative-unique-source-candidates-not-final-timeline',
 uniqueSourceSeconds=sum(x['seconds'] for x in bank['clips']),bodyRatioApproved=False,finalCutAndCaptionApproval=False)
bank['bySourceSeconds']['CJ0_Xh59b98']=sum(x['seconds'] for x in new)
bank['directReview']+=['production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/direct-plucky-mine-review.json']
bank['nextAction']='Write independent matching additive narration for unique actions, measure it, and approve final source/cue framing and exact native boundaries. Do not shorten existing explanations or count idle/dialogue.'
save(BASE/'source-action-bank-v3.json',bank)
print(json.dumps({'allComparisonSheets':len(sheets),'mineSheets':len(proof_sheets),'planningNewClips':len(new),'planningNewSeconds':sum(x['seconds'] for x in new),'totalPlanningSeconds':bank['uniqueSourceSeconds'],'finalRatioApproved':False}))
