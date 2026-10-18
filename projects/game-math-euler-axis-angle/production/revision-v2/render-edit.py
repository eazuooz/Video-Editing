"""Selected FHD60 footage, verified editorial guides, scene assembly and final pair."""
from pathlib import Path
import json,math,subprocess,hashlib,shutil,sys
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v2';E=O/'edit';E.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def current_plan(plan):
 assert plan.get('slug')==P.name and plan.get('timing')=='measured-and-asr-aligned' and plan['fps']==60
 assert plan['actualFrames']*3==plan['explanationFrames']*2 and plan['totalFrames']==plan['bodyFrames']+720
 for path,digest in plan['inputHashes'].items():assert sha(R/path)==digest,('Stale measured timeline input',path)
 for s in plan['scenes']:
  if s['kind']!='actual':continue
  cuts=[c for c in plan['cuts'] if c['scene']==s['id']];cursor=0
  for c in cuts:assert c['startFrame']==cursor and c['globalStartFrame']==s['startFrame']+cursor;curs=c['frames'];cursor+=curs
  assert cursor==s['frames']
def run(cmd,name):
 with (E/(name+'.log')).open('w',encoding='utf8') as f:r=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((E/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3000:])
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(p)]))['streams'][0]
def check(p,n):
 v=probe(p);assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',n),(p,v,n)
def stamp(s):
 h,t=divmod(round(s*100),360000);m,t=divmod(t,6000);sec,cs=divmod(t,100);return f'{h}:{m:02}:{sec:02}.{cs:02}'
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Malgun Gothic,48,&H0057D5F4,&H0057D5F4,&H00101010,&H00101010,-1,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
Style: Credit,Malgun Gothic,26,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
Style: Guide,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H0057D5F4,&H00000000,0,0,0,0,100,100,0,0,1,5,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ENC=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
def interpolate(keys,t):
 if t<keys[0]['sourceTime'] or t>keys[-1]['sourceTime']:return None
 for a,b in zip(keys,keys[1:]):
  if a['sourceTime']<=t<=b['sourceTime']:
   if not(a.get('visible',True) and b.get('visible',True)):return None
   u=(t-a['sourceTime'])/(b['sourceTime']-a['sourceTime']);return {k:[x+(y-x)*u for x,y in zip(a[k],b[k])] for k in ['center','ellipseRadius']}
 return keys[-1]
def ellipse(cx,cy,rx,ry):
 pts=[(cx+rx*math.cos(i*math.tau/48),cy+ry*math.sin(i*math.tau/48)) for i in range(49)]
 return 'm '+' '.join(f'{x:.2f} {y:.2f}' if i==0 else f'l {x:.2f} {y:.2f}' for i,(x,y) in enumerate(pts))
def guide_event(a,b,path,color='57D5F4',layer=2):
 return f'Dialogue: {layer},{stamp(a)},{stamp(b)},Guide,,0,0,0,,{{\\an7\\pos(0,0)\\1a&HFF&\\3c&H{color}&\\p1}}'+path
