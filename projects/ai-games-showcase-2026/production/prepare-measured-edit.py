"""Create frame-exact edits from recognized speech; never stretch clips or voice."""
from pathlib import Path
import json,math,re,sys,hashlib,subprocess
from PIL import ImageFont
from revision_context import paths, ensure_authorized
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';O=P/'production/local/compact-edit';N=R/'shared/output/narration/ai-games-showcase-2026/game-tools-five-second-ppt-v1';M=R/'production/preflight/ai-games-showcase-2026/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
O,N,EDIT_PLAN,STEM=paths();O.mkdir(parents=True,exist_ok=True)
ensure_authorized()
timing=read(N/(STEM+'.timing.json'));assert timing.get('alignment')
script=read(P/'script/narration.ko.json');design=read(P/'planning/production-plan.json');aliases=read(P/'script/pronunciation.json')['aliases'];font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',48)
def display(s):
 for canonical,spoken in sorted(aliases.items(),key=lambda p:len(p[1]),reverse=True):s=re.sub(r'(?<![가-힣A-Za-z0-9])'+re.escape(spoken),lambda _:canonical,s)
 return s
def wrap(text):
 if font.getlength(text)<=1600:return text
 words=text.split();split=min(range(1,len(words)),key=lambda i:abs(font.getlength(' '.join(words[:i]))-font.getlength(' '.join(words[i:]))));lines=[' '.join(words[:split]),' '.join(words[split:])]
 assert max(font.getlength(x) for x in lines)<=1728,(text,lines)
 return '\n'.join(lines)
def stamp(s,ass=False):
 t=round(s*(100 if ass else 1000));scale=100 if ass else 1000;h,t=divmod(t,3600*scale);m,t=divmod(t,60*scale);sec,ms=divmod(t,scale)
 return f'{h}:{m:02d}:{sec:02d}.{ms:02d}' if ass else f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'
def seconds(s):
 h,m,z=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(z)
