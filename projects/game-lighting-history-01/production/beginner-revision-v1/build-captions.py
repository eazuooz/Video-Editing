"""Retain approved utterance-relative cues; map changed speech to the new edit."""
import pathlib,json,hashlib,datetime,importlib.util,math,collections
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1';B=P/'production/local/final-edit-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 assert not (O/'captions.json').exists(),'Reuse completed current captions; only repair actual failures.'
 plan=rd(O/'edit-plan-proposal.json');base=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json');old=rd(B/'captions.json')
 spec=importlib.util.spec_from_file_location('old_caption',P/'production/build-final-captions-v1.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
 changed=rd(O/'voice-alignment-proposal.json');native=rd(O/'native-guides-alignment-reviewed.json')
 assert rd(H/'voice-direct-review.json')['alignmentSha256']==sha(O/'voice-alignment-proposal.json')
 assert rd(H/'native-voice-direct-review.json')['alignmentSha256']==sha(O/'native-guides-alignment-reviewed.json')
 replacement={r['key']:r for r in changed['rows']+native['rows']};sources={'ko':[],'en':[]}
 oldgroups=collections.defaultdict(list);newgroups=collections.defaultdict(list)
 for v in base['voice']:oldgroups[v['key']].append(v)
 for v in plan['voice']:newgroups[v['key']].append(v)
 for lang in sources:
  for c in old['cues'][lang]:
   k=c['key']
   if k in replacement:continue
   vs=oldgroups[k];first=min(v['sourceStartSample'] for v in vs)
   def to_source(t):
    # Cue tails can extend fractions into the retained natural pause.
    v=min(vs,key=lambda q:max(q['startFrame']/60-t,0,t-(q['startFrame']/60+q['samples']/24000)))
    return t-v['startFrame']/60+(v['sourceStartSample']-first)/24000
   sources[lang].append(dict(key=k,text=c['text'],lines=c['lines'],seconds=[to_source(c['startSeconds']),to_source(c['endSeconds'])],reusedLayout=True,baselineCueIndex=c['index']))
  for k,r in replacement.items():
   for c in r[lang+'Cues']:
    ls=c['lines']
    if k=='xsh' and lang=='ko' and c['seconds'][0]==9.58:ls=['표면 방향 때문에 남는 명암과,','다른 면이 빛을 막아서 생기는 그림자를 구별해서 보세요.']
    sources[lang].append(dict(key=k,text=c['text'],lines=ls,seconds=c['seconds'],reusedLayout=False))
 cues={'ko':[],'en':[]}
 for lang,rows in sources.items():
  for c in rows:
   k=c['key'];a,z=c['seconds'];vs=sorted(newgroups[k],key=lambda v:v['utteranceStartSample']);segments=[]
   for v in vs:
    lo,hi=v['utteranceStartSample']/24000,(v['utteranceStartSample']+v['samples'])/24000
    x,y=max(a,lo),min(z,hi)
    if y>x:segments.append((x+v['startFrame']/60-lo,y+v['startFrame']/60-lo))
   assert segments,(k,c)
   # A cue crossing a continuously retained split stays one cue. Sentence
   # cues at intentional xsh pauses are already split on observed words.
   assert all(abs(x[1]-y[0])<.002 for x,y in zip(segments,segments[1:])),('noncontinuous cue',k,c)
   cues[lang].append(dict(c,startSeconds=segments[0][0],endSeconds=segments[-1][1]))
  cues[lang].sort(key=lambda c:c['startSeconds'])
  assert all(a['endSeconds']<=b['startSeconds']+.001 for a,b in zip(cues[lang],cues[lang][1:])),lang
  for i,c in enumerate(cues[lang],1):
   c['index']=i;assert 0<=c['startSeconds']<c['endSeconds']<plan['seconds']-10
   assert len(c['lines'])<=2 and all(cap.font.getlength(t)<=1570 for t in c['lines']),(lang,c)
  assert {c['key'] for c in cues[lang]}==set(newgroups)
  (O/f'captions.{lang}.srt').write_text('\n\n'.join(f"{c['index']}\n{cap.stamp(c['startSeconds'])} --> {cap.stamp(c['endSeconds'])}\n"+'\n'.join(c['lines']) for c in cues[lang])+'\n',encoding='utf8')
 header=(B/'captions.ko.ass').read_text(encoding='utf8').split('Dialogue:',1)[0];events=[]
 def event(layer,c,text):events.append(f"Dialogue: {layer},{cap.stamp(c['startSeconds'],True)},{cap.stamp(c['endSeconds'],True)},Default,,0,0,0,,{text}")
 def rect(layer,c,x,y,w,h,color):event(layer,c,f'{{\\an7\\pos({x:.1f},{y:.1f})\\bord0\\shad0\\1c&H{color}&\\p1}}m 0 0 l {w:.1f} 0 {w:.1f} {h:.1f} 0 {h:.1f}')
 for c in cues['ko']:
  w=math.ceil(max(cap.font.getlength(s) for s in c['lines']))+44;h=62*len(c['lines'])+22;x=960-w/2;y=970-h/2
  rect(0,c,x+14,y+14,w,h,'323C07');rect(1,c,x-1.5,y-1.5,w+3,h+3,'181B16');rect(2,c,x,y,w,h,'FFFFFF')
  for i,line in enumerate(c['lines']):event(3,c,f'{{\\an5\\pos(960,{970+(i-(len(c["lines"])-1)/2)*62:.1f})\\fs48\\bord0\\shad0\\1c&H090B08&}}'+line.replace('{','').replace('}',''))
 (O/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8')
 wr(O/'captions.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),planSha256=sha(O/'edit-plan-proposal.json'),cues=cues,utteranceKeys=150,allCueTextDirectReview=True,reviewBasis='Retained92 approved whole cue maps;52 changed KOEN maps directly reviewed;6 new maps directly reviewed, xsh natural-sentence pause split and balanced final two-line layout.',allEncodedPixelsReviewed=False))
 print(json.dumps({l:len(c) for l,c in cues.items()}))
if __name__=='__main__':main()