def cut_ass(c,annotations):
 duration=c['frames']/60;events=[f'Dialogue: 1,0:00:00.00,{stamp(duration)},Credit,,0,0,0,,{{\\pos(40,36)}}Superflight / Morkala · 독립 게임 플레이 발췌']
 marks=[]
 for w in annotations['windows']:
  if w['scene']!=c['scene'] or w['sourceId']!=c['sourceId']:continue
  low=max(w['sourceIn'],c['sourceStart']);high=min(w['sourceOutExclusive'],c['sourceStart']+duration)
  if high<=low:continue
  a,b=low-c['sourceStart'],high-c['sourceStart'];label='몸통·날개옷의 기울기(화면)' if c['scene']!='20' else '화면 속 몸통 중심(근사)'
  events.append(f'Dialogue: 4,{stamp(a)},{stamp(b)},Label,,0,0,0,,{{\\pos(100,130)}}'+label)
  marks.append(dict(sourceIn=low,sourceOutExclusive=high,label=label,keyframeSource='sources/annotation-plan-v2.json',meaning=w['meaning']))
  for f in range(max(0,math.ceil(a*60)),min(c['frames'],math.ceil(b*60))):
   t=c['sourceStart']+f/60;p=interpolate(w['keyframes'],t)
   if not p:continue
   cx,cy=p['center'];rx,ry=p['ellipseRadius'];path=ellipse(cx,cy,rx,ry)
   events.append(guide_event(f/60,(f+1)/60,path))
   if c['scene']=='20':
    events.append(guide_event(f/60,(f+1)/60,ellipse(cx,cy,8,8),'E8A354',3))
    # Past-only screen-space trace through the verified body centers. No
    # inferred world path, forward axis, velocity or magnified movement.
    past=[k['center'] for k in w['keyframes'] if low<=k['sourceTime']<=t]
    past.append([cx,cy])
    if len(past)>1:
     trail='m '+f'{past[0][0]:.2f} {past[0][1]:.2f}'+' '.join(f' l {x:.2f} {y:.2f}' for x,y in past[1:]);events.append(guide_event(f/60,(f+1)/60,trail,'E8A354',3))
  if c['scene']=='20':events.append(f'Dialogue: 4,{stamp(a)},{stamp(b)},Label,,0,0,0,,{{\\pos(100,194)\\1c&HE8A354&}}화면 속 위치 변화 · 월드 경로 아님')
 return HEADER+'\n'.join(events)+'\n',marks
