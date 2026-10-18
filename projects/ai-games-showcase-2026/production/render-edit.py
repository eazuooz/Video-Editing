"""Render inspected sources at native speed, exact slides, original brand/member."""
from pathlib import Path
import json,subprocess,hashlib,shutil,sys
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';O=P/'production/local/compact-edit'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def run(cmd,name):
 with (O/(name+'.log')).open('w',encoding='utf8') as f:r=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((O/(name+'.log')).read_text(encoding='utf8',errors='replace')[-2500:])
def stamp(s):
 h,s=divmod(s,3600);m,s=divmod(s,60);return f'{int(h)}:{int(m):02d}:{s:05.2f}'
def frames(p):
 v=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(p)]))['streams'][0]
 assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1'),v
 return int(v['nb_frames'])
enc=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Name,Malgun Gothic,34,&H0083CFE8,&H0083CFE8,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Credit,Malgun Gothic,26,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Note,Malgun Gothic,40,&H00FFFFFF,&H00FFFFFF,&H00151F1B,&H00151F1B,-1,0,0,0,100,100,0,0,3,10,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
selected();plan=read(P/'production/edit-plan.json');assert plan['timing']=='measured-and-asr-aligned'
stage=sys.argv[1] if len(sys.argv)>1 else 'cuts'
if stage=='cuts':
 for c in plan['cuts']:
  selected();src=R/c['sourceFile'];out=O/(c['id']+'.mp4');receipt=O/(c['id']+'.json');duration=c['frames']/60;ass=O/(c['id']+'.ass');events=[]
  if c['kind']!='tool-summary':
   scene=next(s for s in plan['scenes'] if s['id']==c['scene']);title=scene['title'] if scene['game'] else '얌얌코딩 · AI 게임 제작 근황'
   events+=[f'Dialogue: 1,0:00:00.00,{stamp(duration)},Name,,0,0,0,,{{\\pos(64,1018)}}'+title,f'Dialogue: 1,0:00:00.00,{stamp(duration)},Credit,,0,0,0,,{{\\an3\\pos(1856,1058)}}'+('게임·자료: '+c['credit'] if c['credit'] else '게임별 제작자 자료 · 출처는 설명란')]
   if c.get('note'):events.append(f'Dialogue: 1,0:00:00.00,{stamp(duration)},Note,,0,0,0,,{{\\an2\\pos(960,1058)}}'+c['note'].replace('제작자 공개 · ',''))
  ass.write_text(header+'\n'.join(events)+'\n',encoding='utf8')
  movie=src.suffix=='.mp4';vf='fps=60,setsar=1'
  if c['kind']!='tool-summary':vf+=',scale=1536:864:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:black'
  if 'augury-preview-1080' in src.name and c['scene']=='06':vf+=",drawbox=x=966:y=506:w=143:h=290:color=0x70D69F:t=6:enable='gte(t,0.35)'"
  vf+=',ass='+ass.relative_to(R).as_posix()
  sig={'sourceSha256':sha(src),'assSha256':sha(ass),'frames':c['frames'],'sourceStart':c['sourceStart'],'filter':vf,'codec':enc}
  if not(out.exists() and receipt.exists() and read(receipt)==sig):
   args=['ffmpeg','-hide_banner','-y','-loglevel','warning']
   args+=['-ss',str(c['sourceStart']),'-i',str(src)] if movie else ['-loop','1','-framerate','60','-i',str(src)]
   args+=['-an','-vf',vf,'-frames:v',str(c['frames']),*enc,str(out)];run(args,c['id']);receipt.write_text(json.dumps(sig,indent=2)+'\n')
  assert frames(out)==c['frames'];print('Rendered',c['id'],flush=True)
 for name,count in [('branding',120),('membership',600)]:
  src=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'/(name+'.mp4');assert frames(src)==count;shutil.copy2(src,O/(name+'.mp4'))
 files=[O/'branding.mp4',*[O/(c['id']+'.mp4') for c in plan['cuts']],O/'membership.mp4'];(O/'concat.txt').write_text('\n'.join("file '"+p.as_posix()+"'" for p in files)+'\n',encoding='utf8')
elif stage=='pair':
 selected();mix=O/'final-mix.wav';aac=O/'final-mix.m4a';sig=sha(mix);receipt=O/'aac-source.json'
 if not(aac.exists() and receipt.exists() and read(receipt).get('sha256')==sig):
  run(['ffmpeg','-hide_banner','-y','-i',str(mix),'-c:a','aac','-b:a','192k','-ar','48000',str(aac)],'audio-encode');receipt.write_text(json.dumps({'sha256':sig})+'\n')
 graph='[0:v]fps=60,setsar=1,split=2[clean][capin];[capin]ass='+(O/'captions.ko.ass').relative_to(R).as_posix()+'[captioned]'
 args=['ffmpeg','-hide_banner','-y','-f','concat','-safe','0','-i',str(O/'concat.txt'),'-i',str(aac),'-filter_complex',graph]
 for kind in ['clean','captioned']:args+=['-map',f'[{kind}]','-map','1:a','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),*enc,'-c:a','copy','-movflags','+faststart',str(O/f'ai-games-{kind}.mp4')]
 run(args,'pair-encode')
 for kind in ['clean','captioned']:assert frames(O/f'ai-games-{kind}.mp4')==plan['totalFrames']
else:raise ValueError(stage)
