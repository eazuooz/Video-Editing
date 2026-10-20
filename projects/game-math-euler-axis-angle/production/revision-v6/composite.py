"""Frame-exact V6 local edit: same testbed, finite demonstrations and clause captions."""
from pathlib import Path
import argparse,json,hashlib,math,subprocess,os
from PIL import Image,ImageEnhance,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v6';E=O/'edit';E.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
ENC=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
FONT='C:/Windows/Fonts/malgun.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf'
WORLD_DIM=.75;DIAGRAM_ALPHA=.76
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def selected():
 c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized'];assert not c.get('automations',{}).get('automaticNextVideo',False)
def run(args,name):
 with (E/(name+'.log')).open('wb') as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 if q.returncode:raise RuntimeError((E/(name+'.log')).read_text(errors='replace')[-3500:])
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))
def check(p,n):
 v=next(v for v in probe(p)['streams'] if v['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',n),(str(p),v,n)
def fpath(v):return R/(v['path'] if isinstance(v,dict) else v)
def framevalue(v):return v if isinstance(v,str) else v['path']
def image_out(path,source,bg=None,dim=1,game=False,answer=None):
 source=fpath(source);sig={'source':sha(source),'background':sha(bg) if bg else None,'dim':dim,'diagramAlpha':DIAGRAM_ALPHA if bg else None,'game':game,'answer':answer}
 receipt=path.with_suffix('.json')
 if path.exists() and receipt.exists() and read(receipt)==sig:return rel(path)
 im=Image.open(source).convert('RGBA')
 if game:
  canvas=Image.new('RGBA',(1920,1080),(8,11,13,255));canvas.alpha_composite(im.resize((1472,828),Image.Resampling.LANCZOS),(224,32));im=canvas
 elif bg:
  im.putalpha(im.getchannel('A').point(lambda a:round(a*DIAGRAM_ALPHA)))
  back=ImageEnhance.Brightness(Image.open(bg).convert('RGB')).enhance(dim).convert('RGBA');back.alpha_composite(im);im=back
 elif dim!=1:im=ImageEnhance.Brightness(im.convert('RGB')).enhance(dim).convert('RGBA')
 if answer:
  dr=ImageDraw.Draw(im);dr.rectangle((190,580,1730,840),fill=(18,24,28,255));font=ImageFont.truetype(FONT,54)
  for i,text in enumerate(answer):dr.text((240,610+i*100),text,font=font,fill='#a4c6a0',stroke_width=1)
 path.parent.mkdir(exist_ok=True,parents=True);im.convert('RGB').save(path);save(receipt,sig);return rel(path)
def recap_grid(source):
 path=E/'states/rotation-recap-grid.png';source=fpath(source);sig={'sourceSha256':sha(source),'authoringSha256':sha(Path(__file__))};receipt=path.with_suffix('.json')
 if path.exists() and receipt.exists() and read(receipt)==sig:return rel(path)
 im=Image.new('RGB',(1920,1080),'#080b0d');draw=ImageDraw.Draw(im);font=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
 draw.text((110,212),'같은 자세를 서로 다르게 기록',font=font(56,True),fill='#e8cf83')
 # Identical actual Unity frame/camera in each column; no second 3D implementation.
 model=Image.open(source).convert('RGB').crop((220,210,1160,850));model.thumbnail((530,360),Image.Resampling.LANCZOS)
 cols=[('오일러 각',['(h,p,b)=(90°,0°,0°)','물체축 Y-X-Z']),('축·각',['n=(0,1,0)','θ=90° = π/2 rad']),('회전벡터',['e=(0,π/2,0)','축 방향 · 길이 π/2 rad'])]
 for i,(title,rows) in enumerate(cols):
  x=110+i*580;draw.text((x,300),title,font=font(44,True),fill='#e8cf83');im.paste(model,(x+(540-model.width)//2,363));draw.line((x,720,x+530,720),fill='#6b7280',width=2)
  for j,text in enumerate(rows):draw.text((x,740+j*56),text,font=font(34),fill='#73c7c2' if j==0 else '#f5f5f5')
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path);save(receipt,sig);return rel(path)
def load_assets():
 math_assets={x['id']:x for x in read(O/'math/outputs.json')['outputs']}
 spatial_plan=read(H/'spatial-plan.json');spatial={b['id']:b for s in spatial_plan['scenes'] for b in s['beats'] if b['renderer']=='Unity'}
 readouts={x['id']:x for x in read(O/'spatial-clips/readouts/outputs.json')['outputs']}
 auxiliary={x['id']:x for x in spatial_plan.get('auxiliaryClips',[])}
 footprint=read(H/'footage-plan.json');games={x['beatId']:x for x in footprint['clips']};finite_games={x['id']:x for x in read(O/'footage/finite-clips/finite-assets.json')['clips']}
 guides={x['beatId']:x for x in read(E/'guide-outputs.json')['clips']} if (E/'guide-outputs.json').exists() else {}
 screens={b['id']:b for s in read(H/'screen-plan.json')['scenes'] for b in s['beats']}
 # The actual capture receipt is authoritative for spatial files, not a planned path.
 for row in spatial.values():
  for key in ['clipFile','firstFrame','lastFrame']:assert (R/row[key]).exists(),('Missing actual Unity capture',row['id'],key)
  numbers=readouts[row['id']];row.update({k:numbers[k] for k in ['assFile','firstDisplay','lastDisplay']})
 for row in auxiliary.values():
  for key in ['clipFile','firstFrame','lastFrame']:assert(R/row[key]).exists(),('Missing auxiliary Unity capture',row['id'],key)
  numbers=readouts[row['id']];row.update({k:numbers[k] for k in ['assFile','firstDisplay','lastDisplay']})
 for key,row in games.items():
  finite=finite_games[row['id']];row['clipFile']=finite['videoFile'];assert sha(R/row['clipFile'])==finite['videoSha256'],'Native game cut changed'
  row.update({k:v for k,v in guides.get(key,{}).items() if k in ['firstDisplay','lastDisplay']})
  assert(R/row['clipFile']).exists(),('Missing actual finite game cut',key,row['clipFile'])
  row['durationFrames']=row['frames'];row['renderer']='independent-gameplay'
 assets={**spatial,**math_assets,**games};assert len(assets)==106 and set(assets)==set(screens),(len(assets),set(screens)-set(assets))
 return assets,screens,auxiliary
def plan_edit():
 selected();t=read(H/'timeline.json');assert t['fps']==60 and (t.get('timing') in ['measured-and-asr-aligned','measured-source-asr-and-quiet-seams','measured-and-verified'] or t.get('status')=='measured-and-asr-aligned')
 assets,screens,auxiliary=load_assets();base=O/'spatial-clips/testbed-still.png';assert base.exists()
 scenes=[];previous=rel(base);world=rel(base);previous_kind='our-unity';previous_game=None
 for scene in t['scenes']:
  start=scene['startFrame'];end=start+scene['frames'];cursor=start;phases=[];last=previous
  def phase(kind,a,b,file,**kw):
   if b>a:phases.append(dict(kind=kind,startFrame=a,endFrame=b,frames=b-a,file=file,**kw))
  for beat in scene['teachingBeats']:
   key=beat['id'];asset=assets[key];spec=screens[key];renderer=spec['renderer'];vstart=beat.get('visualStartFrame',round(beat['visualStart']*60));vend=beat.get('visualEndFrame',round(beat['visualEnd']*60));holdend=beat.get('holdEndFrame',round(beat['holdEnd']*60));speechstart=beat.get('speechStartFrame',round(beat['speechStart']*60))
   assert vend-vstart==asset['durationFrames'],('Timeline differs from finite asset',key,vend-vstart,asset['durationFrames'])
   before=framevalue(asset['firstFrame']);after=framevalue(asset['lastFrame']);source_kind='our-unity'
   if renderer=='Manim':
    # Keep the 3D testbed separate from accumulated panels/game stills.
    background=R/world
    first=image_out(E/'states'/(key+'.first.png'),before,bg=background,dim=WORLD_DIM);final=image_out(E/'states'/(key+'.last.png'),after,bg=background,dim=WORLD_DIM);source_kind='our-calculation'
   elif renderer=='independent-gameplay':
    first=asset.get('firstDisplay') or image_out(E/'states'/(key+'.first.png'),before,game=True);final=asset.get('lastDisplay') or image_out(E/'states'/(key+'.last.png'),after,game=True);source_kind='actual'
   else:first=asset['firstDisplay'];final=asset['lastDisplay'];background=None;world=after
   prefix=max(cursor,speechstart)
   phase('still',cursor,prefix,last,beatId=key,sourceKind=phases[-1]['sourceKind'] if phases else previous_kind,gameSceneId=phases[-1].get('gameSceneId') if phases else previous_game)
   phase('still',prefix,vstart,first,beatId=key,sourceKind='actual-still' if source_kind=='actual' else source_kind,gameSceneId=scene['id'] if source_kind=='actual' else None)
   motion=dict(beatId=key,sourceKind=source_kind,renderer=renderer,asset=asset,gameSceneId=scene['id'] if source_kind=='actual' else None)
   if renderer=='Manim':motion['background']=rel(background)
   phase('motion',vstart,vend,asset['clipFile'],**motion)
   phase('still',vend,holdend,final,beatId=key,sourceKind='actual-still' if source_kind=='actual' else source_kind,gameSceneId=scene['id'] if source_kind=='actual' else None)
   cursor=holdend;last=final
   answer=spec.get('demonstration',{}).get('answerRows') if spec.get('demonstration') else None
   if answer:
    confirmation=beat.get('confirmationStartFrame',round(beat.get('confirmationStart',holdend/60)*60));assert confirmation>=holdend
    phase('still',cursor,confirmation,last,beatId=key,sourceKind=source_kind);cursor=confirmation
    last=image_out(E/'states'/(key+'.answer.png'),final,answer=answer)
   for window in scene.get('auxiliaryVisuals',[]):
    if window.get('parentBeatId',scene['teachingBeats'][-1]['id'])!=key:continue
    aux=auxiliary[window['id']];a=window['visualStartFrame'];b=window['visualEndFrame'];h=window['holdEndFrame'];assert b-a==aux['durationFrames']
    phase('still',cursor,a,last,beatId=key,sourceKind=source_kind);phase('motion',a,b,aux['clipFile'],beatId=aux['id'],sourceKind='our-unity',renderer='Unity',asset=aux);phase('still',b,h,aux['lastDisplay'],beatId=aux['id'],sourceKind='our-unity');cursor=h;world=aux['lastFrame'];last=recap_grid(aux['lastFrame'])
  phase('still',cursor,end,last,beatId=scene['teachingBeats'][-1]['id'],sourceKind='our-comparison' if scene.get('auxiliaryVisuals') else phases[-1]['sourceKind'],gameSceneId=phases[-1].get('gameSceneId'))
  assert phases and phases[0]['startFrame']==start and phases[-1]['endFrame']==end
  assert all(a['endFrame']==b['startFrame'] for a,b in zip(phases,phases[1:])),scene['id']
  scenes.append(dict(id=scene['id'],startFrame=start,frames=scene['frames'],phases=phases,firstFrame=phases[0]['file'],lastFrame=last,previousFrame=previous))
  previous=last;previous_kind=phases[-1]['sourceKind'];previous_game=phases[-1].get('gameSceneId')
 out={'timelineSha256':sha(H/'timeline.json'),'screenPlanSha256':sha(H/'screen-plan.json'),'sceneCount':len(scenes),'scenes':scenes,'inputAssets':{k:{'clip':v['clipFile'],'sha256':sha(R/v['clipFile'])} for k,v in {**assets,**auxiliary}.items()},'actualFrames':sum(x['frames'] for s in scenes for x in s['phases'] if x['kind']=='motion' and x['sourceKind']=='actual'),'ratioEnforced':False}
 save(E/'scene-plan.json',out);return out
def stamp(seconds):
 cs=math.floor(seconds*100+1e-7);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02d}:{s:02d}.{cs:02d}'
UI_HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: UI,Malgun Gothic,42,&H00F5F5F5,&H00F5F5F5,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def ass_event(a,b,text,layer=3):return f'Dialogue: {layer},{stamp(a)},{stamp(b)},UI,,0,0,0,,{text}\n'
def ui_ass(scene,screen):
 # All time values are global, matching final narration/caption timestamps.
 term=screen['termChip'];start=scene['startFrame']/60;end=(scene['startFrame']+scene['frames'])/60;collapse=min(end,start+max(5,min(9,(len(term['en'])+len(term['term'])+len(term['meaning']))/9)))
 windows=[]
 for p in scene['phases']:
  kind=p['sourceKind'];a=p['startFrame']/60;b=p['endFrame']/60
  spans=[(a,b)] if not a<collapse<b else [(a,collapse),(collapse,b)]
  for a,b in spans:
   state=(kind,a<collapse,p.get('gameSceneId'))
   if windows and windows[-1][2]==state and abs(windows[-1][1]-a)<.001:windows[-1]=(windows[-1][0],b,state)
   else:windows.append((a,b,state))
 out=UI_HEADER
 for a,b,(kind,definition,game_scene) in windows:
  actual=kind.startswith('actual');pic='실제 게임 녹화' if kind=='actual' else '실제 게임 녹화 · 정지 관찰' if actual else '우리 모형 · 해설용 계산' if kind=='our-calculation' else '우리 모형 · 비교 도식' if kind=='our-comparison' else '우리 Unity 씬 · 해설용 모형'
  if actual:
   game={'v6-08':r'마리오 카트\N8 디럭스','v6-15':r'젤다의 전설\N티어스 오브\N더 킹덤','v6-22':r'슈퍼 마리오\N오디세이','v6-32':r'젤다의 전설\N티어스 오브\N더 킹덤'}[game_scene or scene['id']]
   out+=ass_event(a,b,r'{\an7\pos(18,48)\fs30\c&H0083CFE8&}'+game)
   out+=ass_event(a,b,r'{\an7\pos(1714,48)\fs28\c&H00B8B8B8&}실제 게임\N녹화'+(r'\N정지 관찰' if kind=='actual-still' else ''))
  else:
   boxh=170 if definition else 112
   out+=ass_event(a,b,r'{\an7\pos(0,0)\p1\c&H00151210&\alpha&H15&}'+f'm 80 34 l 1170 34 1170 {34+boxh} 80 {34+boxh}'+r'{\p0}',2)
   if definition:
    out+=ass_event(a,b,r'{\an7\pos(100,45)\fs30\c&H00B8B8B8&}'+term['en'])
    out+=ass_event(a,b,r'{\an7\pos(100,82)\fs48\b1\c&H0083CFE8&}'+term['term'])
    out+=ass_event(a,b,r'{\an7\pos(100,144)\fs34\c&H00F5F5F5&}'+term['meaning'])
   else:
    out+=ass_event(a,b,r'{\an7\pos(100,44)\fs46\b1\c&H0083CFE8&}'+term['term'])
    out+=ass_event(a,b,r'{\an7\pos(100,103)\fs28\c&H00B8B8B8&}'+pic)
   out+=ass_event(a,b,r'{\an9\pos(1824,48)\fs30\c&H00B8B8B8&}현재 화면\N'+pic)
 path=E/(scene['id']+'.ui.ass');path.write_text(out,encoding='utf8');return path
def render_scenes(selected_scenes=None):
 selected();plan=read(E/'scene-plan.json');assert plan['timelineSha256']==sha(H/'timeline.json') and plan['screenPlanSha256']==sha(H/'screen-plan.json')
 for key,row in plan['inputAssets'].items():assert sha(R/row['clip'])==row['sha256'],('Finite asset changed; rebuild current edit plan',key)
 screens={s['id']:s for s in read(H/'screen-plan.json')['scenes']};cap=O/'captions.ko.ass';assert cap.exists()
 for scene in plan['scenes']:
  if selected_scenes and scene['id'] not in selected_scenes:continue
  selected();sid=scene['id'];ui=ui_ass(scene,screens[sid]);receipt=E/(sid+'.render.json');clean=E/(sid+'.clean.mp4');captioned=E/(sid+'.captioned.mp4')
  input_files={R/scene['previousFrame']}
  for phase in scene['phases']:
   input_files.add(R/phase['file'])
   if phase.get('background'):input_files.add(R/phase['background'])
   if phase.get('renderer')=='independent-gameplay':input_files.add(E/(phase['beatId']+'.guide.ass'))
   if phase.get('renderer')=='Unity':input_files.add(R/phase['asset']['assFile'])
  sig={'scene':scene,'assetFiles':{rel(path):sha(path) for path in sorted(input_files)},'uiSha256':sha(ui),'captionsSha256':sha(cap),'encoder':ENC,'compositor':sha(Path(__file__))}
  if receipt.exists():
   old=read(receipt)
   if old['inputs']==sig and all(Path(R/f['file']).exists() and sha(R/f['file'])==f['sha256'] for f in old['outputs']):print('Cached scene',sid,flush=True);continue
  args=['ffmpeg','-v','warning','-y','-filter_complex_threads','1'];graph=[];labels=[];idx=0
  for j,p in enumerate(scene['phases']):
   n=p['frames'];label=f'p{j}';file=R/p['file']
   if p['kind']=='still':
    args+=['-loop','1','-framerate','1','-t',str(math.ceil(n/60)+1),'-i',str(file)];graph.append(f'[{idx}:v]fps=60,trim=end_frame={n},settb=1/60,setpts=N,setsar=1,format=yuv420p[{label}]');idx+=1
   elif p['renderer']=='Manim':
    args+=['-loop','1','-framerate','1','-t',str(math.ceil(n/60)+1),'-i',str(R/p['background']),'-i',str(file)]
    graph.append(f'[{idx}:v]fps=60,trim=end_frame={n},settb=1/60,setpts=N,lutrgb=r=val*{WORLD_DIM}:g=val*{WORLD_DIM}:b=val*{WORLD_DIM},format=rgba[bg{j}]');graph.append(f'[{idx+1}:v]trim=end_frame={n},settb=1/60,setpts=N,format=rgba,colorchannelmixer=aa={DIAGRAM_ALPHA}[fg{j}]');graph.append(f'[bg{j}][fg{j}]overlay=shortest=1:format=auto,format=yuv420p,setsar=1[{label}]');idx+=2
   elif p['renderer']=='independent-gameplay':
    guide=E/(p['beatId']+'.guide.ass');assert guide.exists(),'Prepare verified footage guides first'
    args+=['-i',str(file)];graph.append(f'[{idx}:v]trim=end_frame={n},settb=1/60,setpts=N,scale=1472:828:flags=lanczos,pad=1920:1080:224:32:color=0x080b0d,ass={rel(guide)},setsar=1,format=yuv420p[{label}]');idx+=1
   else:
    args+=['-i',str(file)];graph.append(f'[{idx}:v]trim=end_frame={n},settb=1/60,setpts=N,ass={p["asset"]["assFile"]},setsar=1,format=yuv420p[{label}]');idx+=1
   labels.append(f'[{label}]')
  graph.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=0[body]')
  # Blend the first12 frames into the preceding verified state without removing time.
  args+=['-loop','1','-framerate','1','-t','2','-i',str(R/scene['previousFrame'])]
  graph.append(f'[{idx}:v]fps=60,trim=end_frame={scene["frames"]},settb=1/60,setpts=N,format=yuv420p[previous]')
  graph.append("[body][previous]blend=all_expr='A*min(N/12,1)+B*(1-min(N/12,1))':shortest=0:repeatlast=1[continuity]")
  graph.append(f'[continuity]settb=1/60,setpts=N+{scene["startFrame"]},ass={rel(ui)},split=2[cleanin][capin]');graph.append('[cleanin]setpts=PTS-STARTPTS[clean]');graph.append(f'[capin]ass={rel(cap)},setpts=PTS-STARTPTS[captioned]')
  script=E/(sid+'.ffgraph');script.write_text(';\n'.join(graph),encoding='utf8');args+=['-filter_complex_script',str(script)]
  for kind,path in [('clean',clean),('captioned',captioned)]:args+=['-map',f'[{kind}]','-an','-frames:v',str(scene['frames']),'-r','60','-fps_mode','cfr','-enc_time_base','1:60',*ENC,str(path)]
  print('Render complete scene',sid,scene['frames'],'frames',flush=True);run(args,sid+'-encode')
  for path in [clean,captioned]:check(path,scene['frames'])
  save(receipt,{'inputs':sig,'outputs':[{'file':rel(path),'sha256':sha(path)} for path in [clean,captioned]]})
def pair():
 selected();plan=read(E/'scene-plan.json');t=read(H/'timeline.json');audio=O/'final-mix.m4a';assert audio.exists()
 for name,count in [('branding',120),('membership',600)]:
  src=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'/(name+'.mp4');check(src,count)
 for kind in ['clean','captioned']:
  files=[R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/branding.mp4']+[E/(s['id']+'.'+kind+'.mp4') for s in plan['scenes']]+[R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/membership.mp4']
  for s,path in zip(plan['scenes'],files[1:-1]):check(path,s['frames'])
  concat=E/(kind+'.concat.txt');concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in files)+'\n',encoding='utf8');out=O/('euler-'+kind+'.mp4');sig={'files':[(rel(p),sha(p)) for p in files],'audioSha256':sha(audio),'timelineSha256':sha(H/'timeline.json')};receipt=out.with_suffix('.json')
  if receipt.exists() and out.exists() and read(receipt).get('inputs')==sig and read(receipt).get('sha256')==sha(out):print('Cached complete master',kind);continue
  run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','60000','-movflags','+faststart',str(out)],kind+'-mux');check(out,t['totalFrames']);save(receipt,{'inputs':sig,'file':rel(out),'sha256':sha(out)})
def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['plan','scenes','pair']);ap.add_argument('--scene',action='append');args=ap.parse_args()
 if args.stage=='plan':plan_edit()
 elif args.stage=='scenes':render_scenes(args.scene)
 else:pair()
if __name__=='__main__':main()
