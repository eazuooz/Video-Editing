import os
"""Create one measured, source-separated edit. Never loop or retime gameplay."""
from pathlib import Path
import json,sys,subprocess,hashlib,math
from collections import defaultdict
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/('production/'+os.environ.get('YAMYAM_D2_LOCAL','local'));MC=R/'motion-canvas/src/projects'/P.name
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def guard():
 c=rd(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def ff(args,log):
 guard();cmd=['ffmpeg','-hide_banner','-nostdin','-loglevel','warning','-threads','2','-filter_threads','1','-filter_complex_threads','1',*map(str,args)]
 with (L/log).open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def make_plan():
 canonical=P/'production/edit-plan.json'
 if canonical.exists() and rd(canonical).get('allocationLocked'):
  plan=rd(canonical);t=rd(L/'timing.json')
  assert plan['bodyFrames']==t['bodyFrames'] and plan['sourceVoiceSha256']==t['sourceSha256']
  assert plan['spokenScriptSha256']==sha(P/'script/narration.spoken-ko.json')
  plan['timingSha256']=sha(L/'timing.json');wr(L/'edit-plan.json',plan)
  jobs=[]
  for c in plan['cuts']:
   if c['kind']!='explanation':continue
   route='/'+c['entry'].split('motion-canvas/',1)[1].replace('.tsx','-project.ts')
   jobs.append({'id':c['id'],'name':Path(c['source']).stem,'frames':c['frames'],'route':route,'visualInputs':c['visualEvidence']})
  wr(L/'diagrams.json',{'jobs':jobs});print('Reused locked measured allocation; no source reallocation',flush=True);return
 t=rd(L/'timing.json');paras=t['paragraphs'];N=t['bodyFrames'];edges=[0]+[round(p['start']*60) for p in paras[1:]]+[N]
 explain={3,10,13,24,27,28,30,32,33,34,35,36,39,40,41,42,43,47,49,55,57,59}
 amounts={p['index']:(0 if p['index'] in explain else edges[p['index']]-edges[p['index']-1]) for p in paras}
 delta=sum(amounts.values())-t['actualFrames'];adjustments=[]
 # A subsecond rounding adjustment extends an already meaningful neighboring
 # explanation across the spoken join, never creates a flashing filler slide.
 if 0<delta<120 and amounts[12]>delta and amounts[13]==0:
  edges[12]-=delta;amounts[12]-=delta
  adjustments.append({'boundaryAfterParagraph':12,'explanationBeginsFramesEarlier':delta,'reason':'carry the early/late power comparison across the adjacent sentence join; no standalone subsecond cut'})
  delta=0
 for i in ([7,16,23,26,31,38,44,46,50,53,54,58] if delta>0 else [13,24,3,30,55,57]):
  capacity=amounts[i] if delta>0 else edges[i]-edges[i-1]-amounts[i]
  n=min(abs(delta),capacity)
  if not n:continue
  amounts[i]+= -n if delta>0 else n;adjustments.append({'paragraph':i,'actualFrameChange':-n if delta>0 else n,'reason':'same narrated object shown as moving demonstration or analyzed diagram; no footage padding or speech deletion'})
  delta+= -n if delta>0 else n
  if delta==0:break
 assert delta==0
 # Candidates are independently inspected source windows for the stated role.
 def win(key,a=0,b=None):return (key,a,b if b is not None else float(rd(L/'sources'/f'{key}.receipt.json')['duration'])-.15)
 spec={
  1:[win('d2-02',108,120)],2:[win('d2-03',52,65),win('d2-01',69,83)],4:[win('vs-02',30,44)],
  5:[win('vs-01',17,35)],6:[win('vs-01',83,96),win('vs-01',105,113)],7:[win('vs-01',35,60)],8:[win('ms-01',3,24)],9:[win('ms-01',25,48)],
  11:[win('vs-01',3,17)],12:[win('vs-03',40,65)],14:[win('vs-02',10,29)],15:[win('vs-03',66,91)],16:[win('vs-02',45,60)],17:[win('d2-02',1,22)],
  18:[win('d2-developer',0,9),win('d2-01',0,6)],19:[win('d2-01',20,44)],20:[win('d2-04',91,109)],21:[win('d2-04',109,121.8)],22:[win('d2-03',43,52),win('d2-01',60,69)],23:[win('d2-02',23,48)],
  25:[win('d2-03',1,25)],26:[win('d2-03',26,42)],29:[win('d2-02',49,70)],31:[win('vs-02',80,100)],37:[win('vs-01',96,105),win('vs-01',113,132)],38:[win('vs-02',110,130)],
  44:[win('d2-03',65,80),win('d2-03',120,126)],45:[win('d2-04',1,21)],46:[win('d2-04',21,40)],48:[win('ms-02',3,32)],50:[win('d2-03',80,100)],51:[win('d2-04',40,61)],52:[win('d2-01',11,20),win('d2-03',100,120)],53:[win('d2-04',61,81)],54:[win('vs-02',60,80)],
  56:[win('d2-developer',9,20),win('vs-03',112,135)],58:[win('vs-02',130,142),win('vs-03',91,102)],60:[win('d2-01',110,121),win('d2-04',109,121)],
  3:[win('d2-01',92,110)],13:[win('vs-03',15,39)],24:[win('d2-02',70,90)],30:[win('d2-02',90,108)],55:[win('d2-04',81,91)],57:[win('d2-03',120,126)]}
 titles={3:('overview','재미와 권리, 두 질문'),7:('loop','조작은 단순하게, 선택은 계속'),10:('expression','규칙과 구체적 표현을 나눠 보기'),13:('power','같은 조작, 달라진 힘'),16:('power','강해지는 경험도 설계입니다'),23:('expression','익숙함을 만드는 구체적인 표현'),24:('quality','재미 · 완성도 · 권리는 별개'),26:('quality','선택의 수와 선택의 깊이'),27:('reactions','초기 반응은 당시 환경의 기록'),28:('reactions','개선 중인 게임, 최종 판정은 별개'),30:('quality','재미에서 이용허락의 질문으로'),31:('expression','같은 규칙과 같은 그림은 다른 질문'),32:('expression','아이디어와 표현'),33:('expression','미국 저작권청의 구분'),34:('court','개별 요소뿐 아니라 결합도 봅니다'),35:('puzzle','같은 큰 규칙, 다른 구체적인 표현'),36:('expression','그림만 바꾸면 언제나 괜찮을까?'),38:('license','구매 후에도 사용 조건을 확인'),39:('notice','공식 고지는 무엇을 말하고 있을까?'),40:('permissions','무료라는 말과 허락은 다릅니다'),41:('files','파일은 어디에서 읽을까?'),42:('notice','임시 호스팅과 글꼴 예외도 고지'),43:('files','정품 보유와 이용허락도 구분'),44:('quality','확인한 사실과 법적 판단'),46:('expression','익숙한 자산을 누가 만들었을까?'),47:('reactions','한 게임에 겹치는 평가 기준'),49:('reactions','개별 댓글을 전체 여론으로 바꾸지 않기'),50:('quality','서로 다른 질문에는 다른 답이 필요'),53:('responsibility','새로운 재미에도 창작자의 권리는 남습니다'),54:('expression','배운 원리와 이용한 자산을 나누기'),55:('responsibility','만들기 전에 확인할 질문'),57:('conclusion','영향 · 표현 · 자산 · 이용허락'),58:('conclusion','재미와 권리를 함께 보기'),59:('choices','여러분이 원래 게임의 개발자라면?')}
 fallback={'01':('overview','재미와 권리, 두 질문'),'02':('loop','성장과 선택의 반복'),'03':('power','선명하게 보이는 성장'),'04':('familiar','익숙한 직업과 장비'),'05':('quality','서로 다른 평가 기준'),'06':('expression','무엇을 이용했고, 허락은 받았을까?'),'07':('reactions','즐거움과 제작 과정의 평가'),'08':('responsibility','원리와 자산의 구분'),'09':('conclusion','재미와 권리를 함께 보기')}
 used=defaultdict(list);cuts=[];jobs=[];image_records=[]
 def reserve(candidates,count):
  chosen=[];need=count
  for key,a,z in candidates:
   free=[(round(a*60),int(z*60))]
   for u,v in used[key]:
    new=[]
    for x,y in free:
     if v<=x or u>=y:new.append((x,y))
     else:
      if x<u:new.append((x,u))
      if v<y:new.append((v,y))
    free=new
   for x,y in free:
    n=min(need,y-x)
    if n<1:continue
    chosen.append((key,x,n));used[key].append((x,x+n));need-=n
    if need==0:return chosen
  raise ValueError(('Insufficient concept-matched unique footage',candidates,count,need))
 def add_actual(p,start,n):
  for key,source_frame,frames in reserve(spec[p['index']],n):
   receipt=rd(L/'sources'/f'{key}.receipt.json');credit={'vs':'Vampire Survivors · The Game Archivist','ms':'Magic Survival · Transcendent','d2':'D2 Survivors · MrLlamaSC'}[key[:2]]
   if key=='d2-developer':credit='D2 Survivors · Paco / framara'
   cuts.append({'id':f'c{len(cuts)+1:03}','paragraph':p['index'],'scene':p['scene'],'kind':'actual','source':rel(L/'sources'/f'{key}.mp4'),'sourceId':key,'sourceSha256':receipt['sha256'],'sourceUrl':receipt['sourceUrl'],'sourceStartFrame':source_frame,'startFrame':start,'frames':frames,'credit':credit,'sourceCrop':{'x':634,'y':0,'w':608,'h':1080} if key.startswith('ms') else None,'audio':'synchronized-game-mix' if key.startswith(('vs','ms')) else 'muted-inseparable-presenter-or-unreviewed-developer-track','observedRole':p['ko'],'annotation':None});start+=frames
 def add_explain(p,start,n):
  kind,title=titles.get(p['index'],fallback[p['scene']]);id=f'c{len(cuts)+1:03}';name=f'vs-d2-{id}-v2';data={'kind':kind,'title':title,'duration':n/60,'currentPicture':'해설용 도식 · 실제 화면 인용','cueTimes':[0.05,min(1.8,n/60*.28),min(4,n/60*.58)]}
  # Use inspected independent screenshots. Conceptual arrows do not claim measured game data.
  key='vs-01' if p['index']<=17 or p['index'] in [37,38,48,54] else 'd2-03'
  f=L/'source-review'/f'{key}-3-native.jpg'
  if kind not in ['files','court','permissions','puzzle']:data['image']='/@fs/'+f.resolve().as_posix()
  if kind in ['power','overview','conclusion']:
   f=L/'source-review'/'d2-03-24-native.jpg' if kind!='power' else L/'source-review'/'vs-01-3-native.jpg'
   g=L/'source-review'/'vs-03-48-native.jpg';data['image']='/@fs/'+f.resolve().as_posix();data['image2']='/@fs/'+g.resolve().as_posix()
  if p['index']==27:data['cueLabels']=['遅延 · 입력 문제 제기'.replace('遅延','지연'),'당시 버전 · 환경','현재 전체 이용자 판정 아님']
  if p['index']==28:data['cueLabels']=['개선 중이라는 답변','난이도 · 시스템 조정','최종 품질 판정과 구분']
  if p['index']==49:data['cueLabels']=['확인한 개별 댓글','전체 이용자 여론 아님','관찰과 해석을 구분']
  if p['index']==42:data['cueLabels']=['전환 기간의 임시 호스팅','한국어 글꼴 일부 예외','전부 로컬 전용으로 단순화 금지']
  entry=MC/f'{id}.tsx';project=MC/f'{id}-project.ts'
  entry.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view) {yield* lesson(view, "+json.dumps(data,ensure_ascii=False)+");});\n",encoding='utf8')
  project.write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './"+id+"?scene';\nexport default makeProject({scenes:[scene]});\n",encoding='utf8')
  jobs.append({'id':id,'name':name,'frames':n,'route':'/src/projects/'+P.name+'/'+id+'-project.ts'})
  sources=[]
  for k in ['image','image2']:
   if data.get(k):f=Path(data[k][5:]);sources.append({'path':rel(f),'sha256':sha(f),'purpose':'show actual narrated game object; image remains explanation footage'})
  jobs[-1]['visualInputs']=sources
  cuts.append({'id':id,'paragraph':p['index'],'scene':p['scene'],'kind':'explanation','startFrame':start,'frames':n,'source':'shared/output/motion-canvas/'+name+'.mp4','diagram':data,'entry':rel(entry),'renderer':'Motion Canvas','visualEvidence':sources,'observedRole':p['ko']})
 for p,a,z in zip(paras,edges,edges[1:]):
  count=amounts[p['index']]
  if count:add_actual(p,a,count)
  if count<z-a:add_explain(p,a+count,z-a-count)
 assert sum(c['frames'] for c in cuts if c['kind']=='actual')==t['actualFrames']
 assert sum(c['frames'] for c in cuts)==N
 for c,d in zip(cuts,cuts[1:]):assert c['startFrame']+c['frames']==d['startFrame']
 # Only verified static UI regions are marked; no invented attack radius, axes or detector outputs.
 for c in cuts:
  if c['kind']!='actual':continue
  if c['paragraph']==5:c['annotation']={'target':'experience-bar','label':'경험치','shape':'hollow rectangle','color':'blue','cue':max(.1,c['frames']/60*.45),'seconds':2.5,'sourceRegion':[2,3,1915,34],'tracking':'screen-fixed UI; clear on every cut'}
  if c['paragraph']==6:c['annotation']={'target':'upgrade-options','label':'다음 강화 선택','shape':'hollow rectangle','color':'green','cue':.5,'seconds':2.5,'sourceRegion':[600,110,755,880],'tracking':'only verified level-up UI interval; clear at menu close or cut'}
  if c['paragraph']==19:c['annotation']={'target':'upgrade-options','label':'빌드 = 선택한 강화의 조합','shape':'hollow rectangle','color':'green','cue':1,'seconds':2.5,'sourceRegion':[370,255,580,545],'tracking':'verified screen-fixed level-up cards; clear at close or cut'}
  if c['paragraph']==20:c['annotation']={'target':'inventory','label':'장비 · 능력치','shape':'hollow rectangle','color':'green','cue':.7,'seconds':3,'sourceRegion':[470,210,990,675],'tracking':'native95s frame directly inspected: stats left, equipment right; clear at close or cut'}
 usage=[]
 for key,ranges in used.items():
  receipt=rd(L/'sources'/f'{key}.receipt.json');usage.append({'source':key,'url':receipt['sourceUrl'],'creator':receipt.get('creator'),'rangesFrames':sorted(ranges),'totalSeconds':sum(z-a for a,z in ranges)/60,'sourceFps':60,'decoded1080p':True,'basis':'limited attributed excerpts closely analyzed for criticism/comparison; no recorder permission or blanket game-asset license claimed','musicRights':'incidental synchronized game mix under critical excerpt basis; no standalone soundtrack use' if key.startswith(('vs','ms')) else 'source track muted; no isolated SFX claimed'})
 plan={'schemaVersion':1,'slug':P.name,'timingSha256':sha(L/'timing.json'),'bodyFrames':N,'actualFrames':t['actualFrames'],'explanationFrames':N-t['actualFrames'],'ratioErrorFrames':abs(t['actualFrames']-N*.6),'brandingFrames':120,'membershipFrames':600,'totalFrames':N+720,'continuousVoice':True,'noSourceLoopsOrRetiming':True,'ratioAdjustments':adjustments,'cuts':cuts,'sourceUsage':usage,'finalHumanReview':'pending'}
 wr(L/'edit-plan.json',plan);wr(L/'diagrams.json',{'jobs':jobs});wr(P/'production/edit-plan.json',plan)
 print(json.dumps({'body':N/60,'actual':t['actualFrames']/60,'explanation':(N-t['actualFrames'])/60,'cuts':len(cuts),'diagrams':len(jobs),'adjustments':adjustments},ensure_ascii=False),flush=True)
