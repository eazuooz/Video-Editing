"""Reuse original cue layouts; align additions to their actual recognition edges."""
import pathlib,json,re,difflib,math,hashlib,datetime
from PIL import ImageFont
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
norm=lambda s:re.sub(r'[^가-힣a-z0-9]','',s.lower())
font=ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',48)
font.set_variation_by_axes([500])
def wrap(text):
 lines=[];line=''
 for word in text.split():
  new=(line+' '+word).strip()
  if line and font.getlength(new)>1570:lines.append(line);line=word
  else:line=new
 if line:lines.append(line)
 return lines
def stamp(t,ass=False):
 unit=100 if ass else 1000;v=round(t*unit);h,v=divmod(v,3600*unit);m,v=divmod(v,60*unit);s,v=divmod(v,unit)
 return f'{h}:{m:02}:{s:02}.{v:02}' if ass else f'{h:02}:{m:02}:{s:02},{v:03}'
def main():
 assert not (O/'captions.json').exists(),'Inspect existing captions instead of regenerating.'
 plan=rd(O/'plan.json');assert plan['finalTimingApproved']
 review=rd(P/'production/native-guides-direct-review-v1.json');design=rd(P/review['designPath'])
 assert review['all36WholeTextsDirectlyCompared'] and review['contentCoverageApproved']
 paras={x['key']:x for x in plan['paragraphs']};cues={'ko':[],'en':[]};guide_maps=[];issues=[]
 for lang,filename in [('ko','current-caption-layout-proposal-v6.json'),('en','current-english-caption-layout-proposal-v9.json')]:
  layout=rd(P/'production'/filename)
  layout_paragraphs=layout.get('paragraphs')
  if layout_paragraphs is None:
   grouped={}
   for c in layout['cues']:grouped.setdefault(c['key'],[]).append(dict(c,text=c['en']))
   layout_paragraphs=[dict(key=k,cues=v) for k,v in grouped.items()]
  for p in layout_paragraphs:
   row=paras[p['key']];delta=row['timelineOffsetFrames']/60;lo=row['sourceStartFrame']/60;hi=row['sourceEndFrame']/60
   for c in p['cues']:
    a=max(c['startSeconds'],lo);z=min(c['endSeconds'],hi)
    assert a<z and a-c['startSeconds']<.02 and c['endSeconds']-z<.02
    cues[lang].append(dict(key=p['key'],startSeconds=a+delta,endSeconds=z+delta,text=c['text'],lines=c['lines'],reusedLayout=True,sourceSubframeClipSeconds=[a-c['startSeconds'],c['endSeconds']-z]))
 # English sentences cover these explicit Korean sentence groups. These are
 # semantic translation relationships, not character-duration interpolation.
 grouping={'g01':[[0],[1,2],[3],[4],[5]],'g13':[[0,1]],'g14':[[0,1],[2],[3]],'g29':[[0],[1],[2],[3],[4,5]],'g30':[[0],[1],[2,3],[4],[5],[6,7],[8],[9],[10],[11],[12]],'g38':[[0,1],[2],[3],[4]],'g41':[[0],[1,2],[3]]}
 for g in design['rows']:
  asr=rd(R/review['asrPaths'][g['id']])
  assert asr['audioSha256']==review['audioHashes'][g['id']]
  placement=next(v for v in plan['voice'] if v['key']==g['id']);delta=placement['startFrame']/60
  words=[]
  for i,w in enumerate(asr['chunks']):
   a,z=w['timestamp']
   if a is None or z is None or z<=a:continue
   if a>=review.get('asrIgnoredAfterSeconds',{}).get(g['id'],float('inf')):continue
   if words and a<words[-1]['start']:raise ValueError(('reverse-ASR-words',g['id'],i))
   words.append(dict(text=w['text'],start=a,end=z,index=i))
  target=norm(g['ko']);recognized='';owners=[]
  for w in words:t=norm(w['text']);recognized+=t;owners.extend([w]*len(t))
  mapping={}
  for a,b,n in difflib.SequenceMatcher(None,target,recognized,autojunk=False).get_matching_blocks():mapping.update({a+i:b+i for i in range(n)})
  tokens=g['ko'].split();counts=[0]
  for t in tokens:counts.append(counts[-1]+len(norm(t)))
  edges={0:(max(0,words[0]['start']),max(0,words[0]['start'])),len(tokens):(min(asr['seconds'],words[-1]['end']),min(asr['seconds'],words[-1]['end']))}
  for i in range(1,len(tokens)):
   l,r=counts[i]-1,counts[i]
   if l in mapping and r in mapping:
    lw,rw=owners[mapping[l]],owners[mapping[r]]
    if lw['index']!=rw['index'] and lw['end']<=rw['start']:edges[i]=(lw['end'],rw['start'])
  # Directly read actual word times: overlap uses the preceding sentence end;
  # the phonetic Deferred variant still identifies the exact next onset.
  edge_repairs={'g19':{49:(25.22,25.22)},'g39':{23:(11.56,11.78)},'g42':{57:(26.26,26.26)}}
  edges.update(edge_repairs.get(g['id'],{}))
  best={0:(0,[])}
  for end in sorted(edges):
   if end==0:continue
   for start in sorted(best):
    if start>=end:continue
    duration=edges[end][0]-edges[start][1]
    if not 0.7<=duration<=9.5:continue
    text=' '.join(tokens[start:end]);lines=wrap(text)
    if len(lines)>2:continue
    score=best[start][0]+(duration-4.8)**2+(0 if text.endswith(('.', '?', '!')) else 20 if text.endswith(',') else 100)
    if end not in best or score<best[end][0]:best[end]=(score,best[start][1]+[dict(key=g['id'],text=text,lines=lines,startSeconds=edges[start][1]+delta,endSeconds=edges[end][0]+delta,source='actual-guide-ASR-word-edges')])
  assert len(tokens) in best,('no-caption-partition',g['id'])
  cues['ko'].extend(best[len(tokens)][1])
  ko_sentences=re.split(r'(?<=[.!?])\s+',g['ko']);en_sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',g['en'])
  groups=grouping.get(g['id'],[[i] for i in range(len(ko_sentences))]);assert len(groups)==len(en_sentences)
  if g['id']=='g38':
   left,right=en_sentences[0].split(', relating ',1)
   en_sentences=[left+',','relating '+right,*en_sentences[1:]];groups=[[0],[1],[2],[3],[4]]
  sent_ranges=[];token_start=0
  for sentence in ko_sentences:
   token_end=token_start+len(sentence.split())
   if token_start not in edges or token_end not in edges:
    issues.append(dict(key=g['id'],kind='sentence-edge-needs-direct-review',startToken=token_start,endToken=token_end))
    sent_ranges.append(None)
   else:sent_ranges.append((edges[token_start][1],edges[token_end][0]))
   token_start=token_end
  for en,group in zip(en_sentences,groups):
   if any(sent_ranges[i] is None for i in group):continue
   a=sent_ranges[group[0]][0];z=sent_ranges[group[-1]][1];lines=wrap(en)
   if g['id']=='g39' and group==[3]:
    left,right=en.split(', but ',1)
    for text,lo,hi in [(left+',',a,14.46),('but '+right,14.46,z)]:
     lines=wrap(text);assert len(lines)<=2
     cues['en'].append(dict(key=g['id'],text=text,lines=lines,startSeconds=lo+delta,endSeconds=hi+delta,source='direct-semantic-clause-actual-word-edge-각-at14.46',koSentenceIndices=group))
    continue
   if len(lines)>2:
    issues.append(dict(key=g['id'],kind='english-semantic-clause-split-needed',text=en,koSentenceIndices=group,seconds=[a,z]));continue
   cues['en'].append(dict(key=g['id'],text=en,lines=lines,startSeconds=a+delta,endSeconds=z+delta,source='explicit-KO-sentence-semantic-map',koSentenceIndices=group))
  guide_maps.append(dict(key=g['id'],koSentences=ko_sentences,enSentences=en_sentences,englishKoGroups=groups,sentenceRanges=sent_ranges,asrSha256=sh(R/review['asrPaths'][g['id']])))
 if issues:
  wr(O/'caption-edge-issues.json',dict(issues=issues,guideMaps=guide_maps));raise ValueError(f'{len(issues)} semantic edges require direct resolution before final captions')
 for lang in cues:
  cues[lang].sort(key=lambda c:c['startSeconds'])
  assert all(a['endSeconds']<=b['startSeconds']+.001 for a,b in zip(cues[lang],cues[lang][1:]))
  for i,c in enumerate(cues[lang],1):c['index']=i;assert len(c['lines'])<=2
  text='\n\n'.join(f"{c['index']}\n{stamp(c['startSeconds'])} --> {stamp(c['endSeconds'])}\n"+'\n'.join(c['lines']) for c in cues[lang])+'\n'
  (O/f'captions.{lang}.srt').write_text(text,encoding='utf-8')
 result=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),planSha256=sh(O/'plan.json'),cues=cues,guideMaps=guide_maps,allCueTextDirectReview=False,allEncodedPixelsReviewed=False)
 wr(O/'captions.json',result)
 # Static medium instance ensures libass and the width preflight use the same
 #500weight rather than an arbitrary variable-font default.
 from fontTools.ttLib import TTFont
 from fontTools.varLib.instancer import instantiateVariableFont
 fonts=O/'fonts';fonts.mkdir(exist_ok=True);font_path=fonts/'YamYamCaptionMedium.ttf'
 if not font_path.exists():
  ft=instantiateVariableFont(TTFont('C:/Windows/Fonts/NotoSansKR-VF.ttf'),{'wght':500},inplace=False)
  for n in ft['name'].names:
   if n.nameID in [1,4,6,16]:n.string=('YamYamCaptionMedium' if n.nameID==6 else 'YamYam Caption Medium').encode(n.getEncoding())
   elif n.nameID in [2,17]:n.string='Regular'.encode(n.getEncoding())
  ft.save(font_path)
 header='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nScaledBorderAndShadow: yes\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,YamYam Caption Medium,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 events=[]
 def event(layer,c,text):events.append(f"Dialogue: {layer},{stamp(c['startSeconds'],True)},{stamp(c['endSeconds'],True)},Default,,0,0,0,,{text}")
 def rect(layer,c,x,y,w,h,color):event(layer,c,f'{{\\an7\\pos({x:.1f},{y:.1f})\\bord0\\shad0\\1c&H{color}&\\p1}}m 0 0 l {w:.1f} 0 {w:.1f} {h:.1f} 0 {h:.1f}')
 for c in cues['ko']:
  w=math.ceil(max(font.getlength(s) for s in c['lines']))+44;h=62*len(c['lines'])+22;x=960-w/2;y=970-h/2
  rect(0,c,x+14,y+14,w,h,'323C07');rect(1,c,x-1.5,y-1.5,w+3,h+3,'181B16');rect(2,c,x,y,w,h,'FFFFFF')
  for i,line in enumerate(c['lines']):
   cy=970+(i-(len(c['lines'])-1)/2)*62
   event(3,c,f'{{\\an5\\pos(960,{cy:.1f})\\fs48\\bord0\\shad0\\1c&H090B08&}}'+line.replace('{','').replace('}',''))
 (O/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf-8')
 print(json.dumps({'ko':len(cues['ko']),'en':len(cues['en']),'allFinalPixelsReviewed':False}))
if __name__=='__main__':main()
