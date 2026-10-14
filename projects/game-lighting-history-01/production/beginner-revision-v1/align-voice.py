"""Propose semantic word edges from actual new speech; never self-approve them."""
import pathlib,json,re,difflib,hashlib,datetime,importlib.util,sys
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
O=P/'production/local/beginner-revision-v1';HERE=pathlib.Path(__file__).parent
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
norm=lambda s:re.sub(r'[^가-힣a-z0-9]','',s.lower())
GROUPS={
 '02-p5':[[0],[1,2],[3,4],[5]],'02-p7':[[0],[1,2],[3]],
 '04-p2':[[0,1],[2],[3]],'04-p7':[[0],[1],[2,3]],'04f-p5':[[0],[1,2]],
 '07-p5':[[0],[1],[2,3]],'07-p6':[[0],[1],[2,3]],'08-p2':[[0],[1,2],[3]],
 '09-p1':[[0],[1,2],[3]],'09a-p5':[[0,1],[2]],'09b-p5':[[0],[1],[2,3]],
 'g01':[[0],[1,2],[3],[4],[5]],'g12':[[0,1],[2],[3]],'g19':[[0],[1],[2,3],[4],[5]],
 'g25':[[0],[1,2],[3]],'g31':[[0],[1],[2,3]],'g38':[[0,1],[2],[3],[4]],
 'g42':[[0],[1],[2,3],[4],[5],[6],[7]],
}
def main():
 native='--native' in sys.argv
 source_dir='native-guides-asr' if native else 'voice-asr'
 state=rd(O/source_dir/'execution.json')
 assert state['status']=='complete-awaiting-direct-review' and len(state['completed'])==(6 if native else 52)
 spec=importlib.util.spec_from_file_location('retained_caption_layout',P/'production/build-final-captions-v1.py')
 cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
 repairs=rd(HERE/'word-edge-repairs.json') if (HERE/'word-edge-repairs.json').exists() else {}
 out=[];issues=[]
 rows=[dict(key=r['id'],ko=r['ko'],en=r['en']) for r in rd(HERE/'native-additions.json')['guideRows']] if native else rd(HERE/'changes.json')['rows']
 for r in rows:
  key=r['key'];f=R/r['asrResultPath'] if r.get('asrResultPath') else O/source_dir/f'{key}.json';a=rd(f);assert a['audioSha256']==sha(R/a['audioPath'])
  words=[]
  for i,w in enumerate(a['chunks']):
   lo,hi=w['timestamp']
   if lo is None or hi is None or hi<lo:issues.append(dict(key=key,kind='invalid-timestamp',word=w));continue
   if words and lo<words[-1]['start']:issues.append(dict(key=key,kind='reverse-word',word=w))
   words.append(dict(text=w['text'],start=lo,end=hi,index=i))
  actual='';owners=[]
  for w in words:
   t=norm(w['text']);actual+=t;owners.extend([w]*len(t))
  target=norm(r['ko']);mapping={}
  match=difflib.SequenceMatcher(None,target,actual,autojunk=False)
  for l,h,n in match.get_matching_blocks():mapping.update({l+i:h+i for i in range(n)})
  tokens=r['ko'].split();counts=[0]
  for t in tokens:counts.append(counts[-1]+len(norm(t)))
  edges={0:(words[0]['start'],words[0]['start']),len(tokens):(min(a['seconds'],words[-1]['end']),min(a['seconds'],words[-1]['end']))}
  for i in range(1,len(tokens)):
   l,h=counts[i]-1,counts[i]
   if l in mapping and h in mapping:
    lw,rw=owners[mapping[l]],owners[mapping[h]]
    if lw['index']!=rw['index'] and lw['end']<=rw['start']:edges[i]=(lw['end'],rw['start'])
  for i,v in repairs.get(key,{}).items():edges[int(i)]=tuple(v['seconds'])
  sentences=[];start=0
  for text in re.split(r'(?<=[.!?])\s+',r['ko']):
   end=start+len(text.split());span=None
   if start in edges and end in edges:span=[edges[start][1],edges[end][0]]
   else:issues.append(dict(key=key,kind='sentence-edge',text=text,startToken=start,endToken=end))
   sentences.append(dict(text=text,startToken=start,endToken=end,seconds=span));start=end
  best={0:(0,[])}
  for end in sorted(edges):
   if not end:continue
   for start in sorted(best):
    if start>=end:continue
    duration=edges[end][0]-edges[start][1];text=' '.join(tokens[start:end]);lines=cap.wrap(text)
    if not .7<=duration<=9.5 or len(lines)>2:continue
    score=best[start][0]+(duration-4.8)**2+(0 if text.endswith(('.','?','!')) else 20 if text.endswith(',') else 100)
    if end not in best or score<best[end][0]:best[end]=(score,best[start][1]+[dict(text=text,lines=lines,seconds=[edges[start][1],edges[end][0]],startToken=start,endToken=end)])
  if len(tokens) not in best:issues.append(dict(key=key,kind='KO-cue-partition'))
  en=re.split(r'(?<=[.!?])\s+(?=[A-Z])',r['en']);groups=GROUPS.get(key,[[i] for i in range(len(sentences))]);assert len(groups)==len(en),key
  ens=[]
  for en_index,(text,g) in enumerate(zip(en,groups)):
   span=[sentences[g[0]]['seconds'][0],sentences[g[-1]]['seconds'][1]] if all(sentences[i]['seconds'] for i in g) else None
   lines=cap.wrap(text)
   split=None
   if key=='04-p7' and en_index==2 and span:
    split=[('Quake II’s tools also computed reflected contributions between surface patches and added them to lightmap samples,', [span[0],sentences[2]['seconds'][1]]),('illuminating places without direct exposure.',sentences[3]['seconds'])]
   elif key=='g42' and en_index==2 and span:
    split=[('If two of four positions are covered, the edge can contribute roughly half the coverage;',sentences[2]['seconds']),('this is an illustrative example, not a claim about the game’s sample setting.',sentences[3]['seconds'])]
   elif key=='g42' and en_index==6 and span:
    split=[('Forward versus Deferred is therefore a choice involving image quality, features and memory costs,',[span[0],33.22]),('not simply which name is newer.',[33.22,span[1]])]
   if split:
    assert norm(' '.join(t for t,_ in split))==norm(text)
    for t,seconds in split:
     ls=cap.wrap(t);assert len(ls)<=2,(key,t)
     ens.append(dict(text=t,lines=ls,seconds=seconds,koSentenceIndices=g,semanticClauseSplitDirectlyReviewed=True))
   else:
    if len(lines)>2:issues.append(dict(key=key,kind='EN-clause-split',text=text,koSentenceIndices=g))
    ens.append(dict(text=text,lines=lines,seconds=span,koSentenceIndices=g))
  out.append(dict(key=key,audioPath=a['audioPath'],audioSha256=a['audioSha256'],samples=a['samples'],seconds=a['seconds'],asrPath=f.relative_to(R).as_posix(),asrSha256=sha(f),actualText=a['text'],expectedText=r['ko'],matchedCharacterFraction=len(mapping)/max(1,len(target)),wordEdges=edges,sentences=sentences,koCues=best.get(len(tokens),(None,[]))[1],enCues=ens,directTextCompared=False,sentenceBoundariesDirectlyReviewed=False))
 wr(O/('native-guides-alignment-proposal.json' if native else 'voice-alignment-proposal.json'),dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=out,issues=issues,currentVoiceReviewed=False,sentenceBoundariesDirectlyReviewed=False,method='Actual word edges; manually authored KO/EN sentence relationships; text/timestamps require direct review.'))
 print(json.dumps(dict(rows=len(out),issues=issues),ensure_ascii=False))
if __name__=='__main__':main()
