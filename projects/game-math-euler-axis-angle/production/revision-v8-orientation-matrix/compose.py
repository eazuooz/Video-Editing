"""Finite paragraph composition with shared decode and two native FHD outputs."""
from pathlib import Path
import importlib.util, argparse, json, hashlib, subprocess, time
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_compose_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
old=c.module('v8_finite_pane_renderer',c.P/'production/revision-v7-part1/compose.py')
E=c.O/'edit';E.mkdir(parents=True,exist_ok=True);old.E=E;old.O=c.O;old.H=H
spec=c.module('v8_ui_spec',H/'board-specs.py')
FONT='C:/Windows/Fonts/malgun.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf'

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def check(p,frames):return old.check_video(p,frames)
def backdrop(p):
 path=E/'ui'/(p['id']+'.png');path.parent.mkdir(exist_ok=True)
 im=Image.new('RGB',(1920,1080),'black');d=ImageDraw.Draw(im);term=list(spec.TERMS[p['sceneId']])
 if p['sceneId']=='m07' and p['line']<4:term=['Unit-vector projection','단위벡터의 성분','한 축이 다른 축을 얼마나 향하는가']
 if p['sceneId']=='m12' and p['line']<4:term=['Rotation vs. deformation','회전과 다른 변형 구분','길이와 직각 관계부터 확인']
 for text,y,size,color,font in [(term[0],10,32,'#b8b8b8',FONT),(term[1],49,46,'#e8cf83',BOLD),(term[2],112,32,'#f5f5f5',FONT)]:
  f=ImageFont.truetype(font,size);assert d.textlength(text,font=f)<=1020,(p['id'],text);d.text((40,y),text,font=f,fill=color)
 if p['layout']=='game-model':
  d.text((1080,32),'현재 그림 · 실제 녹화 + 설명 모형',font=ImageFont.truetype(FONT,32),fill='#b8b8b8')
  d.text((40,195),'젤다의 전설 티어스 오브 더 킹덤',font=ImageFont.truetype(BOLD,32),fill='#f5f5f5')
  d.text((1080,158),'위치와 자세를 따로 바꾸기',font=ImageFont.truetype(BOLD,36),fill='#73c7c2')
  d.text((1080,824),'직접 만든 모형 · 게임 내부 수치 아님',font=ImageFont.truetype(FONT,28),fill='#b8b8b8')
 else:
  d.text((1080,32),'현재 그림 · 직접 구현한 모형과 계산',font=ImageFont.truetype(FONT,32),fill='#b8b8b8')
  d.text((1080,89),'가로 벡터 약속 · 변환 방향 확인',font=ImageFont.truetype(FONT,32),fill='#b8b8b8')
  d.line((1060,180,1060,880),fill='#383838',width=2)
 im.save(path);return path

def gpu_guard(codec):
 c.authorized()
 if codec!='h264_nvenc':return
 lease=c.R/'shared/output/GPU_HANDOFF.json'
 assert lease.exists(),'Acquire a finite render lease before GPU encoding'
 data=c.read(lease);assert data.get('owner')=='game-math-orientation-matrix-v8-render',data

