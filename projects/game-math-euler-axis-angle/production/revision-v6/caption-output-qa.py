"""Read-only QA of the current V6 encoded caption pixels, not audio/listening QA.

One source decode pass extracts selected caption ROIs and representative native
frames together. A sparse ffconcat of one black image renders the same ASS at
the selected global PTS, without rendering an hour of black video. No PyAV or
new dependency is needed. Run only after the complete current master is ready.
"""
from pathlib import Path
from fractions import Fraction
import argparse, bisect, hashlib, json, math, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6'
Q=O/'qa/encoded-captions'
FONT=Path('C:/Windows/Fonts/malgun.ttf')
FPS=60;Y0=880;HEIGHT=200

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def proof(p):return {'file':rel(p),'sha256':sha(p)}
def run(args,log):
 cp=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(cp.stderr,encoding='utf-8')
 if cp.returncode:raise RuntimeError(f'{args[0]} failed; see {rel(log)}\n'+cp.stderr[-1800:])
 return cp
def clock_cs(t):return round(t*100)
def stamp(t):
 v=clock_cs(t);h,v=divmod(v,360000);m,v=divmod(v,6000);s,cs=divmod(v,100)
 return f'{h}:{m:02}:{s:02}.{cs:02}'
def parse_time(s):
 h,m,sec=re.split('[:,.]',s)[:3];fraction=re.split('[:,.]',s)[3]
 return int(h)*3600+int(m)*60+int(sec)+int(fraction)/(10**len(fraction))
def srt_rows(p):
 blocks=re.split(r'\n\s*\n',p.read_text(encoding='utf-8-sig').replace('\r','').strip());out=[]
 for i,block in enumerate(blocks,1):
  lines=block.split('\n');assert int(lines[0])==i
  a,b=lines[1].split(' --> ');out.append({'start':parse_time(a),'end':parse_time(b),'lines':lines[2:]})
 return out
def ass_rows(p):
 out=[]
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if not line.startswith('Dialogue: '):continue
  fields=line[len('Dialogue: '):].split(',',9)
  assert len(fields)==10
  layer,a,b,style=fields[:4]
  if style!='Text':continue
  text=re.sub(r'\{[^}]*\}','',fields[9]).replace(r'\N','\n')
  out.append({'start':a,'end':b,'text':text,'layer':int(layer)})
 return out
def luminance(rgb):
 v=np.asarray(rgb,dtype=float)/255
 v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
 return float(v@[.2126,.7152,.0722])
def contrast(color):
 rgb=[int(color[i:i+2],16) for i in (1,3,5)]
 return 1.05/(luminance(rgb)+.05)

