"""Visual-only v2: preserve v1, insert native FHD gameplay at existing speech cues."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, shutil, math, argparse
from PIL import Image, ImageDraw

P=Path(__file__).resolve().parents[1]; R=P.parents[1]
L=P/'production/local/gameplay-v2'; O=P/'production/local/final-gameplay-v2'
OLD=P/'production/local/final-reviewed'; A=P/'production/local/audio'
SOURCE=L/'l4d2-swamp-526-556.mp4'
REV='flow-map-gameplay-v2'; N=3067; D=N/60
CUTS=[dict(startFrame=1526,endFrame=1812,sourceStart=529.5),dict(startFrame=2836,endFrame=3067,sourceStart=542.5)]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).relative_to(R).as_posix()
def run(cmd):
 r=subprocess.run(cmd,cwd=R,capture_output=True)
 if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace')[-4500:])
 return r.stdout
def guard():
 c=read(R/'shared/publishing/video-production-control.json'); cp=read(P/'production/checkpoint.json')
 assert c['selectedShortVideo']==P.name and c['automaticNextVideoEnabled'] is False
 assert cp['revision']==REV and cp['revisionAuthorization']['priorVideoId']=='9cRdnf8wKEI'
 assert sha(OLD/'captioned.mp4')==cp['revisionAuthorization']['priorMasterSha256']
 assert '다시 업로드' in cp['revisionAuthorization']['userEvidence']
def stamp(t):
 cs=round(t*100); return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
def build():
 guard(); O.mkdir(exist_ok=True)
 assert not (O/'clean.mp4').exists() and not (O/'captioned.mp4').exists()
 info=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(SOURCE)]))
 v=next(x for x in info['streams'] if x['codec_type']=='video')
 assert v['width']>=1920 and v['height']>=1080
 header=(P/'production/header.ass').read_text(encoding='utf-8').split('[Events]')[0]
 ass=header+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 for cut in CUTS:
  a,b=cut['startFrame']/60,cut['endFrame']/60
  def line(text,layer=0):
   nonlocal ass
   ass+=f'Dialogue: {layer},{stamp(a)},{stamp(b)},Header,,0,0,0,,{text}\n'
  line(r'{\pos(840,480)\fs34\b0\c&H00BCC3B8&}실제 게임 화면')
  line(r'{\pos(520,572)\fs43\c&H005AD2FF&}레프트 4 데드 2')
  line(r'{\pos(400,1240)\fs39\c&H00CDD773&}물 표면의 움직이는 무늬')
  # Editorial open contour around a water region, not a measured flow vector.
  # Source region x≈300..800,y≈600..840 remains water in reviewed frames.
  if cut['startFrame']==1526: a,b=27.4,30.1
  else: a,b=47.7,49.1
  line(r'{\an7\pos(0,0)\p1\bord6\shad0\1a&HFF&\3c&H00CDD773&\fad(180,100)}m 218 982 b 208 947 247 931 306 931 b 374 930 429 955 420 989 b 415 1015 360 1031 299 1028 b 259 1027 237 1018 225 1008{\p0}',1)
 (O/'gameplay-labels.ass').write_text(ass,encoding='utf-8')
 fixed_header=(P/'production/header.ass').read_text(encoding='utf-8')
 fixed_header='\n'.join(s for s in fixed_header.splitlines() if '우리 Unity 구현' not in s)+'\n'
 for a,b in [(0,1526/60),(1812/60,2836/60)]:
  fixed_header+=f'Dialogue: 0,{stamp(a)},{stamp(b)},Header,,0,0,0,,'+r'{\pos(840,480)\fs34\b0\c&H00BCC3B8&}우리 Unity 구현'+'\n'
 (O/'fixed-header.ass').write_text(fixed_header,encoding='utf-8')
 # Source, master, captions and narration remain intact. FHD aspect stays16:9.
 filters=[]; enables=[]
 for i,c in enumerate(CUTS):
  a,b=c['startFrame']/60,c['endFrame']/60; d=b-a; ss=c['sourceStart']-526
  enables.append(f'gte(t,{a})*lt(t,{b})')
  filters.append(f'[1:v]trim=start={ss}:duration={d},setpts=PTS-STARTPTS,fps=60,scale=1040:585:flags=lanczos,setsar=1,setpts=PTS+{a}/TB[g{i}]')
  filters.append(f'[1:a]atrim=start={ss}:duration={d},asetpts=PTS-STARTPTS,volume=0.035,afade=t=in:d=0.12,afade=t=out:st={d-.12}:d=0.12,adelay={round(a*1000)}:all=1[a{i}]')
 enable='+'.join(enables)
 filters.append(f"[0:v]drawbox=x=0:y=420:w=1080:h=1160:color=black:t=fill:enable='{enable}'[base]")
 filters.append(f"[base][g0]overlay=20:630:eof_action=pass:enable='{enables[0]}'[first]")
 filters.append(f"[first][g1]overlay=20:630:eof_action=pass:enable='{enables[1]}'[second]")
 # Restore the brand reaction at the closing cue; retain a clear left water area.
 filters.append('[2:v]scale=780:780,format=rgba,fade=t=in:st=48.766667:d=0.12:alpha=1[cat]')
 filters.append("[second][cat]overlay=x='510+40*max(0,1-(t-48.766667)/0.12)':y='980-5*sin(min(1,max(0,(t-48.886667)/0.36))*PI)':enable='gte(t,48.766667)'[withcat]")
 filters.append('[withcat]drawbox=x=0:y=0:w=1080:h=540:color=black:t=fill,ass='+rel(O/'fixed-header.ass')+',ass='+rel(O/'gameplay-labels.ass')+'[v]')
 filters.append('[0:a][a0][a1]amix=inputs=3:duration=first:normalize=0[a]')
 filter_path=O/'composition.ffmpeg';filter_path.write_text(';\n'.join(filters),encoding='utf-8')
 run(['ffmpeg','-v','error','-n','-filter_complex_threads','3','-i',str(OLD/'clean.mp4'),'-i',str(SOURCE),'-loop','1','-framerate','60','-i',str(R/'shared/assets/branding/cat-reactions-v1/relief.png'),'-/filter_complex',str(filter_path),'-map','[v]','-map','[a]','-frames:v',str(N),'-t',str(D),'-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(O/'clean.mp4')])
 run(['ffmpeg','-v','error','-n','-i',str(O/'clean.mp4'),'-vf','ass='+rel(A/'captions.ko.ass'),'-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(O/'captioned.mp4')])
 run(['ffmpeg','-v','error','-n','-i',str(O/'clean.mp4'),'-vn','-c:a','copy',str(O/'final-mix.m4a')])
 save(O/'build.json',dict(revision=REV,frames=N,duration=D,cuts=CUTS,source=rel(SOURCE),sourceSha256=sha(SOURCE),sourceProbe=info,oldMasterSha256=sha(OLD/'captioned.mp4'),voiceSha256=sha(A/'voice/flow-map.wav'),narrationChanged=False,captionsChanged=False,gameAudioGain=0.035,speed=1,sourceKind='independent-gameplay',cleanSha256=sha(O/'clean.mp4'),captionedSha256=sha(O/'captioned.mp4')))
def qa():
 guard(); reports=[]
 for name in ['clean','captioned']:
  f=O/(name+'.mp4');run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
  info=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(f)])); v=next(s for s in info['streams'] if s['codec_type']=='video')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',N)
  reports.append(dict(path=rel(f),sha256=sha(f),probe=info,decodePass=True))
 q=O/'qa';q.mkdir(exist_ok=True)
 points=[25.4,25.45,25.7,26.5,27.5,28.5,29.5,30.18,30.22,47.25,47.3,47.6,48.4,48.8,49.5,50.5,51.0]
 for i,t in enumerate(points):
  target=q/f'{i:02}.jpg'
  if not target.exists():run(['ffmpeg','-v','error','-n','-ss',str(t),'-i',str(O/'captioned.mp4'),'-frames:v','1','-q:v','2',str(target)])
 for j in range(0,len(points),8):
  sheet=Image.new('RGB',(1500,1400),'#222222');d=ImageDraw.Draw(sheet)
  for k,t in enumerate(points[j:j+8]):
   im=Image.open(q/f'{j+k:02}.jpg');im.thumbnail((375,667));x=k%4*375;y=k//4*700;sheet.paste(im,(x,y));d.text((x+10,y+672),str(t),fill='white')
  sheet.save(q/f'sheet{j//8}.jpg')
 save(O/'integrity.json',dict(status='pass',outputs=reports,checkedFrames=points,humanReview='not-claimed'))
 html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>플로 맵 · 실제 게임 추가본</title><style>body{background:#171b19;color:white;font:16px sans-serif;margin:20px}video{width:375px;max-width:100%}button{padding:10px;margin:6px}</style><h2>플로 맵 · 실제 게임 추가본</h2><p>1080×1920 · 60fps · 51초</p><button onclick="v.currentTime=0;v.play()">전체 재생</button><button onclick="v.currentTime=24;v.play()">실제 게임 연결</button><button onclick="v.currentTime=46;v.play()">마무리 연결</button><button onclick="v.style.width='810px'">큰 화면</button><button onclick="v.style.width='375px'">모바일 크기</button><br><video id="v" src="captioned.mp4" controls preload="auto"></video></html>'''
 (O/'playback.html').write_text(html,encoding='utf-8')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['build','qa']);a=p.parse_args();globals()[a.command]()
