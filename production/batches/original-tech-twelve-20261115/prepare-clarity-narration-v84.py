"""Prepare selected source-faithful expanded scripts, retaining exact old PCM."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
C=module('clarity_insertions',H/'clarity-content-v83.py').CONTENT
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 if p.exists():assert read(p)==json.loads(json.dumps(d)),p;return
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def norm(s):return re.sub('[^0-9a-z가-힣]','',s.lower())
def pairs(pair):
 ko,en=pair;a,b=ko.split('|'),en.split('|');assert len(a)==len(b),pair
 return list(zip(a,b))
def main():
 manifest=read(H/'local-final-review-manifest-v2.json');rows=[]
 for row in read(H/'batch.json')['projects']:
  slug=row['slug'];key=next((k for k in C if k in slug),None)
  if key is None:continue
  p=ROOT/'projects'/slug;spec=C[key]
  selection=next(p/'production'/x for x in ['accepted-voice-selection-v27.json','accepted-voice-selection-v10.json']if(p/'production'/x).exists())
  old=read(selection);oldn=read(old['narration']['path']);voice=read(old['voice']['path']);caps=read(old['captionTiming']['path']);technical=read(old['technicalVoiceReview']['path'])
  assert len(oldn['units'])==len(voice['rawChunks'])
  source_units={u['id']:dict(u,sourceRaw=r)for u,r in zip(oldn['units'],voice['rawChunks'])}
  units=[];new=[];reused=[];paragraphs=[];captionparas=[];nextid=1
  # Pixel/frame prerequisites belong immediately after the real-game opening.
  prerequisite=spec.get('before',{}).get('p001',[])if key=='inside'else[]
  def add(pair,pid):
   nonlocal nextid
   uid=f'c84u{nextid:03}';nextid+=1
   display=pairs(pair);u=dict(id=uid,paragraph=pid,ko=' '.join(x[0]for x in display))
   units.append(u);new.append(u);return display
  for para in oldn['paragraphs']:
   pid=para['id'];oldus=[u for u in oldn['units']if u['paragraph']==pid];oldcs=[(c['ko'],c['en'])for c in caps['cues']if c['paragraph']==pid]
   cursor=0;char=0;clauses=[]
   if not(key=='inside'and pid=='p001'):
    for pair in spec.get('before',{}).get(pid,[]):clauses+=add(pair,pid)
   for oldunit in oldus:
    matches=[];target=norm(oldunit['ko']);part=''
    while len(part)<len(target):
     pair=oldcs[cursor];cursor+=1;matches.append(pair);part+=norm(pair[0])
    assert part==target,(slug,oldunit['id'],part,target)
    if oldunit['id']in spec.get('replace',{}):
     for pair in spec['replace'][oldunit['id']]:clauses+=add(pair,pid)
    else:
     u=dict(source_units[oldunit['id']]);u['paragraph']=pid;units.append(u);reused.append(u);clauses+=matches
    if prerequisite and pid=='p001' and oldunit==oldus[0]:
     for pair in prerequisite:clauses+=add(pair,pid)
   assert cursor==len(oldcs)
   for pair in spec.get('after',{}).get(pid,[]):clauses+=add(pair,pid)
   pu=[u for u in units if u['paragraph']==pid];spoken=' '.join(u['ko']for u in pu)
   assert norm(spoken)==norm(' '.join(c[0]for c in clauses))
   paragraphs.append(dict(id=pid,ko=spoken,unitIds=[u['id']for u in pu],previousEnglishMeaning=' '.join(c[1]for c in clauses)))
   captionparas.append(dict(id=pid,clauses=clauses))
  observed=M/'clarity-revision-v83/source-contacts';contacts=[pin(x)for x in observed.glob(key+'*.jpg')]
  if key=='botw':contacts=[pin(observed/'botwfire.jpg')]
  if key=='spiderman':contacts=[pin(observed/'spider.jpg')]
  if key=='kart':contacts=[pin(observed/'kart.jpg'),pin(observed/'kart-detail.jpg')]
  observations={
   'journey':'Dune traversal, broad highlights and view changes verified in original and newly downloaded full FHD source. Compressed gameplay is not proof of internal grain buffers; N-dot-V/camera-only comparisons use labelled authored diagrams.',
   'inside':'Actual forest traversal at145–160 and180–195 shows thin branches and moving boy. Pixel-grid, jitter and history-rejection examples are labelled authored comparisons; original source image and sound remain paired.',
   'spiderman':'Actual disjoint source spans show descent, a visible web line, release/rising travel and building traversal. Source8–32/44–64 inspected. No controller inputs, hidden anchor endpoint or scoring telemetry inferred.',
   'control':'Dense actual source samples1–12 show shots, light fragments/papers and dust in office. Exact desk-fracture/material/constraint demonstrations remain labelled own models. No false identification of paper as a glass fragment.',
   'returnal':'Actual creature emergence at15–35 and battle43–59 inspected. Model shows parent/child previous-frame read, tube volume and orientation; enemy-state timing claim supported by developer article, not inferred from one combat frame.',
   'doom':'Actual DOOM2016 staged enemies and finishers around247.3–251.8 and308.4–320 inspected. The earlier+40health precedes the first finisher and is not attributed to it. Chainsaw/fuel example uses a labelled model unless actual later footage is verified.',
   'botw':'Fire-impact/grassy-tree ignition in local49–55 of3060–3130 source; separate625–750 source shows large ice before fire, fire beside ice27–43 and shrink/disappearance by59. This candidate contains no rain; water/rain examples are authored explanatory models.',
   'kart':'Actual antigravity sideways wheels and glowing post contact226.5–227.5 with spin/boost seen. Nearby second-lap spans show antigravity traversal, not proof of another collision. Other-kart spin rule supported by officialNintendo2014 source and own model.'
  }[key]
  review=p/'planning/source-action-clarity-v84.json'
  save(review,dict(slug=slug,originalActionReview=pin(p/'planning/source-action-review-v3.json'),primaryReview=pin(p/'planning/primary-source-review-v1.json'),contactSheetsActuallyInspected=contacts,observations=observations,realGameVersusAuthoredModelLabelled=True,sourceOrderPreserved=True,actualContinuousPlayback=False,humanApproval=False))
  source_inputs=[pin(H/'selected-clarity-request-v83.json'),pin(H/'clarity-content-v83.py'),pin(review),pin(p/'planning/primary-source-review-v1.json'),pin(p/'planning/source-order-map-v1.json')]
  np=p/'planning/narration-repair-v84.json'
  d=dict(schemaVersion=1,slug=slug,origin=old['narration'],sourceVoice=old['voice'],sourceAsr=technical['sourceAsr'],sourceLevels=technical['sourceLevels'],sourceInputs=source_inputs,units=units,newUnits=new,reuseUnits=reused,newEnglish=[],paragraphs=paragraphs,narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,reason='User-selected clarity and interleaved examples. Original core order retained; added definitions/examples beside relevant passage. New original phrasing, unchanged selected PCM reused byte-exact.',humanApproval=False,voiceAcceptedForFilm=False,headingFreeReadThroughCompleted=True,rawInternalLevelThresholdsUnchanged=True)
  save(np,d)
  save(p/'planning/caption-clauses-repair-v84.json',dict(schemaVersion=1,source=pin(np),paragraphs=captionparas,actualSpeechTimesAssigned=False,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True))
  sp=p/'script/narration.repair-v84.json';save(sp,dict(title=slug,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
  tts=copy.deepcopy(read(ROOT/'projects/shorts-returnal-particle-tentacles/production/tts-manifest-repair-v27.json'))
  tts.update(slug=slug,revision='user-selected-easy-examples-v84');tts['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/')
  tts['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+slug+'/voice-repair-v84',filenameStem='clarity-v84',gpuProfileReason='Existing approvedQwen1.7B/reference profile. User-authorized below35%/8GiB guard, unchanged foreign-work checks and7168MiB cap. One job only.')
  save(p/'production/tts-manifest-repair-v84.json',tts)
  rows.append(dict(order=row['order'],slug=slug,newUnits=len(new),reuseUnits=len(reused),totalUnits=len(units),narration=pin(np),sourceActionReview=pin(review)))
 save(H/'selected-clarity-narration-preparation-v84.json',dict(projects=rows,narrationOrderPreserved=True,unchangedPcmReused=True,newVoiceCompleted=False,finalVideosCompleted=False,humanApproval=False))
 print(json.dumps(rows,ensure_ascii=False))
if __name__=='__main__':main()