def render(p,codec):
 gpu_guard(codec);capmanifest=c.read(H/'captions-manifest.json');caption=capmanifest['paragraphASS'][p['id']];ass=c.R/caption['file']
 assert capmanifest['inputs']['timeline']['sha256']==c.sha(H/'timeline.json')
 assert capmanifest['inputs']['alignment']['sha256']==c.sha(c.O/'audio/source-alignment.json')
 assert (caption['startFrame'],caption['endFrame'])==(p['startFrame'],p['endFrame']) and c.sha(ass)==caption['sha256']
 ui=backdrop(p);old.validate_segments(p['left'],p);old.validate_segments(p['right'],p)
 marks=c.read(H/'annotations-manifest.json');mark=marks['paragraphASS'][p['id']];annotation=c.R/mark['file']
 assert marks['inputs']['editPlan']['sha256']==c.sha(H/'edit-plan.json')
 assert (mark['startFrame'],mark['endFrame'])==(p['startFrame'],p['endFrame']) and c.sha(annotation)==mark['sha256']
 sig=dict(paragraph=p,media=old.segment_media(p['left']+p['right']),ui=c.sha(ui),captions=c.sha(ass),annotations=c.sha(annotation),source=c.sha(Path(__file__)),legacyPaneImplementation=c.sha(c.P/'production/revision-v7-part1/compose.py'),codec=codec)
 key=digest(sig)[:12];folder=E/'paragraphs'/p['id'];folder.mkdir(parents=True,exist_ok=True)
 clean=folder/(key+'.clean.mp4');burned=folder/(key+'.captioned.mp4');receipt=folder/(key+'.json')
 if receipt.exists():
  oldr=c.read(receipt);assert oldr['inputs']==sig
  for r in oldr['outputs']:assert c.sha(c.R/r['file'])==r['sha256'];check(c.R/r['file'],p['frames'])
  print('Reused',p['id'],flush=True);return oldr
 assert not clean.exists() and not burned.exists(),'Inspect incomplete same-signature outputs before retry'
 args=['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-filter_complex_threads','2','-framerate','60','-threads','1','-i',str(ui)]
 filters=[f'[0:v]loop=loop=-1:size=1:start=0,trim=end_frame={p["frames"]},setpts=N/(60*TB),setsar=1[base]']
 leftrect,rightrect=([40,250,1000,562],[1080,220,800,560])if p['layout']=='game-model'else([40,180,1000,700],[1080,180,800,700])
 i,left=old.assemble_pane(p['left'],args,filters,1,'l',tuple(leftrect[2:]));i,right=old.assemble_pane(p['right'],args,filters,i,'r',tuple(rightrect[2:]))
 filters.extend([f'[base][{left}]overlay={leftrect[0]}:{leftrect[1]}:shortest=1:eof_action=endall[left]',f'[left][{right}]overlay={rightrect[0]}:{rightrect[1]}:shortest=1:eof_action=endall[pair]',f'[pair]ass={old.ffescape(annotation)},format=yuv420p,split=2[clean][forcap]',f'[forcap]ass={old.ffescape(ass)}[captioned]'])
 graph=folder/(key+'.filter.txt');graph.write_text(';\n'.join(filters),encoding='utf8');args+=['-/filter_complex',str(graph)]
 for label,dst in [('clean',clean),('captioned',burned)]:args+=['-map',f'[{label}]','-an','-frames:v',str(p['frames']),'-r','60','-fps_mode','cfr',*old.encoder(codec),str(dst)]
 start=time.time();old.run(args,folder/(key+'.log'));outputs=[]
 for kind,file in [('clean',clean),('captioned',burned)]:outputs.append(dict(kind=kind,file=c.rel(file),sha256=c.sha(file),probe=check(file,p['frames'])))
 result=dict(id=p['id'],frames=p['frames'],inputs=sig,outputs=outputs,elapsedSeconds=time.time()-start);c.save(receipt,result);print('Rendered',p['id'],p['frames'],'frames',flush=True);return result

def join(codec):
 c.authorized();plan=c.read(H/'edit-plan.json');timeline=c.read(H/'timeline.json');rows=[]
 for p in plan['paragraphs']:rows.append(render(p,codec))
 intro=c.R/timeline['branding']['intro']['file'];outro=c.R/timeline['branding']['membership']['file'];check(intro,120);check(outro,600);versions=[]
 for kind in ['clean','captioned']:
  files=[intro,*[c.R/next(o['file']for o in row['outputs']if o['kind']==kind)for row in rows],outro]
  listing=E/(kind+'-concat.txt');listing.write_text('\n'.join("file '"+str(f.resolve()).replace('\\','/')+"'"for f in files)+'\n',encoding='utf8')
  file=E/(kind+'-visual.mp4');log=E/(kind+'-concat.log')
  old.run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','60000','-movflags','+faststart',str(file)],log)
  check(file,timeline['totalFrames']);versions.append(dict(kind=kind,file=c.rel(file),sha256=c.sha(file)))
 c.save(E/'visual-build.json',dict(timelineSha256=c.sha(H/'timeline.json'),editPlanSha256=c.sha(H/'edit-plan.json'),paragraphs=rows,versions=versions,frames=timeline['totalFrames'],humanReview='pending'))

def finish():
 c.authorized();t=c.read(H/'timeline.json');audio=c.O/'mix/final-mix.m4a';assert audio.exists();records=[]
 for kind in ['clean','captioned']:
  visual=E/(kind+'-visual.mp4');check(visual,t['totalFrames']);dst=c.O/('orientation-matrix.'+kind+'.mp4')
  old.run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','60000','-t',f'{t["duration"]:.9f}','-movflags','+faststart',str(dst)],E/(kind+'-mux.log'))
  check(dst,t['totalFrames']);records.append(dict(kind=kind,file=c.rel(dst),sha256=c.sha(dst),bytes=dst.stat().st_size))
 c.save(E/'master-build.json',dict(outputs=records,timelineSha256=c.sha(H/'timeline.json'),mixSha256=c.sha(audio),frames=t['totalFrames'],duration=t['duration'],width=1920,height=1080,fps=60,encodedAacCopied=True,humanFinalReview='pending'))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--paragraph');ap.add_argument('--all',action='store_true');ap.add_argument('--finish',action='store_true');ap.add_argument('--codec',default='libx264',choices=['libx264','h264_nvenc']);a=ap.parse_args()
 if a.paragraph:render(next(p for p in c.read(H/'edit-plan.json')['paragraphs']if p['id']==a.paragraph),a.codec)
 elif a.all:join(a.codec)
 elif a.finish:finish()
