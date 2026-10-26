"""Source-code branch audit of every actually used packed explanation reveal.

This mirrors the reviewed wait/animation schedule to catch end-of-cut reveals;
it does not claim to render, see pixels, play motion, or listen to narration.
"""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[4]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for slug in ('in-game-cutscenes','start-with-climax'):
 P=R/'projects'/slug;H=P/'production/batch-v1';M=R/'motion-canvas/src/projects'/slug/'batch-v1';plan=load(H/'edit-plan.json');data=load(M/'motion-data.json');cuts=[c for c in plan['cuts']if c['kind']=='explanation'];assert len(cuts)==len(data['segments']);reviews=[]
 for cut,t in zip(cuts,data['segments']):
  d=t['duration'];clock=0;used=[];events=[]
  def until(i):
   global clock
   assert i<len(t['cues']),(cut['id'],'missing actually-used cue',i)
   q=t['cues'][i];assert 0<=q<d,(cut['id'],'reveal scheduled at/after cut end',i,q,d)
   used.append(i);clock=max(clock,q)
  def event(name,animation=0):
   global clock
   assert clock<d and clock+animation<d,(cut['id'],name,clock,animation,d)
   events.append({'name':name,'start':clock,'fullyVisible':clock+animation,'remainingAfterVisible':d-clock-animation,'globalStart':cut['startFrame']/60+clock,'firstPossibleFrame':math.ceil(clock*60)})
   clock+=animation
  mode=t['kind']
  event('initial diagram state')
  if mode=='overview':
   for i in range(3):
    if slug=='start-with-climax' or i:until(i)
    event('overview example'+str(i+1))
   if slug=='start-with-climax':until(3)
   event('overview benefit')
  elif mode=='formats':
   until(0);event('real-time definition',.2);until(1);event('stored-video definition',.2);until(2);event('two-format summary')
  elif mode=='fixedVideo':
   until(0);event('frame-rate canonical name and plain definition');until(1);event('hypothetical60/30 counts and proportional bars',.8)
  elif mode=='quality':until(1);event('conditional stored-video comparison')
  elif mode=='viewingReward':
   if t.get('rewardOutside'):until(0);event('outside availability condition')
   until(1);event('weaker viewing-access reward'if t.get('rewardOutside')else'process/story relation')
  elif mode=='advance':until(1);event('right movie partial-skip control',.3);until(2);event('different from whole-scene skip')
  elif mode=='playbackControls':event('ordinary progress movement',.8);until(1);event('faster movement',.35);event('seek and viewing-design summary')
  elif mode=='skipScope':until(1);event('whole skip choice');until(2);event('staff-credit scope')
  elif mode=='wholeSkip':until(1);event('save/person separation and choice');until(2);event('previously introduced whole-scene scope reminder')
  elif mode=='skipChoice':until(1);event('optional confirmation and return')
  elif mode=='qte':until(1);event('timed input window',.65);until(2);event('watching-to-reacting caution',.15)
  elif mode=='control':
   event('input step',.24);until(1);event('response step',.24);until(2);event('immediate-goal step',.24)
  elif mode=='earlyPeak':
   event('initial qualitative curve',.8);until(1);event('earlier peak transform',.7);until(2);event('late fallback advice'if t.get('showFallback')else'early appeal summary')
  elif mode=='informationOrder':until(1);event('player information order',.3)
  elif mode in ('ruleUse','evidenceSelection'):until(1);event('inspected after image',.24);until(2);event('action-result summary')
  elif mode=='firstAct':until(1);event('needed rule');until(2);event('direct attempt')
  else:raise ValueError('Review new actually-used branch explicitly: '+mode)
  reviews.append({'cut':cut['id'],'paragraphIds':cut['paragraphIds'],'kind':mode,'duration':d,'usedCueIndices':sorted(set(used)),'unusedCueIndices':[i for i in range(len(t['cues']))if i not in used],'events':events,'allUsedCueRevealsCompleteBeforeCutEnd':True,'captionClockSource':'Current measured captions.json; D28 overview nouns additionally use exact current full-ASR phrase starts.'})
 report={'slug':slug,'status':'all-actually-used-reveals-fit-source-code-audit','sourceSha256':sha(M/'visuals.tsx'),'dataSha256':sha(M/'motion-data.json'),'planSha256':sha(H/'edit-plan.json'),'cutsReviewed':len(reviews),'findingsResolved':['D28 control footer depended on absent cue3 and appeared at cut end; unspoken recap footer removed.','D28 early-peak fallback advice now appears only in08 at its actual last clause, rather than during01.','D28 overview examples now reveal at measured first-battle/giant-enemy/first-trial word starts.','D27 fixedVideo frame-rate definition and60/30 example reveal at their separate spoken clauses.','D27 cut020 continuous-movie control shows at cue1, whole-skip contrast at cue2.'],'reviews':reviews,'renderedPixelsMotionAudio':'pending; this schedule audit does not establish actual encoded node/glyph visibility or listening approval.'}
 (H/'mc-cue-deadline-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(slug,len(reviews),'used-reveal deadlines PASS')
