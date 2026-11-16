"""Bind interleaved examples to reviewed speech units and source clocks."""
from pathlib import Path
import argparse,hashlib,json,math
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
KEYS={
 'journey':['sand-layers','sand-mips','sand-flicker','sand-glints','sand-mask','sand-layers'],
 'inside':['temporal-pixels-easy','temporal-pixels-easy','temporal-reproject','temporal-clip','temporal-history-blur','temporal-reproject'],
 'spiderman':['spider-anchors-easy','spider-rays','spider-volume','spider-criteria','spider-criteria','spider-anchors-easy'],
 'control':['control-hierarchy','control-hierarchy','control-hierarchy','control-bonds','control-pieces-easy','control-surface-hole'],
 'returnal':['returnal-chain-easy','returnal-bodies','returnal-delay','returnal-surface','returnal-surface','returnal-chain-easy'],
 'doom':['doom-rewards']*6,'botw':['botw-rules','botw-motion-state-easy','botw-rules','botw-rules','botw-motion-state-easy','botw-rules','botw-rules'],
 'mariokart8':['kart-conditions']*5}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);a=ap.parse_args();assert a.project=='shorts-mariokart8-spin-boost';p=ROOT/'projects'/a.project;key=next(k for k in KEYS if k in p.name)
 selection=p/'production/accepted-voice-selection-v95.json';sel=read(selection);n=read(sel['narration']['path']);caps=read(sel['captionTiming']['path']);voice=read(sel['voice']['path']);duration=voice['canonical']['duration'];cues=caps['cues'];units=n['units'];beats=[]
 def start_unit(uid):return next(c['start']for c in cues if c['unitId']==uid)
 def locate(prefix):
  matches=[u for u in units if u['ko'].startswith(prefix)];assert len(matches)==1,(prefix,len(matches));return matches[0]['id']
 for para,diagram in zip(n['paragraphs'],KEYS[key]):
  uid=para['unitIds'][0];beats.append(dict(kind='diagram',key=diagram,start=start_unit(uid),paragraph=para['id'],localModelStartSeconds=0))
 beats[0]['start']=0
 def interval(first,last,body):
  # Each interval starts and ends at actual independently recognized unit words.
  first,last=locate(first),locate(last);lo=start_unit(first);lastindex=next(i for i,u in enumerate(units)if u['id']==last)
  hi=start_unit(units[lastindex+1]['id'])if lastindex+1<len(units)else duration
  assert lo<hi
  for b in list(beats):
   if lo<=b['start']<hi:beats.remove(b)
  para=next(u['paragraph']for u in units if u['id']==first);fallback=KEYS[key][int(para[1:])-1]
  beats.append(dict(body,start=lo,paragraph=para))
  if hi<duration:
   nextpara=units[lastindex+1]['paragraph'];beats.append(dict(kind='diagram',key=KEYS[key][int(nextpara[1:])-1],start=hi,paragraph=nextpara,localModelStartSeconds=0))
 def diagram(first,last,k):interval(first,last,dict(kind='diagram',key=k,localModelStartSeconds=0))
 def game(first,last,file,source_start,label):
  interval(first,last,dict(kind='game',source=pin(M/p.name/'sources'/file),sourceStartSeconds=source_start,label=label,sourceSpeed=1,sourceAudio='paired-original'if key=='inside'else'none'))
 def native(first,last,mode,view,frame=0,topic=None,label='해설용 모형 · 직접 만든 비교 장면'):
  interval(first,last,dict(kind='native',mode=mode,view=view,startFrame=frame,topic=topic,label=label))
 if key=='journey':
  file='royaltyfree-PcL6zmz4GM8-full-v83.mp4';label='게임 장면 · Journey · PS5 녹화'
  game('이 게임의 사막은','이 게임의 사막은',file,98,label)
  game('발밑의 작은 빛점과','작은 점은 모래알 느낌을',file,302,label)
  diagram('작은 거울을','입체 모래알 대신','sand-light-view-easy')
  diagram('여기서는 카메라만','모래에 전구를','sand-light-view-easy')
  diagram('처음에는 빛과 시선을','처음에는 빛과 시선을','sand-light-view-easy')
  diagram('이를 바꿔 작은 표면이','비교 모형에서 시선을','sand-mirrors-easy')
  game('언덕을 위에서','언덕을 위에서',file,204,label)
  game('마지막은 모래 언덕에','이 반사광이',file,222,label)
  game('거친 결과 작은 반짝임,','거친 결과 작은 반짝임,',file,326,label)
 elif key=='inside':
  file='pressstartplay-9rwA7qvYnds-full-f299-v3.mp4';label='게임 장면 · INSIDE · Xbox 녹화'
  game('인사이드처럼','인사이드처럼',file,180,label)
  native('매번 픽셀','이를 지터','jitter-only','detail')
  native('한 장에서 놓친','한 장에서 놓친','temporal-clipping','detail')
  game('소년이 오른쪽으로','소년이 오른쪽으로',file,186,label)
  game('소년이 지나가서','소년이 지나가서',file,193,label)
  native('그 정보를 현재 색과','현재 화면과 맞는','temporal-clipping','detail',360)
 elif key=='spiderman':
  file='pressstartplay-5Q4AfoUX1eU-swing-120-190-v4.mp4';label='게임 장면 · Spider-Man · PC Remastered'
  game('스파이더맨은 거미줄이','스파이더맨은 거미줄이',file,10,label)
  game('실제 장면에서 내려갔다가','실제 장면에서 내려갔다가',file,20,label)
  diagram('모형에서는 줄의','모형에서는 줄의','spider-anchors-easy')
  diagram('앞으로 가고 싶은데','또 너무 낮게','spider-anchors-easy')
  game('실제 장면의 줄 방향과','실제 장면의 줄 방향과',file,26,label+' · 이동 비교')
  switch=next(c for c in cues if c['ko'].startswith('모형의 높은 점과 낮은 점을'));beats.append(dict(kind='diagram',key='spider-anchors-easy',start=switch['start'],paragraph=switch['paragraph'],localModelStartSeconds=0))
  game('실제 영상만으로','실제 영상만으로',file,44,label)
  native('줄이 팽팽해지면','줄이 팽팽해지면','a','overview',120,'spiderman')
  native('좋은 부착점이 있어야','좋은 부착점이 있어야','b','overview',120,'spiderman')
  game('같은 도시라도','같은 도시라도',file,60,label)
 elif key=='control':
  file='control-free-TVfahIR7lYQ-candidate-copy-v2.mp4';label='게임 장면 · Control · Xbox Series S'
  game('컨트롤에서 책상이','컨트롤에서 책상이',file,0,label+' · 전투 맥락')
  game('이 사무실에서는','이 사무실에서는',file,6,label+' · 총격과 먼지')
  diagram('비교 모형에서 큰 판이','그 옆의 작은 조각과','control-pieces-easy')
  native('만들어 둔 조각과','어디가 떨어지고','a','detail',0,'control')
  native('충격으로 연결이','충격으로 연결이','b','detail',150,'control')
  diagram('큰 판이 떨어지는','물리 조각은','control-pieces-easy')
 elif key=='returnal':
  file='nohud-8-OJj2JoPfQ-candidate-45-105-copy-v2.mp4';label='게임 장면 · Returnal · PC 녹화'
  game('리터널의 적은','개발진은 이런 표현에',file,15,label)
  game('촉수의 뿌리와','둘이 똑같이',file,27,label)
  diagram('앞사람의 바로 전','모형의 점들이','returnal-chain-easy')
  game('이 움직임은','아티스트와 애니메이터는',file,43,label+' · 전투 맥락')
 elif key=='doom':
  file='genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4';label='게임 장면 · DOOM 2016'
  game('둠에서 체력이','둠에서 체력이',file,242,label)
  oldsel=read(p/'production/accepted-voice-selection-v10.json');oldn=read(oldsel['narration']['path']);oldp1=[u for u in oldn['units']if u['paragraph']=='p001'];native(oldp1[1]['ko'],oldp1[-1]['ko'],'b','detail',54,'doom')
  game('적이 잠깐 빛나며','적이 잠깐 빛나며',file,306.8,label+' · 비틀거리는 적')
  game('여기서는 마무리 뒤','여기서는 마무리 뒤',file,247.3,label+' · 마무리와 회복')
  native('공격으로 적을','공격으로 적을','b','detail',120,'doom') if any(u['ko'].startswith('공격으로 적을')for u in units)else None
  game('위험을 감수하고','위험을 감수하고',file,315.3,label+' · 다른 교전 예시')
 elif key=='botw':
  fire='botw-part2-rain-candidate-3060-3130-v3.mp4';ice='botw-part2-fire-candidate-625-750-v3.mp4';label='게임 장면 · 야생의 숨결 · Cemu 녹화'
  game('야생의 숨결에서는','야생의 숨결에서는',fire,42,label)
  game('이 풀밭에 불이','이 풀밭에 불이',fire,49,label+' · 풀밭 점화')
  diagram('이 상태 변화를','화학 엔진은 불이 붙거나','botw-motion-state-easy')
  game('실제 장면에서는 불 가까이에','실제 장면에서는 불 가까이에',ice,34,label+' · 불 가까이의 얼음')
  native('비교 모형에서는 나무에','비교 모형에서는 나무에','b','detail',300,'botw','해설용 모형 · 물과 불')
  diagram('나무 상자 둘이','충돌로 밀리는','botw-motion-state-easy')
  game('정리하면 물리 엔진은','정리하면 물리 엔진은',ice,48,label+' · 상태 변화 결과')
 elif key=='mariokart8':
  file='royaltyfree-npz4T7sznog-full-f299-v3.mp4';label='게임 장면 · Mario Kart 8'
  game('마리오 카트 에이트에서는','마리오 카트 에이트에서는',file,214,label)
  game('우선 바퀴가','우선 바퀴가',file,269.5,label+' · 다른 랩의 반중력 진입')
  game('길이 벽으로','길이 벽으로',file,233,label+' · 반중력 구간 예시')
  native('반중력 구간에서 다른 카트와','이 효과가 있으니','b','detail',108,'mariokart8')
  game('여기서는 빛나는 기둥에','여기서는 빛나는 기둥에',file,225.9,label+' · 기둥 접촉 예시')
  game('그래서 반중력 구간에서는','새로운 주행 공간에',file,289,label+' · 경로 선택')
 # Coalesce identical starts and remove no-duration residues from replacements.
 unique={round(b['start']*24000):b for b in beats};beats=sorted(unique.values(),key=lambda b:b['start']);beats[0]['start']=0
 for i,b in enumerate(beats):b['end']=beats[i+1]['start']if i+1<len(beats)else duration;assert b['end']>b['start']
 if key=='inside':nativeproof=ROOT/'shared/output/original-tech-twelve-20261115'/p.name/'native-completion-v6/accepted-full.json';nativevisual=nativeproof.parent/'full-visual-review-v6.json'
 else:nativeproof=ROOT/'shared/output/original-tech-twelve-20261115/remaining-seven/native-reviewed-pose-v35/accepted-full.json';nativevisual=nativeproof.parent/'full-visual-review-v35.json'
 capture=read(nativeproof)
 for b in beats:
  if b['kind']=='native':
   clip=next(c for c in capture['clips']if c['mode']==b['mode']and c['camera']==b['view']and c.get('topic')==b.get('topic'));assert b['startFrame']+math.ceil((b['end']-b['start'])*60)<=capture['framesPerCamera'],b
  if b['kind']=='game':
   import av
   with av.open(b['source']['path'])as c:
    st=c.streams.video[0];assert st.width>=1920 and st.height>=1080;assert b['sourceStartSeconds']+b['end']-b['start']<float(st.duration*st.time_base)
 for file in {b['source']['path']for b in beats if b['kind']=='game'}:
  bs=[b for b in beats if b['kind']=='game'and b['source']['path']==file];ranges=[]
  for b in bs:
   lo=b['sourceStartSeconds'];hi=lo+b['end']-b['start'];assert all(hi<=x or lo>=y for x,y in ranges),('Unlabelled replay',b);ranges.append((lo,hi))
 plan=p/'planning/film-beats-clarity-v95.json';save(plan,dict(slug=p.name,captionTiming=sel['captionTiming'],sourceNarration=sel['narration'],sourceActionReview=pin(p/'planning/source-action-clarity-v84.json'),sourceOrderPreserved=True,sourceGameAudioPairRequired=key=='inside',semanticClauses=sel['clauses'],beats=beats,duration=duration,sourceSpeed=1,arbitraryFreezeLoopOrSlowMotion=False,humanApproval=False))
 save(p/'production/film-inputs-v95.json',dict(voiceSelection=pin(selection),captionTiming=sel['captionTiming'],filmPlan=pin(plan),mixProofPath=str(M/p.name/'clarity-revision-v83/audio-mix-v95/audio-build.json'),nativeFullProofPath=str(nativeproof),nativeVisualReviewPath=str(nativevisual),nativeFullFrames=capture['framesPerCamera']))
 print(json.dumps(dict(project=p.name,duration=duration,beats=len(beats),gameExamples=sum(b['kind']=='game'for b in beats),nativeExamples=sum(b['kind']=='native'for b in beats),plan=pin(plan))))
if __name__=='__main__':main()