def input_contract(timeline,sceneplan,captions,layout,ass,srt):
 assert timeline['revision']=='article-flow-v6' and timeline['slug']==P.name
 assert timeline['fps']==60 and timeline['width']==1920 and timeline['height']==1080
 assert captions['timelineSha256']==sha(H/'timeline.json')==sceneplan['timelineSha256']==layout['timelineSha256']
 assert captions['sameSemanticBilingualCueTimes'] and captions['captionBox']=='boxed-white-forest-v1'
 assert captions['captionGeometry']['x']==960 and captions['captionGeometry']['y']==970
 assert captions['captionGeometry']['fontSize']==48 and captions['captionGeometry']['maxLines']==2
 cues=captions['cues'];assert len(cues)==captions['cueCount'] and len({c['id'] for c in cues})==len(cues)
 alias_file=H/'caption-aliases.json'
 assert captions['inputs']['canonicalAliasMapSha256']==sha(alias_file),'Canonical alias map differs from final captions'
 width_rows={};source_paragraphs=[];inverse_count=0
 for language in ['ko','en']:
  title=language.title();srts=srt_rows(srt if language=='ko' else O/'captions.en.srt');events=ass_rows(ass if language=='ko' else O/'captions.en.ass')
  assert len(srts)==len(cues)
  geom={x['id']:x for x in layout['rows'][language]};event_index=0;width_rows[language]=[]
  source_file=P/f'script/revision-v6-article-flow/narration.{language}.json';source=read(source_file)
  assert captions['inputs'][language+'Sha256']==sha(source_file),'Current captions must bind the complete approved source'
  ordered_cue_ids=[]
  for scene in source['scenes']:
   for line_number,paragraph in enumerate(scene['lines'],1):
    parts=[c for c in cues if c['scene']==scene['id'] and c['line']==line_number]
    assert parts and all('source'+title in c and 'display'+title in c for c in parts),'Rebuild canonical source/display captions first'
    rebuilt=' '.join(c['source'+title] for c in parts)
    assert rebuilt==paragraph,(scene['id'],line_number,language,'Source paragraph lost/reordered; display aliases are checked separately')
    source_paragraphs.append({'language':language,'scene':scene['id'],'line':line_number,'cueIds':[c['id'] for c in parts],'sourceSha256':hashlib.sha256(paragraph.encode()).hexdigest(),'exactSourceReconstruction':True})
    ordered_cue_ids.extend(c['id'] for c in parts)
  assert ordered_cue_ids==[c['id'] for c in cues],(language,'Cue order/coverage differs from the complete approved source sequence')
  for cue,subtitle in zip(cues,srts):
   lines=cue[language+'Lines'];assert 1<=len(lines)<=2
   assert ' '.join(lines)==cue['display'+title],(cue['id'],language,'Wrapped display differs from canonical display text')
   restored=cue['display'+title]
   for alias in sorted(cue['displayAliases'+title],key=lambda a:a['displayStart'],reverse=True):
    a,b=alias['displayStart'],alias['displayEnd']
    assert restored[a:b]==alias['display'],(cue['id'],language,'Alias display interval differs')
    restored=restored[:a]+alias['spoken']+restored[b:];inverse_count+=1
   assert restored==cue['source'+title],(cue['id'],language,'Canonical alias inverse loses original spoken clause')
   assert subtitle['lines']==lines,(cue['id'],language,'SRT text differs from current displayed lines')
   assert abs(subtitle['start']-cue['start'])<=.00051 and abs(subtitle['end']-cue['end'])<=.00051
   for text in lines:
    event=events[event_index];event_index+=1
    assert (event['start'],event['end'],event['text'])==(stamp(cue['start']),stamp(cue['end']),text),(cue['id'],language,'ASS text/timing differs from current display')
   g=geom[cue['id']];assert max(g['widths'])<=1570+1e-6
   x,y,w,h=g['box'];assert x>=150 and y>=880 and x+w<=1770 and y+h+14<=1060
   assert len(g['widths'])==len(lines)
   width_rows[language].append({'id':cue['id'],'lineWidths':g['widths'],'box':g['box'],'emphasis':g.get('emphasis')})
  assert event_index==len(events),(language,'Unexpected extra ASS caption text')
 assert len(source_paragraphs)==500,'250 approved paragraphs in each language'
 ratios={key:contrast(value) for key,value in captions['palette'].items()}
 assert min(ratios.values())>=4.5,'Semantic text colors need contrast against the white box'
 assert all(contrast(c)>=4.5 for c in ['#080b09'])
 return {'sameKoEnSrtAssCanonicalDisplayedTextAndTiming':True,'all250SourceParagraphsReconstructedInEachLanguage':True,'canonicalAliasMap':proof(alias_file),'canonicalAliasSegmentsExactlyInverted':inverse_count,'sourceCoverageMeaning':'Exact approved script text through sourceKo/sourceEn, separate from canonical displayKo/displayEn; not a fresh ASR or actual-listening claim','sourceParagraphs':source_paragraphs,'allKoEnCueWidthsWithin1570':True,'fixedBox960x970Font48Max2Lines':True,'contrastRatiosAgainstWhite':ratios,'rows':width_rows}

