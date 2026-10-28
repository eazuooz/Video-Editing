"""Author only directly inspected target marks, in source coordinates and time."""
from pathlib import Path
import json,copy
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 plan=a.read(H/'edit-plan.draft.json');inventory=a.read(H/'evidence/annotation-sources-v1/evidence.json');rows=[]
 def add(cid,name,label,shape,keys,labelPosition,color='green'):
  c=next(x for x in plan['cuts'] if x['id']==cid);scale=c['viewport'][2]/1920;ox,oy=c['viewport'][:2]
  transformed=[];proof=[]
  for k in keys:
   t=k[0]-c['sourceStart']
   if shape=='path':d={'t':t,'points':[[ox+x*scale,oy+y*scale] for x,y in k[1]]}
   else:
    x,y,w,h=k[1:];d={'t':t,'x':ox+x*scale,'y':oy+y*scale,'w':w*scale,'h':h*scale}
   transformed.append(d)
   rec=next(x for x in inventory['records'] if x['source']==c['source']);nearest=min(rec['frames'],key=lambda x:abs(x['seconds']-k[0]));assert abs(nearest['seconds']-k[0])<.018;proof.append(nearest)
  mark={'id':name,'shape':shape,'t0':transformed[0]['t'],'t1':transformed[-1]['t'],'color':color,'thickness':8,'label':label,'fontSize':44,'labelPosition':labelPosition,'keyframes':transformed,'revealSeconds':.22,'sourceEvidence':{'sourceSha256':c['sourceSha256'],'frames':proof,'meaning':'editorial target guide; direct source-frame inspection, not detector output or game measurement'},'movingPixelReview':'pending final encoded frames'}
  if not 0<=mark['t0']<mark['t1']<=c['frames']/60:raise ValueError('Mark leaves cut')
  keyline=copy.deepcopy(mark);keyline.update(id='keyline-'+name,color='#000000',thickness=16)
  rows.extend([{'cutId':cid,'mark':keyline},{'cutId':cid,'mark':mark}])
 add('c019','visible-question-mark','네모 + 물음표','circle',[(9.5095,1210,300,180,180),(10.01,1010,300,180,180),(10.5105,810,300,180,180),(11.011,617,300,180,180)],[1050,240])
 add('c019','petal-outline','꽃잎의 윤곽','circle',[(13.5135,1125,370,180,180),(14.014,925,370,180,180),(14.5145,725,370,180,180)],[1040,250])
 # Keep the flower target inside the ellipse, below its native speech bubble.
 add('c020','flower-response','가까이 가면 반응','circle',[(16,1350,410,160,110),(16.5,1560,410,160,110),(17,1590,410,160,110),(17.5,1420,410,160,110),(18,1240,410,160,110),(18.5,1040,410,160,110),(19,840,410,160,110)],[990,240])
 # Foreground path and distant mountain regions are visible at the spoken list.
 # Open strokes leave the actual edge readable instead of filling the region.
 add('c028','foreground-walkable-edge','앞쪽 길','path',[(23.490133,[[950,718],[1230,718],[1510,642]]),(23.990633,[[740,718],[1020,718],[1320,645]]),(24.491133,[[650,730],[940,704],[1230,640]])],[490,800])
 add('c028','distant-scenery','멀리 있는 풍경','rect',[(25.992633,1080,190,700,410),(26.493133,1020,190,700,410),(26.993633,960,190,700,410)],[1160,175],'blue')
 # Final encoded inspection isolates the pink cliff, excluding foreground coins
 # and spray. Keep the measured clock and label; these are OUTPUT coordinates.
 refinement=a.read(H/'c028-distant-scenery-refinement.json')['editScope']
 for row in rows:
  if row['cutId']=='c028' and row['mark']['id'] in refinement['markIds']:
   assert [k['t'] for k in row['mark']['keyframes']]==[k['t'] for k in refinement['newKeyframes']]
   row['mark']['keyframes']=copy.deepcopy(refinement['newKeyframes'])
 inventory['status']='directly-viewed';inventory['review']={'allSixContactSheetsViewed':True,'selectedNativeFullFramesViewed':True,'topics':['question-mark block outline','flower outline/response','foreground path','distant scenery'],'notClaimed':'continuous playback or every-frame tracking approval; final encoded moving review remains pending'};a.save(H/'evidence/annotation-sources-v1/evidence.json',inventory)
 a.save(H/'source-marks.json',{'status':'authored-from-directly-inspected-frames','proof':a.artifact(H/'evidence/annotation-sources-v1/evidence.json'),'marks':rows,'finalMovingAnd375Pixels':'pending'})
 # Stable replacement, so repeated authoring never duplicates annotations.
 for c in plan['cuts']:c['marks']=[m for m in c['marks'] if not m.get('sourceEvidence')]
 for row in rows:next(c for c in plan['cuts'] if c['id']==row['cutId'])['marks'].append(row['mark'])
 import video_pipeline as v
 for c in plan['cuts']:
  if c['kind']=='independent-gameplay':v.annotations(c,plan)
 a.save(H/'edit-plan.draft.json',plan)
 print(f'{len(rows)//2} inspected target marks added; geometric clearance passes')
if __name__=='__main__':main()
