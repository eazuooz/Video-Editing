"""Align the eight expanded paragraphs to measured word edges; leave review explicit."""
import pathlib,json,re,difflib,hashlib,datetime
import soundfile as sf
from PIL import ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/review-v3';A=R/'shared/output/narration/game-lighting-history-01/review-v3'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'[^가-힣a-z0-9]','',s.lower())
font=ImageFont.truetype(str(P/'production/local/final-edit-v1/fonts/YamYamCaptionMedium.ttf'),48)
def wrap(t):
 lines=[];line=''
 for w in t.split():
  new=(line+' '+w).strip()
  if line and font.getlength(new)>1570:lines.append(line);line=w
  else:line=new
 if line:lines.append(line)
 if len(lines)==2:
  words=t.split();choices=[]
  for i in range(1,len(words)):
   a,b=' '.join(words[:i]),' '.join(words[i:]);wa,wb=font.getlength(a),font.getlength(b)
   if max(wa,wb)<=1570:choices.append((abs(wa-wb)-(100 if a.endswith((',', ';', '.')) else 0),[a,b]))
  if choices:lines=min(choices,key=lambda x:x[0])[1]
 return lines
def main():
 d=rd(H/'design.json');rows=d['rows'];out=[];issues=[]
 repairs=rd(O/'word-edge-repairs.json') if (O/'word-edge-repairs.json').exists() else {}
 for r in rows:
  idx=r
  assert r['key']==idx['key'];key=r['key'];base=R/idx['overrideDirectory'] if idx.get('overrideDirectory') else A
  a=rd(base/'asr'/f"{idx['id']}.json");wav=base/'chunks'/f"{idx['id']}-scene.wav";info=sf.info(wav)
  assert sha(wav)==a['audio_sha256'] and info.samplerate==24000
  words=[dict(text=w['text'],start=w['timestamp'][0],end=w['timestamp'][1],index=i) for i,w in enumerate(a['words']) if None not in w['timestamp']]
  target=norm(r['ko']);actual='';owners=[]
  for w in words:t=norm(w['text']);actual+=t;owners.extend([w]*len(t))
  mapping={}
  for l,h,n in difflib.SequenceMatcher(None,target,actual,autojunk=False).get_matching_blocks():mapping.update({l+i:h+i for i in range(n)})
  tokens=r['ko'].split();counts=[0]
  for t in tokens:counts.append(counts[-1]+len(norm(t)))
  edges={0:[words[0]['start'],words[0]['start']],len(tokens):[min(info.duration,words[-1]['end'])]*2}
  for i in range(1,len(tokens)):
   l,h=counts[i]-1,counts[i]
   if l in mapping and h in mapping:
    lw,rw=owners[mapping[l]],owners[mapping[h]]
    if lw['index']!=rw['index'] and lw['end']<=rw['start']:edges[i]=[lw['end'],rw['start']]
  edges.update({int(i):v for i,v in repairs.get(key,{}).items()})
  sentences=[];start=0
  for s in re.split(r'(?<=[.!?])\s+',r['ko']):
   end=start+len(s.split());span=[edges[start][1],edges[end][0]] if start in edges and end in edges else None
   if span is None:issues.append(dict(key=key,kind='sentence-edge',startToken=start,endToken=end,text=s))
   sentences.append(dict(text=s,seconds=span,startToken=start,endToken=end));start=end
  best={0:(0,[])}
  for end in sorted(edges):
   if not end:continue
   for start in sorted(best):
    if start>=end:continue
    duration=edges[end][0]-edges[start][1];text=' '.join(tokens[start:end]);lines=wrap(text)
    if not .7<=duration<=9.5 or len(lines)>2:continue
    score=best[start][0]+(duration-4.8)**2+(0 if text.endswith(('.','?','!')) else 20 if text.endswith(',') else 100)
    if end not in best or score<best[end][0]:best[end]=(score,best[start][1]+[dict(text=text,lines=lines,seconds=[edges[start][1],edges[end][0]],startToken=start,endToken=end)])
  if len(tokens) not in best:issues.append(dict(key=key,kind='KO-partition'))
  ens=[];en=re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])',r['en']);groups=[[0],[1,2],[3]] if key=='10-p1' else [[i] for i in range(len(sentences))]
  assert len(en)==len(groups),(key,len(en),len(groups))
  for i,(t,g) in enumerate(zip(en,groups)):
   if any(sentences[j]['seconds'] is None for j in g):continue
   lo=sentences[g[0]]['seconds'][0];hi=sentences[g[-1]]['seconds'][1];splits=[(t,[lo,hi])]
   if key=='04-p1' and i==1:
    cut=tokens.index('어디가');part=t.split('; ',1)
    if cut not in edges:issues.append(dict(key=key,kind='clause-edge',token=cut));continue
    splits=[(part[0]+';',[lo,edges[cut][0]]),(part[1],[edges[cut][1],hi])]
   elif key=='04t-p6' and i==0:
    cut=tokens.index('투명하거나');part=t.split(', while ',1)
    if cut not in edges:issues.append(dict(key=key,kind='clause-edge',token=cut));continue
    splits=[(part[0]+',',[lo,edges[cut][0]]),('while '+part[1],[edges[cut][1],hi])]
   elif key=='10-p1' and i==1:
    part=t.split(' because ',1);splits=[(part[0],sentences[1]['seconds']),('because '+part[1],sentences[2]['seconds'])]
   for text,span in splits:
    ls=wrap(text)
    if len(ls)>2:issues.append(dict(key=key,kind='EN-width',text=text))
    ens.append(dict(text=text,lines=ls,seconds=span,koSentenceIndices=g))
  out.append(dict(key=key,id=idx['id'],audioPath=wav.relative_to(R).as_posix(),audioSha256=sha(wav),samples=info.frames,seconds=info.duration,expectedText=r['ko'],actualText=a['text'],matchedCharacterFraction=len(mapping)/len(target),wordEdges=edges,sentences=sentences,koCues=best.get(len(tokens),(0,[]))[1],enCues=ens,directReview=False))
 result=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=out,issues=issues,wholeSourceTextDirectlyReviewed=False,sentenceEdgesReviewed=False)
 (O/'alignment-proposal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(rows=len(out),issues=issues),ensure_ascii=False))
if __name__=='__main__':main()
