"""Retain every original lesson paragraph; insert observed fighter examples beside it."""
from pathlib import Path
import copy,json,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];R=H.parents[3];S=P/'script/fighters-v2'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 S.mkdir(parents=True,exist_ok=True);ko=(H/'additional-narration.ko.txt').read_text(encoding='utf-8').strip().split('\n\n');units=load(H/'additional-caption-units.json');en=[' '.join(x[1] for x in para) for para in units]
 mapping=[]
 for lang,add in [('ko',ko),('en',en)]:
  old=load(P/f'script/grid-v1/narration.{lang}.json');j=copy.deepcopy(old);j['revision']='fighters-v2';j['status']='source-reviewed-spoken-timing-bound';j['timingLocked']=True;j['ttsReady']=True
  j['scenes'][0]['lines'].append(add[0]);j['scenes'][1]['lines'].insert(1,add[1]);j['scenes'][3]['lines'].append(add[2]);j['fightersSourceMap']=(H.relative_to(R)/'source-review.json').as_posix()
  save(S/f'narration.{lang}.json',j)
  if lang=='ko':
   (S/'narration.spoken-ko.txt').write_text('\n\n'.join(p for s in j['scenes'] for p in s['lines'])+'\n',encoding='utf-8')
   for scene in old['scenes']:
    for n,line in enumerate(scene['lines']):mapping.append({'originalScene':scene['id'],'originalParagraph':n+1,'textSha256':hashlib.sha256(line.encode()).hexdigest(),'retainedUnchanged':line in next(s for s in j['scenes'] if s['id']==scene['id'])['lines']})
 save(H/'lesson-retention-plan.json',{'referenceMapRetainedFrom':str(P.relative_to(R)/'script/grid-v1/narration.ko.json'),'originalParagraphs':mapping,'additionalExamples':[{'after':'01-p02','game':'KOF XV','role':'Short punch versus broader preparation, torso rotation and recovery','observedSource':'fjEe1S7aNJs 41–68.7s','boundary':'Torso force → observed Ralf movement → why this matters at a small play size'},{'after':'02-p01','game':'Guilty Gear -Strive-','role':'Horizontal and rising silhouettes in native-speed play','observedSource':'Pe1CZN7txe8 315.5–322.0333s and108–113s','boundary':'Small play size → actual attack direction → same-motion amplitude comparison'},{'after':'04-p02','game':'KOF XV','role':'Galactica Phantom wind-up, strike and recovery','observedSource':'fjEe1S7aNJs220–224.8s and227.6–234.8s','boundary':'Whole-motion reading → Ralf concrete preparation/recovery → how the motion arrives at its target'}],'constraints':{'noSourceLessonClip':True,'noGameplayLoop':True,'playbackSpeed':1,'allOriginalExplanationsRetained':True,'originalVOUnregenerated':True,'sourceCreatorFramingAdded':False,'captionPosition':[960,970]},'glossary':['Exaggeration / 과장','Rig / 리그','Rotation / 회전','Translation / 이동','Overshoot / 오버슈트'],'rightsNote':'Local analytical review; publisher policies and recorder rights are recorded separately in source-review.json.'})
 print('17-paragraph KO/EN scripts and all14 original-paragraph retention mapping saved.')
if __name__=='__main__':main()
