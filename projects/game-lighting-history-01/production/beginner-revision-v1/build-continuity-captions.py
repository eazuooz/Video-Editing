"""Retain unchanged cues; update the14 measured paragraphs and two safe moves."""
import pathlib,json,hashlib,math,datetime,importlib.util
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;B=P/'production/local/beginner-revision-v1';O=P/'production/local/continuity-v2'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(t,ass=False):
 unit=100 if ass else 1000;v=round(t*unit);h,v=divmod(v,3600*unit);m,v=divmod(v,60*unit);s,v=divmod(v,unit)
 return f'{h}:{m:02}:{s:02}.{v:02}' if ass else f'{h:02}:{m:02}:{s:02},{v:03}'
def main():
 plan=rd(O/'plan.json');assert plan['finalTimingApproved'];old=rd(B/'plan.json');cap=rd(B/'captions.json');a=rd(O/'alignment-proposal.json');review=rd(O/'source-review.json');assert review['alignmentSha256']==sha(O/'alignment-proposal.json') and review['fullTextAndEdgesReviewed']
 changed={r['key']:r for r in a['rows']};oldv={v['key']:v for v in old['voice']};vs={v['key']:v for v in plan['voice']};cues={l:[] for l in ['ko','en']}
 sp=importlib.util.spec_from_file_location('captionlayout',H/'align-continuity.py');layout=importlib.util.module_from_spec(sp);sp.loader.exec_module(layout)
 for lang in cues:
  for c in cap['cues'][lang]:
   if c['key'] in changed:continue
   c=dict(c);delta=(vs[c['key']]['startFrame']-oldv[c['key']]['startFrame'])/60
   c.update(startSeconds=c['startSeconds']+delta,endSeconds=c['endSeconds']+delta,reusedLayout=True);cues[lang].append(c)
  for key,r in changed.items():
   offset=vs[key]['startFrame']/60
   for c in r[lang+'Cues']:cues[lang].append(dict(c,key=key,startSeconds=offset+c['seconds'][0],endSeconds=offset+c['seconds'][1],reusedLayout=False))
  cues[lang].sort(key=lambda c:c['startSeconds'])
  assert all(x['endSeconds']<=y['startSeconds']+.001 for x,y in zip(cues[lang],cues[lang][1:])),lang
  for i,c in enumerate(cues[lang],1):
   c['index']=i;assert len(c['lines'])<=2 and all(layout.font.getlength(s)<=1570 for s in c['lines']);assert 0<=c['startSeconds']<c['endSeconds']<plan['seconds']-10
  (O/f'captions.{lang}.srt').write_text('\n\n'.join(f"{c['index']}\n{stamp(c['startSeconds'])} --> {stamp(c['endSeconds'])}\n"+'\n'.join(c['lines']) for c in cues[lang])+'\n',encoding='utf8')
 header=(B/'captions.ko.ass').read_text(encoding='utf8').split('Dialogue:',1)[0];events=[]
 def event(layer,c,text):events.append(f"Dialogue: {layer},{stamp(c['startSeconds'],True)},{stamp(c['endSeconds'],True)},Default,,0,0,0,,{text}")
 def rect(layer,c,x,y,w,h,color):event(layer,c,f'{{\\an7\\pos({x:.1f},{y:.1f})\\bord0\\shad0\\1c&H{color}&\\p1}}m 0 0 l {w:.1f} 0 {w:.1f} {h:.1f} 0 {h:.1f}')
 for c in cues['ko']:
  w=math.ceil(max(layout.font.getlength(s) for s in c['lines']))+44;h=62*len(c['lines'])+22;x=960-w/2;y=970-h/2
  rect(0,c,x+14,y+14,w,h,'323C07');rect(1,c,x-1.5,y-1.5,w+3,h+3,'181B16');rect(2,c,x,y,w,h,'FFFFFF')
  for i,line in enumerate(c['lines']):event(3,c,f'{{\\an5\\pos(960,{970+(i-(len(c["lines"])-1)/2)*62:.1f})\\fs48\\bord0\\shad0\\1c&H090B08&}}'+line.replace('{','').replace('}',''))
 (O/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8')
 wr(O/'captions.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),planSha256=sha(O/'plan.json'),cues=cues,utteranceKeys=150,allCueTextDirectReview=True,reviewBasis='136 retained current paragraph sources;14 measured paired-transition replacements with direct KO/EN text/edge review. Two retained PCM placements shifted inside relevant scenes. New two-line layouts balanced. Final encoded pixels pending.',allEncodedPixelsReviewed=False))
 print(json.dumps({k:len(v) for k,v in cues.items()}))
if __name__=='__main__':main()
