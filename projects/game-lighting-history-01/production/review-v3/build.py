"""Build one measured 57:43 edit and captions, retaining v2 PCM and source cuts."""
import copy,json,pathlib,hashlib,math,importlib.util,datetime
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/review-v3';B=P/'production/local/continuity-v2'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=rd(O/'alignment-proposal.json');assert not a['issues'];review=rd(O/'source-review.json');assert review['fullTextAndEdgesReviewed'] and review['alignmentSha256']==sha(O/'alignment-proposal.json')
 base=rd(B/'plan.json');design=rd(H/'design.json');rows=a['rows'];assert len(rows)==8
 spec=importlib.util.spec_from_file_location('layout',H/'align.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
 displayPairs=[('영 점 팔육육','0.866'),('영 점 칠구삼','0.793'),('영 점 팔','0.8'),('영 점 이','0.2'),('영 점 일','0.1'),('영 점 오','0.5'),('삼십 도','30도'),('육십 도','60도'),('구십 도','90도'),('영 도','0도'),('일, 영, 영','1, 0, 0'),('일인 두','1인 두'),('일로 맞춘','1로 맞춘'),('영으로 제한','0으로 제한'),('일이 되는','1이 되는'),('영에서 일','0에서 1'),('도면 일','도면 1'),('도면 영입니다','도면 0입니다'),('영이 됩니다','0이 됩니다'),('하프라이프 투','하프라이프2'),('이천사 년','2004년')]
 for row in rows:
  for cue in row['koCues']:
   for old,new in displayPairs:cue['text']=cue['text'].replace(old,new)
   cue['lines']=layout.wrap(cue['text'])
   assert len(cue['lines'])<=2

 # Existing whole-body actual footage is retained. A useful settling/review beat
 # may complete a calculation, but never create arbitrary idle quota filler.
 measured=sum(math.ceil(r['samples']/400) for r in rows);target=round(base['actualFrames']/.57)-base['actualFrames']-(base['explanationFrames']-2785)
 assert measured<=target,(measured,target,'Do not time-stretch or truncate speech to fit a quota; re-plan the relevant footage.')
 gap=target-measured;assert gap<=240,(gap,'Review excess silence instead of padding')
 durations=[math.ceil(r['samples']/400) for r in rows]
 # A short readable result hold is attached to each scene, not a repeated clip.
 for i in range(gap):durations[i%8]+=1
 nodes=[];replaced={'08-p2','08-p3','08-p4'};cursor=0;newvs=[];newblocks=[]
 for old in base['nodes']:
  key=old.get('anchor')
  if key=='08-p2' and old['role']=='explanation':
   for r,length in zip(rows,durations):
    newvs.append(dict(key=r['key'],kind='review-v3-expansion',path=r['audioPath'],audioSha256=r['audioSha256'],sourceStartSample=r.get('sourceStartSample',0),utteranceStartSample=0,samples=r['samples'],frames=math.ceil(r['samples']/400),startFrame=cursor,targetStartSample=cursor*400))
    path=(O/'scenes'/f"{r['key']}.mp4").relative_to(R).as_posix();nodes.append(dict(id='e-'+r['key'],anchor=r['key'],role='explanation',path=path,framedPath=path,sourceStartFrame=0,framedStartFrame=0,frames=length,startFrame=cursor,endFrame=cursor+length))
    newblocks.append(dict(key=r['key'],frames=length,sentences=r['sentences'],koCues=r['koCues'],audioSha256=r['audioSha256'],resultHoldFrames=length-math.ceil(r['samples']/400),renderer='Three.js',learningSteps=next(q['learningSteps'] for q in design['rows'] if q['key']==r['key'])))
    cursor+=length
  if key in replaced and old['role']=='explanation':continue
  n=copy.deepcopy(old);n.update(baselineStartFrame=old['startFrame'],baselineEndFrame=old['endFrame'],framedPath=(B/'pair-exact-v2/visual.mp4').relative_to(R).as_posix(),framedStartFrame=old['startFrame'],startFrame=cursor,endFrame=cursor+old['frames'])
  if key=='03-p7' and old['role']=='explanation':n.update(framedPath=(O/'motion-canvas/doom-project.mp4').relative_to(R).as_posix(),framedStartFrame=0,visualReviewCorrection='Rear-wall overlay before actor; foreground wall retains occlusion')
  nodes.append(n);cursor+=n['frames']
 delta=cursor-base['frames'];mapf=lambda f:f if f<64119 else f+target-1834 if f<66973 else f+delta
 voices=[]
 for old in base['voice']:
  if old['key'] in replaced:continue
  v=copy.deepcopy(old);v['startFrame']=mapf(old['startFrame']);v['targetStartSample']=v['startFrame']*400;voices.append(v)
 voices=sorted(voices+newvs,key=lambda v:v['startFrame'])
 assert all(v['targetStartSample']+v['samples']<=w['targetStartSample'] for v,w in zip(voices,voices[1:]))
 plan=copy.deepcopy(base);plan.update(revision='review-v3',frames=cursor,seconds=cursor/60,nodes=nodes,voice=voices,actualFrames=base['actualFrames'],explanationFrames=sum(n['frames'] for n in nodes if n['role']=='explanation'),bodyFrames=cursor-720,bodyRatioApproved=True,ratioTarget={'actual':.57,'explanation':.43},finalTimingApproved=True,finalMixAsrApproved=False,allFinalPixelsApproved=False,finalPairComplete=False,baselinePlan=(B/'plan.json').relative_to(R).as_posix(),baselinePlanSha256=sha(B/'plan.json'),retainedVoiceKeys=[v['key'] for v in voices if not v['key'].startswith('08-r')],replacedVoiceKeys=sorted(replaced),newExplanationFrames=target,removedRedundantParagraph='08-p4: all claims expanded in08-r5..r7',timingReview='Unchanged retained frames and PCM; eight measured semantic replacements; no time stretch.')
 plan['ratioRoundingErrorFrames']=abs(plan['actualFrames']-.57*plan['bodyFrames']);assert plan['ratioRoundingErrorFrames']<=1
 for arr in ['chapters','audioChapterBoundaries']:
  plan[arr]=copy.deepcopy(base[arr])
  for ch in plan[arr]:
   ch['startFrame']=mapf(ch['startFrame'])
   if 'startSeconds' in ch:ch['startSeconds']=ch['startFrame']/60
   if 'visualStartFrame' in ch:ch['visualStartFrame']=mapf(ch['visualStartFrame'])
 headers=[]
 def header(key,title,sub,offset=0,stop=None):
  n=next(n for n in base['nodes'] if n.get('anchor')==key and n['role']=='explanation');lo=n['startFrame']+offset;hi=n['endFrame'] if stop is None else n['startFrame']+stop
  row=dict(key=key,startFrame=mapf(lo),endFrame=mapf(hi),baselineStartFrame=lo,baselineEndFrame=hi)
  for k,text in [('titleFile',title),('subtitleFile',sub)]:
   path=H/f'{key}-{offset}-{k}.txt';path.write_text(text,encoding='utf8');row[k]=path.relative_to(R).as_posix()
  headers.append(row)
 header('09-p1','섀도 맵 · Shadow Map','광원에서 본 첫 표면의 깊이를 기록하고 비교합니다')
 header('09-p7','퍼센티지 클로저 필터링 · PCF','Percentage-Closer Filtering · 깊이 비교 결과를 평균합니다')
 header('09-p9','퍼센티지 클로저 소프트 섀도 · PCSS','Percentage-Closer Soft Shadows · 가림 관계로 필터 폭 조절',stop=496)
 header('09-p9','분산 섀도 맵 · Variance Shadow Maps','VSM · 깊이의 평균과 제곱 평균을 저장합니다',offset=496)
 header('09-p10','분산 섀도 맵과 가상 섀도 맵','Variance Shadow Maps ≠ Virtual Shadow Maps · 같은 VSM, 다른 기법')
 header('09a-p1','캐스케이드 섀도 맵 · CSM','Cascaded Shadow Maps · 카메라 거리 구간마다 섀도 맵을 배정합니다')
 plan['termHeaders']=headers;plan['changedBaselineRanges']=[[18879,19838],[64119,67924]]+sorted({(h['baselineStartFrame'],h['baselineEndFrame']) for h in headers})
 plan['audioSplices']=[dict(kind='retained',oldStartFrame=0,oldEndFrame=64119,newStartFrame=0),dict(kind='new',newStartFrame=64119,frames=target),dict(kind='retained',oldStartFrame=65953,oldEndFrame=66973,newStartFrame=64119+target),dict(kind='retained',oldStartFrame=67924,oldEndFrame=base['frames'],newStartFrame=64119+target+1020)]
 wr(O/'plan.json',plan);wr(H/'measured-scene-plan.json',dict(scenes=newblocks,currentVoiceReviewed=True,sentenceBoundariesDirectlyReviewed=True,sourceReviewSha256=sha(O/'source-review.json'),planSha256=sha(O/'plan.json')))
 spec=importlib.util.spec_from_file_location('layout',H/'align.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
 cues={l:[] for l in ['ko','en']};oldv={v['key']:v for v in base['voice']};newv={v['key']:v for v in voices}
 for lang in cues:
  for c in rd(B/'captions.json')['cues'][lang]:
   if c['key'] in replaced:continue
   c=copy.deepcopy(c);shift=(newv[c['key']]['startFrame']-oldv[c['key']]['startFrame'])/60;c['startSeconds']+=shift;c['endSeconds']+=shift;c['reusedLayout']=True;cues[lang].append(c)
  for r in rows:
   for c in r[lang+'Cues']:cues[lang].append(dict(c,key=r['key'],startSeconds=newv[r['key']]['startFrame']/60+c['seconds'][0],endSeconds=newv[r['key']]['startFrame']/60+c['seconds'][1],reusedLayout=False))
  cues[lang].sort(key=lambda c:c['startSeconds'])
  assert all(c['endSeconds']<=d['startSeconds']+.001 for c,d in zip(cues[lang],cues[lang][1:]))
  for i,c in enumerate(cues[lang],1):c['index']=i;assert len(c['lines'])<=2 and all(layout.font.getlength(s)<=1570 for s in c['lines'])
 def stamp(t,ass=False):
  u=100 if ass else 1000;v=round(t*u);h,v=divmod(v,3600*u);m,v=divmod(v,60*u);s,v=divmod(v,u);return f'{h}:{m:02}:{s:02}.{v:02}' if ass else f'{h:02}:{m:02}:{s:02},{v:03}'
 for lang in cues:(O/f'captions.{lang}.srt').write_text('\n\n'.join(f"{c['index']}\n{stamp(c['startSeconds'])} --> {stamp(c['endSeconds'])}\n"+'\n'.join(c['lines']) for c in cues[lang])+'\n',encoding='utf8')
 head=(B/'captions.ko.ass').read_text(encoding='utf8').split('Dialogue:',1)[0];events=[]
 def event(layer,c,text):events.append(f"Dialogue: {layer},{stamp(c['startSeconds'],True)},{stamp(c['endSeconds'],True)},Default,,0,0,0,,{text}")
 def rect(layer,c,x,y,w,h,color):event(layer,c,f'{{\\an7\\pos({x:.1f},{y:.1f})\\bord0\\shad0\\1c&H{color}&\\p1}}m 0 0 l {w:.1f} 0 {w:.1f} {h:.1f} 0 {h:.1f}')
 for c in cues['ko']:
  w=math.ceil(max(layout.font.getlength(s) for s in c['lines']))+44;h=62*len(c['lines'])+22;x=960-w/2;y=970-h/2
  rect(0,c,x+14,y+14,w,h,'323C07');rect(1,c,x-1.5,y-1.5,w+3,h+3,'181B16');rect(2,c,x,y,w,h,'FFFFFF')
  for i,line in enumerate(c['lines']):event(3,c,f'{{\\an5\\pos(960,{970+(i-(len(c["lines"])-1)/2)*62:.1f})\\fs48\\bord0\\shad0\\1c&H090B08&}}'+line.replace('{','').replace('}',''))
 (O/'captions.ko.ass').write_text(head+'\n'.join(events)+'\n',encoding='utf8');wr(O/'captions.json',dict(planSha256=sha(O/'plan.json'),cues=cues,allCueTextDirectReview=True,allEncodedPixelsReviewed=False))
 print(json.dumps(dict(frames=cursor,explanationNewFrames=target,measuredNewFrames=measured,resultHoldTotalFrames=gap,ratio=plan['ratioRoundingErrorFrames'],delta=delta)))
if __name__=='__main__':main()
