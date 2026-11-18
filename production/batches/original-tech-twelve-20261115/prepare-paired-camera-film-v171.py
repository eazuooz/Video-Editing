"""Preserve the accepted speech; bind both panels to actual source frame clocks."""
from pathlib import Path
import copy,json,math
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-mario64-lakitu-camera'
def main():
 old=json.loads((P/'planning/film-beats-comparison-v154.json').read_text('utf8'));d=copy.deepcopy(old)
 mario=next(b['source']for p in old['paragraphs']for b in p['beats']if b.get('source',{}).get('sha256')=='47ce1fea4eb524e33c0732e931d8fe6d00b1c6ac1b8d9372fd0074f3a27dba90')
 intro=d['paragraphs'][0]['beats'];new=[]
 for source,idx,left,right in [(intro[0],0,.05,82),(intro[1],1,20,1154.4),(intro[1],3,25.76,1164.5),(intro[2],4,28.6,1167.34)]:
  b=copy.deepcopy(source);b.update(kind='pairedGame',source=intro[0]['source'],credit=intro[0]['credit'],firstClauseIndex=idx,sourceStartSeconds=left,rightSource=mario,rightSourceStartSeconds=right,label='실제 게임 · 서로 다른 녹화 비교');b.pop('guide',None);new.append(b)
 assert all(b['source']['sha256']=='3ab05a5105a173514cf731a5ce8d39e723e552526532e5dbdb71ecb22dc1b0ec'and b['rightSource']['sha256']=='47ce1fea4eb524e33c0732e931d8fe6d00b1c6ac1b8d9372fd0074f3a27dba90'and b['credit']=='World of Longplays · longplays.org · Spazbo4'for b in new)
 d['paragraphs'][0]['beats']=new
 for p in d['paragraphs'][1:]:
  if p['id']=='p003b':
   p['beats']=[dict(firstClauseIndex=0,kind='pairedNative',mode='look-around',view='player',startFrame=0,label='해설용 Unity 시연 · 같은 캐릭터',sourceSpeed=1)];continue
  for b in p['beats']:
   if b['kind']=='native':
    b.update(kind='pairedNative',view='player',label='해설용 Unity 시연 · 같은 캐릭터')
    if b['mode']=='follow':b['startFrame']=180
 caps=json.loads((P/'production/caption-timing-v147.json').read_text('utf8'));beats=[]
 for p in d['paragraphs']:
  for b in p['beats']:
   c=next(c for c in caps['cues']if c['paragraph']==p['id']and c['clauseIndex']==b['firstClauseIndex']);beats.append(dict(b,paragraph=p['id'],start=c['start']))
 for i,b in enumerate(beats):
  b['end']=beats[i+1]['start']if i+1<len(beats)else 93.2
  if b['kind']=='pairedNative':assert b['startFrame']+math.ceil((b['end']-b['start'])*60)<=720,(b['paragraph'],b['startFrame'],b['end']-b['start'])
 d.update(revision='paired-camera-v171',titleKo='3D 게임의 판도를 바꾼 마리오64',newFixedNativeProofPath='C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/shorts-mario64-lakitu-camera/camera-paired-v164/native-v166/accepted-full.json',nativePairRule='Same source frame index and independently matched model state. New fixed view left, approved original player view right. Authored model demonstration, not original commercial game implementation.',actualGameComparison='Original RE2 and Mario64 independent recordings shown concurrently, without synchronized input claims.',sourceTimeChanges='New right intro82..85.4,1154.4..1160.16,1164.5..1171.62; body86.4+,199+,220+,1139+. Original aspect, no actual-game replay or speed change.',narrationAndMusicPreserved=True,voiceSeconds=93.2,sourceRightsUnchanged=True)
 p=P/'planning/film-beats-paired-v171.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');print('Prepared '+str(len(beats))+' source-bound paired beats')
if __name__=='__main__':main()
