"""Bind approved speech to finite, native-speed visual actions and exact states."""
from pathlib import Path
import importlib.util, argparse
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_edit_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
t=c.module('v8_edit_clock',H/'timing.py');bc=c.module('v8_board_cues',H/'board-cues.py')

def seg(start,end,file,kind='still',source=0,**extra):
 assert end>=start
 return dict(startFrame=start,endFrameExclusive=end,file=file,kind=kind,sourceStartFrame=source,nativeSpeed=1,**extra)

def check(rows,start,end):
 rows[:]=[r for r in rows if r['endFrameExclusive']>r['startFrame']]
 p=start
 for r in rows:
  assert r['startFrame']==p,(p,r);p=r['endFrameExclusive'];assert (c.R/r['file']).is_file(),r['file']
 assert p==end,(p,end)
 return rows

def main():
 c.authorized();clock=t.Clock();u=c.read(H/'unity-plan.json');native={r['id']:r for r in c.read(H/'labeled-native.json')['records']}
 boards={(r['scene'],r['line']):r for r in c.read(H/'board-manifest.json')['records']}
 maths={r['key']:r for r in c.read(H/'math-manifest.json')['records']};states={(r['key'],r['frame']):r['file']for r in c.read(H/'math-states.json')}
 game=c.read(H/'game-cut-plan.json');gs={r['id']:r for r in game['stills']};ep=c.read(c.O/'game/held-translate-end.json')
 exact=c.rel(c.O/'game/stills/held-translate-end.png');assert (c.R/exact).exists()
 paragraphs=[];gamecuts=[];adjustments=[]
 def state(asset,f):
  n=native[asset];return n['states'][str(f)]['file']
 def visual(sid,line,a,b,binding):
  base=binding['asset'];n=native[base];out=[]
  acts=[binding]+binding.get('secondary',[])
  initial=binding.get('sourceWindow',[0,n['frames']-1])[0] if binding['state']=='motion' or binding.get('cue') else (0 if binding['state']=='first' else n['frames']-1)
  cursor=a;picture=state(base,initial)
  for action in acts:
   asset=action['asset'];n=native[asset]
   if not action.get('cue'):continue
   cue=clock.cueframe(sid,line,action['cue']);assert a<=cue<b
   assert cue>=cursor,('overlapping native actions',sid,line,cursor,cue)
   out.append(seg(cursor,cue,picture))
   if action['state']=='motion':
    f0,f1=action.get('sourceWindow',[0,n['frames']-1]);end=cue+f1-f0
    assert end<=b,('Motion cannot fit speech interval without retiming',sid,line,asset,end,b)
    out.append(seg(cue,end,n['file'],'video',f0,unityAsset=asset));picture=state(asset,f1);cursor=end
   else:picture=state(asset,n['frames']-1);cursor=cue
  out.append(seg(cursor,b,picture));return out
 def steps(sid,line,a,b,asset,initial,actions):
  n=native[asset];out=[];cursor=a;picture=state(asset,initial)
  for literal,f0,f1 in actions:
   cue=clock.cueframe(sid,line,literal);assert cue>=cursor,(sid,line,literal,cursor,cue)
   out.append(seg(cursor,cue,picture));end=cue+f1-f0;assert end<=b
   out.append(seg(cue,end,n['file'],'video',f0,unityAsset=asset));picture=state(asset,f1);cursor=end
  out.append(seg(cursor,b,picture));return out
 # A visual substitution uses the spoken sequence, rather than forcing a
 # continuous sweep whose endpoint disagrees with the current explanation.
 overrides={
  ('m04',4):('point-sum',0,[('오른쪽 축을 한 번 따라가고',0,90),('새 앞쪽 축은 두 번',90,180)]),
  ('m07',1):('projection',180,[('정확히 같은 방향이면',0,0),('직각이면',180,180),('정반대면',360,360)]),
  ('m07',2):('projection',0,[('화살표가 옆으로 누울수록',0,180),('육십 도를 벌리면',180,120)]),
  ('m07',3):('projection',120,[]),
  ('m07',4):('projection',0,[('직각의 코사인은 영',0,180),('반대 방향의 코사인은',180,360)])}
 # Reverse source windows are not played backwards: a named angle is an
 # explicit exact-state comparison. No gameplay or animation is time-warped.
 def custom(sid,line,a,b,asset,initial,actions):
  out=[];cursor=a;picture=state(asset,initial);n=native[asset]
  for literal,f0,f1 in actions:
   cue=clock.cueframe(sid,line,literal);assert cue>=cursor,(sid,line,literal,cursor,cue)
   out.append(seg(cursor,cue,picture))
   if f1>f0:
    # First and last named angles must be present at their spoken words.
    # Use up to the finite native transition before the exact target cue
    # only where there is enough preceding explanatory speech.
    if sid=='m07' and line in [1,4]:
     picture=state(asset,f1);cursor=cue
    else:
     end=cue+f1-f0;assert end<=b;out.append(seg(cue,end,n['file'],'video',f0,unityAsset=asset));picture=state(asset,f1);cursor=end
   else:picture=state(asset,f1);cursor=cue
  out.append(seg(cursor,b,picture));return out
 mathbind={
  ('m04',2):('rows',[(0,60,'첫 줄에는'),(60,120,'둘째 줄의'),(120,180,'셋째 줄의')]),
  ('m04',4):('weighted',[(0,60,'오른쪽 축을 한 번'),(60,120,'위쪽 축은 영 번'),(120,180,'새 앞쪽 축은 두 번'),(180,240,'합치면')]),
  ('m05',3):('transpose',[(0,180,'첫째 행을')]),
  ('m08',2):('dcm',[(0,60,'첫째 행은'),(60,180,'행을 내려가면')]),
  ('m09',5):('composition',[(0,60,'에이에서 비로'),(60,120,'비에서 씨로'),(120,180,'두 행렬을 먼저 곱해')]),
  ('m10',3):('storage',[(0,60,'행렬 하나는'),(60,120,'이것을 이백이십오'),(120,180,'한 프레임에')])}
 for binding in u['paragraphs']:
  sid,line=binding['sceneId'],binding['line'];a,b=clock.paragraph(sid,line);pid=binding['paragraphId'];key=(sid,line)
  left=visual(sid,line,a,b,binding)
  if key in overrides:
   asset,initial,actions=overrides[key];left=custom(sid,line,a,b,asset,initial,actions)
   adjustments.append(dict(paragraphId=pid,reason='Exact target/property states aligned to spoken order, preserving approved narration',actions=actions))
  q=boards[key];cuts=[a]+[clock.cueframe(sid,line,x)for x in bc.CUES[sid][line-1]]+[b]
  assert cuts==sorted(cuts),(pid,cuts)
  right=[seg(cuts[i],cuts[i+1],q['states'][i]['file'])for i in range(3)]
  if key in mathbind:
   name,actions=mathbind[key];m=maths[name];out=[];cursor=a;picture=states[(name,0)]
   for f0,f1,literal in actions:
    cue=clock.cueframe(sid,line,literal);assert cue>=cursor,(pid,name,literal,cursor,cue)
    out.append(seg(cursor,cue,picture));end=cue+f1-f0;assert end<=b
    out.append(seg(cue,end,m['file'],'video',f0));picture=states[(name,f1)];cursor=end
   out.append(seg(cursor,b,picture));right=out
  layout='model-math'
  if key==('m01',2):
   right=left;left=[];cursor=a;picture=gs['ground']['file']
   for clip in game['clips']:
    cue=clock.frame(sid,line,clip['cue']['sourceKoOffset']);assert cue>=cursor,('Gameplay overlap needs review',cue,cursor)
    left.append(seg(cursor,cue,picture,sourceFrameForGuide=59925 if cursor==a else 60195,classification='gameplay-derived-analysis'))
    end=cue+clip['frames'];assert end<=b
    left.append(seg(cue,end,clip['file'],'video',clip['sourceStartFrame'],classification='independent-gameplay'))
    gamecuts.append(dict(clip,outputStartFrame=cue,outputEndFrame=end,startFrame=cue,endFrame=end))
    picture=exact if clip['id']=='totk-translate'else gs['upright']['file'];cursor=end
   left.append(seg(cursor,b,picture,sourceFrameForGuide=60390,classification='gameplay-derived-analysis'));layout='game-model'
  paragraphs.append(dict(id=pid,sceneId=sid,line=line,startFrame=a,endFrame=b,frames=b-a,layout=layout,left=check(left,a,b),right=check(right,a,b),narrationContinues=True,observationSilence=0))
 for cut in gamecuts:cut['endFrameExclusive']=cut['endFrame']
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',timelineSha256=c.sha(H/'timeline.json'),unityPlanSha256=c.sha(H/'unity-plan.json'),labeledNativeSha256=c.sha(H/'labeled-native.json'),boardManifestSha256=c.sha(H/'board-manifest.json'),mathManifestSha256=c.sha(H/'math-manifest.json'),paragraphs=paragraphs,gameCuts=gamecuts,liveGameCuts=gamecuts,adjustments=adjustments,sourcePlaybackRate=1,automaticLoops=False,gameFootageSeconds=sum(x['frames']for x in gamecuts)/60,gameQuota='concept-sized lecture; no fixed share')
 c.save(H/'edit-plan.json',result);print('Bound',len(paragraphs),'paragraphs /',len(gamecuts),'native game actions.')
if __name__=='__main__':main()