def main():
 selected();plan=read(P/'production/revision-v2/timeline.json');current_plan(plan);stage=sys.argv[1] if len(sys.argv)>1 else 'actual'
 if stage=='actual':
  annotations=read(P/'sources/annotation-plan-v2.json');rendered=[];source_hashes={}
  for c in plan['cuts']:
   if c.get('kind') not in ['actual','independent-gameplay'] and c.get('sourceId') is None:continue
   selected();src=R/c['sourceFile'];v=probe(src);assert v['width']>=1920 and v['height']>=1080 and v['r_frame_rate']=='60/1'
   if c['sourceFile'] not in source_hashes:source_hashes[c['sourceFile']]=sha(src)
   assert source_hashes[c['sourceFile']]==c['sourceSha256'],('Source bytes changed after measured selection',c['sourceId'])
   out=E/(c['id']+'.mp4');ass=E/(c['id']+'.ass');receipt=E/(c['id']+'.json');body,marks=cut_ass(c,annotations);ass.write_text(body,encoding='utf8')
   vf='fps=60,setsar=1,ass='+ass.relative_to(R).as_posix()
   sig=dict(sourceSha256=source_hashes[c['sourceFile']],sourceStart=c['sourceStart'],frames=c['frames'],assSha256=sha(ass),videoFilter=vf,codec=ENC,nativeSpeed=1,upscale=False)
   if not(out.exists() and receipt.exists() and read(receipt)==sig):
    run(['ffmpeg','-hide_banner','-y','-loglevel','warning','-ss',str(c['sourceStart']),'-i',str(src),'-an','-vf',vf,'-frames:v',str(c['frames']),*ENC,str(out)],c['id']);receipt.write_text(json.dumps(sig,indent=2)+'\n')
   check(out,c['frames']);rendered.append(dict(**c,file=out.relative_to(R).as_posix(),marks=marks));print('Rendered',c['id'],flush=True)
  (O/'actual-render-report.json').write_text(json.dumps(dict(cuts=rendered,movingPixelReview='pending',annotationInterpolation='manual verified half-second keyframes; clear at each source cut/visibility interval',classification='actual',nativeSpeed=1),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 elif stage=='assemble':
  files=[]
  for name,count in [('branding',120),('membership',600)]:
   src=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'/(name+'.mp4');check(src,count);shutil.copy2(src,E/(name+'.mp4'))
  files.append(E/'branding.mp4')
  for s in plan['scenes']:
   if s['kind']=='actual':
    cuts=[c for c in plan['cuts'] if c['scene']==s['id']];assert sum(c['frames'] for c in cuts)==s['frames']
    for c in cuts:
     f=E/(c['id']+'.mp4');check(f,c['frames']);receipt=read(E/(c['id']+'.json'))
     assert receipt['sourceSha256']==c['sourceSha256'] and receipt['sourceStart']==c['sourceStart'] and receipt['frames']==c['frames'],'Stale actual clip; render current actual stage'
     files.append(f)
   else:
    f=O/'spatial'/(s['id']+'.mp4') if s['id'] in ['03','04','06','07','09','10','12','16','18','19','21','22'] else O/'flat'/(s['id']+'.mp4')
    check(f,s['frames']);files.append(f)
  files.append(E/'membership.mp4');(E/'concat.txt').write_text('\n'.join("file '"+f.as_posix()+"'" for f in files)+'\n',encoding='utf8')
  (O/'assembly-inputs.json').write_text(json.dumps(dict(timelineSha256=sha(P/'production/revision-v2/timeline.json'),concatSha256=sha(E/'concat.txt'),files=[dict(file=f.relative_to(R).as_posix(),sha256=sha(f)) for f in files]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 elif stage=='pair':
  assembly=read(O/'assembly-inputs.json');assert assembly['timelineSha256']==sha(P/'production/revision-v2/timeline.json') and assembly['concatSha256']==sha(E/'concat.txt'),'Reassemble current timeline before pair'
  for f in assembly['files']:assert sha(R/f['file'])==f['sha256'],('Scene bytes changed after assembly',f['file'])
  layout=read(O/'caption-layout.json');assert layout['timelineSha256']==assembly['timelineSha256'] and layout['koSrtSha256']==sha(O/'captions.ko.srt') and layout['enSrtSha256']==sha(O/'captions.en.srt'),'Prepare current captions before pair'
  mix=O/'final-mix.wav';aac=O/'final-mix.m4a';receipt=O/'aac-source.json';sig=dict(sha256=sha(mix),rate=48000,bitrate='192k')
  audio_build=read(O/'audio-build.json');assert audio_build['timelineSha256']==assembly['timelineSha256'],'Stale mixed audio; rebuild current measured mix'
  assert next(v for v in audio_build['outputs'] if v['file']==mix.relative_to(R).as_posix())['sha256']==sig['sha256'],'Mixed WAV changed after audio report'
  if not(aac.exists() and receipt.exists() and read(receipt)==sig):run(['ffmpeg','-hide_banner','-y','-i',str(mix),'-c:a','aac','-b:a','192k','-ar','48000',str(aac)],'audio-encode');receipt.write_text(json.dumps(sig)+'\n')
  graph='[0:v]settb=expr=1/60,setpts=N,setsar=1,split=2[clean][capin];[capin]ass='+(O/'captions.ko.ass').relative_to(R).as_posix()+'[captioned]'
  pair_inputs=dict(timelineSha256=assembly['timelineSha256'],assemblySha256=sha(O/'assembly-inputs.json'),captionAssSha256=sha(O/'captions.ko.ass'),aacSha256=sha(aac),filterGraph=graph,codec=ENC)
  pair_receipt=O/'pair-source.json'
  if pair_receipt.exists() and read(pair_receipt).get('inputs')==pair_inputs:
   old=read(pair_receipt)
   if all((O/f'euler-{kind}.mp4').exists() and sha(O/f'euler-{kind}.mp4')==old['outputs'][kind]['sha256'] for kind in ['clean','captioned']):
    for kind in ['clean','captioned']:check(O/f'euler-{kind}.mp4',plan['totalFrames'])
    print('Reusing current clean/captioned pair');return
  args=['ffmpeg','-hide_banner','-y','-reinit_filter','0','-f','concat','-safe','0','-i',str(E/'concat.txt'),'-i',str(aac),'-filter_complex',graph]
  for kind in ['clean','captioned']:args+=['-map',f'[{kind}]','-map','1:a','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),'-r','60','-fps_mode','cfr','-enc_time_base','1:60',*ENC,'-c:a','copy','-movflags','+faststart',str(O/f'euler-{kind}.mp4')]
  run(args,'pair-encode')
  for kind in ['clean','captioned']:check(O/f'euler-{kind}.mp4',plan['totalFrames'])
  pair_receipt.write_text(json.dumps(dict(inputs=pair_inputs,outputs={kind:dict(file=(O/f'euler-{kind}.mp4').relative_to(R).as_posix(),sha256=sha(O/f'euler-{kind}.mp4')) for kind in ['clean','captioned']}),indent=2)+'\n',encoding='utf8')
 else:raise ValueError(stage)
if __name__=='__main__':main()
