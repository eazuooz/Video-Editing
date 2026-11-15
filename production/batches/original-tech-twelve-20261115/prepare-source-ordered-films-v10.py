"""Untimed cuts from primary-source order; actual speech edges are bound later."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DROOT=ROOT/'shared/output/original-tech-twelve-20261115'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,d):assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def diagram(cl,key):return dict(firstClauseIndex=cl,kind='diagram',key=key,localModelStartSeconds=0)
def native(cl,mode,view,start=0,topic=None,label='해설용 모형 · 직접 만든 비교 장면'):
 d=dict(firstClauseIndex=cl,kind='native',mode=mode,view=view,startFrame=start,label=label,sourceSpeed=1)
 if topic:d['topic']=topic
 return d
def main():
 slugs=['shorts-horizon-gpu-placement','shorts-inside-temporal-antialiasing','shorts-spiderman-swing-anchor','shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules'];results=[]
 for slug in slugs:
  P=ROOT/'projects'/slug;nv='v7'if'inside'in slug else'v6';cp=P/('planning/caption-clauses-repair-'+nv+'.json');old=read(P/'planning/film-beats-v2.json');src=next(b['source']for p in old['paragraphs']for b in p['beats']if b['kind']=='game')
  def game(cl,start,label):return dict(firstClauseIndex=cl,kind='game',source=src,sourceStartSeconds=start,label=label,sourceSpeed=1,sourceAudio='paired-original'if'inside'in slug else'none')
  def para(pid,*beats):return dict(id=pid,beats=list(beats))
  if 'horizon'in slug:
   ps=[para('p001',game(0,5,'게임 장면 · PS5 녹화')),para('p002',native(0,'all-candidates','map'),native(3,'density-map','map')),para('p003',native(0,'density-map','map'),native(2,'road-water-exclusion','map')),para('p004',native(0,'all-candidates','map'),native(2,'road-water-exclusion','map',240)),para('p005',native(0,'terrain-aligned','forest',240),native(3,'terrain-aligned','map',240)),para('p006',native(0,'two-placement-layers','forest',240),native(2,'two-placement-layers','map',240)),para('p007',game(0,40,'게임 장면 · PS5 녹화'))];nb=DROOT/slug/'native-completion-v6';mixversion='v10'
  elif 'inside'in slug:
   def n(cl,mode,start=0):return native(cl,mode,'detail',start,label='해설 모형 · 내부 540px 테스트')
   ps=[para('p001',game(0,145,'게임 장면 · Xbox 녹화'),n(3,'no-aa'),diagram(4,'temporal-history-blur')),para('p002',n(0,'jitter-only'),n(3,'temporal-clipping')),para('p003',diagram(0,'temporal-reproject')),para('p004',diagram(0,'temporal-clip')),para('p005',n(0,'temporal-clipping',180),diagram(2,'temporal-history-blur')),para('p006',diagram(0,'temporal-reproject'),diagram(1,'temporal-clip'),n(2,'temporal-clipping',360))];nb=DROOT/slug/'native-completion-v6';mixversion='v11'
  elif 'spiderman'in slug:
   def n(cl,mode,start=0):return native(cl,mode,'overview',start,'spiderman')
   ps=[para('p001',game(0,10,'게임 장면 · PC Remastered'),n(3,'a')),para('p002',diagram(0,'spider-rays')),para('p003',diagram(0,'spider-volume')),para('p004',diagram(0,'spider-criteria')),para('p005',diagram(0,'spider-criteria')),para('p006',n(0,'a',120),n(1,'b',120),game(2,28,'게임 장면 · PC Remastered'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  elif 'control'in slug:
   def n(cl,mode,start=0):return native(cl,mode,'detail',start,'control')
   ps=[para('p001',game(0,10,'게임 장면 · Xbox Series S'),n(1,'b',150)),para('p002',diagram(0,'control-hierarchy')),para('p003',diagram(0,'control-hierarchy')),para('p004',diagram(0,'control-bonds'),n(2,'a')),para('p005',n(0,'b',150),diagram(3,'control-hierarchy')),para('p006',diagram(0,'control-surface-hole'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  elif 'returnal'in slug:
   ps=[para('p001',game(0,10,'게임 장면 · PC 녹화')),para('p002',diagram(0,'returnal-bodies')),para('p003',diagram(0,'returnal-delay')),para('p004',diagram(0,'returnal-surface')),para('p005',diagram(0,'returnal-surface')),para('p006',native(0,'b','detail',180,'returnal','연결된 점의 표현 예 · 해설용 모형'),game(2,45,'게임 장면 · PC 녹화'),diagram(3,'returnal-delay'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  elif 'ratchet'in slug:
   def n(cl,mode):return native(cl,mode,'overview',0,'ratchet','가상의 처리시간 · 해설용 모형')
   ps=[para('p001',game(0,29,'게임 장면 · PS5 녹화')),para('p002',diagram(0,'ratchet-read-decompress')),para('p003',diagram(0,'ratchet-read-decompress'),n(2,'a')),para('p004',n(0,'a'),n(2,'b')),para('p005',game(0,44,'게임 장면 · PS5 녹화'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  elif 'doom'in slug:
   def n(cl,mode,start=0):return native(cl,mode,'detail',start,'doom')
   ps=[para('p001',game(0,242,'게임 장면 · DOOM 2016'),n(1,'b',60)),para('p002',n(0,'a'),n(3,'b',120)),para('p003',game(0,247.3,'게임 장면 · DOOM 2016'),n(2,'b',120)),para('p004',diagram(0,'doom-rewards')),para('p005',diagram(0,'doom-rewards')),para('p006',game(0,308.4,'게임 장면 · DOOM 2016'),diagram(3,'doom-rewards'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  else:
   caps=read(cp);first=caps['paragraphs'][0];assert first['clauses'][0][0]=='야생의 숨결에서는 풀에 불이 붙고 비가 불을 끕니다.';first['clauses']=[['야생의 숨결에서는 풀에 불이 붙고','In Breath of the Wild, grass catches fire,'],['비가 불을 끕니다.','and rain puts it out.']]+first['clauses'][1:];caps['sourceRefinement']=dict(previous=pin(cp),reason='Cut at the actual whole ASR word 비가 so a fire-only source clip is never used as evidence of rain. No spoken text changes.');cp=P/'planning/caption-clauses-source-ordered-v10.json';save(cp,caps)
   def n(cl,mode,start=0):return native(cl,mode,'detail',start,'botw')
   ps=[para('p001',game(0,49,'게임 장면 · Cemu 녹화'),n(1,'b',300),diagram(2,'botw-rules')),para('p002',diagram(0,'botw-rules')),para('p003',n(0,'a',60)),para('p004',diagram(0,'botw-rules')),para('p005',diagram(0,'botw-rules')),para('p006',n(0,'b',300),diagram(2,'botw-rules')),para('p007',diagram(0,'botw-rules'))];nb=DROOT/'remaining-seven/native-completion-v6';mixversion='v10'
  clauses=read(cp)
  for p in ps:
   valid=next(x for x in clauses['paragraphs']if x['id']==p['id']);assert p['beats'][0]['firstClauseIndex']==0 and all(0<=b['firstClauseIndex']<len(valid['clauses'])for b in p['beats'])
  plan=P/'planning/film-beats-v10.json';save(plan,dict(schemaVersion=1,slug=slug,semanticClauses=pin(cp),paragraphs=ps,sourceOrderReviewed=True,sourceGameReplays=False,sourceGameAudioPairRequired=('inside'in slug),nativeModelsNeverOriginalGameTelemetry=True,actualNativeFullRequired=True,actualSpeechTimesAssigned=False))
  results.append(dict(slug=slug,plan=pin(plan),nativeFullProofPath=str(nb/'accepted-full.json'),nativeVisualReviewPath=str(nb/'full-visual-review-v6.json'),nativeFullFrames=720,mixProofPath=str(DROOT/slug/('audio-mix-'+mixversion)/'audio-build.json')))
 save(HERE/'source-ordered-film-contracts-v10.json',dict(projects=results,sourceOrderReviewed=True,fullSourcesAndVoicesStillRequired=True));print(json.dumps(dict(projects=len(results),actualFilmsCompleted=0)))
if __name__=='__main__':main()