def sample_plan(timeline,sceneplan,captions,layout):
 total=timeline['totalFrames'];tags={};native={}
 def add(frame,tag,full=False):
  frame=max(0,min(total-1,int(frame)));tags.setdefault(frame,[]).append(tag)
  if full:native.setdefault(frame,[]).append(tag)
 def boundary(frame,tag):
  for offset in [-1,0,1]:add(frame+offset,tag+f':{offset:+}')
 cue_mid={}
 for cue in captions['cues']:
  lo=Fraction(clock_cs(cue['start']),100);hi=Fraction(clock_cs(cue['end']),100)
  first=math.ceil(lo*FPS);last=math.ceil(hi*FPS)-1;assert first<=last
  frame=(first+last)//2;cue_mid[cue['id']]=frame;add(frame,'cue:'+cue['id'])
 for scene in timeline['scenes']:
  boundary(scene['startFrame'],'scene-start:'+scene['id']);boundary(scene['endFrame'],'scene-end:'+scene['id'])
 for cut in timeline['cuts']:
  boundary(cut['globalStartFrame'],'game-start:'+cut['id']);boundary(cut['globalStartFrame']+cut['frames'],'game-end:'+cut['id'])
  add(cut['globalStartFrame']+cut['frames']//2,'game-mid:'+cut['id'],True)
  add(cut['globalStartFrame'],'game-entry:'+cut['id'],True)
  add(cut['globalStartFrame']+cut['frames'],'game-exit:'+cut['id'],True)
 for scene in sceneplan['scenes']:
  for phase in scene['phases']:
   boundary(phase['startFrame'],'phase-start:'+scene['id']+':'+phase['kind'])
   boundary(phase['endFrame'],'phase-end:'+scene['id']+':'+phase['kind'])
 add(0,'branding-start');boundary(timeline['temporalContract']['outroStartFrame'],'member-start')
 sizes={x['id']:max(x['widths']) for x in layout['rows']['ko']}
 for cue in sorted(captions['cues'],key=lambda c:sizes[c['id']],reverse=True)[:6]:add(cue_mid[cue['id']],'native-longest:'+cue['id'],True)
 for sid in ['v6-14','v6-25','v6-33','v6-39']:
  choices=[c for c in captions['cues'] if c['scene']==sid]
  cue=max(choices,key=lambda c:sizes[c['id']]);add(cue_mid[cue['id']],'native-math:'+cue['id'],True)
 for line in [3,4,5,6]:
  choices=[c for c in captions['cues'] if c['scene']=='v6-26' and c['line']==line]
  cue=max(choices,key=lambda c:sizes[c['id']]);add(cue_mid[cue['id']],'native-code:'+cue['id'],True)
 return {'totalFrames':total,'cueCount':len(captions['cues']),'samples':[{'frame':f,'seconds':f/FPS,'tags':sorted(set(tags[f])),'nativeTags':sorted(set(native.get(f,[])))} for f in sorted(tags)],'nativeFrames':sorted(native),'sampling':'All cue midpoint frames plus each actual scene/source/phase boundary at-1/0/+1 frame; representative full frames share the same single source decode pass.'}

def extract_actual(master,plan,out,master_sha):
 out.mkdir(parents=True,exist_ok=True);roi=out/'actual';native=out/'native';roi.mkdir(exist_ok=True);native.mkdir(exist_ok=True)
 frames=[x['frame'] for x in plan['samples']];full=plan['nativeFrames']
 signature={'masterSha256':master_sha,'frames':frames,'nativeFrames':full,'roi':[0,Y0,1920,HEIGHT],'format':'RGB PNG','decodePasses':1}
 receipt=out/'actual-extraction.json'
 if receipt.exists():
  old=read(receipt)
  if old['inputs']==signature and all((R/x['file']).exists() and sha(R/x['file'])==x['sha256'] for x in old['files']):return old
  raise AssertionError('Existing extraction differs. Preserve it and select a new --qa-directory; never overwrite/redecode unchanged evidence')
 assert not list(roi.glob('*.png')) and not list(native.glob('*.png')),'Partial source extraction exists without a receipt; preserve it and use a fresh --qa-directory'
 select=lambda values:'+'.join(f'eq(n\\,{f})' for f in values)
 graph=f'[0:v]split=2[r][n];[r]select={select(frames)},crop=1920:200:0:880,format=rgb24[rout];[n]select={select(full)},format=rgb24[nout]'
 graph_path=out/'actual-extraction.ffgraph';graph_path.write_text(graph,encoding='utf-8')
 run(['ffmpeg','-nostdin','-hide_banner','-loglevel','warning','-threads','2','-filter_complex_threads','1','-i',str(master),'-filter_complex_script',str(graph_path),'-map','[rout]','-fps_mode','passthrough','-start_number','0','-frames:v',str(len(frames)),'-compression_level','1',str(roi/'%06d.png'),'-map','[nout]','-fps_mode','passthrough','-start_number','0','-frames:v',str(len(full)),'-compression_level','1',str(native/'%06d.png')],out/'actual-extraction.log')
 files=[]
 for folder,count in [(roi,len(frames)),(native,len(full))]:
  got=sorted(folder.glob('*.png'));assert len(got)==count,(folder,len(got),count)
  files.extend(proof(x) for x in got)
 data={'inputs':signature,'files':files,'frameMapping':dict(roi=frames,native=full),'scope':'One complete source-video decode/split pass; no audio extraction/ASR/render; cropped QA rasters only'};save(receipt,data);return data

def render_expected(ass,frames,out):
 out.mkdir(parents=True,exist_ok=True);folder=out/'expected';folder.mkdir(exist_ok=True)
 expected_filter=f'settb=1/60000,setsar=1,scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,ass={rel(ass)},crop=1920:200:0:880,scale=in_range=tv:out_range=pc:in_color_matrix=bt709,format=rgb24,showinfo'
 signature={'assSha256':sha(ass),'frames':frames,'raster':[1920,1080],'roi':[0,Y0,1920,HEIGHT],'fontSha256':sha(FONT),'captionWorkingFormat':'TV BT709 yuv420p before ASS, full-range RGB PNG after ASS','filter':expected_filter}
 receipt=out/'expected-extraction.json'
 if receipt.exists():
  old=read(receipt)
  if old['inputs']==signature and all((R/x['file']).exists() and sha(R/x['file'])==x['sha256'] for x in old['files']):return old
  raise AssertionError('Expected ASS changed; preserve prior QA directory and use a fresh one')
 assert not list(folder.glob('*.png')),'Partial expected raster extraction exists without a receipt; preserve it and use a fresh --qa-directory'
 black=out/'black.png';Image.new('RGB',(1920,1080),'black').save(black)
 lines=['ffconcat version 1.0']
 for i,frame in enumerate(frames):
  gap=(frames[i+1]-frame) if i+1<len(frames) else 1
  lines += ["file '"+black.resolve().as_posix()+"'",'option framerate 60',f'duration {gap/FPS:.12f}']
 assert frames[0]==0
 concat=out/'expected.ffconcat';concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 log=out/'expected-extraction.log'
 run(['ffmpeg','-nostdin','-hide_banner','-loglevel','info','-threads','1','-filter_threads','1','-copyts','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-vf',expected_filter,'-fps_mode','passthrough','-enc_time_base','1:60000','-frames:v',str(len(frames)),'-start_number','0','-compression_level','1',str(folder/'%06d.png')],log)
 records=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',log.read_text(encoding='utf-8'))
 assert len(records)==len(frames),(len(records),len(frames))
 pts=[int(v) for _,v in records]
 assert pts==[f*1000 for f in frames],('Sparse expected stream lost global PTS',list(zip(frames,pts))[:10])
 files=sorted(folder.glob('*.png'));assert len(files)==len(frames)
 data={'inputs':signature,'files':[proof(x) for x in files],'globalPts':pts,'timeBase':'1/60000','sparseFrameCount':len(frames),'fullBlackVideoRendered':False,'method':'One black PNG reused via ffconcat durations; exact emitted PTS asserted against every requested global frame'};save(receipt,data);return data

def comparison(actual,expected,box):
 x,y,w,h=box;pad=7
 x0=math.ceil(x)+pad;x1=math.floor(x+w)-pad;y0=math.ceil(y)-Y0+pad;y1=math.floor(y+h)-Y0-pad
 assert 0<=x0<x1<=1920 and 0<=y0<y1<=HEIGHT
 a=np.asarray(actual.convert('RGB'),dtype=np.float32)[y0:y1,x0:x1]
 e=np.asarray(expected.convert('RGB'),dtype=np.float32)[y0:y1,x0:x1]
 delta=np.abs(a-e);per=delta.max(axis=2);ink=e.min(axis=2)<205
 mae=float(delta.mean());bad=float(np.mean(per>45));ink_mae=float(delta[ink].mean()) if ink.any() else 0
 tiles=[]
 for top in range(0,a.shape[0],48):
  for left in range(0,a.shape[1],48):
   tile=delta[top:top+48,left:left+48];et=e[top:top+48,left:left+48];at=a[top:top+48,left:left+48]
   if min(tile.shape[:2])>=12 and ((et.min(axis=2)<205).sum()>=12 or (at.min(axis=2)<205).sum()>=12):tiles.append(float(tile.mean()))
 worst=max(tiles,default=0)
 passed=mae<=5.0 and bad<=.012 and ink_mae<=12.0 and worst<=18.0
 return {'pass':passed,'interiorRectInRoi':[x0,y0,x1,y1],'rgbMeanAbsoluteError':round(mae,4),'fractionMaxChannelErrorAbove45':round(bad,6),'expectedInkMeanAbsoluteError':round(ink_mae,4),'worst48pxTextTileMeanAbsoluteError':round(worst,4),'limits':{'rgbMae':5,'badFraction':.012,'inkMae':12,'worst48pxTileMae':18},'note':'Opaque white box interior only; excludes border/shadow and underlying game/Unity pixels. Compression tolerance is not OCR/semantic proof.'}

def unexpected_caption_like_box(image):
 a=np.asarray(image.convert('RGB'))[17:178,150:1770]
 white=(a.min(axis=2)>232)&((a.max(axis=2).astype(int)-a.min(axis=2))<15)
 rows=np.sum(white,axis=1);area=int(white.sum());count=int(np.sum(rows>=150))
 # Protected lower reserve should not contain an opaque white caption box
 # during observation gaps. Ambiguous candidates require manual inspection.
 return {'unexpectedWhiteBoxCandidate':area>=8000 and count>=40,'whitePixels':area,'rowsWithAtLeast150WhitePixels':count,'classification':'caption-like white area; inspect before attributing it to a stale cue'}

def boards(plan,out):
 files=[];font=ImageFont.truetype(str(FONT),19)
 samples={x['frame']:x for x in plan['samples']};frames=plan['nativeFrames']
 for kind,w,h,cols,rows in [('native',960,540,2,3),('mobile',375,211,4,3)]:
  per=cols*rows
  for start in range(0,len(frames),per):
   board=Image.new('RGB',(w*cols,(h+48)*rows),'#151515');draw=ImageDraw.Draw(board)
   for j,frame in enumerate(frames[start:start+per]):
    index=frames.index(frame);src=out/'native'/f'{index:06d}.png';im=Image.open(src).convert('RGB')
    im=im.resize((w,h),Image.Resampling.LANCZOS);x=(j%cols)*w;y=(j//cols)*(h+48)
    board.paste(im,(x,y+48));label=f'f{frame} {frame/FPS:.3f}s '+','.join(samples[frame]['nativeTags'])
    draw.text((x+5,y+4),label[:100 if kind=='native' else 32],font=font,fill='white')
    draw.text((x+5,y+25),'current encoded master; '+('1920px original saved' if kind=='native' else '375px derived from same frame'),font=font,fill='#bbbbbb')
   dest=out/f'{kind}-contact-{start//per:02d}.jpg';board.save(dest,quality=94);files.append(proof(dest))
 return {'boards':files,'nativeFullFrames':[{'frame':f,**proof(out/'native'/f'{i:06d}.png')} for i,f in enumerate(frames)],'mobileDerivedFromSameDecodedNativeFrames':True,'humanPixelReview':'pending actual opening; generation is not viewing'}

def execute(master,out):
 control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
 t=read(H/'timeline.json');s=read(O/'edit/scene-plan.json');c=read(O/'captions/captions.json');layout=read(O/'captions/caption-layout.json');ass=O/'captions.ko.ass';srt=O/'captions.ko.srt'
 assert master.exists() and master.stat().st_size>0
 checked=input_contract(t,s,c,layout,ass,srt);plan=sample_plan(t,s,c,layout)
 stat=(master.stat().st_size,master.stat().st_mtime_ns);master_sha=sha(master)
 probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames,color_range,color_space,color_primaries,color_transfer','-of','json',str(master)],capture_output=True,text=True,check=True)
 v=json.loads(probe.stdout)['streams'][0];assert (v['width'],v['height'],Fraction(v['avg_frame_rate']))==(1920,1080,Fraction(60))
 assert v.get('color_range')=='tv' and v.get('color_space')=='bt709','Expected pixels require the actual TV BT709 master; do not silently substitute a different color conversion'
 assert int(v['nb_frames'])==t['totalFrames'],'Master is partial/stale or has a different timeline'
 inputs={'master':{'file':rel(master),'sha256':master_sha,'bytes':stat[0]},'timeline':proof(H/'timeline.json'),'scenePlan':proof(O/'edit/scene-plan.json'),'captions':proof(O/'captions/captions.json'),'canonicalAliasMap':proof(H/'caption-aliases.json'),'captionLayout':proof(O/'captions/caption-layout.json'),'assKo':proof(ass),'srtKo':proof(srt),'assEn':proof(O/'captions.en.ass'),'srtEn':proof(O/'captions.en.srt'),'sourceKo':proof(P/'script/revision-v6-article-flow/narration.ko.json'),'sourceEn':proof(P/'script/revision-v6-article-flow/narration.en.json'),'implementation':proof(Path(__file__))}
 final=out/'caption-output-review.json'
 if final.exists():
  old=read(final)
  assert old['inputs']==inputs,'Existing QA report belongs to different inputs; preserve it and use a fresh directory'
  print('Cached current encoded-caption QA:',rel(final),old['status']);return
 save(out/'sample-plan.json',plan);save(out/'caption-input-contract.json',{'inputs':inputs,**checked})
 extraction=extract_actual(master,plan,out,master_sha);frames=[x['frame'] for x in plan['samples']];expected=render_expected(ass,frames,out)
 cues=c['cues'];starts=[Fraction(clock_cs(x['start']),100) for x in cues];geom={x['id']:x for x in layout['rows']['ko']}
 results=[];fail=[];body_end=t['temporalContract']['outroStartFrame']
 for index,sample in enumerate(plan['samples']):
  frame=sample['frame'];moment=Fraction(frame,FPS);i=bisect.bisect_right(starts,moment)-1;cue=cues[i] if i>=0 and moment<Fraction(clock_cs(cues[i]['end']),100) else None
  actual=Image.open(out/'actual'/f'{index:06d}.png');reference=Image.open(out/'expected'/f'{index:06d}.png')
  if cue:
   detail=comparison(actual,reference,geom[cue['id']]['box']);passed=detail['pass'];kind='expected-caption'
  elif 120<=frame<body_end:
   detail=unexpected_caption_like_box(actual);passed=not detail['unexpectedWhiteBoxCandidate'];kind='expected-no-caption'
  else:detail={'excluded':'original branding/member identity; no lecture caption expected'};passed=True;kind='preserved-branding-or-members'
  row={'frame':frame,'seconds':float(moment),'tags':sample['tags'],'expectedCueId':cue['id'] if cue else None,'kind':kind,'pass':passed,'metrics':detail,'actualRoi':rel(out/'actual'/f'{index:06d}.png'),'expectedRoi':rel(out/'expected'/f'{index:06d}.png')};results.append(row)
  if not passed:fail.append(row)
 assert stat==(master.stat().st_size,master.stat().st_mtime_ns),'Master changed during extraction; discard pass status'
 contacts=boards(plan,out)
 report={'schemaVersion':1,'revision':'article-flow-v6','inputs':inputs,'status':'pass within automated caption-pixel and exact current-input coverage scope' if not fail else 'fail: inspect missing/stale/mismatched caption candidates before approval','captionCueCount':len(cues),'sampleCount':len(frames),'failureCount':len(fail),'scope':{'everyKoCueMidpoint':True,'everySceneAndPhaseCutAtMinusOneZeroPlusOne':True,'sourceMasterDecodePasses':1,'expectedSparseGlobalPtsVerified':True,'actualRoi':[0,Y0,1920,HEIGHT],'comparison':'Expected current ASS over black vs opaque encoded caption box interior; no invented OCR result','fullFrameHumanReview':False,'humanWholeListening':'pending','realTimeMotionReview':'pending'},'inputCoverage':proof(out/'caption-input-contract.json'),'actualExtraction':proof(out/'actual-extraction.json'),'expectedExtraction':proof(out/'expected-extraction.json'),'samples':results,'failures':fail,'contacts':contacts,'notPassedByThisTool':['Semantic correctness of every translated clause','Narration pronunciation and natural pace','Whole-video human listening','Every moving guide/spatial frame','User review or YouTube approval']}
 save(final,report);print('Encoded caption samples',len(frames),'failures',len(fail),rel(final))
 if fail:raise SystemExit(2)

def self_test():
 out=Q/'self-test-v4';out.mkdir(parents=True,exist_ok=True)
 header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Text,Malgun Gothic,48,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,3,10,0,5,0,0,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 ass=out/'probe.ass';ass.write_text(header+r'Dialogue: 0,0:00:01.00,0:00:03.00,Text,,0,0,0,,{\an5\pos(960,970)}TEST X θ'+ '\n',encoding='utf-8')
 frames=[0,90,123,240,600];receipt=render_expected(ass,frames,out)
 assert receipt['globalPts']==[0,90000,123000,240000,600000]
 images=[Image.open(out/'expected'/f'{i:06d}.png').convert('RGB') for i in range(5)]
 assert np.asarray(images[0]).max()==0 and np.asarray(images[3]).max()==0 and np.asarray(images[4]).max()==0
 assert np.asarray(images[1]).max()>240 and np.asarray(images[2]).max()>240
 box=[700,920,520,100]
 assert comparison(images[1],images[1],box)['pass']
 assert not comparison(Image.new('RGB',(1920,200),'black'),images[1],box)['pass']
 modified=images[1].copy();ImageDraw.Draw(modified).rectangle((900,70,950,120),fill='white')
 assert not comparison(modified,images[1],box)['pass'],'Changed/missing text tile should fail'
 save(out/'self-test.json',{'scope':'Tiny synthetic sparse-PTS black-frame test only; no project master read/decode','implementationSha256':sha(Path(__file__)),'arbitraryGlobalPtsPreserved':True,'onlyFiveExpectedFramesRendered':True,'samePixelsPass':True,'missingCaptionFails':True,'changedGlyphTileFails':True,'pyAvNeeded':False,'newSoftwareInstalled':False})
 print('PASS sparse globalPTS/opaque-pixel synthetic test',rel(out/'self-test.json'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--master',type=Path,default=O/'euler-captioned.mp4');ap.add_argument('--qa-directory',type=Path,default=Q);ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:self_test()
 else:execute(args.master,args.qa_directory)

if __name__=='__main__':main()