captions=[]
fishEntry=next(e for e in timing['entries'] if e['scene_id']=='02')
fishFirstWord=read(N/'asr/02.json')['words'][0]['timestamp'][0]
leadingCorrection={'scene':'02','from':fishEntry['voice_start']+2,'to':fishEntry['start']+fishFirstWord+2,'reason':'ASR renders the spoken Korean game title in Latin letters; restore first title caption to the actual first recognized word onset. Raw ASR and PCM remain unchanged.'}
for lang in ['ko','en']:
 blocks=[];prev=0
 for i,block in enumerate((O/f'body.{lang}.srt').read_text(encoding='utf8').strip().split('\n\n'),1):
  lines=block.splitlines();a,b=[seconds(s)+2 for s in lines[1].split(' --> ')]
  if abs(a-leadingCorrection['from'])<.002:a=leadingCorrection['to']
  text=' '.join(lines[2:]);text=wrap(display(text)) if lang=='ko' else '\n'.join(lines[2:]);assert a>=prev-.002 and b>a;prev=b
  blocks.append(f'{i}\n{stamp(a)} --> {stamp(b)}\n{text}')
  if lang=='ko':captions.append({'id':i,'cue':i,'start':a,'end':b,'text':text})
 (O/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
header=(P/'production/local/tool-slides/captions.ass').read_text(encoding='utf8').split('[Events]')[0]+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
events=[f"Dialogue: 2,{stamp(c['start'],True)},{stamp(c['end'],True)},Caption,,0,0,0,,{{\\pos(960,970)}}"+c['text'].replace('\n',r'\N') for c in captions]
(O/'captions.ko.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8');save(O/'caption-layout.json',{'style':'boxed-white-forest-v1','rows':captions,'textWidthMaximum':1728,'allMeasured':True})
scenes=[];total=math.ceil((2+timing['duration_seconds']+10)*60);cuts=[]
def asset(name,start=0,label=None):return {'sourceFile':rel(M/name),'sourceStart':start,'note':label}
visuals={
 '01':[[asset('fish-creator-demo.mp4',6),asset('vector-creator-demo.mp4',10),asset('augury-preview-1080.png')],[asset('rally-creator-demo.mp4',.2),asset('vector-creator-demo.mp4',50)],[asset('fish-creator-demo.mp4',10)]],
 '02':[[asset('fish-creator-demo.mp4',20)],[asset('fish-creator-demo.mp4',72)],[asset('fish-creator-demo.mp4',80)],[asset('fish-creator-demo.mp4',100)],[asset('fish-creator-demo.mp4',120)]],
 '03':[[asset('emberfall-village-1080.png',label='본게임 · 카메라 회전 전'),asset('emberfall-rotated-1080.png',label='본게임 · 카메라 회전 후')],[asset('emberfall-title-1080.png',label='본게임 플레이')],[asset('emberfall-village-1080.png',label='본게임'),asset('emberfall-editor-1080.png',label='별도 레벨 에디터')],[asset('emberfall-rotated-1080.png',label='정확한 모델·전체 기간 미확인')]],
 '04':[[asset('nightshoal-trailer.mp4',2)],[asset('nightshoal-trailer.mp4',14)],[asset('nightshoal-week11.mp4',3),asset('nightshoal-week11.mp4',44)],[asset('nightshoal-week11.mp4',18)]],
 '05':[[asset('vector-creator-demo.mp4',14)],[asset('vector-creator-demo.mp4',32)],[asset('vector-creator-demo.mp4',43)],[asset('vector-creator-demo.mp4',72)]],
 '06':[[asset('augury-before-1080.png',label='행동 선택 중 · 일시 정지'),asset('augury-preview-1080.png',label='초록색 모습 · 예상 위치'),asset('augury-after-1080.png',label='선택 확정 후 결과')],[asset('augury-title-1080.png')],[asset('augury-before-1080.png'),asset('augury-raijin-reference.webp',label='제작자 공개 · 생성된 캐릭터 참고 그림'),asset('augury-raijin-composite.webp',label='제작자 공개 · 도트 가공과 소품 합성')],[asset('augury-after-1080.png',label='공개 데모 · 실제 상태 캡처')]],
 '07':[[asset('rally-creator-demo.mp4',.2),asset('rally-creator-demo.mp4',10)],[asset('rally-creator-demo.mp4',5.2)],[asset('rally-creator-demo.mp4',17)],[asset('rally-creator-demo.mp4',31.2),asset('rally-creator-demo.mp4',22)],[asset('rally-creator-demo.mp4',25)]],
 '08':[[asset('fish-creator-demo.mp4',128),asset('vector-creator-demo.mp4',97),asset('augury-after-1080.png')],[asset('nightshoal-week11.mp4',36),asset('emberfall-village-1080.png')],[asset('fish-creator-demo.mp4',144)]]}
credits={'fish':'Fork Dev / ForkedPush','emberfall':'Emberfall / Luminati','nightshoal':'Nightshoal / ProFactor','vector':'W2DGAMES','augury':'Rahul Ghosh','rally':'titkun / Sandscape'}
for idx,s in enumerate(script['scenes']):
 sid=s['id'];entries=[e for e in timing['entries'] if e['scene_id']==sid];a=round((entries[0]['start']+2)*60)
 nextEntries=[e for e in timing['entries'] if e['scene_id']==script['scenes'][idx+1]['id']] if idx+1<len(script['scenes']) else []
 b=round((nextEntries[0]['start']+2)*60) if nextEntries else total-600
 ds=design['scenes'][idx];scene={'id':sid,'title':s['title'],'game':ds['game'],'voiceStart':entries[0]['start']+2,'startFrame':a,'endFrame':b,'paragraphs':entries};scenes.append(scene)
 pieces=[]
 for j,e in enumerate(entries):
  start=a if j==0 else round((e['voice_start']+2)*60);end=round((entries[j+1]['voice_start']+2)*60) if j+1<len(entries) else b
  options=visuals[sid][j]
  for k,v in enumerate(options):
   x=start+round((end-start)*k/len(options));y=start+round((end-start)*(k+1)/len(options));pieces.append(dict(**v,startFrame=x,frames=y-x,paragraph=j+1,scene=sid))
 card=ds.get('developmentSummary');slideStart=round((entries[card['paragraph']-1]['voice_start']+2)*60) if card else None
 for c in pieces:
  x,y=c['startFrame'],c['startFrame']+c['frames'];spans=[(x,y)]
  if card:spans=[(lo,hi) for lo,hi in [(x,min(y,slideStart)),(max(x,slideStart+300),y)] if hi>lo]
  for lo,hi in spans:
   p=R/c['sourceFile'];movie=p.suffix=='.mp4';v=dict(c,startFrame=lo,frames=hi-lo,sourceStart=c['sourceStart']+(lo-x)/60 if movie else 0,kind='independent-gameplay' if movie else 'actual-state-or-development-still')
   if movie:
    dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(p)]))['format']['duration']);assert v['sourceStart']+v['frames']/60<=dur-.1,(sid,c['paragraph'],v,dur)
   sourceGame=p.name.split('-')[0]
   v['credit']=credits.get(ds['game'] or sourceGame,'');v['originalAudio']='exclude';cuts.append(v)
 if card:
  cuts.append({'scene':sid,'paragraph':card['paragraph'],'startFrame':slideStart,'frames':300,'sourceFile':card['png'],'sourceStart':0,'kind':'tool-summary','credit':'','note':None});card['frameTiming']={'startFrame':slideStart,'endFrame':slideStart+300};card['status']='measured300frame-placement'
cuts.sort(key=lambda c:c['startFrame']);cursor=120
for i,c in enumerate(cuts):assert c['startFrame']==cursor,(i,c,cursor);cursor+=c['frames'];c['endFrame']=cursor;c['id']=f'cut-{i+1:03d}';c['sourceSha256']=sha(R/c['sourceFile'])
assert cursor==total-600
plan={'schemaVersion':1,'timing':'measured-and-asr-aligned','totalFrames':total,'bodyFrames':total-720,'fps':60,'scenes':scenes,'cuts':cuts,'toolSlideFrames':1800,'captionStartCorrections':[leadingCorrection],'sourcesNoUpscale':True,'stillSequenceNotContinuousGameplay':True,'humanWholeListening':'pending'}
save(EDIT_PLAN,plan);save(P/'planning/production-plan.json',design)
print(json.dumps({'duration':total/60,'cuts':len(cuts),'captions':len(captions),'toolSlides':6}))