def render():
 plan=rd(L/'edit-plan.json');out=L/'cuts';out.mkdir(exist_ok=True)
 asshead='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Yamyam Caption,42.68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 def tm(s):
  v=round(s*100);h,v=divmod(v,360000);m,v=divmod(v,6000);ss,v=divmod(v,100);return f'{h}:{m:02}:{ss:02}.{v:02}'
 for c in plan['cuts']:
  output=out/(c['id']+'.mp4');receipt=out/(c['id']+'.json');source=R/c['source'];signature={'cut':c,'inputSha256':sha(source),'codec':'x264-fast-crf18-fhd60-bt709-v1'}
  if output.exists() and receipt.exists() and rd(receipt).get('signature')==signature and rd(receipt).get('sha256')==sha(output):continue
  assert not output.exists(),('Changed cut requires reviewed new output name',output)
  length=c['frames']/60;events=[]
  def ev(a,z,text,layer=0):events.append(f'Dialogue: {layer},{tm(a)},{tm(z)},Default,,0,0,0,,{text}')
  if c['kind']=='actual':
   # Editorial source/creator credits belong only at the description bottom.
   # Original embedded notices stay inside the preserved source frame.
   key=c['sourceId']
   if key.startswith('ms'):
    ev(0,length,'{\\an5\\pos(350,160)\\fs68.286}매직 서바이벌')
    ev(0,length,'{\\an5\\pos(350,220)\\fs45.524\\c&HBBBBBB&}Magic Survival')
   else:
    labels=['뱀파이어','서바이버'] if key.startswith('vs') else ['D2','Survivors']
    for i,label in enumerate(labels):ev(0,length,f'{{\\an5\\pos(88,{70+i*44})\\fs45.524}}'+label)
   note=c.get('annotation')
   if note:
    a=note['cue'];z=min(length,a+note['seconds']);x,y,w,h=note['sourceRegion'];x=176+x*49/60;y*=49/60;w*=49/60;h*=49/60;color={'blue':'E3B86B','green':'AAD8A6'}[note['color']]
    ev(a,z,f'{{\\an7\\pos({x:.2f},{y:.2f})\\p1\\1a&HFF&\\bord6\\3c&H{color}&\\fad(160,160)}}m 0 0 l {w:.2f} 0 {w:.2f} {h:.2f} 0 {h:.2f} 0 0',1)
    # Plain short labels are placed away from the marked detail and captions.
    lx,ly=(960,115) if note['target']=='experience-bar' else (1480,150)
    ev(a,z,f'{{\\an5\\pos({lx},{ly})\\fs60\\c&H{color}&\\bord3\\fad(160,160)}}'+note['label'],2)
  else:
   pass
  ass=out/(c['id']+'.ass');ass.write_text(asshead+'\n'.join(events)+'\n',encoding='utf8')
  assfilter=f'ass=filename=\'{rel(ass)}\':fontsdir=\'{rel(L/"fonts")}\''
  if c['kind']=='actual':
   crop=c.get('sourceCrop');vf=(f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']},scale=497:882:flags=lanczos,pad=1920:1080:711:0:black" if crop else 'scale=1568:882:flags=lanczos,pad=1920:1080:176:0:black')
   args=['-ss',str(c['sourceStartFrame']/60),'-i',source]
  else:vf='scale=1920:1080:flags=lanczos';args=['-i',source]
  vf+=',setsar=1,fps=60,format=yuv420p,'+assfilter
  ff(['-n',*args,'-an','-vf',vf,'-frames:v',c['frames'],'-c:v','libx264','-preset','fast','-crf','18','-g','120','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000',output],f'cuts/{c["id"]}.log')
  v=probe(output)['streams'][0];assert int(v['nb_frames'])==c['frames'] and v['r_frame_rate']=='60/1'
  wr(receipt,{'signature':signature,'sha256':sha(output),'geometry':[1920,1080,60],'frames':c['frames'],'pixelReview':'pending'})
  print('Rendered',c['id'],c['kind'],c['frames'],flush=True)
 # Retain the exact approved branding/member visuals and identities; standardize only encoding.
 base=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'
 for key,n in [('branding',120),('membership',600)]:
  dest=out/(key+'.mp4')
  if not dest.exists():ff(['-n','-i',base/(key+'.mp4'),'-an','-vf','scale=1920:1080,setsar=1,fps=60,format=yuv420p','-frames:v',n,'-c:v','libx264','-preset','fast','-crf','18','-g','120','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000',dest],f'cuts/{key}.log')
  assert int(probe(dest)['streams'][0]['nb_frames'])==n
 files=[out/'branding.mp4',*[out/(c['id']+'.mp4') for c in plan['cuts']],out/'membership.mp4']
 (L/'visual-concat.txt').write_text('\n'.join("file '"+p.resolve().as_posix()+"'" for p in files)+'\n',encoding='utf8')
 dest=L/'visual.mp4'
 if not dest.exists():ff(['-n','-f','concat','-safe','0','-i',L/'visual-concat.txt','-an','-c:v','copy','-movflags','+faststart',dest],'visual-concat.log')
 assert int(probe(dest)['streams'][0]['nb_frames'])==plan['totalFrames']
 wr(L/'visual-build.json',{'planSha256':sha(L/'edit-plan.json'),'visualSha256':sha(dest),'frames':plan['totalFrames'],'allCutsRendered':True,'pixelReview':'pending','brandingSourceSha256':sha(base/'branding.mp4'),'membershipSourceSha256':sha(base/'membership.mp4')})
if __name__=='__main__':
 guard()
 if sys.argv[1]=='plan':make_plan()
 elif sys.argv[1]=='render':render()
 else:raise ValueError(sys.argv[1])
